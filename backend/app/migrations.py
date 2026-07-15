from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine


RUN_COLUMNS = {
  'approved_at': 'DATETIME',
  'exit_code': 'INTEGER',
  'error_summary': 'TEXT',
  'result_json_path': 'VARCHAR(500)',
  'html_report_path': 'VARCHAR(500)',
  'stdout_log_path': 'VARCHAR(500)',
  'stderr_log_path': 'VARCHAR(500)',
  'created_by_operator_id': 'INTEGER REFERENCES operators(id)',
  'approved_by_operator_id': 'INTEGER REFERENCES operators(id)',
  'executed_by_operator_id': 'INTEGER REFERENCES operators(id)',
  'cancelled_by_operator_id': 'INTEGER REFERENCES operators(id)',
}

OPERATOR_COLUMNS = {
  'password_changed_at': 'DATETIME',
  'password_expires_at': 'DATETIME',
  'password_version': 'INTEGER NOT NULL DEFAULT 1',
  'force_password_change_reason': 'VARCHAR(80)',
  'credentials_updated_at': 'DATETIME',
}

SESSION_COLUMNS = {
  'session_name': 'VARCHAR(160)',
  'revoked_by_operator_id': 'INTEGER REFERENCES operators(id)',
  'revoke_reason': 'VARCHAR(200)',
  'last_activity_at': 'DATETIME',
  'password_version_at_login': 'INTEGER NOT NULL DEFAULT 1',
}

CONNECTION_TARGET_COLUMNS = {
  'execution_enabled': 'BOOLEAN NOT NULL DEFAULT 0',
  'execution_submitted_by': 'INTEGER REFERENCES operators(id)',
  'execution_submitted_at': 'DATETIME',
  'execution_approved_by': 'INTEGER REFERENCES operators(id)',
  'execution_approved_at': 'DATETIME',
}

AUTOMATED_RUN_COLUMNS = {
  'risk_level': "VARCHAR(30) NOT NULL DEFAULT 'READ_ONLY'",
  'preflight_status': "VARCHAR(30) NOT NULL DEFAULT 'PENDING'",
  'dns_pinning_status': "VARCHAR(30) NOT NULL DEFAULT 'PENDING'",
  'runtime_secret_status': "VARCHAR(80) NOT NULL DEFAULT 'NOT_REQUIRED'",
}

REPORT_EXPORT_COLUMNS = {
  'export_key',
  'report_type',
  'export_format',
  'filters_json',
  'relative_path',
  'sha256',
  'created_by',
}

REPORT_DEFINITION_COLUMNS = {
  'name',
  'report_type',
  'filters_json',
  'frequency',
  'enabled',
  'owner_operator_id',
}


AUDIT_TRIGGERS = (
  "CREATE TRIGGER IF NOT EXISTS audit_events_no_update BEFORE UPDATE ON audit_events BEGIN SELECT RAISE(ABORT, 'audit_events are append-only'); END",
  "CREATE TRIGGER IF NOT EXISTS audit_events_no_delete BEFORE DELETE ON audit_events BEGIN SELECT RAISE(ABORT, 'audit_events are append-only'); END",
)

PASSWORD_HISTORY_TRIGGERS = (
  "CREATE TRIGGER IF NOT EXISTS password_history_no_update BEFORE UPDATE ON password_history BEGIN SELECT RAISE(ABORT, 'password_history is append-only'); END",
  "CREATE TRIGGER IF NOT EXISTS password_history_no_delete BEFORE DELETE ON password_history BEGIN SELECT RAISE(ABORT, 'password_history is append-only'); END",
)

TEST_CASE_VERSION_TRIGGERS = (
  "CREATE TRIGGER IF NOT EXISTS test_case_versions_no_update BEFORE UPDATE ON test_case_versions BEGIN SELECT RAISE(ABORT, 'test_case_versions are append-only'); END",
  "CREATE TRIGGER IF NOT EXISTS test_case_versions_no_delete BEFORE DELETE ON test_case_versions BEGIN SELECT RAISE(ABORT, 'test_case_versions are append-only'); END",
)

