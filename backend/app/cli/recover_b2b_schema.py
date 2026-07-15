from __future__ import annotations

import argparse
import json
from pathlib import Path
import sqlite3

from app.migration_safety import data_snapshot, database_health, schema_snapshot


ACCIDENTAL_TABLES = {'project_members', 'project_backfill_reports'}


def _url(path: Path) -> str:
  return f'sqlite:///{path.resolve().as_posix()}'


def _quote(identifier: str) -> str:
  return '"' + identifier.replace('"', '""') + '"'


def prove_recovery_safe(database: Path, reference: Path) -> dict:
  database_url = _url(database)
  reference_url = _url(reference)
  live_schema = schema_snapshot(database_url, allow_active=True)
  reference_schema = schema_snapshot(reference_url)
  live_tables = set(live_schema['tables'])
  reference_tables = set(reference_schema['tables'])
  extra = live_tables - reference_tables
  missing = reference_tables - live_tables
  if extra != ACCIDENTAL_TABLES or missing:
    raise RuntimeError(f'Unexpected schema delta: extra={sorted(extra)}, missing={sorted(missing)}.')
  if any(live_schema['tables'][name] != reference_schema['tables'][name] for name in reference_tables):
    raise RuntimeError('A pre-existing table differs from the approved B2B preflight schema.')

  health = database_health(database_url, allow_active=True)
  if health.integrity != 'ok' or health.foreign_key_violations:
    raise RuntimeError(f'Active database health check failed: {health}.')

  live_data = data_snapshot(database_url, allow_active=True, ignore_worker_heartbeat=True)
  reference_data = data_snapshot(reference_url, ignore_worker_heartbeat=True)
  differences = {
    name: {'reference': reference_data[name], 'active': live_data[name]}
    for name in sorted(reference_tables)
    if reference_data[name] != live_data[name]
  }
  if differences:
    raise RuntimeError(f'Pre-existing data differs from the approved preflight copy: {differences}.')

  connection = sqlite3.connect(database)
  try:
    accidental_rows = {
      name: connection.execute(f'SELECT COUNT(1) FROM {_quote(name)}').fetchone()[0]
      for name in sorted(ACCIDENTAL_TABLES)
    }
    if any(accidental_rows.values()):
      raise RuntimeError(f'Accidental tables are not empty: {accidental_rows}.')
    dependent_rows: list[dict] = []
    for table in sorted(live_tables):
      for foreign_key in connection.execute(f'PRAGMA foreign_key_list({_quote(table)})'):
        referred_table = foreign_key[2]
        source_column = foreign_key[3]
        if referred_table not in ACCIDENTAL_TABLES:
          continue
        count = connection.execute(
          f'SELECT COUNT(1) FROM {_quote(table)} WHERE {_quote(source_column)} IS NOT NULL'
        ).fetchone()[0]
        dependent_rows.append({
          'table': table,
          'column': source_column,
          'referred_table': referred_table,
          'rows': count,
        })
    if any(item['rows'] for item in dependent_rows):
      raise RuntimeError(f'Foreign-key data depends on an accidental table: {dependent_rows}.')
    version = connection.execute('SELECT version_num FROM alembic_version').fetchone()
  finally:
    connection.close()
  return {
    'active_revision': version[0] if version else None,
    'active_table_count': len(live_tables),
    'reference_table_count': len(reference_tables),
    'extra_tables': sorted(extra),
    'accidental_rows': accidental_rows,
    'foreign_key_references': dependent_rows,
    'common_schema_equal': True,
    'common_data_equal': True,
    'integrity': health.integrity,
    'foreign_key_violations': health.foreign_key_violations,
  }


def recover(database: Path, reference: Path) -> dict:
  proof = prove_recovery_safe(database, reference)
  connection = sqlite3.connect(database, isolation_level=None)
  try:
    connection.execute('PRAGMA foreign_keys=ON')
    connection.execute('PRAGMA wal_checkpoint(FULL)')
    connection.execute('BEGIN IMMEDIATE')
    connection.execute('DROP TABLE project_backfill_reports')
    connection.execute('DROP TABLE project_members')
    connection.execute('COMMIT')
    connection.execute('PRAGMA wal_checkpoint(TRUNCATE)')
  except Exception:
    if connection.in_transaction:
      connection.execute('ROLLBACK')
    raise
  finally:
    connection.close()

  database_url = _url(database)
  reference_url = _url(reference)
  if schema_snapshot(database_url, allow_active=True) != schema_snapshot(reference_url):
    raise RuntimeError('Targeted recovery did not reproduce the exact approved 45-table schema.')
  live_data = data_snapshot(database_url, allow_active=True, ignore_worker_heartbeat=True)
  reference_data = data_snapshot(reference_url, ignore_worker_heartbeat=True)
  if live_data != reference_data:
    raise RuntimeError('Targeted recovery changed or failed to reproduce approved preflight data.')
  health = database_health(database_url, allow_active=True)
  if health.integrity != 'ok' or health.foreign_key_violations:
    raise RuntimeError(f'Post-recovery database health check failed: {health}.')
  return {
    **proof,
    'recovered_table_count': len(schema_snapshot(database_url, allow_active=True)['tables']),
    'post_recovery_schema_equal': True,
    'post_recovery_data_equal': True,
    'post_recovery_integrity': health.integrity,
    'post_recovery_foreign_key_violations': health.foreign_key_violations,
  }


def main() -> None:
  parser = argparse.ArgumentParser(description='Recover the two verified-empty B2B tables created outside Alembic.')
  parser.add_argument('--database', type=Path, required=True)
  parser.add_argument('--reference', type=Path, required=True)
  parser.add_argument('--execute', action='store_true')
  args = parser.parse_args()
  result = recover(args.database, args.reference) if args.execute else prove_recovery_safe(args.database, args.reference)
  print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
  main()
