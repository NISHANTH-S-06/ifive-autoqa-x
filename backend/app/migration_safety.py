from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
import sqlite3
from typing import Any
from uuid import uuid4

from alembic import command
from sqlalchemy import create_engine, inspect

from app.migration_config import make_alembic_config, sqlite_path_for_url, validate_migration_url


BASELINE_REVISION = '20260715_01'


@dataclass(frozen=True)
class DatabaseHealth:
  integrity: str
  foreign_key_violations: int


@dataclass(frozen=True)
class StampResult:
  revision: str
  table_count: int
  row_counts: dict[str, int]
  health: DatabaseHealth


def _normalized_default(value: Any) -> str | None:
  if value is None:
    return None
  normalized = ' '.join(str(value).strip().split())
  while normalized.startswith('(') and normalized.endswith(')'):
    normalized = normalized[1:-1].strip()
  return normalized


def _sorted_constraints(items: list[dict], keys: tuple[str, ...]) -> list[dict]:
  normalized = [{key: item.get(key) for key in keys} for item in items]
  return sorted(normalized, key=lambda item: json.dumps(item, sort_keys=True, default=str))


def schema_snapshot(database_url: str, *, allow_active: bool = False) -> dict[str, Any]:
  validated = validate_migration_url(database_url, allow_active=allow_active)
  engine = create_engine(validated)
  try:
    inspector = inspect(engine)
    table_names = sorted(name for name in inspector.get_table_names() if name != 'alembic_version')
    tables: dict[str, Any] = {}
    for table_name in table_names:
      columns = sorted([
        {
          'name': column['name'],
          'type': str(column['type']).upper(),
          'nullable': bool(column['nullable']),
          'default': _normalized_default(column.get('default')),
        }
        for column in inspector.get_columns(table_name)
      ], key=lambda column: column['name'])
      tables[table_name] = {
        'columns': columns,
        'primary_key': list(inspector.get_pk_constraint(table_name).get('constrained_columns') or []),
        'indexes': _sorted_constraints(
          inspector.get_indexes(table_name), ('name', 'column_names', 'unique')
        ),
        'unique_constraints': _sorted_constraints(
          inspector.get_unique_constraints(table_name), ('name', 'column_names')
        ),
        'foreign_keys': _sorted_constraints(
          inspector.get_foreign_keys(table_name),
          ('name', 'constrained_columns', 'referred_schema', 'referred_table', 'referred_columns', 'options'),
        ),
        'check_constraints': _sorted_constraints(
          inspector.get_check_constraints(table_name), ('name', 'sqltext')
        ),
      }
    triggers: dict[str, str] = {}
    if engine.dialect.name == 'sqlite':
      with engine.connect() as connection:
        rows = connection.exec_driver_sql(
          "SELECT name, sql FROM sqlite_master WHERE type='trigger' ORDER BY name"
        )
        triggers = {name: ' '.join(sql.split()) for name, sql in rows}
    return {'tables': tables, 'triggers': triggers}
  finally:
    engine.dispose()


def assert_schema_matches(reference_url: str, candidate_url: str) -> None:
  reference = schema_snapshot(reference_url)
  candidate = schema_snapshot(candidate_url)
  if reference != candidate:
    reference_tables = set(reference['tables'])
    candidate_tables = set(candidate['tables'])
    raise RuntimeError(
      'Existing database schema does not match the Alembic baseline: '
      f'missing={sorted(reference_tables - candidate_tables)}, '
      f'extra={sorted(candidate_tables - reference_tables)}, '
      f'detail_match={reference == candidate}.'
    )


def database_health(database_url: str, *, allow_active: bool = False) -> DatabaseHealth:
  validated = validate_migration_url(database_url, allow_active=allow_active)
  path = sqlite_path_for_url(validated)
  connection = sqlite3.connect(path)
  try:
    integrity = connection.execute('PRAGMA integrity_check').fetchone()[0]
    violations = len(connection.execute('PRAGMA foreign_key_check').fetchall())
    return DatabaseHealth(integrity=integrity, foreign_key_violations=violations)
  finally:
    connection.close()


def data_snapshot(database_url: str, *, allow_active: bool = False) -> dict[str, dict[str, Any]]:
  validated = validate_migration_url(database_url, allow_active=allow_active)
  path = sqlite_path_for_url(validated)
  connection = sqlite3.connect(path)
  try:
    tables = [
      row[0] for row in connection.execute(
        "SELECT name FROM sqlite_master WHERE type='table' "
        "AND name NOT LIKE 'sqlite_%' AND name <> 'alembic_version' ORDER BY name"
      )
    ]
    snapshot: dict[str, dict[str, Any]] = {}
    for table_name in tables:
      quoted = '"' + table_name.replace('"', '""') + '"'
      columns = [row[1] for row in connection.execute(f'PRAGMA table_info({quoted})')]
      rows = connection.execute(f'SELECT * FROM {quoted} ORDER BY rowid').fetchall()
      encoded_rows = [
        [value.hex() if isinstance(value, bytes) else value for value in row]
        for row in rows
      ]
      payload = json.dumps({'columns': columns, 'rows': encoded_rows}, sort_keys=True, default=str).encode()
      snapshot[table_name] = {'rows': len(rows), 'sha256': sha256(payload).hexdigest()}
    return snapshot
  finally:
    connection.close()


def stamp_existing_database(database_url: str, reference_directory: Path) -> StampResult:
  """Schema-compare and stamp an existing copied SQLite database without data changes."""
  validated = validate_migration_url(database_url)
  before_health = database_health(validated)
  if before_health.integrity != 'ok' or before_health.foreign_key_violations:
    raise RuntimeError(f'Existing database health check failed: {before_health}.')
  before_schema = schema_snapshot(validated)
  before_data = data_snapshot(validated)

  reference_directory.mkdir(parents=True, exist_ok=True)
  reference_path = reference_directory / f'alembic-baseline-reference-{uuid4().hex}.db'
  reference_url = f'sqlite:///{reference_path.as_posix()}'
  try:
    command.upgrade(make_alembic_config(reference_url), 'head')
    assert_schema_matches(reference_url, validated)
    command.stamp(make_alembic_config(validated), BASELINE_REVISION)
    command.upgrade(make_alembic_config(validated), 'head')

    after_schema = schema_snapshot(validated)
    after_data = data_snapshot(validated)
    after_health = database_health(validated)
    if before_schema != after_schema:
      raise RuntimeError('Stamping changed the existing business schema.')
    if before_data != after_data:
      raise RuntimeError('Stamping or head upgrade changed existing data.')
    if after_health.integrity != 'ok' or after_health.foreign_key_violations:
      raise RuntimeError(f'Post-stamp database health check failed: {after_health}.')
    return StampResult(
      revision=BASELINE_REVISION,
      table_count=len(after_schema['tables']),
      row_counts={name: detail['rows'] for name, detail in after_data.items()},
      health=after_health,
    )
  finally:
    if reference_path.exists():
      reference_path.unlink()