CONNECTION_TARGET_VERSION_TRIGGERS = (
  "CREATE TRIGGER IF NOT EXISTS connection_target_versions_no_update BEFORE UPDATE ON connection_target_versions BEGIN SELECT RAISE(ABORT, 'connection_target_versions are append-only'); END",
  "CREATE TRIGGER IF NOT EXISTS connection_target_versions_no_delete BEFORE DELETE ON connection_target_versions BEGIN SELECT RAISE(ABORT, 'connection_target_versions are append-only'); END",
)

DEFECT_IMMUTABLE_TRIGGERS = (
  "CREATE TRIGGER IF NOT EXISTS defect_comments_no_update BEFORE UPDATE ON defect_comments BEGIN SELECT RAISE(ABORT, 'defect_comments are append-only'); END",
  "CREATE TRIGGER IF NOT EXISTS defect_comments_no_delete BEFORE DELETE ON defect_comments BEGIN SELECT RAISE(ABORT, 'defect_comments are append-only'); END",
  "CREATE TRIGGER IF NOT EXISTS defect_history_no_update BEFORE UPDATE ON defect_history BEGIN SELECT RAISE(ABORT, 'defect_history is append-only'); END",
  "CREATE TRIGGER IF NOT EXISTS defect_history_no_delete BEFORE DELETE ON defect_history BEGIN SELECT RAISE(ABORT, 'defect_history is append-only'); END",
  "CREATE TRIGGER IF NOT EXISTS defect_retests_no_update BEFORE UPDATE ON defect_retests BEGIN SELECT RAISE(ABORT, 'defect_retests are append-only'); END",
  "CREATE TRIGGER IF NOT EXISTS defect_retests_no_delete BEFORE DELETE ON defect_retests BEGIN SELECT RAISE(ABORT, 'defect_retests are append-only'); END",
  "CREATE TRIGGER IF NOT EXISTS defect_evidence_links_no_update BEFORE UPDATE ON defect_evidence_links BEGIN SELECT RAISE(ABORT, 'defect_evidence_links are append-only'); END",
  "CREATE TRIGGER IF NOT EXISTS defect_evidence_links_no_delete BEFORE DELETE ON defect_evidence_links BEGIN SELECT RAISE(ABORT, 'defect_evidence_links are append-only'); END",
)


def migrate_stage4_schema(engine: Engine) -> None:
  inspector = inspect(engine)
  tables = set(inspector.get_table_names())
  with engine.begin() as connection:
    if 'test_runs' in tables:
      columns = {column['name'] for column in inspector.get_columns('test_runs')}
      for name, sql_type in RUN_COLUMNS.items():
        if name not in columns:
          connection.execute(text(f'ALTER TABLE test_runs ADD COLUMN {name} {sql_type}'))

    if 'test_results' in tables:
      columns = {column['name'] for column in inspector.get_columns('test_results')}
      if 'test_run_id' not in columns:
        connection.execute(text('ALTER TABLE test_results RENAME TO test_results_legacy'))

    if 'evidence' in tables:
      columns = {column['name'] for column in inspector.get_columns('evidence')}
      if 'test_run_id' not in columns:
        connection.execute(text('ALTER TABLE evidence RENAME TO evidence_legacy'))


def migrate_stage6_schema(engine: Engine) -> None:
  inspector = inspect(engine)
  tables = set(inspector.get_table_names())
  with engine.begin() as connection:
    if 'operators' in tables:
      columns = {column['name'] for column in inspector.get_columns('operators')}
      for name, sql_type in OPERATOR_COLUMNS.items():
        if name not in columns:
          connection.execute(text(f'ALTER TABLE operators ADD COLUMN {name} {sql_type}'))

    if 'operator_sessions' in tables:
      columns = {column['name'] for column in inspector.get_columns('operator_sessions')}
      for name, sql_type in SESSION_COLUMNS.items():
        if name not in columns:
          connection.execute(text(f'ALTER TABLE operator_sessions ADD COLUMN {name} {sql_type}'))


