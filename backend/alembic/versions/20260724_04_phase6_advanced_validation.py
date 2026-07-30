"""Add Phase 6 Advanced Validation Pack tables

Revision ID: 20260724_04_phase6
Revises: cf0b42482745
Create Date: 2026-07-24 16:15:00.000000
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = '20260724_04_phase6'
down_revision: str | None = 'cf0b42482745'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        'advanced_validation_profiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=120), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('enabled', sa.Boolean(), nullable=False),
        sa.Column('api_validation_enabled', sa.Boolean(), nullable=False),
        sa.Column('db_validation_enabled', sa.Boolean(), nullable=False),
        sa.Column('accessibility_enabled', sa.Boolean(), nullable=False),
        sa.Column('performance_enabled', sa.Boolean(), nullable=False),
        sa.Column('console_network_enabled', sa.Boolean(), nullable=False),
        sa.Column('evidence_completeness_enabled', sa.Boolean(), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['operators.id']),
        sa.ForeignKeyConstraint(['project_id'], ['test_projects.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_advanced_validation_profiles_project_id'), 'advanced_validation_profiles', ['project_id'], unique=False)

    op.create_table(
        'api_validation_definitions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('validation_profile_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=120), nullable=False),
        sa.Column('method', sa.String(length=10), nullable=False),
        sa.Column('path', sa.String(length=255), nullable=False),
        sa.Column('request_headers_template', sa.Text(), nullable=True),
        sa.Column('request_body_template', sa.Text(), nullable=True),
        sa.Column('expected_status', sa.Integer(), nullable=False),
        sa.Column('expected_schema_json', sa.Text(), nullable=True),
        sa.Column('expected_json_paths', sa.Text(), nullable=True),
        sa.Column('timeout_ms', sa.Integer(), nullable=False),
        sa.Column('auth_profile_reference', sa.String(length=100), nullable=True),
        sa.Column('enabled', sa.Boolean(), nullable=False),
        sa.Column('order_index', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['validation_profile_id'], ['advanced_validation_profiles.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_api_validation_definitions_validation_profile_id'), 'api_validation_definitions', ['validation_profile_id'], unique=False)

    op.create_table(
        'database_validation_definitions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('validation_profile_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=120), nullable=False),
        sa.Column('connection_profile_reference', sa.String(length=100), nullable=False),
        sa.Column('query_template', sa.Text(), nullable=False),
        sa.Column('expected_result_json', sa.Text(), nullable=True),
        sa.Column('timeout_ms', sa.Integer(), nullable=False),
        sa.Column('max_rows', sa.Integer(), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=False),
        sa.Column('order_index', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['validation_profile_id'], ['advanced_validation_profiles.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_database_validation_definitions_validation_profile_id'), 'database_validation_definitions', ['validation_profile_id'], unique=False)

    op.create_table(
        'accessibility_validation_definitions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('validation_profile_id', sa.Integer(), nullable=False),
        sa.Column('route', sa.String(length=255), nullable=False),
        sa.Column('standard', sa.String(length=50), nullable=False),
        sa.Column('severity_threshold', sa.String(length=20), nullable=False),
        sa.Column('include_rules', sa.Text(), nullable=True),
        sa.Column('exclude_rules', sa.Text(), nullable=True),
        sa.Column('enabled', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['validation_profile_id'], ['advanced_validation_profiles.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_accessibility_validation_definitions_validation_profile_id'), 'accessibility_validation_definitions', ['validation_profile_id'], unique=False)

    op.create_table(
        'performance_validation_definitions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('validation_profile_id', sa.Integer(), nullable=False),
        sa.Column('route', sa.String(length=255), nullable=False),
        sa.Column('metric', sa.String(length=50), nullable=False),
        sa.Column('warning_threshold', sa.Float(), nullable=False),
        sa.Column('failure_threshold', sa.Float(), nullable=False),
        sa.Column('sample_count', sa.Integer(), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['validation_profile_id'], ['advanced_validation_profiles.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_performance_validation_definitions_validation_profile_id'), 'performance_validation_definitions', ['validation_profile_id'], unique=False)

    op.create_table(
        'advanced_validation_runs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('automated_run_id', sa.Integer(), nullable=True),
        sa.Column('test_plan_id', sa.Integer(), nullable=False),
        sa.Column('test_plan_version_id', sa.Integer(), nullable=False),
        sa.Column('validation_profile_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=30), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('summary_json', sa.Text(), nullable=False),
        sa.Column('result_hash', sa.String(length=64), nullable=True),
        sa.ForeignKeyConstraint(['automated_run_id'], ['automated_runs.id']),
        sa.ForeignKeyConstraint(['project_id'], ['test_projects.id']),
        sa.ForeignKeyConstraint(['test_plan_id'], ['test_plans.id']),
        sa.ForeignKeyConstraint(['test_plan_version_id'], ['test_plan_versions.id']),
        sa.ForeignKeyConstraint(['validation_profile_id'], ['advanced_validation_profiles.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_advanced_validation_runs_automated_run_id'), 'advanced_validation_runs', ['automated_run_id'], unique=False)
    op.create_index(op.f('ix_advanced_validation_runs_project_id'), 'advanced_validation_runs', ['project_id'], unique=False)
    op.create_index(op.f('ix_advanced_validation_runs_test_plan_id'), 'advanced_validation_runs', ['test_plan_id'], unique=False)
    op.create_index(op.f('ix_advanced_validation_runs_test_plan_version_id'), 'advanced_validation_runs', ['test_plan_version_id'], unique=False)
    op.create_index(op.f('ix_advanced_validation_runs_validation_profile_id'), 'advanced_validation_runs', ['validation_profile_id'], unique=False)

    op.create_table(
        'advanced_validation_results',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('advanced_validation_run_id', sa.Integer(), nullable=False),
        sa.Column('validator_type', sa.String(length=30), nullable=False),
        sa.Column('definition_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('severity', sa.String(length=20), nullable=False),
        sa.Column('expected_json', sa.Text(), nullable=True),
        sa.Column('actual_json', sa.Text(), nullable=True),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('duration_ms', sa.Integer(), nullable=False),
        sa.Column('artifact_ids', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['advanced_validation_run_id'], ['advanced_validation_runs.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_advanced_validation_results_advanced_validation_run_id'), 'advanced_validation_results', ['advanced_validation_run_id'], unique=False)

    op.create_table(
        'local_schedules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=120), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=False),
        sa.Column('cron_expression', sa.String(length=60), nullable=False),
        sa.Column('timezone', sa.String(length=60), nullable=False),
        sa.Column('approved_test_plan_id', sa.Integer(), nullable=False),
        sa.Column('approved_version_number', sa.Integer(), nullable=False),
        sa.Column('validation_profile_id', sa.Integer(), nullable=False),
        sa.Column('browser', sa.String(length=30), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('approved_by', sa.Integer(), nullable=True),
        sa.Column('last_run_at', sa.DateTime(), nullable=True),
        sa.Column('next_run_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['approved_by'], ['operators.id']),
        sa.ForeignKeyConstraint(['approved_test_plan_id'], ['test_plans.id']),
        sa.ForeignKeyConstraint(['created_by'], ['operators.id']),
        sa.ForeignKeyConstraint(['project_id'], ['test_projects.id']),
        sa.ForeignKeyConstraint(['validation_profile_id'], ['advanced_validation_profiles.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_local_schedules_approved_test_plan_id'), 'local_schedules', ['approved_test_plan_id'], unique=False)
    op.create_index(op.f('ix_local_schedules_project_id'), 'local_schedules', ['project_id'], unique=False)
    op.create_index(op.f('ix_local_schedules_validation_profile_id'), 'local_schedules', ['validation_profile_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_local_schedules_validation_profile_id'), table_name='local_schedules')
    op.drop_index(op.f('ix_local_schedules_project_id'), table_name='local_schedules')
    op.drop_index(op.f('ix_local_schedules_approved_test_plan_id'), table_name='local_schedules')
    op.drop_table('local_schedules')

    op.drop_index(op.f('ix_advanced_validation_results_advanced_validation_run_id'), table_name='advanced_validation_results')
    op.drop_table('advanced_validation_results')

    op.drop_index(op.f('ix_advanced_validation_runs_validation_profile_id'), table_name='advanced_validation_runs')
    op.drop_index(op.f('ix_advanced_validation_runs_test_plan_version_id'), table_name='advanced_validation_runs')
    op.drop_index(op.f('ix_advanced_validation_runs_test_plan_id'), table_name='advanced_validation_runs')
    op.drop_index(op.f('ix_advanced_validation_runs_project_id'), table_name='advanced_validation_runs')
    op.drop_index(op.f('ix_advanced_validation_runs_automated_run_id'), table_name='advanced_validation_runs')
    op.drop_table('advanced_validation_runs')

    op.drop_index(op.f('ix_performance_validation_definitions_validation_profile_id'), table_name='performance_validation_definitions')
    op.drop_table('performance_validation_definitions')

    op.drop_index(op.f('ix_accessibility_validation_definitions_validation_profile_id'), table_name='accessibility_validation_definitions')
    op.drop_table('accessibility_validation_definitions')

    op.drop_index(op.f('ix_database_validation_definitions_validation_profile_id'), table_name='database_validation_definitions')
    op.drop_table('database_validation_definitions')

    op.drop_index(op.f('ix_api_validation_definitions_validation_profile_id'), table_name='api_validation_definitions')
    op.drop_table('api_validation_definitions')

    op.drop_index(op.f('ix_advanced_validation_profiles_project_id'), table_name='advanced_validation_profiles')
    op.drop_table('advanced_validation_profiles')
