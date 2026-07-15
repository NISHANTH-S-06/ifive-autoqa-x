from __future__ import annotations

from sqlalchemy import Column, DefaultClause, ForeignKey, Index, Integer, MetaData, String, Table, Text, text

from app.database import Base
from app.models import (
  agent_suggestion,
  audit_event,
  automated_execution,
  connection_target,
  defect,
  evidence,
  operator,
  operator_session,
  password_history,
  project,
  reporting,
  test_case,
  test_management,
  test_result,
  test_run,
  test_suite,
)


# These imports register all 42 current ORM tables on Base.metadata. The names
# are retained above deliberately so static analysis does not remove them.
_REGISTERED_MODEL_MODULES = (
  agent_suggestion, audit_event, automated_execution, connection_target,
  defect, evidence, operator, operator_session, password_history, project,
  reporting, test_case, test_management, test_result, test_run, test_suite,
)

_LEGACY_SERVER_DEFAULTS = {
  ('automated_runs', 'risk_level'): "'READ_ONLY'",
  ('automated_runs', 'preflight_status'): "'PENDING'",
  ('automated_runs', 'dns_pinning_status'): "'PENDING'",
  ('automated_runs', 'runtime_secret_status'): "'NOT_REQUIRED'",
  ('connection_targets', 'execution_enabled'): '0',
  ('operator_sessions', 'password_version_at_login'): '1',
  ('operators', 'password_version'): '1',
}


def _add_legacy_tables(metadata: MetaData) -> None:
  legacy_results = Table(
    'test_results_legacy', metadata,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('run_id', Integer, ForeignKey('test_runs.id'), nullable=False),
    Column('test_case_id', Integer, ForeignKey('test_cases.id'), nullable=False),
    Column('status', String(40), nullable=False),
    Column('duration_ms', Integer, nullable=False),
    Column('error_message', Text),
  )
  Index('ix_test_results_id', legacy_results.c.id)

  legacy_evidence = Table(
    'evidence_legacy', metadata,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('result_id', Integer, ForeignKey('test_results_legacy.id'), nullable=False),
    Column('evidence_type', String(40), nullable=False),
    Column('path', String(500), nullable=False),
  )
  Index('ix_evidence_id', legacy_evidence.c.id)

  legacy_defects = Table(
    'defects_legacy', metadata,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('result_id', Integer, ForeignKey('test_results_legacy.id'), nullable=False),
    Column('title', String(220), nullable=False),
    Column('severity', String(40), nullable=False),
    Column('owner', String(120)),
    Column('status', String(40), nullable=False),
  )
  Index('ix_defects_id', legacy_defects.c.id)


def get_migration_metadata() -> MetaData:
  """Return migration metadata matching the validated pre-Alembic schema."""
  metadata = MetaData()
  for table in Base.metadata.sorted_tables:
    table.to_metadata(metadata)

  # The ORM declared this index, but it was never created by the legacy schema.
  # Preserve the database exactly in the baseline; a later migration may add it.
  results = metadata.tables['test_results']
  for index in tuple(results.indexes):
    if index.name == 'ix_test_results_test_run_id':
      results.indexes.remove(index)

  for (table_name, column_name), default_sql in _LEGACY_SERVER_DEFAULTS.items():
    metadata.tables[table_name].c[column_name].server_default = DefaultClause(text(default_sql))

  _add_legacy_tables(metadata)
  return metadata
