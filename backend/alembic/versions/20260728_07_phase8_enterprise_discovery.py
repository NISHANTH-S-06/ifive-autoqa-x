"""Add Phase 8 Enterprise Hierarchy and Discovery tables

Revision ID: 20260728_07_enterprise_discovery
Revises: 20260728_06_visual_regression
Create Date: 2026-07-28 17:50:00.000000
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = '20260728_07_enterprise_discovery'
down_revision: str | None = '20260728_06_visual_regression'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        'companies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=180), nullable=False),
        sa.Column('code', sa.String(length=60), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code', name='uq_companies_code')
    )
    op.create_index(op.f('ix_companies_code'), 'companies', ['code'], unique=False)

    op.create_table(
        'company_products',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=180), nullable=False),
        sa.Column('code', sa.String(length=60), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('company_id', 'code', name='uq_company_products_company_code')
    )
    op.create_index(op.f('ix_company_products_company_id'), 'company_products', ['company_id'], unique=False)

    op.create_table(
        'company_modules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=180), nullable=False),
        sa.Column('code', sa.String(length=60), nullable=False),
        sa.Column('category', sa.String(length=60), nullable=False),
        sa.Column('parent_module_id', sa.Integer(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['parent_module_id'], ['company_modules.id']),
        sa.ForeignKeyConstraint(['product_id'], ['company_products.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('product_id', 'code', name='uq_company_modules_product_code')
    )
    op.create_index(op.f('ix_company_modules_product_id'), 'company_modules', ['product_id'], unique=False)

    op.create_table(
        'discovery_results',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=True),
        sa.Column('product_id', sa.Integer(), nullable=True),
        sa.Column('module_id', sa.Integer(), nullable=True),
        sa.Column('target_id', sa.Integer(), nullable=True),
        sa.Column('target_url', sa.String(length=1000), nullable=False),
        sa.Column('ui_map_json', sa.Text(), nullable=False),
        sa.Column('module_tree_json', sa.Text(), nullable=False),
        sa.Column('flow_graph_json', sa.Text(), nullable=False),
        sa.Column('recommendations_json', sa.Text(), nullable=False),
        sa.Column('risk_assessment_json', sa.Text(), nullable=False),
        sa.Column('confidence_score', sa.Float(), nullable=False),
        sa.Column('status', sa.String(length=30), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('reviewed_by', sa.Integer(), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.ForeignKeyConstraint(['created_by'], ['operators.id']),
        sa.ForeignKeyConstraint(['module_id'], ['company_modules.id']),
        sa.ForeignKeyConstraint(['product_id'], ['company_products.id']),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
        sa.ForeignKeyConstraint(['reviewed_by'], ['operators.id']),
        sa.ForeignKeyConstraint(['target_id'], ['connection_targets.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_discovery_results_created_at'), 'discovery_results', ['created_at'], unique=False)
    op.create_index(op.f('ix_discovery_results_project_id'), 'discovery_results', ['project_id'], unique=False)
    op.create_index(op.f('ix_discovery_results_status'), 'discovery_results', ['status'], unique=False)
    op.create_index(op.f('ix_discovery_results_target_id'), 'discovery_results', ['target_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_discovery_results_target_id'), table_name='discovery_results')
    op.drop_index(op.f('ix_discovery_results_status'), table_name='discovery_results')
    op.drop_index(op.f('ix_discovery_results_project_id'), table_name='discovery_results')
    op.drop_index(op.f('ix_discovery_results_created_at'), table_name='discovery_results')
    op.drop_table('discovery_results')

    op.drop_index(op.f('ix_company_modules_product_id'), table_name='company_modules')
    op.drop_table('company_modules')

    op.drop_index(op.f('ix_company_products_company_id'), table_name='company_products')
    op.drop_table('company_products')

    op.drop_index(op.f('ix_companies_code'), table_name='companies')
    op.drop_table('companies')
