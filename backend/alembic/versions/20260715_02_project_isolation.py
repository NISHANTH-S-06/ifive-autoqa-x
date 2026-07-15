"""Add project membership and deterministic project isolation.

Revision ID: 20260715_02
Revises: 20260715_01
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = '20260715_02'
down_revision = '20260715_01'
branch_labels = None
depends_on = None


# Tables whose existing ``project_id`` refers to the legacy test-management
# project use ``access_project_id`` to avoid changing that public contract.
PROJECT_COLUMNS = {
  'connection_targets': 'project_id',
  'connection_target_versions': 'project_id',
  'connection_checks': 'project_id',
  'target_credential_profiles': 'project_id',
  'automated_runs': 'project_id',
  'automated_run_cases': 'project_id',
  'automated_step_results': 'project_id',
  'execution_jobs': 'project_id',
  'execution_attempts': 'project_id',
  'execution_events': 'project_id',
  'execution_artifacts': 'project_id',
  'test_results': 'project_id',
  'evidence': 'project_id',
  'test_projects': 'access_project_id',
  'test_modules': 'access_project_id',
  'managed_test_suites': 'access_project_id',
  'managed_test_cases': 'access_project_id',
  'test_case_steps': 'access_project_id',
  'test_case_versions': 'access_project_id',
  'test_case_tags': 'access_project_id',
  'manual_test_runs': 'access_project_id',
  'manual_test_run_cases': 'access_project_id',
  'manual_step_results': 'access_project_id',
  'manual_evidence': 'access_project_id',
  'defects': 'access_project_id',
  'defect_comments': 'project_id',
  'defect_history': 'project_id',
  'defect_evidence_links': 'project_id',
  'defect_retests': 'project_id',
  'report_exports': 'project_id',
  'report_definitions': 'project_id',
  'agent_suggestions': 'project_id',
  'test_results_legacy': 'project_id',
  'evidence_legacy': 'project_id',
  'defects_legacy': 'project_id',
}

IMMUTABLE_TABLES = {
  'connection_target_versions': 'connection_target_versions are append-only',
  'defect_comments': 'defect_comments are append-only',
  'defect_evidence_links': 'defect_evidence_links are append-only',
  'defect_history': 'defect_history is append-only',
  'defect_retests': 'defect_retests are append-only',
  'test_case_versions': 'test_case_versions are append-only',
}


def _restore_sqlite_triggers(connection) -> None:
  if connection.dialect.name != 'sqlite':
    return
  for table, message in IMMUTABLE_TABLES.items():
    for operation in ('update', 'delete'):
      connection.exec_driver_sql(
        f"CREATE TRIGGER IF NOT EXISTS {table}_no_{operation} "
        f"BEFORE {operation.upper()} ON {table} BEGIN "
        f"SELECT RAISE(ABORT, '{message}'); END"
      )


def _drop_sqlite_scope_triggers(connection) -> None:
  if connection.dialect.name != 'sqlite':
    return
  for table in IMMUTABLE_TABLES:
    for operation in ('update', 'delete'):
      connection.exec_driver_sql(f'DROP TRIGGER IF EXISTS {table}_no_{operation}')


def _scalar(connection, sql: str, **params) -> int:
  return int(connection.execute(sa.text(sql), params).scalar_one())


def _add_scope_columns() -> None:
  for table, column in PROJECT_COLUMNS.items():
    op.add_column(table, sa.Column(column, sa.Integer(), nullable=True))
    op.create_index(f'ix_{table}_{column}', table, [column], unique=False)


def _backfill(connection, legacy_id: int) -> None:
  # The managed ERP cases are the strongest relationship for the existing
  # target and its automated runs. This keeps every existing parent/child
  # chain in one project instead of guessing from the generic AUTOQA key.
  erp_id = connection.execute(
    sa.text("SELECT id FROM projects WHERE upper(product_code) = 'ERP' ORDER BY id LIMIT 1")
  ).scalar()
  target_project = int(erp_id or legacy_id)

  direct = {
    'connection_targets': f'UPDATE connection_targets SET project_id = {target_project}',
    'test_projects': (
      "UPDATE test_projects SET access_project_id = COALESCE((SELECT p.id FROM projects p "
      "WHERE upper(test_projects.code) LIKE '%' || upper(p.product_code) || '%' "
      "AND p.id <> :legacy_id ORDER BY length(p.product_code) DESC, p.id LIMIT 1), :legacy_id)"
    ),
    'test_results': (
      'UPDATE test_results SET project_id = '
      '(SELECT project_id FROM test_runs WHERE test_runs.id = test_results.test_run_id)'
    ),
    'evidence': (
      'UPDATE evidence SET project_id = '
      '(SELECT project_id FROM test_runs WHERE test_runs.id = evidence.test_run_id)'
    ),
    'report_exports': 'UPDATE report_exports SET project_id = :legacy_id',
    'report_definitions': 'UPDATE report_definitions SET project_id = :legacy_id',
    'agent_suggestions': 'UPDATE agent_suggestions SET project_id = :legacy_id',
    'test_results_legacy': (
      'UPDATE test_results_legacy SET project_id = '
      'COALESCE((SELECT project_id FROM test_runs WHERE test_runs.id = test_results_legacy.run_id), :legacy_id)'
    ),
  }
  for sql in direct.values():
    connection.execute(sa.text(sql), {'legacy_id': legacy_id})

  parent_mappings = {
    'connection_target_versions': ('connection_targets', 'target_id', 'project_id'),
    'connection_checks': ('connection_targets', 'target_id', 'project_id'),
    'target_credential_profiles': ('connection_targets', 'target_id', 'project_id'),
    'automated_runs': ('connection_targets', 'target_id', 'project_id'),
    'automated_run_cases': ('automated_runs', 'run_id', 'project_id'),
    'automated_step_results': ('automated_run_cases', 'run_case_id', 'project_id'),
    'execution_jobs': ('automated_runs', 'run_id', 'project_id'),
    'execution_attempts': ('automated_runs', 'run_id', 'project_id'),
    'execution_events': ('automated_runs', 'run_id', 'project_id'),
    'execution_artifacts': ('automated_runs', 'run_id', 'project_id'),
    'test_modules': ('test_projects', 'project_id', 'access_project_id'),
    'managed_test_suites': ('test_projects', 'project_id', 'access_project_id'),
    'managed_test_cases': ('test_projects', 'project_id', 'access_project_id'),
    'test_case_steps': ('managed_test_cases', 'test_case_id', 'access_project_id'),
    'test_case_versions': ('managed_test_cases', 'test_case_id', 'access_project_id'),
    'test_case_tags': ('managed_test_cases', 'test_case_id', 'access_project_id'),
    'manual_test_runs': ('test_projects', 'project_id', 'access_project_id'),
    'manual_test_run_cases': ('manual_test_runs', 'run_id', 'access_project_id'),
    'manual_step_results': ('manual_test_run_cases', 'run_case_id', 'access_project_id'),
    'manual_evidence': ('manual_test_run_cases', 'run_case_id', 'access_project_id'),
    'defects': ('test_projects', 'project_id', 'access_project_id'),
    'defect_comments': ('defects', 'defect_id', 'access_project_id'),
    'defect_history': ('defects', 'defect_id', 'access_project_id'),
    'defect_evidence_links': ('defects', 'defect_id', 'access_project_id'),
    'defect_retests': ('defects', 'defect_id', 'access_project_id'),
    'evidence_legacy': ('test_results_legacy', 'result_id', 'project_id'),
    'defects_legacy': ('test_results_legacy', 'result_id', 'project_id'),
  }
  for child, (parent, fk, parent_column) in parent_mappings.items():
    child_column = PROJECT_COLUMNS[child]
    connection.execute(sa.text(
      f'UPDATE {child} SET {child_column} = COALESCE('
      f'(SELECT {parent_column} FROM {parent} WHERE {parent}.id = {child}.{fk}), :legacy_id)'
    ), {'legacy_id': legacy_id})

  # Fail closed before making columns mandatory.
  for table, column in PROJECT_COLUMNS.items():
    missing = _scalar(connection, f'SELECT count(*) FROM {table} WHERE {column} IS NULL')
    if missing:
      raise RuntimeError(f'Project backfill left {missing} unscoped rows in {table}.{column}.')

  # One report row per mapped source row, including zero-row tables by absence.
  ambiguous_tables = {'report_exports', 'report_definitions', 'agent_suggestions'}
  for table, column in PROJECT_COLUMNS.items():
    decision = 'LEGACY_UNASSIGNED' if table in ambiguous_tables else 'RELATIONSHIP_DERIVED'
    ambiguous = 1 if table in ambiguous_tables else 0
    source_id = 'test_case_id' if table == 'test_case_tags' else 'id'
    connection.execute(sa.text(
      'INSERT INTO project_backfill_reports '
      '(source_table, source_id, project_id, decision, provenance, ambiguous, created_at) '
      f"SELECT :table, {source_id}, {column}, :decision, :provenance, :ambiguous, CURRENT_TIMESTAMP FROM {table}"
    ), {
      'table': table,
      'decision': decision,
      'provenance': (
        'No deterministic project relationship existed; retained under explicit Legacy / Unassigned scope.'
        if ambiguous else 'Mapped through an existing parent, run, target, or test-project relationship.'
      ),
      'ambiguous': ambiguous,
    })


def _backfill_memberships(connection, legacy_id: int) -> None:
  # Existing active global administrators retain justified emergency/admin
  # access to every project. INSERT OR IGNORE prevents duplicate memberships.
  connection.execute(sa.text(
    "INSERT OR IGNORE INTO project_members "
    "(project_id, operator_id, role, status, created_by, joined_at, created_at, updated_at) "
    "SELECT p.id, o.id, 'ADMIN', 'ACTIVE', o.id, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP "
    "FROM projects p JOIN operators o ON o.role = 'ADMIN' AND o.is_active = 1"
  ))

  # A legacy test-project creator is the only current creator relationship
  # that deterministically establishes ownership of a core project.
  connection.execute(sa.text(
    "INSERT OR IGNORE INTO project_members "
    "(project_id, operator_id, role, status, created_by, joined_at, created_at, updated_at) "
    "SELECT access_project_id, created_by, 'OWNER', 'ACTIVE', created_by, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP "
    "FROM test_projects"
  ))
  connection.execute(sa.text(
    "UPDATE project_members SET role = 'OWNER', updated_at = CURRENT_TIMESTAMP WHERE EXISTS ("
    "SELECT 1 FROM test_projects tp WHERE tp.access_project_id = project_members.project_id "
    "AND tp.created_by = project_members.operator_id)"
  ))

  # Preserve valid access held through existing records, while translating
  # global roles into the narrower project role vocabulary.
  sources = [
    ('connection_targets', 'project_id', 'created_by'),
    ('connection_targets', 'project_id', 'approved_by'),
    ('test_runs', 'project_id', 'created_by_operator_id'),
    ('defects', 'access_project_id', 'created_by'),
    ('defects', 'access_project_id', 'reporter_id'),
  ]
  for table, project_column, operator_column in sources:
    connection.execute(sa.text(
      "INSERT OR IGNORE INTO project_members "
      "(project_id, operator_id, role, status, created_by, joined_at, created_at, updated_at) "
      f"SELECT s.{project_column}, o.id, "
      "CASE o.role WHEN 'ADMIN' THEN 'ADMIN' WHEN 'APPROVER' THEN 'APPROVER' "
      "WHEN 'VIEWER' THEN 'VIEWER' ELSE 'TESTER' END, 'ACTIVE', o.id, "
      "CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP "
      f"FROM {table} s JOIN operators o ON o.id = s.{operator_column} "
      f"WHERE s.{operator_column} IS NOT NULL AND o.is_active = 1"
    ))

  connection.execute(sa.text(
    "INSERT INTO project_backfill_reports "
    "(source_table, source_id, project_id, decision, provenance, ambiguous, created_at) "
    "SELECT 'project_members', id, project_id, 'MEMBERSHIP_BACKFILL', "
    "'Derived from active administrator, creator, approver, run, or defect provenance.', 0, CURRENT_TIMESTAMP "
    "FROM project_members"
  ))


def upgrade() -> None:
  connection = op.get_bind()
  _drop_sqlite_scope_triggers(connection)
  connection.execute(sa.text(
    "INSERT INTO projects (name, product_code, description, environment, is_active, created_at, updated_at) "
    "SELECT 'Legacy / Unassigned', 'LEGACY', "
    "'Explicit holding scope for records with no deterministic historical project relationship.', "
    "'legacy', 0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP "
    "WHERE NOT EXISTS (SELECT 1 FROM projects WHERE name = 'Legacy / Unassigned')"
  ))
  legacy_id = _scalar(connection, "SELECT id FROM projects WHERE name = 'Legacy / Unassigned'")

  op.create_table(
    'project_members',
    sa.Column('id', sa.Integer(), primary_key=True),
    sa.Column('project_id', sa.Integer(), sa.ForeignKey('projects.id'), nullable=False),
    sa.Column('operator_id', sa.Integer(), sa.ForeignKey('operators.id'), nullable=False),
    sa.Column('role', sa.String(20), nullable=False),
    sa.Column('status', sa.String(20), nullable=False, server_default='ACTIVE'),
    sa.Column('created_by', sa.Integer(), sa.ForeignKey('operators.id'), nullable=True),
    sa.Column('joined_at', sa.DateTime(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('deactivated_at', sa.DateTime(), nullable=True),
    sa.CheckConstraint("role IN ('OWNER','ADMIN','APPROVER','TESTER','VIEWER')", name='ck_project_members_role'),
    sa.CheckConstraint("status IN ('ACTIVE','INACTIVE')", name='ck_project_members_status'),
    sa.UniqueConstraint('project_id', 'operator_id', name='uq_project_members_project_operator'),
  )
  op.create_index('ix_project_members_project_status', 'project_members', ['project_id', 'status'])
  op.create_index('ix_project_members_operator_status', 'project_members', ['operator_id', 'status'])
  op.create_index('ix_project_members_project_role', 'project_members', ['project_id', 'role'])

  op.create_table(
    'project_backfill_reports',
    sa.Column('id', sa.Integer(), primary_key=True),
    sa.Column('source_table', sa.String(80), nullable=False),
    sa.Column('source_id', sa.Integer(), nullable=True),
    sa.Column('project_id', sa.Integer(), sa.ForeignKey('projects.id'), nullable=False),
    sa.Column('decision', sa.String(40), nullable=False),
    sa.Column('provenance', sa.Text(), nullable=False),
    sa.Column('ambiguous', sa.Boolean(), nullable=False, server_default=sa.false()),
    sa.Column('created_at', sa.DateTime(), nullable=False),
  )
  op.create_index('ix_project_backfill_reports_source', 'project_backfill_reports', ['source_table', 'source_id'])
  op.create_index('ix_project_backfill_reports_project', 'project_backfill_reports', ['project_id'])
  op.create_index('ix_project_backfill_reports_ambiguous', 'project_backfill_reports', ['ambiguous'])

  _add_scope_columns()
  _backfill(connection, legacy_id)
  _backfill_memberships(connection, legacy_id)

  for table, column in PROJECT_COLUMNS.items():
    with op.batch_alter_table(table) as batch:
      batch.alter_column(column, existing_type=sa.Integer(), nullable=False)
      batch.create_foreign_key(f'fk_{table}_{column}_projects', 'projects', [column], ['id'])
  _restore_sqlite_triggers(connection)
  if connection.dialect.name == 'sqlite':
    violations = connection.exec_driver_sql('PRAGMA foreign_key_check').fetchall()
    if violations:
      raise RuntimeError(f'Project-isolation migration introduced FK violations: {violations[:5]}')


def downgrade() -> None:
  connection = op.get_bind()
  _drop_sqlite_scope_triggers(connection)
  for table, column in reversed(tuple(PROJECT_COLUMNS.items())):
    with op.batch_alter_table(table) as batch:
      batch.drop_constraint(f'fk_{table}_{column}_projects', type_='foreignkey')
      batch.drop_index(f'ix_{table}_{column}')
      batch.drop_column(column)
  op.drop_table('project_backfill_reports')
  op.drop_table('project_members')
  op.execute("DELETE FROM projects WHERE name = 'Legacy / Unassigned' AND product_code = 'LEGACY'")
  _restore_sqlite_triggers(connection)
  if connection.dialect.name == 'sqlite':
    violations = connection.exec_driver_sql('PRAGMA foreign_key_check').fetchall()
    if violations:
      raise RuntimeError(f'Project-isolation downgrade introduced FK violations: {violations[:5]}')
