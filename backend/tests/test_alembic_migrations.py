from pathlib import Path
import sqlite3

from alembic import command
from alembic.migration import MigrationContext
from alembic.script import ScriptDirectory
from alembic.autogenerate import compare_metadata
import pytest
from sqlalchemy import create_engine

from app.config import settings
from app.migration_config import make_alembic_config, validate_migration_url
from app.migration_metadata import get_migration_metadata
from app.migration_safety import (
  BASELINE_REVISION,
  PROJECT_ISOLATION_REVISION,
  TASK_CONNECTOR_REVISION,
  assert_database_at_head,
  assert_schema_matches,
  data_snapshot,
  database_health,
  schema_snapshot,
  stamp_existing_database,
)
from app.cli.recover_b2b_schema import prove_recovery_safe, recover


def sqlite_url(path: Path) -> str:
  return f'sqlite:///{path.as_posix()}'


def business_tables(database_url: str) -> set[str]:
  path = Path(database_url.removeprefix('sqlite:///'))
  connection = sqlite3.connect(path)
  try:
    return {
      row[0] for row in connection.execute(
        "SELECT name FROM sqlite_master WHERE type='table' "
        "AND name NOT LIKE 'sqlite_%' AND name <> 'alembic_version'"
      )
    }
  finally:
    connection.close()


def test_alembic_configuration_is_fail_closed_and_postgresql_ready(tmp_path):
  with pytest.raises(RuntimeError, match='required'):
    validate_migration_url('')
  with pytest.raises(RuntimeError, match='active application database'):
    validate_migration_url(settings.database_url)
  assert validate_migration_url(settings.database_url, allow_active=True) == settings.database_url
  assert validate_migration_url(sqlite_url(tmp_path / 'copy.db')).startswith('sqlite:///')
  assert validate_migration_url('postgresql+psycopg://migration_user@example.invalid/autoqa').startswith('postgresql')


def test_application_startup_requires_alembic_head(tmp_path):
  database_url = sqlite_url(tmp_path / 'startup-guard.db')
  command.upgrade(make_alembic_config(database_url), BASELINE_REVISION)
  with pytest.raises(RuntimeError, match='Database migration required before startup'):
    assert_database_at_head(database_url)
  command.upgrade(make_alembic_config(database_url), 'head')
  from alembic.script import ScriptDirectory
  expected_head = ScriptDirectory.from_config(make_alembic_config(database_url)).get_current_head()
  assert assert_database_at_head(database_url) == expected_head


def test_targeted_recovery_removes_only_verified_empty_accidental_tables(tmp_path):
  reference_path = tmp_path / 'recovery-reference.db'
  candidate_path = tmp_path / 'recovery-candidate.db'
  command.upgrade(make_alembic_config(sqlite_url(reference_path)), BASELINE_REVISION)
  candidate_path.write_bytes(reference_path.read_bytes())
  connection = sqlite3.connect(candidate_path)
  try:
    connection.execute('CREATE TABLE project_members (id INTEGER PRIMARY KEY)')
    connection.execute('CREATE TABLE project_backfill_reports (id INTEGER PRIMARY KEY)')
    connection.commit()
  finally:
    connection.close()
  proof = prove_recovery_safe(candidate_path, reference_path)
  assert proof['extra_tables'] == ['project_backfill_reports', 'project_members']
  assert proof['accidental_rows'] == {'project_backfill_reports': 0, 'project_members': 0}
  result = recover(candidate_path, reference_path)
  assert result['recovered_table_count'] == 45
  assert schema_snapshot(sqlite_url(candidate_path)) == schema_snapshot(sqlite_url(reference_path))


def test_migration_metadata_matches_existing_schema(tmp_path):
  database_url = sqlite_url(tmp_path / 'metadata.db')
  command.upgrade(make_alembic_config(database_url), 'head')
  engine = create_engine(database_url)
  try:
    with engine.connect() as connection:
      context = MigrationContext.configure(
        connection, opts={'compare_type': True, 'compare_server_default': True}
      )
      diffs = compare_metadata(context, get_migration_metadata())
      assert isinstance(diffs, list)
  finally:
    engine.dispose()


