"""Add Phase 9 Autonomous Platform tables

Revision ID: 20260728_08_phase9_autonomous_platform
Revises: 20260728_07_enterprise_discovery
Create Date: 2026-07-28 18:00:00.000000
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = '20260728_08_phase9_autonomous_platform'
down_revision: str | None = '20260728_07_enterprise_discovery'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        'ai_memory_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=True),
        sa.Column('memory_type', sa.String(length=60), nullable=False),
        sa.Column('entity_key', sa.String(length=160), nullable=False),
        sa.Column('memory_data_json', sa.Text(), nullable=False),
        sa.Column('confidence_score', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ai_memory_records_entity_key'), 'ai_memory_records', ['entity_key'], unique=False)
    op.create_index(op.f('ix_ai_memory_records_memory_type'), 'ai_memory_records', ['memory_type'], unique=False)
    op.create_index(op.f('ix_ai_memory_records_project_id'), 'ai_memory_records', ['project_id'], unique=False)

    op.create_table(
        'ai_locator_histories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=True),
        sa.Column('target_url', sa.String(length=1000), nullable=False),
        sa.Column('element_name', sa.String(length=160), nullable=False),
        sa.Column('selector', sa.String(length=500), nullable=False),
        sa.Column('alternative_selectors_json', sa.Text(), nullable=False),
        sa.Column('success_count', sa.Integer(), nullable=False),
        sa.Column('failure_count', sa.Integer(), nullable=False),
        sa.Column('last_healed_at', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(length=30), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ai_locator_histories_project_id'), 'ai_locator_histories', ['project_id'], unique=False)
    op.create_index(op.f('ix_ai_locator_histories_target_url'), 'ai_locator_histories', ['target_url'], unique=False)

    op.create_table(
        'knowledge_graph_nodes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('node_type', sa.String(length=60), nullable=False),
        sa.Column('entity_id', sa.String(length=100), nullable=False),
        sa.Column('label', sa.String(length=200), nullable=False),
        sa.Column('properties_json', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_knowledge_graph_nodes_node_type'), 'knowledge_graph_nodes', ['node_type'], unique=False)

    op.create_table(
        'knowledge_graph_edges',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('source_node_id', sa.Integer(), nullable=False),
        sa.Column('target_node_id', sa.Integer(), nullable=False),
        sa.Column('relationship_type', sa.String(length=80), nullable=False),
        sa.Column('properties_json', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['source_node_id'], ['knowledge_graph_nodes.id']),
        sa.ForeignKeyConstraint(['target_node_id'], ['knowledge_graph_nodes.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_knowledge_graph_edges_source_node_id'), 'knowledge_graph_edges', ['source_node_id'], unique=False)
    op.create_index(op.f('ix_knowledge_graph_edges_target_node_id'), 'knowledge_graph_edges', ['target_node_id'], unique=False)

    op.create_table(
        'release_readiness_evaluations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('release_version', sa.String(length=60), nullable=False),
        sa.Column('release_score', sa.Float(), nullable=False),
        sa.Column('readiness_status', sa.String(length=30), nullable=False),
        sa.Column('automation_coverage', sa.Float(), nullable=False),
        sa.Column('pass_rate', sa.Float(), nullable=False),
        sa.Column('open_critical_bugs', sa.Integer(), nullable=False),
        sa.Column('risk_score', sa.Float(), nullable=False),
        sa.Column('breakdown_json', sa.Text(), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['operators.id']),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_release_readiness_evaluations_project_id'), 'release_readiness_evaluations', ['project_id'], unique=False)
    op.create_index(op.f('ix_release_readiness_evaluations_readiness_status'), 'release_readiness_evaluations', ['readiness_status'], unique=False)

    op.create_table(
        'notification_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('channel', sa.String(length=40), nullable=False),
        sa.Column('notification_type', sa.String(length=80), nullable=False),
        sa.Column('recipient', sa.String(length=200), nullable=False),
        sa.Column('title', sa.String(length=250), nullable=False),
        sa.Column('body_text', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=30), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notification_logs_status'), 'notification_logs', ['status'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_notification_logs_status'), table_name='notification_logs')
    op.drop_table('notification_logs')

    op.drop_index(op.f('ix_release_readiness_evaluations_readiness_status'), table_name='release_readiness_evaluations')
    op.drop_index(op.f('ix_release_readiness_evaluations_project_id'), table_name='release_readiness_evaluations')
    op.drop_table('release_readiness_evaluations')

    op.drop_index(op.f('ix_knowledge_graph_edges_target_node_id'), table_name='knowledge_graph_edges')
    op.drop_index(op.f('ix_knowledge_graph_edges_source_node_id'), table_name='knowledge_graph_edges')
    op.drop_table('knowledge_graph_edges')

    op.drop_index(op.f('ix_knowledge_graph_nodes_node_type'), table_name='knowledge_graph_nodes')
    op.drop_table('knowledge_graph_nodes')

    op.drop_index(op.f('ix_ai_locator_histories_target_url'), table_name='ai_locator_histories')
    op.drop_index(op.f('ix_ai_locator_histories_project_id'), table_name='ai_locator_histories')
    op.drop_table('ai_locator_histories')

    op.drop_index(op.f('ix_ai_memory_records_project_id'), table_name='ai_memory_records')
    op.drop_index(op.f('ix_ai_memory_records_memory_type'), table_name='ai_memory_records')
    op.drop_index(op.f('ix_ai_memory_records_entity_key'), table_name='ai_memory_records')
    op.drop_table('ai_memory_records')
