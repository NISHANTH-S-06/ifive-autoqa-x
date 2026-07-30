"""Add Phase 12 Zero-Code Enterprise Autonomous QA Ecosystem tables

Revision ID: 20260728_11_phase12_zero_code_ecosystem
Revises: 20260728_10_phase11_self_evolving_brain
Create Date: 2026-07-28 19:00:00.000000
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = '20260728_11_phase12_zero_code_ecosystem'
down_revision: str | None = '20260728_10_phase11_self_evolving_brain'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        'onboarding_wizard_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=True),
        sa.Column('company_name', sa.String(length=200), nullable=False),
        sa.Column('product_name', sa.String(length=200), nullable=False),
        sa.Column('application_url', sa.String(length=500), nullable=False),
        sa.Column('auth_type', sa.String(length=60), nullable=False),
        sa.Column('auth_config_json', sa.Text(), nullable=False),
        sa.Column('browser_selection', sa.String(length=60), nullable=False),
        sa.Column('environment', sa.String(length=30), nullable=False),
        sa.Column('validation_status', sa.String(length=30), nullable=False),
        sa.Column('validation_results_json', sa.Text(), nullable=False),
        sa.Column('current_step', sa.Integer(), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['operators.id']),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_onboarding_wizard_sessions_project_id', 'onboarding_wizard_sessions', ['project_id'])

    op.create_table(
        'zero_code_test_studio_flows',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=True),
        sa.Column('flow_name', sa.String(length=200), nullable=False),
        sa.Column('flow_type', sa.String(length=60), nullable=False),
        sa.Column('flow_definition_json', sa.Text(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['operators.id']),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_zero_code_test_studio_flows_project_id', 'zero_code_test_studio_flows', ['project_id'])
    op.create_index('ix_zero_code_test_studio_flows_flow_type', 'zero_code_test_studio_flows', ['flow_type'])

    op.create_table(
        'test_lab_browser_workers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('worker_name', sa.String(length=100), nullable=False),
        sa.Column('browser_type', sa.String(length=60), nullable=False),
        sa.Column('worker_status', sa.String(length=30), nullable=False),
        sa.Column('current_job_id', sa.String(length=100), nullable=True),
        sa.Column('jobs_completed', sa.Integer(), nullable=False),
        sa.Column('jobs_failed', sa.Integer(), nullable=False),
        sa.Column('last_heartbeat', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_test_lab_browser_workers_browser_type', 'test_lab_browser_workers', ['browser_type'])
    op.create_index('ix_test_lab_browser_workers_worker_status', 'test_lab_browser_workers', ['worker_status'])

    op.create_table(
        'test_data_factory_datasets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=True),
        sa.Column('dataset_name', sa.String(length=200), nullable=False),
        sa.Column('data_category', sa.String(length=60), nullable=False),
        sa.Column('record_count', sa.Integer(), nullable=False),
        sa.Column('is_masked', sa.Boolean(), nullable=False),
        sa.Column('dataset_json', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_test_data_factory_datasets_project_id', 'test_data_factory_datasets', ['project_id'])
    op.create_index('ix_test_data_factory_datasets_data_category', 'test_data_factory_datasets', ['data_category'])

    op.create_table(
        'release_war_room_metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('snapshot_label', sa.String(length=100), nullable=False),
        sa.Column('total_projects', sa.Integer(), nullable=False),
        sa.Column('total_companies', sa.Integer(), nullable=False),
        sa.Column('running_executions', sa.Integer(), nullable=False),
        sa.Column('overall_risk_score', sa.Float(), nullable=False),
        sa.Column('overall_coverage_pct', sa.Float(), nullable=False),
        sa.Column('open_critical_defects', sa.Integer(), nullable=False),
        sa.Column('release_health_score', sa.Float(), nullable=False),
        sa.Column('deployment_recommendation', sa.String(length=30), nullable=False),
        sa.Column('metrics_json', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'plugin_marketplace_packages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('package_name', sa.String(length=150), nullable=False),
        sa.Column('package_version', sa.String(length=30), nullable=False),
        sa.Column('plugin_type', sa.String(length=60), nullable=False),
        sa.Column('author', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('is_installed', sa.Boolean(), nullable=False),
        sa.Column('config_schema_json', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_plugin_marketplace_packages_plugin_type', 'plugin_marketplace_packages', ['plugin_type'])

    op.create_table(
        'enterprise_integration_configs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=True),
        sa.Column('integration_type', sa.String(length=60), nullable=False),
        sa.Column('integration_name', sa.String(length=150), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('config_json', sa.Text(), nullable=False),
        sa.Column('last_sync_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_enterprise_integration_configs_project_id', 'enterprise_integration_configs', ['project_id'])
    op.create_index('ix_enterprise_integration_configs_integration_type', 'enterprise_integration_configs', ['integration_type'])


def downgrade() -> None:
    op.drop_index('ix_enterprise_integration_configs_integration_type', 'enterprise_integration_configs')
    op.drop_index('ix_enterprise_integration_configs_project_id', 'enterprise_integration_configs')
    op.drop_table('enterprise_integration_configs')

    op.drop_index('ix_plugin_marketplace_packages_plugin_type', 'plugin_marketplace_packages')
    op.drop_table('plugin_marketplace_packages')

    op.drop_table('release_war_room_metrics')

    op.drop_index('ix_test_data_factory_datasets_data_category', 'test_data_factory_datasets')
    op.drop_index('ix_test_data_factory_datasets_project_id', 'test_data_factory_datasets')
    op.drop_table('test_data_factory_datasets')

    op.drop_index('ix_test_lab_browser_workers_worker_status', 'test_lab_browser_workers')
    op.drop_index('ix_test_lab_browser_workers_browser_type', 'test_lab_browser_workers')
    op.drop_table('test_lab_browser_workers')

    op.drop_index('ix_zero_code_test_studio_flows_flow_type', 'zero_code_test_studio_flows')
    op.drop_index('ix_zero_code_test_studio_flows_project_id', 'zero_code_test_studio_flows')
    op.drop_table('zero_code_test_studio_flows')

    op.drop_index('ix_onboarding_wizard_sessions_project_id', 'onboarding_wizard_sessions')
    op.drop_table('onboarding_wizard_sessions')
