"""Add Phase 13 Enterprise Autonomous AI QA Cloud Platform tables

Revision ID: 20260729_12_phase13_enterprise_cloud_platform
Revises: 20260728_11_phase12_zero_code_ecosystem
Create Date: 2026-07-29 11:00:00.000000
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = '20260729_12_phase13_enterprise_cloud_platform'
down_revision: str | None = '20260728_11_phase12_zero_code_ecosystem'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ── Module 1: Distributed Execution Orchestrator ─────────────────────────
    op.create_table(
        'execution_worker_nodes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('worker_name', sa.String(length=120), nullable=False),
        sa.Column('worker_status', sa.String(length=30), nullable=False),
        sa.Column('region', sa.String(length=60), nullable=False),
        sa.Column('capacity', sa.Integer(), nullable=False),
        sa.Column('active_jobs', sa.Integer(), nullable=False),
        sa.Column('browser_types_json', sa.Text(), nullable=False),
        sa.Column('jobs_completed', sa.Integer(), nullable=False),
        sa.Column('jobs_failed', sa.Integer(), nullable=False),
        sa.Column('avg_job_duration_ms', sa.Float(), nullable=False),
        sa.Column('total_cost_usd', sa.Float(), nullable=False),
        sa.Column('last_heartbeat', sa.DateTime(), nullable=True),
        sa.Column('registered_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_exec_worker_nodes_status', 'execution_worker_nodes', ['worker_status'])
    op.create_index('ix_exec_worker_nodes_region', 'execution_worker_nodes', ['region'])

    op.create_table(
        'execution_queue_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('job_id', sa.String(length=100), nullable=False, unique=True),
        sa.Column('project_id', sa.Integer(), nullable=True),
        sa.Column('queue_status', sa.String(length=30), nullable=False),
        sa.Column('priority', sa.Integer(), nullable=False),
        sa.Column('browser_type', sa.String(length=40), nullable=False),
        sa.Column('worker_id', sa.Integer(), nullable=True),
        sa.Column('retry_count', sa.Integer(), nullable=False),
        sa.Column('max_retries', sa.Integer(), nullable=False),
        sa.Column('estimated_duration_ms', sa.Integer(), nullable=False),
        sa.Column('actual_duration_ms', sa.Integer(), nullable=True),
        sa.Column('cost_usd', sa.Float(), nullable=False),
        sa.Column('payload_json', sa.Text(), nullable=False),
        sa.Column('result_json', sa.Text(), nullable=False),
        sa.Column('queued_at', sa.DateTime(), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
        sa.ForeignKeyConstraint(['worker_id'], ['execution_worker_nodes.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_exec_queue_status', 'execution_queue_items', ['queue_status'])
    op.create_index('ix_exec_queue_priority', 'execution_queue_items', ['priority'])
    op.create_index('ix_exec_queue_project_id', 'execution_queue_items', ['project_id'])

    # ── Module 2: Cloud Browser Farm ─────────────────────────────────────────
    op.create_table(
        'browser_farm_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.String(length=100), nullable=False, unique=True),
        sa.Column('browser_type', sa.String(length=40), nullable=False),
        sa.Column('session_status', sa.String(length=30), nullable=False),
        sa.Column('reserved_by_job_id', sa.String(length=100), nullable=True),
        sa.Column('health_score', sa.Float(), nullable=False),
        sa.Column('recording_url', sa.String(length=500), nullable=True),
        sa.Column('metrics_json', sa.Text(), nullable=False),
        sa.Column('region', sa.String(length=60), nullable=False),
        sa.Column('reserved_at', sa.DateTime(), nullable=True),
        sa.Column('released_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_browser_farm_sessions_status', 'browser_farm_sessions', ['session_status'])
    op.create_index('ix_browser_farm_sessions_browser', 'browser_farm_sessions', ['browser_type'])

    # ── Module 3: Execution Stream ────────────────────────────────────────────
    op.create_table(
        'execution_stream_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('job_id', sa.String(length=100), nullable=False),
        sa.Column('event_type', sa.String(length=60), nullable=False),
        sa.Column('event_payload_json', sa.Text(), nullable=False),
        sa.Column('sequence_num', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_exec_stream_events_job', 'execution_stream_events', ['job_id'])
    op.create_index('ix_exec_stream_events_type', 'execution_stream_events', ['event_type'])

    # ── Module 4: Observability Platform ─────────────────────────────────────
    op.create_table(
        'observability_metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=True),
        sa.Column('metric_name', sa.String(length=120), nullable=False),
        sa.Column('metric_value', sa.Float(), nullable=False),
        sa.Column('metric_unit', sa.String(length=30), nullable=False),
        sa.Column('metric_source', sa.String(length=60), nullable=False),
        sa.Column('labels_json', sa.Text(), nullable=False),
        sa.Column('trace_id', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_obs_metrics_name', 'observability_metrics', ['metric_name'])
    op.create_index('ix_obs_metrics_source', 'observability_metrics', ['metric_source'])
    op.create_index('ix_obs_metrics_created', 'observability_metrics', ['created_at'])
    op.create_index('ix_obs_metrics_project_id', 'observability_metrics', ['project_id'])

    # ── Module 5: Enterprise Analytics ───────────────────────────────────────
    op.create_table(
        'enterprise_analytics_snapshots',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=True),
        sa.Column('snapshot_type', sa.String(length=60), nullable=False),
        sa.Column('quality_score', sa.Float(), nullable=False),
        sa.Column('pass_rate', sa.Float(), nullable=False),
        sa.Column('coverage_pct', sa.Float(), nullable=False),
        sa.Column('flaky_count', sa.Integer(), nullable=False),
        sa.Column('cost_usd', sa.Float(), nullable=False),
        sa.Column('data_json', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_ent_analytics_type', 'enterprise_analytics_snapshots', ['snapshot_type'])
    op.create_index('ix_ent_analytics_created', 'enterprise_analytics_snapshots', ['created_at'])
    op.create_index('ix_ent_analytics_project_id', 'enterprise_analytics_snapshots', ['project_id'])

    # ── Module 6: Release Governance ──────────────────────────────────────────
    op.create_table(
        'release_governance_stages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=True),
        sa.Column('release_version', sa.String(length=60), nullable=False),
        sa.Column('stage_order', sa.Integer(), nullable=False),
        sa.Column('stage_name', sa.String(length=80), nullable=False),
        sa.Column('required_role', sa.String(length=60), nullable=False),
        sa.Column('stage_status', sa.String(length=30), nullable=False),
        sa.Column('is_blocking', sa.Boolean(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_rel_gov_stages_status', 'release_governance_stages', ['stage_status'])
    op.create_index('ix_rel_gov_stages_project_id', 'release_governance_stages', ['project_id'])

    op.create_table(
        'release_governance_approvals',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('stage_id', sa.Integer(), nullable=False),
        sa.Column('approver_id', sa.Integer(), nullable=True),
        sa.Column('approver_name', sa.String(length=120), nullable=False),
        sa.Column('approver_role', sa.String(length=60), nullable=False),
        sa.Column('decision', sa.String(length=20), nullable=False),
        sa.Column('digital_signature', sa.String(length=256), nullable=False),
        sa.Column('ip_address', sa.String(length=60), nullable=False),
        sa.Column('comments', sa.Text(), nullable=False),
        sa.Column('signed_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['approver_id'], ['operators.id']),
        sa.ForeignKeyConstraint(['stage_id'], ['release_governance_stages.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_rel_gov_approvals_stage', 'release_governance_approvals', ['stage_id'])

    # ── Module 7: Compliance Center ───────────────────────────────────────────
    op.create_table(
        'compliance_reports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('compliance_standard', sa.String(length=30), nullable=False),
        sa.Column('report_scope', sa.String(length=120), nullable=False),
        sa.Column('report_status', sa.String(length=30), nullable=False),
        sa.Column('compliance_score', sa.Float(), nullable=False),
        sa.Column('findings_json', sa.Text(), nullable=False),
        sa.Column('recommendations_json', sa.Text(), nullable=False),
        sa.Column('generated_by', sa.Integer(), nullable=True),
        sa.Column('generated_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['generated_by'], ['operators.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_compliance_reports_standard', 'compliance_reports', ['compliance_standard'])
    op.create_index('ix_compliance_reports_status', 'compliance_reports', ['report_status'])

    # ── Module 8: Enterprise API Hub ──────────────────────────────────────────
    op.create_table(
        'api_hub_keys',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('key_name', sa.String(length=120), nullable=False),
        sa.Column('key_prefix', sa.String(length=20), nullable=False),
        sa.Column('key_hash', sa.String(length=256), nullable=False),
        sa.Column('key_status', sa.String(length=20), nullable=False),
        sa.Column('sdk_type', sa.String(length=30), nullable=False),
        sa.Column('rate_limit_rpm', sa.Integer(), nullable=False),
        sa.Column('permissions_json', sa.Text(), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('last_used_at', sa.DateTime(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['operators.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_api_hub_keys_status', 'api_hub_keys', ['key_status'])

    op.create_table(
        'api_hub_webhooks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('webhook_name', sa.String(length=120), nullable=False),
        sa.Column('target_url', sa.String(length=500), nullable=False),
        sa.Column('event_types_json', sa.Text(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('secret_hash', sa.String(length=256), nullable=False),
        sa.Column('delivery_count', sa.Integer(), nullable=False),
        sa.Column('failure_count', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )

    # ── Module 9: Marketplace Ecosystem ───────────────────────────────────────
    op.create_table(
        'marketplace_plugins',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('plugin_name', sa.String(length=150), nullable=False),
        sa.Column('plugin_version', sa.String(length=30), nullable=False),
        sa.Column('plugin_category', sa.String(length=60), nullable=False),
        sa.Column('author', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('install_status', sa.String(length=20), nullable=False),
        sa.Column('install_count', sa.Integer(), nullable=False),
        sa.Column('rating', sa.Float(), nullable=False),
        sa.Column('manifest_json', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_marketplace_plugins_category', 'marketplace_plugins', ['plugin_category'])
    op.create_index('ix_marketplace_plugins_status', 'marketplace_plugins', ['install_status'])

    # ── Module 10: Enterprise DevOps ──────────────────────────────────────────
    op.create_table(
        'devops_pipelines',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=True),
        sa.Column('pipeline_name', sa.String(length=150), nullable=False),
        sa.Column('ci_tool', sa.String(length=40), nullable=False),
        sa.Column('repo_url', sa.String(length=500), nullable=False),
        sa.Column('branch', sa.String(length=100), nullable=False),
        sa.Column('pipeline_status', sa.String(length=30), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('config_json', sa.Text(), nullable=False),
        sa.Column('last_triggered_at', sa.DateTime(), nullable=True),
        sa.Column('last_run_duration_ms', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_devops_pipelines_tool', 'devops_pipelines', ['ci_tool'])
    op.create_index('ix_devops_pipelines_status', 'devops_pipelines', ['pipeline_status'])
    op.create_index('ix_devops_pipelines_project_id', 'devops_pipelines', ['project_id'])

    # ── Module 11: Multi-Region Cloud ─────────────────────────────────────────
    op.create_table(
        'cloud_region_configs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('cloud_provider', sa.String(length=30), nullable=False),
        sa.Column('region_name', sa.String(length=60), nullable=False),
        sa.Column('region_display', sa.String(length=100), nullable=False),
        sa.Column('region_status', sa.String(length=30), nullable=False),
        sa.Column('failover_priority', sa.Integer(), nullable=False),
        sa.Column('is_primary', sa.Boolean(), nullable=False),
        sa.Column('is_disaster_recovery', sa.Boolean(), nullable=False),
        sa.Column('replication_lag_ms', sa.Integer(), nullable=False),
        sa.Column('last_backup_at', sa.DateTime(), nullable=True),
        sa.Column('config_json', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_cloud_region_provider', 'cloud_region_configs', ['cloud_provider'])
    op.create_index('ix_cloud_region_status', 'cloud_region_configs', ['region_status'])

    # ── Module 12: Enterprise Security Center ────────────────────────────────
    op.create_table(
        'security_vault_entries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('key_name', sa.String(length=150), nullable=False, unique=True),
        sa.Column('secret_type', sa.String(length=40), nullable=False),
        sa.Column('encrypted_value', sa.Text(), nullable=False),
        sa.Column('entry_status', sa.String(length=20), nullable=False),
        sa.Column('rotation_schedule_days', sa.Integer(), nullable=False),
        sa.Column('last_rotated_at', sa.DateTime(), nullable=True),
        sa.Column('next_rotation_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['operators.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_sec_vault_status', 'security_vault_entries', ['entry_status'])
    op.create_index('ix_sec_vault_key', 'security_vault_entries', ['key_name'])

    # ── Module 13: AI Execution Optimizer ────────────────────────────────────
    op.create_table(
        'ai_optimizer_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=True),
        sa.Column('optimization_target', sa.String(length=60), nullable=False),
        sa.Column('old_value_json', sa.Text(), nullable=False),
        sa.Column('new_value_json', sa.Text(), nullable=False),
        sa.Column('reasoning', sa.Text(), nullable=False),
        sa.Column('confidence_score', sa.Float(), nullable=False),
        sa.Column('optimization_status', sa.String(length=30), nullable=False),
        sa.Column('impact_delta', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_ai_optimizer_target', 'ai_optimizer_logs', ['optimization_target'])
    op.create_index('ix_ai_optimizer_status', 'ai_optimizer_logs', ['optimization_status'])
    op.create_index('ix_ai_optimizer_project_id', 'ai_optimizer_logs', ['project_id'])

    # ── Module 14: Executive Command Center ──────────────────────────────────
    op.create_table(
        'executive_command_snapshots',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('snapshot_label', sa.String(length=100), nullable=False),
        sa.Column('total_companies', sa.Integer(), nullable=False),
        sa.Column('total_projects', sa.Integer(), nullable=False),
        sa.Column('total_executions_today', sa.Integer(), nullable=False),
        sa.Column('active_workers', sa.Integer(), nullable=False),
        sa.Column('browser_farm_utilization_pct', sa.Float(), nullable=False),
        sa.Column('ai_health_score', sa.Float(), nullable=False),
        sa.Column('release_readiness_score', sa.Float(), nullable=False),
        sa.Column('compliance_score', sa.Float(), nullable=False),
        sa.Column('security_score', sa.Float(), nullable=False),
        sa.Column('overall_quality_score', sa.Float(), nullable=False),
        sa.Column('kpi_data_json', sa.Text(), nullable=False),
        sa.Column('alerts_json', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_exec_cmd_created', 'executive_command_snapshots', ['created_at'])


def downgrade() -> None:
    # Module 14
    op.drop_index('ix_exec_cmd_created', 'executive_command_snapshots')
    op.drop_table('executive_command_snapshots')

    # Module 13
    op.drop_index('ix_ai_optimizer_project_id', 'ai_optimizer_logs')
    op.drop_index('ix_ai_optimizer_status', 'ai_optimizer_logs')
    op.drop_index('ix_ai_optimizer_target', 'ai_optimizer_logs')
    op.drop_table('ai_optimizer_logs')

    # Module 12
    op.drop_index('ix_sec_vault_key', 'security_vault_entries')
    op.drop_index('ix_sec_vault_status', 'security_vault_entries')
    op.drop_table('security_vault_entries')

    # Module 11
    op.drop_index('ix_cloud_region_status', 'cloud_region_configs')
    op.drop_index('ix_cloud_region_provider', 'cloud_region_configs')
    op.drop_table('cloud_region_configs')

    # Module 10
    op.drop_index('ix_devops_pipelines_project_id', 'devops_pipelines')
    op.drop_index('ix_devops_pipelines_status', 'devops_pipelines')
    op.drop_index('ix_devops_pipelines_tool', 'devops_pipelines')
    op.drop_table('devops_pipelines')

    # Module 9
    op.drop_index('ix_marketplace_plugins_status', 'marketplace_plugins')
    op.drop_index('ix_marketplace_plugins_category', 'marketplace_plugins')
    op.drop_table('marketplace_plugins')

    # Module 8
    op.drop_table('api_hub_webhooks')
    op.drop_index('ix_api_hub_keys_status', 'api_hub_keys')
    op.drop_table('api_hub_keys')

    # Module 7
    op.drop_index('ix_compliance_reports_status', 'compliance_reports')
    op.drop_index('ix_compliance_reports_standard', 'compliance_reports')
    op.drop_table('compliance_reports')

    # Module 6
    op.drop_index('ix_rel_gov_approvals_stage', 'release_governance_approvals')
    op.drop_table('release_governance_approvals')
    op.drop_index('ix_rel_gov_stages_project_id', 'release_governance_stages')
    op.drop_index('ix_rel_gov_stages_status', 'release_governance_stages')
    op.drop_table('release_governance_stages')

    # Module 5
    op.drop_index('ix_ent_analytics_project_id', 'enterprise_analytics_snapshots')
    op.drop_index('ix_ent_analytics_created', 'enterprise_analytics_snapshots')
    op.drop_index('ix_ent_analytics_type', 'enterprise_analytics_snapshots')
    op.drop_table('enterprise_analytics_snapshots')

    # Module 4
    op.drop_index('ix_obs_metrics_project_id', 'observability_metrics')
    op.drop_index('ix_obs_metrics_created', 'observability_metrics')
    op.drop_index('ix_obs_metrics_source', 'observability_metrics')
    op.drop_index('ix_obs_metrics_name', 'observability_metrics')
    op.drop_table('observability_metrics')

    # Module 3
    op.drop_index('ix_exec_stream_events_type', 'execution_stream_events')
    op.drop_index('ix_exec_stream_events_job', 'execution_stream_events')
    op.drop_table('execution_stream_events')

    # Module 2
    op.drop_index('ix_browser_farm_sessions_browser', 'browser_farm_sessions')
    op.drop_index('ix_browser_farm_sessions_status', 'browser_farm_sessions')
    op.drop_table('browser_farm_sessions')

    # Module 1
    op.drop_index('ix_exec_queue_project_id', 'execution_queue_items')
    op.drop_index('ix_exec_queue_priority', 'execution_queue_items')
    op.drop_index('ix_exec_queue_status', 'execution_queue_items')
    op.drop_table('execution_queue_items')
    op.drop_index('ix_exec_worker_nodes_region', 'execution_worker_nodes')
    op.drop_index('ix_exec_worker_nodes_status', 'execution_worker_nodes')
    op.drop_table('execution_worker_nodes')
