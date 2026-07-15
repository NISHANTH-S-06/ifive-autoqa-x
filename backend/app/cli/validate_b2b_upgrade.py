from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import sqlite3

from app.migration_safety import PROJECT_ISOLATION_REVISION, database_health, schema_snapshot


def _url(path: Path) -> str:
  return f'sqlite:///{path.resolve().as_posix()}'


def _quote(identifier: str) -> str:
  return '"' + identifier.replace('"', '""') + '"'


def _table_columns(connection: sqlite3.Connection, table: str) -> list[str]:
  return [row[1] for row in connection.execute(f'PRAGMA table_info({_quote(table)})')]


def _primary_key_columns(connection: sqlite3.Connection, table: str) -> list[str]:
  return [row[1] for row in sorted(
    (row for row in connection.execute(f'PRAGMA table_info({_quote(table)})') if row[5]),
    key=lambda row: row[5],
  )]


def _rows(connection: sqlite3.Connection, table: str, columns: list[str], allowed_ids: list | None = None) -> list[list]:
  selected = ', '.join(_quote(column) for column in columns)
  primary_key = _primary_key_columns(connection, table)
  order = ', '.join(_quote(column) for column in primary_key) if primary_key else 'rowid'
  parameters: tuple = ()
  where = ''
  if allowed_ids is not None:
    if primary_key != ['id']:
      raise RuntimeError(f'Expected a single id primary key for filtered table {table}.')
    placeholders = ','.join('?' for _ in allowed_ids)
    where = f' WHERE "id" IN ({placeholders})'
    parameters = tuple(allowed_ids)
  values = connection.execute(
    f'SELECT {selected} FROM {_quote(table)}{where} ORDER BY {order}', parameters
  ).fetchall()
  return [[value.hex() if isinstance(value, bytes) else value for value in row] for row in values]