@pytest.fixture
def rehearsal_database_url(tmp_path):
  database_url = sqlite_url(tmp_path / 'existing.db')
  command.upgrade(make_alembic_config(database_url), BASELINE_REVISION)
  command.stamp(make_alembic_config(database_url), 'base', purge=True)
  connection = sqlite3.connect(tmp_path / 'existing.db')
  try:
    connection.execute(
      "INSERT INTO projects (name, product_code, description, environment, is_active, created_at, updated_at) "
      "VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)",
      ('Migration fixture', 'MIGRATION', 'Synthetic migration test row.', 'test', 1),
    )
    connection.commit()
  finally:
    connection.close()
  return database_url


def test_empty_database_upgrade_to_head(tmp_path):
  database_url = sqlite_url(tmp_path / 'empty-upgrade.db')
  command.upgrade(make_alembic_config(database_url), 'head')
  snapshot = schema_snapshot(database_url)
  assert len(snapshot['tables']) == 147
  assert len(snapshot['triggers']) == 16
  connection = sqlite3.connect(tmp_path / 'empty-upgrade.db')
  try:
    expected_head = ScriptDirectory.from_config(make_alembic_config(database_url)).get_current_head()
    assert connection.execute('SELECT version_num FROM alembic_version').fetchone() == (expected_head,)
  finally:
    connection.close()
  assert database_health(database_url).integrity == 'ok'
  assert database_health(database_url).foreign_key_violations == 0


def test_existing_database_is_compared_then_stamped_without_data_loss(tmp_path, rehearsal_database_url):
  before = data_snapshot(rehearsal_database_url)
  result = stamp_existing_database(rehearsal_database_url, tmp_path / 'reference')
  assert result.revision == BASELINE_REVISION
  assert result.table_count == 45
  assert result.row_counts['projects'] == 1
  assert data_snapshot(rehearsal_database_url) == before


def test_active_snapshot_ignores_only_worker_heartbeat_timestamps(tmp_path):
  database_url = sqlite_url(tmp_path / 'worker-heartbeat.db')
  connection = sqlite3.connect(tmp_path / 'worker-heartbeat.db')
  try:
    connection.execute(
      'CREATE TABLE execution_workers ('
      'id INTEGER PRIMARY KEY, worker_key TEXT, status TEXT, heartbeat_at TEXT, updated_at TEXT)'
    )
    connection.execute(
      'INSERT INTO execution_workers VALUES (1, ?, ?, ?, ?)',
      ('worker-1', 'ONLINE', '2026-07-15 12:00:00', '2026-07-15 12:00:00'),
    )
    connection.commit()
  finally:
    connection.close()

  before_exact = data_snapshot(database_url)
  before_stable = data_snapshot(database_url, ignore_worker_heartbeat=True)
  connection = sqlite3.connect(tmp_path / 'worker-heartbeat.db')
  try:
    connection.execute(
      'UPDATE execution_workers SET heartbeat_at = ?, updated_at = ? WHERE id = 1',
      ('2026-07-15 12:01:00', '2026-07-15 12:01:00'),
    )
    connection.commit()
  finally:
    connection.close()

  assert data_snapshot(database_url) != before_exact
  assert data_snapshot(database_url, ignore_worker_heartbeat=True) == before_stable


def test_schema_mismatch_blocks_existing_database_stamp(tmp_path, rehearsal_database_url):
  reference_url = sqlite_url(tmp_path / 'reference.db')
  command.upgrade(make_alembic_config(reference_url), 'head')
  connection = sqlite3.connect(Path(rehearsal_database_url.removeprefix('sqlite:///')))
  try:
    connection.execute('CREATE TABLE unexpected_table (id INTEGER PRIMARY KEY)')
    connection.commit()
  finally:
    connection.close()
  with pytest.raises(RuntimeError, match='schema does not match'):
    assert_schema_matches(reference_url, rehearsal_database_url)


def test_empty_database_downgrade_and_upgrade_rehearsal(tmp_path):
  database_url = sqlite_url(tmp_path / 'rollback.db')
  baseline_url = sqlite_url(tmp_path / 'rollback-baseline-reference.db')
  command.upgrade(make_alembic_config(baseline_url), BASELINE_REVISION)
  command.upgrade(make_alembic_config(database_url), 'head')
  first_schema = schema_snapshot(database_url)
  command.downgrade(make_alembic_config(database_url), BASELINE_REVISION)
  assert len(business_tables(database_url)) == 45
  assert schema_snapshot(database_url) == schema_snapshot(baseline_url)
  command.upgrade(make_alembic_config(database_url), 'head')
  assert schema_snapshot(database_url) == first_schema
  assert database_health(database_url).integrity == 'ok'
  assert database_health(database_url).foreign_key_violations == 0
