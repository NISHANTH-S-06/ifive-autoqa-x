from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.test_management import Page


class AutomatedRunStatus(str, Enum):
  DRAFT = 'DRAFT'
  SUBMITTED = 'SUBMITTED'
  APPROVED = 'APPROVED'
  QUEUED = 'QUEUED'
  RUNNING = 'RUNNING'
  PASSED = 'PASSED'
  FAILED = 'FAILED'
  CANCELLED = 'CANCELLED'
  TIMED_OUT = 'TIMED_OUT'
  BLOCKED = 'BLOCKED'


class AutomationActionType(str, Enum):
  NAVIGATE = 'NAVIGATE'
  CLICK = 'CLICK'
  FILL = 'FILL'
  SELECT = 'SELECT'
  CHECK = 'CHECK'
  UNCHECK = 'UNCHECK'
  PRESS_KEY = 'PRESS_KEY'
  WAIT_FOR_ELEMENT = 'WAIT_FOR_ELEMENT'
  ASSERT_TEXT = 'ASSERT_TEXT'
  ASSERT_VISIBLE = 'ASSERT_VISIBLE'
  ASSERT_HIDDEN = 'ASSERT_HIDDEN'
  ASSERT_URL_PATH = 'ASSERT_URL_PATH'
  ASSERT_TITLE = 'ASSERT_TITLE'
  SCREENSHOT = 'SCREENSHOT'
  READ_TEXT = 'READ_TEXT'
  RELOAD = 'RELOAD'
  GO_BACK = 'GO_BACK'
  GO_FORWARD = 'GO_FORWARD'


class AutomatedRunCreate(BaseModel):
  name: str = Field(min_length=1, max_length=180)
  description: str | None = Field(default=None, max_length=2000)
  target_id: int
  case_ids: list[int] = Field(min_length=1, max_length=100)
  timeout_seconds: int = Field(default=60, ge=5, le=300)
  max_retries: int = Field(default=1, ge=0, le=2)
  runtime_secret_required: bool = False

  @field_validator('name')
  @classmethod
  def strip_name(cls, value: str) -> str:
    value = value.strip()
    if not value:
      raise ValueError('must not be blank')
    return value


class WorkerHeartbeat(BaseModel):
  worker_key: str = Field(min_length=3, max_length=120)


class AcceptanceReadinessRead(BaseModel):
  active_admin_count: int
  admin_prerequisite_met: bool
  real_target_authorized: bool
  real_target_status: str
  dns_pinning_status: str
  runtime_secret_status: str
  allowed_risk_levels: list[str]
  blocked_risk_levels: list[str]


class ExecutionPreflightRead(BaseModel):
  run_id: int
  status: str
  checks: dict[str, bool]
  risk_level: str
  dns_pinning_status: str
  runtime_secret_status: str
  safe_message: str | None = None


class AutomatedRunRead(BaseModel):
  model_config = ConfigDict(from_attributes=True)
  id: int
  project_id: int
  run_key: str
  name: str
  description: str | None
  target_id: int
  target_version: int
  target_origin: str
  status: str
  risk_level: str
  preflight_status: str
  dns_pinning_status: str
  runtime_secret_status: str
  created_by: int
  submitted_by: int | None
  approved_by: int | None
  queued_by: int | None
  cancelled_by: int | None
  worker_key: str | None
  timeout_seconds: int
  max_retries: int
  attempt_count: int
  total_steps: int
  completed_steps: int
  failed_steps: int
  failure_classification: str | None
  safe_error_message: str | None
  submitted_at: datetime | None
  approved_at: datetime | None
  queued_at: datetime | None
  started_at: datetime | None
  completed_at: datetime | None
  cancelled_at: datetime | None
  created_at: datetime
  updated_at: datetime
  progress: str | None = None


class AutomatedRunList(BaseModel):
  items: list[AutomatedRunRead]
  page: Page


class AutomatedRunCaseRead(BaseModel):
  model_config = ConfigDict(from_attributes=True)
  id: int
  run_id: int
  test_case_id: int | None = None
  test_case_version: int | None = None
  test_plan_id: int | None = None
  test_plan_version: int | None = None
  test_plan_version_id: int | None = None
  plan_hash: str | None = None
  source_revision: int | None = None
  case_snapshot_json: str
  sort_order: int
  status: str
  failure_classification: str | None = None
  safe_error_message: str | None = None
  started_at: datetime | None = None
  completed_at: datetime | None = None


class AutomatedStepResultRead(BaseModel):
  model_config = ConfigDict(from_attributes=True)
  id: int
  run_case_id: int
  step_number: int
  action_type: str
  selector: str | None
  value_redacted: str | None
  expected_redacted: str | None
  status: str
  failure_classification: str | None
  safe_error_message: str | None
  started_at: datetime | None
  completed_at: datetime | None
  duration_ms: int | None


class ExecutionJobRead(BaseModel):
  model_config = ConfigDict(from_attributes=True)
  id: int
  run_id: int
  status: str
  priority: int
  lease_owner: str | None
  lease_expires_at: datetime | None
  attempts: int
  created_at: datetime
  updated_at: datetime


class ExecutionWorkerRead(BaseModel):
  model_config = ConfigDict(from_attributes=True)
  id: int
  worker_key: str
  status: str
  max_concurrency: int
  current_run_id: int | None
  heartbeat_at: datetime
  created_at: datetime
  updated_at: datetime


class ExecutionEventRead(BaseModel):
  model_config = ConfigDict(from_attributes=True)
  id: int
  run_id: int
  event_type: str
  status: str
  safe_message: str | None
  metadata_json: str
  created_at: datetime


class ExecutionArtifactRead(BaseModel):
  model_config = ConfigDict(from_attributes=True)
  id: int
  run_id: int
  run_case_id: int | None
  step_result_id: int | None
  artifact_type: str
  original_filename: str
  mime_type: str
  size_bytes: int
  sha256: str
  safe: bool
  created_at: datetime
