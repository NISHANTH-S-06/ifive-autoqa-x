"""Task model for Mock Task Portal."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base

VALID_STATUSES = {
    'CREATED', 'ASSIGNED', 'IN_PROGRESS', 'TESTING_L1', 'TESTING_L2',
    'QA_RUNNING', 'QA_PASSED', 'QA_FAILED', 'REWORK',
    'DELIVERY_READY', 'DELIVERY_COMPLETED',
    'NEED_CLARITY', 'HOLD', 'CANCELLED',
}

VALID_PRIORITIES = {'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'}

# Allowed transitions: {from_status: {to_status: {roles that can perform}}}
ALLOWED_TRANSITIONS: dict[str, dict[str, set[str]]] = {
    'CREATED':            {'ASSIGNED': {'SUPERADMIN'}},
    'ASSIGNED':           {'IN_PROGRESS': {'DEVELOPER'}, 'NEED_CLARITY': {'DEVELOPER', 'SUPERADMIN'}, 'HOLD': {'SUPERADMIN'}, 'CANCELLED': {'SUPERADMIN'}},
    'IN_PROGRESS':        {'TESTING_L1': {'DEVELOPER'}, 'NEED_CLARITY': {'DEVELOPER', 'SUPERADMIN'}, 'HOLD': {'SUPERADMIN'}, 'CANCELLED': {'SUPERADMIN'}},
    'TESTING_L1':         {'TESTING_L2': {'DEVELOPER', 'SUPERADMIN'}, 'IN_PROGRESS': {'DEVELOPER'}, 'NEED_CLARITY': {'DEVELOPER', 'SUPERADMIN'}, 'HOLD': {'SUPERADMIN'}, 'CANCELLED': {'SUPERADMIN'}},
    'TESTING_L2':         {'QA_RUNNING': {'TESTER'}, 'NEED_CLARITY': {'TESTER', 'SUPERADMIN'}, 'HOLD': {'SUPERADMIN'}, 'CANCELLED': {'SUPERADMIN'}},
    'QA_RUNNING':         {'QA_PASSED': {'TESTER'}, 'QA_FAILED': {'TESTER'}, 'NEED_CLARITY': {'TESTER', 'SUPERADMIN'}, 'HOLD': {'SUPERADMIN'}, 'CANCELLED': {'SUPERADMIN'}},
    'QA_FAILED':          {'REWORK': {'TESTER', 'SUPERADMIN'}},
    'REWORK':             {'IN_PROGRESS': {'DEVELOPER'}, 'NEED_CLARITY': {'DEVELOPER', 'SUPERADMIN'}, 'CANCELLED': {'SUPERADMIN'}},
    'QA_PASSED':          {'DELIVERY_READY': {'SUPERADMIN'}},
    'DELIVERY_READY':     {'DELIVERY_COMPLETED': {'DELIVERY'}, 'HOLD': {'SUPERADMIN'}},
    'NEED_CLARITY':       {'ASSIGNED': {'SUPERADMIN'}, 'IN_PROGRESS': {'DEVELOPER', 'SUPERADMIN'}, 'HOLD': {'SUPERADMIN'}, 'CANCELLED': {'SUPERADMIN'}},
    'HOLD':               {'ASSIGNED': {'SUPERADMIN'}, 'IN_PROGRESS': {'DEVELOPER', 'SUPERADMIN'}, 'CANCELLED': {'SUPERADMIN'}},
    'DELIVERY_COMPLETED': {},
    'CANCELLED':          {},
}

TERMINAL_STATUSES = {'DELIVERY_COMPLETED', 'CANCELLED'}


class Task(Base):
    __tablename__ = 'tasks'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_code: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    project_name: Mapped[str] = mapped_column(String(128), nullable=False)
    module_name: Mapped[str] = mapped_column(String(128), nullable=False)
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    assigned_developer: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    assigned_tester: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    task_given_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    target_date: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    priority: Mapped[str] = mapped_column(String(16), nullable=False, default='MEDIUM')
    application_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    page_path: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    environment: Mapped[str] = mapped_column(String(64), nullable=False, default='local')
    expected_result: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    acceptance_criteria: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    test_data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    developer_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    rework_remarks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    revision: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default='CREATED')
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    testing_l2_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
