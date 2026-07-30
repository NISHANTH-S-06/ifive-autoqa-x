"""Add Phase 15 Enterprise Software Quality Intelligence Platform (SQIP) tables

Revision ID: 20260729_14_phase15_quality_intelligence
Revises: 20260729_13_phase14_enterprise_ai_os
Create Date: 2026-07-29 13:00:00.000000
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = '20260729_14_phase15_quality_intelligence'
down_revision: str | None = '20260729_13_phase14_enterprise_ai_os'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Software Graph
    op.create_table(
        'software_graph_nodes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('node_key', sa.String(length=150), nullable=False, unique=True),
        sa.Column('label', sa.String(length=200), nullable=False),
        sa.Column('node_type', sa.String(length=60), nullable=False),
        sa.Column('attributes_json', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_sg_nodes_type', 'software_graph_nodes', ['node_type'])

    op.create_table(
        'software_graph_edges',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('source_node_id', sa.Integer(), nullable=False),
        sa.Column('target_node_id', sa.Integer(), nullable=False),
        sa.Column('relationship_type', sa.String(length=60), nullable=False),
        sa.Column('impact_weight', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['source_node_id'], ['software_graph_nodes.id']),
        sa.ForeignKeyConstraint(['target_node_id'], ['software_graph_nodes.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_sg_edges_source', 'software_graph_edges', ['source_node_id'])
    op.create_index('ix_sg_edges_target', 'software_graph_edges', ['target_node_id'])

    # Change Impact Records
    op.create_table(
        'change_impact_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('commit_hash', sa.String(length=100), nullable=False),
        sa.Column('author', sa.String(length=100), nullable=False),
        sa.Column('changed_files_json', sa.Text(), nullable=False),
        sa.Column('impacted_modules_json', sa.Text(), nullable=False),
        sa.Column('impacted_apis_json', sa.Text(), nullable=False),
        sa.Column('affected_tests_json', sa.Text(), nullable=False),
        sa.Column('risk_score', sa.Float(), nullable=False),
        sa.Column('estimated_execution_cost_usd', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_change_impact_commit', 'change_impact_records', ['commit_hash'])

    # Code Review Records
    op.create_table(
        'code_review_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('file_path', sa.String(length=300), nullable=False),
        sa.Column('language', sa.String(length=40), nullable=False),
        sa.Column('bugs_found_count', sa.Integer(), nullable=False),
        sa.Column('security_issues_count', sa.Integer(), nullable=False),
        sa.Column('code_smells_count', sa.Integer(), nullable=False),
        sa.Column('test_gaps_count', sa.Integer(), nullable=False),
        sa.Column('review_comments_json', sa.Text(), nullable=False),
        sa.Column('reviewed_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_code_review_file', 'code_review_records', ['file_path'])

    # Coverage Metrics
    op.create_table(
        'coverage_metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('dimension_type', sa.String(length=60), nullable=False),
        sa.Column('target_name', sa.String(length=150), nullable=False),
        sa.Column('coverage_pct', sa.Float(), nullable=False),
        sa.Column('missing_items_count', sa.Integer(), nullable=False),
        sa.Column('details_json', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_coverage_dimension', 'coverage_metrics', ['dimension_type'])

    # Release Intelligences
    op.create_table(
        'release_intelligences',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('release_version', sa.String(length=60), nullable=False),
        sa.Column('composite_release_score', sa.Float(), nullable=False),
        sa.Column('deployment_risk_pct', sa.Float(), nullable=False),
        sa.Column('rollback_risk_pct', sa.Float(), nullable=False),
        sa.Column('business_risk_pct', sa.Float(), nullable=False),
        sa.Column('security_risk_pct', sa.Float(), nullable=False),
        sa.Column('performance_risk_pct', sa.Float(), nullable=False),
        sa.Column('customer_risk_pct', sa.Float(), nullable=False),
        sa.Column('recommendation', sa.String(length=30), nullable=False),
        sa.Column('breakdown_json', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_release_intel_version', 'release_intelligences', ['release_version'])

    # Defect Clusters
    op.create_table(
        'defect_clusters',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('cluster_name', sa.String(length=150), nullable=False),
        sa.Column('root_cause_pattern', sa.Text(), nullable=False),
        sa.Column('defect_count', sa.Integer(), nullable=False),
        sa.Column('assigned_owner', sa.String(length=100), nullable=False),
        sa.Column('estimated_fix_hours', sa.Float(), nullable=False),
        sa.Column('priority', sa.String(length=30), nullable=False),
        sa.Column('customer_impact_rating', sa.String(length=30), nullable=False),
        sa.Column('defects_json', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )

    # Engineering Metrics
    op.create_table(
        'engineering_metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('metric_name', sa.String(length=100), nullable=False),
        sa.Column('metric_value', sa.Float(), nullable=False),
        sa.Column('unit', sa.String(length=30), nullable=False),
        sa.Column('trend_json', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_engineering_metric_type', 'engineering_metrics', ['metric_name'])

    # Quality Knowledge (Knowledge Lake)
    op.create_table(
        'quality_knowledges',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('item_type', sa.String(length=60), nullable=False),
        sa.Column('title', sa.String(length=250), nullable=False),
        sa.Column('content_text', sa.Text(), nullable=False),
        sa.Column('tags_json', sa.Text(), nullable=False),
        sa.Column('media_url', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_quality_knowledge_type', 'quality_knowledges', ['item_type'])

    # Mission Control Snapshots
    op.create_table(
        'mission_control_snapshots',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('global_health_score', sa.Float(), nullable=False),
        sa.Column('overall_risk_score', sa.Float(), nullable=False),
        sa.Column('overall_quality_score', sa.Float(), nullable=False),
        sa.Column('overall_coverage_pct', sa.Float(), nullable=False),
        sa.Column('ai_confidence_pct', sa.Float(), nullable=False),
        sa.Column('active_incidents_count', sa.Integer(), nullable=False),
        sa.Column('active_workers_count', sa.Integer(), nullable=False),
        sa.Column('monthly_cost_usd', sa.Float(), nullable=False),
        sa.Column('kpi_breakdown_json', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    op.drop_table('mission_control_snapshots')
    op.drop_index('ix_quality_knowledge_type', 'quality_knowledges')
    op.drop_table('quality_knowledges')
    op.drop_index('ix_engineering_metric_type', 'engineering_metrics')
    op.drop_table('engineering_metrics')
    op.drop_table('defect_clusters')
    op.drop_index('ix_release_intel_version', 'release_intelligences')
    op.drop_table('release_intelligences')
    op.drop_index('ix_coverage_dimension', 'coverage_metrics')
    op.drop_table('coverage_metrics')
    op.drop_index('ix_code_review_file', 'code_review_records')
    op.drop_table('code_review_records')
    op.drop_index('ix_change_impact_commit', 'change_impact_records')
    op.drop_table('change_impact_records')
    op.drop_index('ix_sg_edges_target', 'software_graph_edges')
    op.drop_index('ix_sg_edges_source', 'software_graph_edges')
    op.drop_table('software_graph_edges')
    op.drop_index('ix_sg_nodes_type', 'software_graph_nodes')
    op.drop_table('software_graph_nodes')
