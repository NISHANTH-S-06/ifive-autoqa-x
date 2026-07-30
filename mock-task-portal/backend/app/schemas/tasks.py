"""Pydantic schemas for tasks."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator

from app.models.task import VALID_PRIORITIES, VALID_STATUSES


class TaskCreate(BaseModel):
    task_code: str = Field(..., min_length=1, max_length=64)
    project_name: str = Field(..., min_length=1, max_length=128)
    module_name: str = Field(..., min_length=1, max_length=128)
    title: str = Field(..., min_length=1, max_length=256)
    description: Optional[str] = None
    assigned_developer: Optional[str] = None
    assigned_tester: Optional[str] = None
    task_given_by: Optional[str] = None
    target_date: Optional[str] = None
    priority: str = 'MEDIUM'
    application_url: Optional[str] = None
    page_path: Optional[str] = None
    environment: str = 'local'
    expected_result: Optional[str] = None
    acceptance_criteria: Optional[str] = None
    test_data: Optional[str] = None

    @field_validator('priority')
    @classmethod
    def validate_priority(cls, v: str) -> str:
        if v not in VALID_PRIORITIES:
            raise ValueError(f'priority must be one of {VALID_PRIORITIES}')
        return v


class TaskUpdate(BaseModel):
    project_name: Optional[str] = None
    module_name: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    assigned_developer: Optional[str] = None
    assigned_tester: Optional[str] = None
    task_given_by: Optional[str] = None
    target_date: Optional[str] = None
    priority: Optional[str] = None
    application_url: Optional[str] = None
    page_path: Optional[str] = None
    environment: Optional[str] = None
    expected_result: Optional[str] = None
    acceptance_criteria: Optional[str] = None
    test_data: Optional[str] = None

    @field_validator('priority')
    @classmethod
    def validate_priority(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in VALID_PRIORITIES:
            raise ValueError(f'priority must be one of {VALID_PRIORITIES}')
        return v


class StatusTransitionRequest(BaseModel):
    new_status: str
    reason: Optional[str] = None

    @field_validator('new_status')
    @classmethod
    def validate_status(cls, v: str) -> str:
        if v not in VALID_STATUSES:
            raise ValueError(f'status must be one of {VALID_STATUSES}')
        return v


class DeveloperNotesRequest(BaseModel):
    notes: str = Field(..., min_length=1)


class ReworkRemarksRequest(BaseModel):
    remarks: str = Field(..., min_length=1)


class QAResultRequest(BaseModel):
    result: str  # PASS, FAIL, BLOCKED
    reason: Optional[str] = None

    @field_validator('result')
    @classmethod
    def validate_result(cls, v: str) -> str:
        if v not in {'PASS', 'FAIL', 'BLOCKED'}:
            raise ValueError('result must be PASS, FAIL, or BLOCKED')
        return v


class TaskOut(BaseModel):
    id: int
    task_code: str
    project_name: str
    module_name: str
    title: str
    description: Optional[str]
    assigned_developer: Optional[str]
    assigned_tester: Optional[str]
    task_given_by: Optional[str]
    target_date: Optional[str]
    priority: str
    application_url: Optional[str]
    page_path: Optional[str]
    environment: str
    expected_result: Optional[str]
    acceptance_criteria: Optional[str]
    test_data: Optional[str]
    developer_notes: Optional[str]
    rework_remarks: Optional[str]
    revision: int
    status: str
    created_at: datetime
    updated_at: datetime
    testing_l2_at: Optional[datetime]
    completed_at: Optional[datetime]

    model_config = {'from_attributes': True}


class TestingL2TaskOut(BaseModel):
    """Connector contract for AutoQA integration — do not change field names."""
    source_system: str = 'MOCK_TASK_PORTAL'
    source_task_id: int
    source_revision: int
    project_name: str
    module_name: str
    title: str
    description: Optional[str]
    application_url: Optional[str]
    page_path: Optional[str]
    environment: str
    expected_result: Optional[str]
    acceptance_criteria: Optional[str]
    test_data: Optional[str]
    assigned_developer: Optional[str]
    assigned_tester: Optional[str]
    priority: str
    developer_notes: Optional[str]
    status: str
    testing_l2_at: Optional[datetime]

    model_config = {'from_attributes': True}
