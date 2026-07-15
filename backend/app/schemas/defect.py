from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.test_management import Page


class DefectStatus(str, Enum):
  NEW = 'NEW'
  TRIAGED = 'TRIAGED'
  ASSIGNED = 'ASSIGNED'
  IN_PROGRESS = 'IN_PROGRESS'
  FIXED = 'FIXED'
  READY_FOR_RETEST = 'READY_FOR_RETEST'
  RETEST_PASSED = 'RETEST_PASSED'
  REOPENED = 'REOPENED'
  CLOSED = 'CLOSED'
  REJECTED = 'REJECTED'
  DUPLICATE = 'DUPLICATE'


class SeverityPriority(str, Enum):
  LOW = 'LOW'
  MEDIUM = 'MEDIUM'
  HIGH = 'HIGH'
  CRITICAL = 'CRITICAL'


class DefectSourceType(str, Enum):
  MANUAL_RUN_CASE = 'MANUAL_RUN_CASE'
  MANUAL_STEP = 'MANUAL_STEP'
  AUTOMATED_RUN = 'AUTOMATED_RUN'
  AUTOMATED_RUN_CASE = 'AUTOMATED_RUN_CASE'
  AUTOMATED_STEP = 'AUTOMATED_STEP'


def _strip(value: str) -> str:
  value = value.strip()
  if not value:
    raise ValueError('must not be blank')
  if any(ord(ch) < 32 and ch not in '\r\n\t' for ch in value):
    raise ValueError('control characters are not allowed')
  return value


class DefectCreate(BaseModel):
  title: str = Field(min_length=1, max_length=220)
  description: str | None = Field(default=None, max_length=5000)
  project_id: int
  module_id: int | None = None
  suite_id: int | None = None
  test_case_id: int | None = None
  test_case_version: int | None = Field(default=None, ge=1)
  severity: SeverityPriority = SeverityPriority.MEDIUM
  priority: SeverityPriority = SeverityPriority.MEDIUM
  assigned_to: int | None = None
  environment: str | None = Field(default=None, max_length=80)
  failure_category: str | None = Field(default=None, max_length=80)
  expected_result: str | None = Field(default=None, max_length=5000)
  actual_result: str | None = Field(default=None, max_length=5000)
  reproduction_steps: str | None = Field(default=None, max_length=5000)

  @field_validator('title')
  @classmethod
  def strip_title(cls, value: str) -> str:
    return _strip(value)


class DefectFromRunCreate(BaseModel):
  source_type: DefectSourceType
  manual_run_case_id: int | None = None
  manual_step_result_id: int | None = None
  automated_run_id: int | None = None
  automated_run_case_id: int | None = None
  automated_step_result_id: int | None = None
  title: str | None = Field(default=None, max_length=220)
  severity: SeverityPriority = SeverityPriority.MEDIUM
  priority: SeverityPriority = SeverityPriority.MEDIUM
  assigned_to: int | None = None
  confirm: bool = False


class DefectUpdate(BaseModel):
  title: str | None = Field(default=None, min_length=1, max_length=220)
  description: str | None = Field(default=None, max_length=5000)
  severity: SeverityPriority | None = None
  priority: SeverityPriority | None = None
  assigned_to: int | None = None


class DefectTransition(BaseModel):
  reason: str | None = Field(default=None, max_length=1000)
  resolution: str | None = Field(default=None, max_length=2000)
  assigned_to: int | None = None
  duplicate_of_defect_id: int | None = None


class DefectCommentCreate(BaseModel):
  body: str = Field(min_length=1, max_length=5000)

  @field_validator('body')
  @classmethod
  def strip_body(cls, value: str) -> str:
    return _strip(value)


class DefectRetestCreate(BaseModel):
  use_latest_approved_version: bool = False
  result_status: str = Field(default='PLANNED', max_length=30)
  notes: str | None = Field(default=None, max_length=2000)


class DefectRead(BaseModel):
  model_config = ConfigDict(from_attributes=True)
  id: int
  defect_key: str
  title: str
  description: str | None
  project_id: int
  module_id: int | None
  suite_id: int | None
  test_case_id: int | None
  test_case_version: int | None
  manual_run_id: int | None
  manual_run_case_id: int | None
  manual_step_result_id: int | None
  automated_run_id: int | None
  automated_run_case_id: int | None
  automated_step_result_id: int | None
  severity: str
  priority: str
  status: str
  assigned_to: int | None
  reporter_id: int
  environment: str | None
  target_id: int | None
  target_version: int | None
  failure_category: str | None
  expected_result: str | None
  actual_result: str | None
  reproduction_steps: str | None
  resolution: str | None
  duplicate_of_defect_id: int | None
  created_by: int
  created_at: datetime
  updated_at: datetime
  closed_at: datetime | None
  archived_at: datetime | None


class DefectList(BaseModel):
  items: list[DefectRead]
  page: Page


class DefectCommentRead(BaseModel):
  model_config = ConfigDict(from_attributes=True)
  id: int
  defect_id: int
  body: str
  created_by: int
  created_at: datetime


class DefectHistoryRead(BaseModel):
  model_config = ConfigDict(from_attributes=True)
  id: int
  defect_id: int
  event_type: str
  old_value: str | None
  new_value: str | None
  safe_message: str | None
  created_by: int
  created_at: datetime


class DefectEvidenceLinkRead(BaseModel):
  model_config = ConfigDict(from_attributes=True)
  id: int
  defect_id: int
  manual_evidence_id: int | None
  execution_artifact_id: int | None
  link_type: str
  created_by: int
  created_at: datetime


class DefectRetestRead(BaseModel):
  model_config = ConfigDict(from_attributes=True)
  id: int
  defect_id: int
  manual_run_id: int | None
  automated_run_id: int | None
  test_case_id: int | None
  test_case_version: int | None
  target_id: int | None
  target_version: int | None
  result_status: str
  safe_notes: str | None
  created_by: int
  created_at: datetime
