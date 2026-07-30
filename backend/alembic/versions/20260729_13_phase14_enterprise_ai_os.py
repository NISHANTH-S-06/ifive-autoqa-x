"""Add Phase 14 Enterprise Autonomous AI QA Operating System tables

Revision ID: 20260729_13_phase14_enterprise_ai_os
Revises: 20260729_12_phase13_enterprise_cloud_platform
Create Date: 2026-07-29 12:00:00.000000
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = '20260729_13_phase14_enterprise_ai_os'
down_revision: str | None = '20260729_12_phase13_enterprise_cloud_platform'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ── Module 1: AI Enterprise Command Brain ─────────────────────────────────
    op.create_table(
        'enterprise_brain_runs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('run_id', sa.String(length=100), nullable=False, unique=True),
        sa.Column('project_id', sa.Integer(), nullable=True),
        sa.Column('goal_description', sa.Text(), nullable=False),
        sa.Column('run_status', sa.String(length=30), nullable=False),
        sa.Column('priority', sa.Integer(), nullable=False),
        sa.Column('decision_tree_json', sa.Text(), nullable=False),
        sa.Column('dag_tasks_json', sa.Text(), nullable=False),
        sa.Column('execution_plan_json', sa.Text(), nullable=False),
        sa.Column('resource_allocation_json', sa.Text(), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_brain_runs_status', 'enterprise_brain_runs', ['run_status'])
    op.create_index('ix_brain_runs_project', 'enterprise_brain_runs', ['project_id'])

    # ── Module 2: Autonomous Workflow Composer ────────────────────────────────
    op.create_table(
        'workflow_templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('template_name', sa.String(length=150), nullable=False),
        sa.Column('category', sa.String(length=60), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('graph_definition_json', sa.Text(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['operators.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_workflow_templates_category', 'workflow_templates', ['category'])

    op.create_table(
        'workflow_executions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('template_id', sa.Integer(), nullable=True),
        sa.Column('execution_name', sa.String(length=150), nullable=False),
        sa.Column('execution_status', sa.String(length=30), nullable=False),
        sa.Column('current_step_id', sa.String(length=100), nullable=True),
        sa.Column('state_json', sa.Text(), nullable=False),
        sa.Column('execution_log_json', sa.Text(), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['template_id'], ['workflow_templates.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_workflow_executions_status', 'workflow_executions', ['execution_status'])

    # ── Module 3: Enterprise AI Agents Marketplace ───────────────────────────
    op.create_table(
        'agent_packages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('agent_name', sa.String(length=150), nullable=False),
        sa.Column('agent_key', sa.String(length=100), nullable=False, unique=True),
        sa.Column('agent_category', sa.String(length=60), nullable=False),
        sa.Column('version', sa.String(length=30), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('install_status', sa.String(length=30), nullable=False),
        sa.Column('health_status', sa.String(length=30), nullable=False),
        sa.Column('permissions_json', sa.Text(), nullable=False),
        sa.Column('config_json', sa.Text(), nullable=False),
        sa.Column('installed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_agent_packages_category', 'agent_packages', ['agent_category'])
    op.create_index('ix_agent_packages_status', 'agent_packages', ['install_status'])

    # ── Module 4: AI Business Process Understanding ──────────────────────────
    op.create_table(
        'business_processes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=True),
        sa.Column('process_name', sa.String(length=150), nullable=False),
        sa.Column('domain_type', sa.String(length=60), nullable=False),
        sa.Column('risk_score', sa.Float(), nullable=False),
        sa.Column('is_critical_path', sa.Boolean(), nullable=False),
        sa.Column('flow_graph_json', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_business_processes_domain', 'business_processes', ['domain_type'])

    op.create_table(
        'business_rules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('process_id', sa.Integer(), nullable=False),
        sa.Column('rule_name', sa.String(length=150), nullable=False),
        sa.Column('rule_condition', sa.Text(), nullable=False),
        sa.Column('severity', sa.String(length=30), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['process_id'], ['business_processes.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_business_rules_process', 'business_rules', ['process_id'])

    # ── Module 5: Autonomous Release Simulation ──────────────────────────────
    op.create_table(
        'release_simulations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('release_version', sa.String(length=60), nullable=False),
        sa.Column('simulated_by', sa.Integer(), nullable=True),
        sa.Column('rollback_probability_pct', sa.Float(), nullable=False),
        sa.Column('predicted_failures_count', sa.Integer(), nullable=False),
        sa.Column('perf_degradation_pct', sa.Float(), nullable=False),
        sa.Column('financial_risk_usd', sa.Float(), nullable=False),
        sa.Column('customer_impact_score', sa.Float(), nullable=False),
        sa.Column('breakdown_json', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['simulated_by'], ['operators.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_release_simulations_version', 'release_simulations', ['release_version'])

    # ── Module 7: Autonomous Incident Commander ──────────────────────────────
    op.create_table(
        'incidents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('incident_number', sa.String(length=100), nullable=False, unique=True),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('severity', sa.String(length=30), nullable=False),
        sa.Column('incident_status', sa.String(length=30), nullable=False),
        sa.Column('assigned_team', sa.String(length=100), nullable=False),
        sa.Column('root_cause_summary', sa.Text(), nullable=False),
        sa.Column('predicted_eta_minutes', sa.Integer(), nullable=False),
        sa.Column('recommendations_json', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_incidents_status', 'incidents', ['incident_status'])
    op.create_index('ix_incidents_severity', 'incidents', ['severity'])

    op.create_table(
        'incident_timelines',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('incident_id', sa.Integer(), nullable=False),
        sa.Column('event_type', sa.String(length=60), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('evidence_json', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['incident_id'], ['incidents.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_incident_timelines_incident', 'incident_timelines', ['incident_id'])

    # ── Module 8: Enterprise Knowledge Universe ─────────────────────────────
    op.create_table(
        'knowledge_universe_nodes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('node_key', sa.String(length=150), nullable=False, unique=True),
        sa.Column('label', sa.String(length=200), nullable=False),
        sa.Column('node_type', sa.String(length=60), nullable=False),
        sa.Column('attributes_json', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_ku_nodes_type', 'knowledge_universe_nodes', ['node_type'])

    op.create_table(
        'knowledge_universe_edges',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('source_node_id', sa.Integer(), nullable=False),
        sa.Column('target_node_id', sa.Integer(), nullable=False),
        sa.Column('relationship_type', sa.String(length=60), nullable=False),
        sa.Column('weight', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['source_node_id'], ['knowledge_universe_nodes.id']),
        sa.ForeignKeyConstraint(['target_node_id'], ['knowledge_universe_nodes.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_ku_edges_source', 'knowledge_universe_edges', ['source_node_id'])
    op.create_index('ix_ku_edges_target', 'knowledge_universe_edges', ['target_node_id'])

    # ── Module 9: AI Executive Advisor ───────────────────────────────────────
    op.create_table(
        'executive_insights',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('query_text', sa.Text(), nullable=False),
        sa.Column('resolved_intent', sa.String(length=100), nullable=False),
        sa.Column('advice_summary', sa.Text(), nullable=False),
        sa.Column('confidence_score', sa.Float(), nullable=False),
        sa.Column('details_json', sa.Text(), nullable=False),
        sa.Column('asked_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['asked_by'], ['operators.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    # ── Module 10: Autonomous Optimization Engine V2 ────────────────────────
    op.create_table(
        'optimization_histories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('target_subsystem', sa.String(length=60), nullable=False),
        sa.Column('before_state_json', sa.Text(), nullable=False),
        sa.Column('after_state_json', sa.Text(), nullable=False),
        sa.Column('gain_pct', sa.Float(), nullable=False),
        sa.Column('reasoning', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_opt_hist_target', 'optimization_histories', ['target_subsystem'])

    # ── Module 11: Enterprise Governance Center ──────────────────────────────
    op.create_table(
        'governance_policies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('policy_name', sa.String(length=150), nullable=False),
        sa.Column('policy_type', sa.String(length=60), nullable=False),
        sa.Column('rules_json', sa.Text(), nullable=False),
        sa.Column('is_enforced', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )

    # ── Module 12: AI Forecast Center ────────────────────────────────────────
    op.create_table(
        'forecast_metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('metric_type', sa.String(length=60), nullable=False),
        sa.Column('horizon_days', sa.Integer(), nullable=False),
        sa.Column('forecasted_value', sa.Float(), nullable=False),
        sa.Column('confidence_interval_low', sa.Float(), nullable=False),
        sa.Column('confidence_interval_high', sa.Float(), nullable=False),
        sa.Column('trend_json', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_forecast_metrics_type', 'forecast_metrics', ['metric_type'])

    # ── Module 13: Enterprise Report Factory V2 ──────────────────────────────
    op.create_table(
        'enterprise_reports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('report_title', sa.String(length=200), nullable=False),
        sa.Column('report_persona', sa.String(length=60), nullable=False),
        sa.Column('export_format', sa.String(length=20), nullable=False),
        sa.Column('content_json', sa.Text(), nullable=False),
        sa.Column('download_url', sa.String(length=500), nullable=True),
        sa.Column('generated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_enterprise_reports_persona', 'enterprise_reports', ['report_persona'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index('ix_enterprise_reports_persona', 'enterprise_reports')
    op.drop_table('enterprise_reports')

    op.drop_index('ix_forecast_metrics_type', 'forecast_metrics')
    op.drop_table('forecast_metrics')

    op.drop_table('governance_policies')

    op.drop_index('ix_opt_hist_target', 'optimization_histories')
    op.drop_table('optimization_histories')

    op.drop_table('executive_insights')

    op.drop_index('ix_ku_edges_target', 'knowledge_universe_edges')
    op.drop_index('ix_ku_edges_source', 'knowledge_universe_edges')
    op.drop_table('knowledge_universe_edges')
    op.drop_index('ix_ku_nodes_type', 'knowledge_universe_nodes')
    op.drop_table('knowledge_universe_nodes')

    op.drop_index('ix_incident_timelines_incident', 'incident_timelines')
    op.drop_table('incident_timelines')
    op.drop_index('ix_incidents_severity', 'incidents')
    op.drop_index('ix_incidents_status', 'incidents')
    op.drop_table('incidents')

    op.drop_index('ix_release_simulations_version', 'release_simulations')
    op.drop_table('release_simulations')

    op.drop_index('ix_business_rules_process', 'business_rules')
    op.drop_table('business_rules')
    op.drop_index('ix_business_processes_domain', 'business_processes')
    op.drop_table('business_processes')

    op.drop_index('ix_agent_packages_status', 'agent_packages')
    op.drop_index('ix_agent_packages_category', 'agent_packages')
    op.drop_table('agent_packages')

    op.drop_index('ix_workflow_executions_status', 'workflow_executions')
    op.drop_table('workflow_executions')
    op.drop_index('ix_workflow_templates_category', 'workflow_templates')
    op.drop_table('workflow_templates')

    op.drop_index('ix_brain_runs_project', 'enterprise_brain_runs')
    op.drop_index('ix_brain_runs_status', 'enterprise_brain_runs')
    op.drop_table('enterprise_brain_runs')
