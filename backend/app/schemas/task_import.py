"""Pydantic schemas for Task Import API."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class TaskImportOut(BaseModel):
    id: int
    project_id: int
    source_system: str
    source_task_id: str
    source_revision: int
    source_status: str
    project_name: str
    module_name: str
    title: str
    description: Optional[str] = None
    application_url: str
    page_path: str
    environment: str
    expected_result: Optional[str] = None
    acceptance_criteria: Optional[str] = None
    test_data: Optional[str] = None
    assigned_developer: Optional[str] = None
    assigned_tester: Optional[str] = None
    priority: str
    developer_notes: Optional[str] = None
    imported_at: datetime
    last_synced_at: datetime
    import_status: str
    template_type: Optional[str] = None
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    linked_test_plan_id: Optional[int] = None
    linked_run_id: Optional[int] = None
    callback_status: Optional[str] = None
    callback_error: Optional[str] = None

    model_config = {'from_attributes': True}
