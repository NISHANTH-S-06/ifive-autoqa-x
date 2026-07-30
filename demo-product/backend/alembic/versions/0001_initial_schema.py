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
        'sessions',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
        sa.Column('token_hash', sa.String(256), nullable=False, unique=True),
        sa.Column('expires_at', sa.DateTime, nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.current_timestamp()),
    )

    op.create_table(
        'departments',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(128), nullable=False, unique=True),
    )

    op.create_table(
        'employees',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('employee_code', sa.String(64), nullable=False, unique=True),
        sa.Column('name', sa.String(128), nullable=False),
        sa.Column('email', sa.String(128), nullable=False, unique=True),
        sa.Column('department_id', sa.Integer, sa.ForeignKey('departments.id'), nullable=False),
        sa.Column('joining_date', sa.String(32), nullable=False),
        sa.Column('active', sa.Boolean, nullable=False, default=True),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.current_timestamp()),
    )

    op.create_table(
        'products',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('product_code', sa.String(64), nullable=False, unique=True),
        sa.Column('name', sa.String(256), nullable=False),
        sa.Column('current_quantity', sa.Integer, nullable=False, default=0),
    )

    op.create_table(
        'stock_counts',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('product_id', sa.Integer, sa.ForeignKey('products.id'), nullable=False),
        sa.Column('previous_quantity', sa.Integer, nullable=False),
        sa.Column('counted_quantity', sa.Integer, nullable=False),
        sa.Column('difference', sa.Integer, nullable=False),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('created_by', sa.String(64), nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.current_timestamp()),
    )

    op.create_table(
        'demo_settings',
        sa.Column('key', sa.String(64), primary_key=True),
        sa.Column('enabled', sa.Boolean, nullable=False, default=False),
        sa.Column('value', sa.Text, nullable=True),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.current_timestamp()),
    )


def downgrade() -> None:
    op.drop_table('demo_settings')
    op.drop_table('stock_counts')
    op.drop_table('products')
    op.drop_table('employees')
    op.drop_table('departments')
    op.drop_table('sessions')
    op.drop_table('users')
