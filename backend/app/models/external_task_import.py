"""ExternalTaskImport model for Phase 3 Connector Integration."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ExternalTaskImport(Base):
    __tablename__ = 'external_task_imports'
    __table_args__ = (
        UniqueConstraint(
            'project_id',
            'source_system',
            'source_task_id',
            'source_revision',
            name='uq_external_task_import_revision',
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey('projects.id'), nullable=False)

    source_system: Mapped[str] = mapped_column(String(64), nullable=False, default='MOCK_TASK_PORTAL')
    source_task_id: Mapped[str] = mapped_column(String(64), nullable=False)
    source_revision: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    source_status: Mapped[str] = mapped_column(String(64), nullable=False, default='TESTING_L2')

    project_name: Mapped[str] = mapped_column(String(128), nullable=False)
    module_name: Mapped[str] = mapped_column(String(128), nullable=False)
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    application_url: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    page_path: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    environment: Mapped[str] = mapped_column(String(64), nullable=False, default='local')

    expected_result: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    acceptance_criteria: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    test_data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    assigned_developer: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    assigned_tester: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    priority: Mapped[str] = mapped_column(String(32), nullable=False, default='MEDIUM')
    developer_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    imported_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    last_synced_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    import_status: Mapped[str] = mapped_column(String(64), nullable=False, default='DRAFT')
    template_type: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    approved_by: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    linked_test_plan_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('managed_test_cases.id'), nullable=True)
    linked_run_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('automated_runs.id'), nullable=True)

    callback_status: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    callback_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
