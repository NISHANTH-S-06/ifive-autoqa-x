"""external task imports

Revision ID: 20260721_03
Revises: 20260715_02
Create Date: 2026-07-21 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20260721_03'
down_revision = '20260715_02'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'external_task_imports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('source_system', sa.String(length=64), nullable=False),
        sa.Column('source_task_id', sa.String(length=64), nullable=False),
        sa.Column('source_revision', sa.Integer(), nullable=False),
        sa.Column('source_status', sa.String(length=64), nullable=False),
        sa.Column('project_name', sa.String(length=128), nullable=False),
        sa.Column('module_name', sa.String(length=128), nullable=False),
        sa.Column('title', sa.String(length=256), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('application_url', sa.String(length=256), nullable=True),
        sa.Column('page_path', sa.String(length=256), nullable=True),
        sa.Column('environment', sa.String(length=64), nullable=False),
        sa.Column('expected_result', sa.Text(), nullable=True),
        sa.Column('acceptance_criteria', sa.Text(), nullable=True),
        sa.Column('test_data', sa.Text(), nullable=True),
        sa.Column('assigned_developer', sa.String(length=128), nullable=True),
        sa.Column('assigned_tester', sa.String(length=128), nullable=True),
        sa.Column('priority', sa.String(length=32), nullable=False),
        sa.Column('developer_notes', sa.Text(), nullable=True),
        sa.Column('imported_at', sa.DateTime(), nullable=False),
        sa.Column('last_synced_at', sa.DateTime(), nullable=False),
        sa.Column('import_status', sa.String(length=64), nullable=False),
        sa.Column('template_type', sa.String(length=64), nullable=True),
        sa.Column('approved_by', sa.String(length=128), nullable=True),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.Column('linked_test_plan_id', sa.Integer(), nullable=True),
        sa.Column('linked_run_id', sa.Integer(), nullable=True),
        sa.Column('callback_status', sa.String(length=64), nullable=True),
        sa.Column('callback_error', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['linked_run_id'], ['automated_runs.id'], ),
        sa.ForeignKeyConstraint(['linked_test_plan_id'], ['managed_test_cases.id'], ),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('project_id', 'source_system', 'source_task_id', 'source_revision', name='uq_external_task_import_revision')
    )


def downgrade() -> None:
    op.drop_table('external_task_imports')