def validate(database: Path, reference: Path) -> dict:
  candidate_url = _url(database)
  reference_url = _url(reference)
  candidate_schema = schema_snapshot(candidate_url, allow_active=True)
  reference_schema = schema_snapshot(reference_url)
  if len(candidate_schema['tables']) != 47 or len(reference_schema['tables']) != 45:
    raise RuntimeError('Expected 47 migrated tables and 45 approved preflight tables.')
  if set(candidate_schema['tables']) - set(reference_schema['tables']) != {'project_members', 'project_backfill_reports'}:
    raise RuntimeError('Unexpected post-migration table set.')
  if len(candidate_schema['triggers']) != 16:
    raise RuntimeError(f'Expected 16 protected triggers, found {len(candidate_schema["triggers"])}.')

  candidate = sqlite3.connect(database)
  reference_db = sqlite3.connect(reference)
  try:
    version = candidate.execute('SELECT version_num FROM alembic_version').fetchone()
    if version != (PROJECT_ISOLATION_REVISION,):
      raise RuntimeError(f'Unexpected Alembic revision: {version}.')
    reference_tables = sorted(reference_schema['tables'])
    table_results: dict[str, dict] = {}
    combined_reference: dict[str, list] = {}
    combined_candidate: dict[str, list] = {}
    project_ids = [row[0] for row in reference_db.execute('SELECT id FROM projects ORDER BY id')]
    for table in reference_tables:
      columns = _table_columns(reference_db, table)
      if table == 'execution_workers':
        columns = [column for column in columns if column not in {'heartbeat_at', 'updated_at'}]
      reference_rows = _rows(reference_db, table, columns)
      allowed_ids = project_ids if table == 'projects' else None
      candidate_rows = _rows(candidate, table, columns, allowed_ids=allowed_ids)
      if candidate_rows != reference_rows:
        raise RuntimeError(f'Existing IDs or values changed in {table}.')
      reference_count = reference_db.execute(f'SELECT COUNT(1) FROM {_quote(table)}').fetchone()[0]
      candidate_count = candidate.execute(f'SELECT COUNT(1) FROM {_quote(table)}').fetchone()[0]
      expected_candidate_count = reference_count + (1 if table == 'projects' else 0)
      if candidate_count != expected_candidate_count:
        raise RuntimeError(
          f'Unexpected row count for {table}: reference={reference_count}, candidate={candidate_count}.'
        )
      table_results[table] = {
        'reference_rows': reference_count,
        'candidate_rows': candidate_count,
        'existing_ids_and_values_preserved': True,
      }
      combined_reference[table] = reference_rows
      combined_candidate[table] = candidate_rows

    legacy = candidate.execute(
      "SELECT id, name, product_code, is_active FROM projects WHERE name = 'Legacy / Unassigned'"
    ).fetchall()
    if len(legacy) != 1 or legacy[0][2:] != ('LEGACY', 0):
      raise RuntimeError(f'Legacy / Unassigned project is missing or invalid: {legacy}.')
    legacy_id = legacy[0][0]

    memberships = candidate.execute('SELECT COUNT(1) FROM project_members').fetchone()[0]
    backfill_rows = candidate.execute('SELECT COUNT(1) FROM project_backfill_reports').fetchone()[0]
    ambiguous = candidate.execute(
      'SELECT source_table, COUNT(1) FROM project_backfill_reports '
      'WHERE ambiguous = 1 GROUP BY source_table ORDER BY source_table'
    ).fetchall()
    if memberships != 9 or backfill_rows != 139 or ambiguous != [('report_exports', 2)]:
      raise RuntimeError(
        f'Backfill differs from rehearsal: memberships={memberships}, reports={backfill_rows}, ambiguous={ambiguous}.'
      )
    ambiguous_wrong_project = candidate.execute(
      'SELECT COUNT(1) FROM project_backfill_reports WHERE ambiguous = 1 AND project_id != ?', (legacy_id,)
    ).fetchone()[0]
    if ambiguous_wrong_project:
      raise RuntimeError('An ambiguous row was not assigned to Legacy / Unassigned.')

    invalid_scopes: dict[str, dict] = {}
    project_id_set = {row[0] for row in candidate.execute('SELECT id FROM projects')}
    for table in reference_tables:
      reference_columns = set(_table_columns(reference_db, table))
      for column in set(_table_columns(candidate, table)) - reference_columns:
        if column not in {'project_id', 'access_project_id'}:
          continue
        null_count = candidate.execute(
          f'SELECT COUNT(1) FROM {_quote(table)} WHERE {_quote(column)} IS NULL'
        ).fetchone()[0]
        values = {row[0] for row in candidate.execute(
          f'SELECT DISTINCT {_quote(column)} FROM {_quote(table)} WHERE {_quote(column)} IS NOT NULL'
        )}
        missing_projects = sorted(values - project_id_set)
        if null_count or missing_projects:
          invalid_scopes[f'{table}.{column}'] = {
            'null_rows': null_count,
            'missing_project_ids': missing_projects,
          }
    if invalid_scopes:
      raise RuntimeError(f'Unauthorized global or invalid project scope remains: {invalid_scopes}.')

    duplicate_memberships = candidate.execute(
      'SELECT COUNT(1) FROM (SELECT project_id, operator_id FROM project_members '
      'GROUP BY project_id, operator_id HAVING COUNT(1) > 1)'
    ).fetchone()[0]
    if duplicate_memberships:
      raise RuntimeError('Duplicate project memberships were created.')
  finally:
    candidate.close()
    reference_db.close()

  health = database_health(candidate_url, allow_active=True)
  if health.integrity != 'ok' or health.foreign_key_violations:
    raise RuntimeError(f'Migrated database health check failed: {health}.')
  encoded_reference = json.dumps(combined_reference, sort_keys=True, default=str).encode()
  encoded_candidate = json.dumps(combined_candidate, sort_keys=True, default=str).encode()
  return {
    'revision': PROJECT_ISOLATION_REVISION,
    'table_count': len(candidate_schema['tables']),
    'trigger_count': len(candidate_schema['triggers']),
    'memberships': memberships,
    'backfill_rows': backfill_rows,
    'ambiguous_rows': [{'source_table': table, 'rows': count} for table, count in ambiguous],
    'legacy_project_id': legacy_id,
    'original_tables_reconciled': len(table_results),
    'original_data_sha256': sha256(encoded_reference).hexdigest(),
    'candidate_preserved_data_sha256': sha256(encoded_candidate).hexdigest(),
    'existing_ids_and_values_preserved': encoded_reference == encoded_candidate,
    'invalid_or_global_scopes': invalid_scopes,
    'integrity': health.integrity,
    'foreign_key_violations': health.foreign_key_violations,
  }


def main() -> None:
  parser = argparse.ArgumentParser(description='Validate the active B2B project-isolation upgrade.')
  parser.add_argument('--database', type=Path, required=True)
  parser.add_argument('--reference', type=Path, required=True)
  args = parser.parse_args()
  print(json.dumps(validate(args.database, args.reference), indent=2, sort_keys=True))


if __name__ == '__main__':
  main()
