"""Add Phase 11 Self-Evolving Brain tables

Revision ID: 20260728_10_phase11_self_evolving_brain
Revises: 20260728_09_phase10_digital_qa_engineer
Create Date: 2026-07-28 18:40:00.000000
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = '20260728_10_phase11_self_evolving_brain'
down_revision: str | None = '20260728_09_phase10_digital_qa_engineer'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        'ai_experience_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=True),
        sa.Column('experience_type', sa.String(length=60), nullable=False),
        sa.Column('entity_key', sa.String(length=160), nullable=False),
        sa.Column('experience_data_json', sa.Text(), nullable=False),
        sa.Column('confidence_score', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ai_experience_records_entity_key'), 'ai_experience_records', ['entity_key'], unique=False)
    op.create_index(op.f('ix_ai_experience_records_experience_type'), 'ai_experience_records', ['experience_type'], unique=False)
    op.create_index(op.f('ix_ai_experience_records_project_id'), 'ai_experience_records', ['project_id'], unique=False)

    op.create_table(
        'pattern_detection_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=True),
        sa.Column('pattern_type', sa.String(length=80), nullable=False),
        sa.Column('pattern_key', sa.String(length=160), nullable=False),
        sa.Column('pattern_score', sa.Float(), nullable=False),
        sa.Column('details_json', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_pattern_detection_records_pattern_type'), 'pattern_detection_records', ['pattern_type'], unique=False)
    op.create_index(op.f('ix_pattern_detection_records_project_id'), 'pattern_detection_records', ['project_id'], unique=False)

    op.create_table(
        'test_evolution_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=True),
        sa.Column('action_type', sa.String(length=60), nullable=False),
        sa.Column('test_name', sa.String(length=200), nullable=False),
        sa.Column('details_json', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_test_evolution_records_action_type'), 'test_evolution_records', ['action_type'], unique=False)
    op.create_index(op.f('ix_test_evolution_records_project_id'), 'test_evolution_records', ['project_id'], unique=False)

    op.create_table(
        'root_cause_graph_nodes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=True),
        sa.Column('entity_type', sa.String(length=60), nullable=False),
        sa.Column('entity_key', sa.String(length=160), nullable=False),
        sa.Column('label', sa.String(length=200), nullable=False),
        sa.Column('metadata_json', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_root_cause_graph_nodes_entity_type'), 'root_cause_graph_nodes', ['entity_type'], unique=False)
    op.create_index(op.f('ix_root_cause_graph_nodes_project_id'), 'root_cause_graph_nodes', ['project_id'], unique=False)

    op.create_table(
        'root_cause_graph_edges',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('source_node_id', sa.Integer(), nullable=False),
        sa.Column('target_node_id', sa.Integer(), nullable=False),
        sa.Column('relationship_type', sa.String(length=80), nullable=False),
        sa.Column('properties_json', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['source_node_id'], ['root_cause_graph_nodes.id']),
        sa.ForeignKeyConstraint(['target_node_id'], ['root_cause_graph_nodes.id']),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('root_cause_graph_edges')

    op.drop_index(op.f('ix_root_cause_graph_nodes_project_id'), table_name='root_cause_graph_nodes')
    op.drop_index(op.f('ix_root_cause_graph_nodes_entity_type'), table_name='root_cause_graph_nodes')
    op.drop_table('root_cause_graph_nodes')

    op.drop_index(op.f('ix_test_evolution_records_project_id'), table_name='test_evolution_records')
    op.drop_index(op.f('ix_test_evolution_records_action_type'), table_name='test_evolution_records')
    op.drop_table('test_evolution_records')

    op.drop_index(op.f('ix_pattern_detection_records_project_id'), table_name='pattern_detection_records')
    op.drop_index(op.f('ix_pattern_detection_records_pattern_type'), table_name='pattern_detection_records')
    op.drop_table('pattern_detection_records')

    op.drop_index(op.f('ix_ai_experience_records_project_id'), table_name='ai_experience_records')
    op.drop_index(op.f('ix_ai_experience_records_experience_type'), table_name='ai_experience_records')
    op.drop_index(op.f('ix_ai_experience_records_entity_key'), table_name='ai_experience_records')
    op.drop_table('ai_experience_records')
