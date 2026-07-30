"""Add Phase 10 Digital QA Engineer tables

Revision ID: 20260728_09_phase10_digital_qa_engineer
Revises: 20260728_08_phase9_autonomous_platform
Create Date: 2026-07-28 18:20:00.000000
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = '20260728_09_phase10_digital_qa_engineer'
down_revision: str | None = '20260728_08_phase9_autonomous_platform'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        'ai_digital_qa_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=True),
        sa.Column('action_type', sa.String(length=60), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('payload_json', sa.Text(), nullable=False),
        sa.Column('reasoning_tree_json', sa.Text(), nullable=False),
        sa.Column('confidence_score', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ai_digital_qa_records_action_type'), 'ai_digital_qa_records', ['action_type'], unique=False)
    op.create_index(op.f('ix_ai_digital_qa_records_project_id'), 'ai_digital_qa_records', ['project_id'], unique=False)

    op.create_table(
        'digital_twin_entities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=True),
        sa.Column('product_id', sa.Integer(), nullable=True),
        sa.Column('entity_type', sa.String(length=60), nullable=False),
        sa.Column('entity_key', sa.String(length=160), nullable=False),
        sa.Column('label', sa.String(length=200), nullable=False),
        sa.Column('metadata_json', sa.Text(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.ForeignKeyConstraint(['product_id'], ['company_products.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_digital_twin_entities_company_id'), 'digital_twin_entities', ['company_id'], unique=False)
    op.create_index(op.f('ix_digital_twin_entities_entity_key'), 'digital_twin_entities', ['entity_key'], unique=False)
    op.create_index(op.f('ix_digital_twin_entities_entity_type'), 'digital_twin_entities', ['entity_type'], unique=False)
    op.create_index(op.f('ix_digital_twin_entities_product_id'), 'digital_twin_entities', ['product_id'], unique=False)

    op.create_table(
        'continuous_monitor_alerts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=True),
        sa.Column('target_url', sa.String(length=1000), nullable=False),
        sa.Column('alert_type', sa.String(length=80), nullable=False),
        sa.Column('severity', sa.String(length=30), nullable=False),
        sa.Column('details_json', sa.Text(), nullable=False),
        sa.Column('is_resolved', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_continuous_monitor_alerts_alert_type'), 'continuous_monitor_alerts', ['alert_type'], unique=False)
    op.create_index(op.f('ix_continuous_monitor_alerts_company_id'), 'continuous_monitor_alerts', ['company_id'], unique=False)
    op.create_index(op.f('ix_continuous_monitor_alerts_severity'), 'continuous_monitor_alerts', ['severity'], unique=False)

    op.create_table(
        'predictive_quality_metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=True),
        sa.Column('metric_type', sa.String(length=80), nullable=False),
        sa.Column('target_entity', sa.String(length=160), nullable=False),
        sa.Column('predicted_score', sa.Float(), nullable=False),
        sa.Column('confidence_score', sa.Float(), nullable=False),
        sa.Column('details_json', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_predictive_quality_metrics_metric_type'), 'predictive_quality_metrics', ['metric_type'], unique=False)
    op.create_index(op.f('ix_predictive_quality_metrics_project_id'), 'predictive_quality_metrics', ['project_id'], unique=False)

    op.create_table(
        'self_optimization_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('optimization_type', sa.String(length=80), nullable=False),
        sa.Column('improvement_summary', sa.String(length=250), nullable=False),
        sa.Column('metrics_before_json', sa.Text(), nullable=False),
        sa.Column('metrics_after_json', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_self_optimization_logs_optimization_type'), 'self_optimization_logs', ['optimization_type'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_self_optimization_logs_optimization_type'), table_name='self_optimization_logs')
    op.drop_table('self_optimization_logs')

    op.drop_index(op.f('ix_predictive_quality_metrics_project_id'), table_name='predictive_quality_metrics')
    op.drop_index(op.f('ix_predictive_quality_metrics_metric_type'), table_name='predictive_quality_metrics')
    op.drop_table('predictive_quality_metrics')

    op.drop_index(op.f('ix_continuous_monitor_alerts_severity'), table_name='continuous_monitor_alerts')
    op.drop_index(op.f('ix_continuous_monitor_alerts_company_id'), table_name='continuous_monitor_alerts')
    op.drop_index(op.f('ix_continuous_monitor_alerts_alert_type'), table_name='continuous_monitor_alerts')
    op.drop_table('continuous_monitor_alerts')

    op.drop_index(op.f('ix_digital_twin_entities_product_id'), table_name='digital_twin_entities')
    op.drop_index(op.f('ix_digital_twin_entities_entity_type'), table_name='digital_twin_entities')
    op.drop_index(op.f('ix_digital_twin_entities_entity_key'), table_name='digital_twin_entities')
    op.drop_index(op.f('ix_digital_twin_entities_company_id'), table_name='digital_twin_entities')
    op.drop_table('digital_twin_entities')

    op.drop_index(op.f('ix_ai_digital_qa_records_project_id'), table_name='ai_digital_qa_records')
    op.drop_index(op.f('ix_ai_digital_qa_records_action_type'), table_name='ai_digital_qa_records')
    op.drop_table('ai_digital_qa_records')
