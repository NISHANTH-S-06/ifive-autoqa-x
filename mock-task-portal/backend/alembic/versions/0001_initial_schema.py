"""0001 initial schema

Revision ID: 0001
Revises:
Create Date: 2026-07-21
"""
from __future__ import annotations
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '0001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('username', sa.String(64), nullable=False, unique=True),
        sa.Column('display_name', sa.String(128), nullable=False),
        sa.Column('password_hash', sa.String(256), nullable=False),
        sa.Column('role', sa.String(32), nullable=False),
        sa.Column('is_active', sa.Boolean, nullable=False, default=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.current_timestamp()),
    )

    op.create_table(
        'tasks',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('task_code', sa.String(64), nullable=False, unique=True),
        sa.Column('project_name', sa.String(128), nullable=False),
        sa.Column('module_name', sa.String(128), nullable=False),
        sa.Column('title', sa.String(256), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('assigned_developer', sa.String(64), nullable=True),
        sa.Column('assigned_tester', sa.String(64), nullable=True),
        sa.Column('task_given_by', sa.String(64), nullable=True),
        sa.Column('target_date', sa.String(32), nullable=True),
        sa.Column('priority', sa.String(16), nullable=False, default='MEDIUM'),
        sa.Column('application_url', sa.String(512), nullable=True),
        sa.Column('page_path', sa.String(256), nullable=True),
        sa.Column('environment', sa.String(64), nullable=False, default='local'),
        sa.Column('expected_result', sa.Text, nullable=True),
        sa.Column('acceptance_criteria', sa.Text, nullable=True),
        sa.Column('test_data', sa.Text, nullable=True),
        sa.Column('developer_notes', sa.Text, nullable=True),
        sa.Column('rework_remarks', sa.Text, nullable=True),
        sa.Column('revision', sa.Integer, nullable=False, default=0),
        sa.Column('status', sa.String(32), nullable=False, default='CREATED'),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column('testing_l2_at', sa.DateTime, nullable=True),
        sa.Column('completed_at', sa.DateTime, nullable=True),
    )

    op.create_table(
        'task_history',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('task_id', sa.Integer, sa.ForeignKey('tasks.id'), nullable=False),
        sa.Column('previous_status', sa.String(32), nullable=True),
        sa.Column('new_status', sa.String(32), nullable=False),
        sa.Column('changed_by', sa.String(64), nullable=False),
        sa.Column('reason', sa.Text, nullable=True),
        sa.Column('timestamp', sa.DateTime, nullable=False, server_default=sa.func.current_timestamp()),
    )

    op.create_table(
        'user_sessions',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
        sa.Column('token_hash', sa.String(256), nullable=False, unique=True),
        sa.Column('expires_at', sa.DateTime, nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.current_timestamp()),
    )


def downgrade() -> None:
    op.drop_table('user_sessions')
    op.drop_table('task_history')
    op.drop_table('tasks')
    op.drop_table('users')
