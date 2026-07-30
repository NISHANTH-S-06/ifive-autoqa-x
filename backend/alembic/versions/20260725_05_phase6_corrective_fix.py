"""Phase 6 corrective migration.

Fixes two issues discovered during Phase 6 audit against the live database:
1. The original 20260724_04_phase6 migration created 28 columns across the 8
   new advanced-validation tables with server_default values that do not
   match this repository's convention (ORM-side default only, no
   server_default). This corrects those columns to match the corrected
   migration source and the ORM metadata, eliminating metadata drift.
2. The live database was originally stamped (not upgraded) onto the
   20260715_01 baseline revision and is missing 4 append-only "no_delete"
   triggers for defect_comments, defect_evidence_links, defect_history, and
   defect_retests that a fresh install receives from that baseline
   migration. This restores them using the same idempotent
   CREATE TRIGGER IF NOT EXISTS pattern, closing an audit-integrity gap on
   defect evidence tables without altering any existing data.

Revision ID: 20260725_05
Revises: 20260724_04_phase6
"""
from alembic import op
import sqlalchemy as sa

revision = "20260725_05"
down_revision = "20260724_04_phase6"
branch_labels = None
depends_on = None

_PHASE6_DEFAULT_COLUMNS = [
    ("accessibility_validation_definitions", "standard", sa.String(length=50), "'WCAG21AA'"),
    ("accessibility_validation_definitions", "severity_threshold", sa.String(length=20), "'critical'"),
    ("accessibility_validation_definitions", "enabled", sa.Boolean(), "1"),
    ("advanced_validation_profiles", "enabled", sa.Boolean(), "1"),
    ("advanced_validation_profiles", "api_validation_enabled", sa.Boolean(), "1"),
    ("advanced_validation_profiles", "db_validation_enabled", sa.Boolean(), "1"),
    ("advanced_validation_profiles", "accessibility_enabled", sa.Boolean(), "0"),
    ("advanced_validation_profiles", "performance_enabled", sa.Boolean(), "0"),
    ("advanced_validation_profiles", "console_network_enabled", sa.Boolean(), "1"),
    ("advanced_validation_profiles", "evidence_completeness_enabled", sa.Boolean(), "1"),
    ("advanced_validation_results", "severity", sa.String(length=20), "'INFO'"),
    ("advanced_validation_results", "duration_ms", sa.Integer(), "0"),
    ("advanced_validation_runs", "status", sa.String(length=30), "'RUNNING'"),
    ("advanced_validation_runs", "summary_json", sa.Text(), "'{}'"),
    ("api_validation_definitions", "method", sa.String(length=10), "'GET'"),
    ("api_validation_definitions", "expected_status", sa.Integer(), "200"),
    ("api_validation_definitions", "timeout_ms", sa.Integer(), "5000"),
    ("api_validation_definitions", "enabled", sa.Boolean(), "1"),
    ("api_validation_definitions", "order_index", sa.Integer(), "0"),
    ("database_validation_definitions", "timeout_ms", sa.Integer(), "5000"),
    ("database_validation_definitions", "max_rows", sa.Integer(), "100"),
    ("database_validation_definitions", "enabled", sa.Boolean(), "1"),
    ("database_validation_definitions", "order_index", sa.Integer(), "0"),
    ("local_schedules", "enabled", sa.Boolean(), "1"),
    ("local_schedules", "timezone", sa.String(length=60), "'UTC'"),
    ("local_schedules", "browser", sa.String(length=30), "'chromium'"),
    ("performance_validation_definitions", "sample_count", sa.Integer(), "1"),
    ("performance_validation_definitions", "enabled", sa.Boolean(), "1"),
]

_MISSING_DEFECT_NO_DELETE_TRIGGERS = [
    ("defect_comments", "defect_comments", "defect_comments are append-only"),
    ("defect_evidence_links", "defect_evidence_links", "defect_evidence_links are append-only"),
    ("defect_history", "defect_history", "defect_history is append-only"),
    ("defect_retests", "defect_retests", "defect_retests are append-only"),
]


def upgrade() -> None:
    for table, column, coltype, old_default in _PHASE6_DEFAULT_COLUMNS:
        with op.batch_alter_table(table, schema=None) as batch_op:
            batch_op.alter_column(
                column,
                existing_type=coltype,
                existing_nullable=False,
                existing_server_default=sa.text(old_default),
                server_default=None,
            )

    for trigger_prefix, table_name, error_message in _MISSING_DEFECT_NO_DELETE_TRIGGERS:
        op.execute(
            f"CREATE TRIGGER IF NOT EXISTS {trigger_prefix}_no_delete "
            f"BEFORE DELETE ON {table_name} BEGIN "
            f"SELECT RAISE(ABORT, '{error_message}'); END"
        )


def downgrade() -> None:
    for table, column, coltype, old_default in _PHASE6_DEFAULT_COLUMNS:
        with op.batch_alter_table(table, schema=None) as batch_op:
            batch_op.alter_column(
                column,
                existing_type=coltype,
                existing_nullable=False,
                server_default=sa.text(old_default),
            )
    # The restored defect no_delete triggers are an audit-integrity fix and
    # are intentionally not removed on downgrade.