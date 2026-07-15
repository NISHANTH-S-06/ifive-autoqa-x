from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.schemas.result import EvidenceRead, TestResultRead


class TestRunStatus(str, Enum):
  QUEUED = 'QUEUED'
  APPROVED = 'APPROVED'
  RUNNING = 'RUNNING'
  PASSED = 'PASSED'
  FAILED = 'FAILED'
  CANCELLED = 'CANCELLED'


class TestRunRead(BaseModel):
  model_config = ConfigDict(from_attributes=True)

  id: int
  run_code: str
  project_id: int
  created_by_operator_id: int | None
  approved_by_operator_id: int | None
  executed_by_operator_id: int | None
  cancelled_by_operator_id: int | None
  suite_name: str
  browser: str
  environment: str
  status: TestRunStatus
  total_tests: int
  passed_tests: int
  failed_tests: int
  skipped_tests: int
  duration_seconds: float
  report_path: str | None
  approved_at: datetime | None
  started_at: datetime | None
  completed_at: datetime | None
  exit_code: int | None
  error_summary: str | None
  result_json_path: str | None
  html_report_path: str | None
  stdout_log_path: str | None
  stderr_log_path: str | None
  created_at: datetime


class TestRunDetail(TestRunRead):
  results: list[TestResultRead] = []
  evidence: list[EvidenceRead] = []


class ApprovalRequest(BaseModel):
  confirmation: str


class ExecuteRequest(BaseModel):
  confirm_local_execution: bool


class TestRunRequest(BaseModel):
  project_id: int
  suite_name: str = Field(min_length=1, max_length=160)
  browser: str = 'chromium'
  environment: str = 'local'

  @field_validator('suite_name')
  @classmethod
  def strip_suite_name(cls, value: str) -> str:
    if not value.strip():
      raise ValueError('must not be blank')
    return value.strip()

  @field_validator('browser')
  @classmethod
  def chromium_only(cls, value: str) -> str:
    if value.lower() != 'chromium':
      raise ValueError('Only chromium is supported in Stage 3.')
    return 'chromium'
