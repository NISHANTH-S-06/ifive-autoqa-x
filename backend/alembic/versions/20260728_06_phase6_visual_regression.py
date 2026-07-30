"""Add Phase 6 Visual Regression Engine tables

Revision ID: 20260728_06_visual_regression
Revises: 20260725_05
Create Date: 2026-07-28 16:00:00.000000
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = '20260728_06_visual_regression'
down_revision: str | None = '15503d8e5637'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        'visual_baselines',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=120), nullable=False),
        sa.Column('module', sa.String(length=60), nullable=False),
        sa.Column('browser', sa.String(length=30), nullable=False),
        sa.Column('viewport_width', sa.Integer(), nullable=False),
        sa.Column('viewport_height', sa.Integer(), nullable=False),
        sa.Column('capture_type', sa.String(length=30), nullable=False),
        sa.Column('element_selector', sa.String(length=255), nullable=True),
        sa.Column('route_path', sa.String(length=255), nullable=False),
        sa.Column('image_path', sa.String(length=255), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('ignore_rules_json', sa.Text(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['operators.id']),
        sa.ForeignKeyConstraint(['project_id'], ['test_projects.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_visual_baselines_browser'), 'visual_baselines', ['browser'], unique=False)
    op.create_index(op.f('ix_visual_baselines_module'), 'visual_baselines', ['module'], unique=False)
    op.create_index(op.f('ix_visual_baselines_project_id'), 'visual_baselines', ['project_id'], unique=False)

    op.create_table(
        'visual_baseline_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('baseline_id', sa.Integer(), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('image_path', sa.String(length=255), nullable=False),
        sa.Column('ignore_rules_json', sa.Text(), nullable=True),
        sa.Column('change_summary', sa.Text(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['baseline_id'], ['visual_baselines.id']),
        sa.ForeignKeyConstraint(['created_by'], ['operators.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_visual_baseline_history_baseline_id'), 'visual_baseline_history', ['baseline_id'], unique=False)

    op.create_table(
        'visual_comparison_runs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('run_id', sa.Integer(), nullable=True),
        sa.Column('baseline_id', sa.Integer(), nullable=False),
        sa.Column('baseline_version', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=120), nullable=False),
        sa.Column('status', sa.String(length=30), nullable=False),
        sa.Column('browser', sa.String(length=30), nullable=False),
        sa.Column('viewport_width', sa.Integer(), nullable=False),
        sa.Column('viewport_height', sa.Integer(), nullable=False),
        sa.Column('module', sa.String(length=60), nullable=False),
        sa.Column('capture_type', sa.String(length=30), nullable=False),
        sa.Column('diff_percentage', sa.Float(), nullable=False),
        sa.Column('total_pixels_changed', sa.Integer(), nullable=False),
        sa.Column('layout_shifts', sa.Integer(), nullable=False),
        sa.Column('missing_elements_count', sa.Integer(), nullable=False),
        sa.Column('color_changes_count', sa.Integer(), nullable=False),
        sa.Column('font_changes_count', sa.Integer(), nullable=False),
        sa.Column('icon_changes_count', sa.Integer(), nullable=False),
        sa.Column('alignment_issues_count', sa.Integer(), nullable=False),
        sa.Column('spacing_changes_count', sa.Integer(), nullable=False),
        sa.Column('responsive_changes_count', sa.Integer(), nullable=False),
        sa.Column('ai_classification', sa.String(length=30), nullable=False),
        sa.Column('ai_confidence_score', sa.Integer(), nullable=False),
        sa.Column('ai_severity', sa.String(length=30), nullable=False),
        sa.Column('ai_root_cause', sa.Text(), nullable=True),
        sa.Column('ai_recommendation', sa.Text(), nullable=True),
        sa.Column('current_image_path', sa.String(length=255), nullable=False),
        sa.Column('diff_image_path', sa.String(length=255), nullable=True),
        sa.Column('overlay_image_path', sa.String(length=255), nullable=True),
        sa.Column('heatmap_image_path', sa.String(length=255), nullable=True),
        sa.Column('bounding_box_image_path', sa.String(length=255), nullable=True),
        sa.Column('metadata_json', sa.Text(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['baseline_id'], ['visual_baselines.id']),
        sa.ForeignKeyConstraint(['created_by'], ['operators.id']),
        sa.ForeignKeyConstraint(['project_id'], ['test_projects.id']),
        sa.ForeignKeyConstraint(['run_id'], ['automated_runs.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_visual_comparison_runs_ai_classification'), 'visual_comparison_runs', ['ai_classification'], unique=False)
    op.create_index(op.f('ix_visual_comparison_runs_baseline_id'), 'visual_comparison_runs', ['baseline_id'], unique=False)
    op.create_index(op.f('ix_visual_comparison_runs_browser'), 'visual_comparison_runs', ['browser'], unique=False)
    op.create_index(op.f('ix_visual_comparison_runs_module'), 'visual_comparison_runs', ['module'], unique=False)
    op.create_index(op.f('ix_visual_comparison_runs_project_id'), 'visual_comparison_runs', ['project_id'], unique=False)
    op.create_index(op.f('ix_visual_comparison_runs_run_id'), 'visual_comparison_runs', ['run_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_visual_comparison_runs_run_id'), table_name='visual_comparison_runs')
    op.drop_index(op.f('ix_visual_comparison_runs_project_id'), table_name='visual_comparison_runs')
    op.drop_index(op.f('ix_visual_comparison_runs_module'), table_name='visual_comparison_runs')
    op.drop_index(op.f('ix_visual_comparison_runs_browser'), table_name='visual_comparison_runs')
    op.drop_index(op.f('ix_visual_comparison_runs_baseline_id'), table_name='visual_comparison_runs')
    op.drop_index(op.f('ix_visual_comparison_runs_ai_classification'), table_name='visual_comparison_runs')
    op.drop_table('visual_comparison_runs')

    op.drop_index(op.f('ix_visual_baseline_history_baseline_id'), table_name='visual_baseline_history')
    op.drop_table('visual_baseline_history')

    op.drop_index(op.f('ix_visual_baselines_project_id'), table_name='visual_baselines')
    op.drop_index(op.f('ix_visual_baselines_module'), table_name='visual_baselines')
    op.drop_index(op.f('ix_visual_baselines_browser'), table_name='visual_baselines')
    op.drop_table('visual_baselines')