def migrate_stage8_schema(engine: Engine) -> None:
  with engine.begin() as connection:
    inspector = inspect(connection)
    tables = set(inspector.get_table_names())
    if 'test_case_versions' in tables:
      for statement in TEST_CASE_VERSION_TRIGGERS:
        connection.execute(text(statement))


def migrate_stage9_schema(engine: Engine) -> None:
  with engine.begin() as connection:
    inspector = inspect(connection)
    tables = set(inspector.get_table_names())
    if 'connection_target_versions' in tables:
      for statement in CONNECTION_TARGET_VERSION_TRIGGERS:
        connection.execute(text(statement))


def migrate_stage10_schema(engine: Engine) -> None:
  with engine.begin() as connection:
    inspector = inspect(connection)
    tables = set(inspector.get_table_names())
    if 'connection_targets' in tables:
      columns = {column['name'] for column in inspector.get_columns('connection_targets')}
      for name, sql_type in CONNECTION_TARGET_COLUMNS.items():
        if name not in columns:
          connection.execute(text(f'ALTER TABLE connection_targets ADD COLUMN {name} {sql_type}'))


def migrate_stage11_schema(engine: Engine) -> None:
  with engine.begin() as connection:
    inspector = inspect(connection)
    tables = set(inspector.get_table_names())
    if 'automated_runs' in tables:
      columns = {column['name'] for column in inspector.get_columns('automated_runs')}
      for name, sql_type in AUTOMATED_RUN_COLUMNS.items():
        if name not in columns:
          connection.execute(text(f'ALTER TABLE automated_runs ADD COLUMN {name} {sql_type}'))


def migrate_stage12_schema(engine: Engine) -> None:
  with engine.begin() as connection:
    inspector = inspect(connection)
    tables = set(inspector.get_table_names())
    if 'defects' in tables:
      columns = {column['name'] for column in inspector.get_columns('defects')}
      if 'defect_key' not in columns:
        connection.execute(text('ALTER TABLE defects RENAME TO defects_legacy'))
        tables.remove('defects')
    for table in {'defect_comments', 'defect_history', 'defect_retests', 'defect_evidence_links'} & tables:
      columns = {column['name'] for column in inspector.get_columns(table)}
      if table == 'defect_history' and 'event_type' not in columns:
        connection.execute(text(f'ALTER TABLE {table} RENAME TO {table}_legacy'))


def migrate_stage13_schema(engine: Engine) -> None:
  with engine.begin() as connection:
    inspector = inspect(connection)
    tables = set(inspector.get_table_names())
    if 'report_exports' in tables:
      columns = {column['name'] for column in inspector.get_columns('report_exports')}
      if not REPORT_EXPORT_COLUMNS <= columns:
        connection.execute(text('ALTER TABLE report_exports RENAME TO report_exports_legacy'))
    if 'report_definitions' in tables:
      columns = {column['name'] for column in inspector.get_columns('report_definitions')}
      if not REPORT_DEFINITION_COLUMNS <= columns:
        connection.execute(text('ALTER TABLE report_definitions RENAME TO report_definitions_legacy'))


def install_audit_protection(engine: Engine) -> None:
  with engine.begin() as connection:
    for statement in AUDIT_TRIGGERS:
      connection.execute(text(statement))
    inspector = inspect(connection)
    if 'password_history' in set(inspector.get_table_names()):
      for statement in PASSWORD_HISTORY_TRIGGERS:
        connection.execute(text(statement))
    if 'test_case_versions' in set(inspector.get_table_names()):
      for statement in TEST_CASE_VERSION_TRIGGERS:
        connection.execute(text(statement))
    if 'connection_target_versions' in set(inspector.get_table_names()):
      for statement in CONNECTION_TARGET_VERSION_TRIGGERS:
        connection.execute(text(statement))
    tables = set(inspector.get_table_names())
    if {'defect_comments', 'defect_history', 'defect_retests', 'defect_evidence_links'} <= tables:
      for statement in DEFECT_IMMUTABLE_TRIGGERS:
        connection.execute(text(statement))
