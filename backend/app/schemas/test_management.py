from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class RecordStatus(str, Enum):
  ACTIVE = 'ACTIVE'
  ARCHIVED = 'ARCHIVED'


class LifecycleState(str, Enum):
  DRAFT = 'DRAFT'
  IN_REVIEW = 'IN_REVIEW'
  APPROVED = 'APPROVED'
  REJECTED = 'REJECTED'
  ARCHIVED = 'ARCHIVED'


class TestType(str, Enum):
  FUNCTIONAL = 'FUNCTIONAL'
  REGRESSION = 'REGRESSION'
  SMOKE = 'SMOKE'
  SECURITY = 'SECURITY'
  INTEGRATION = 'INTEGRATION'


class Priority(str, Enum):
  LOW = 'LOW'
  MEDIUM = 'MEDIUM'
  HIGH = 'HIGH'
  CRITICAL = 'CRITICAL'


class ManualRunStatus(str, Enum):
  PLANNED = 'PLANNED'
  IN_PROGRESS = 'IN_PROGRESS'
  COMPLETED = 'COMPLETED'
  CANCELLED = 'CANCELLED'


class ManualResultStatus(str, Enum):
  NOT_RUN = 'NOT_RUN'
  IN_PROGRESS = 'IN_PROGRESS'
  PASSED = 'PASSED'
  FAILED = 'FAILED'
  BLOCKED = 'BLOCKED'
  SKIPPED = 'SKIPPED'


def _strip(value: str) -> str:
  value = value.strip()
  if not value:
    raise ValueError('must not be blank')
  if any(ord(ch) < 32 and ch not in '\r\n\t' for ch in value):
    raise ValueError('control characters are not allowed')
  return value


class Page(BaseModel):
  limit: int
  offset: int
  total: int


class TestProjectCreate(BaseModel):
  access_project_id: int | None = Field(default=None, gt=0)
  name: str = Field(min_length=1, max_length=160)
  code: str = Field(min_length=2, max_length=40)
  description: str | None = Field(default=None, max_length=2000)
  owner_operator_id: int | None = None

  @field_validator('name', 'code')
  @classmethod
  def strip_required(cls, value: str) -> str:
    return _strip(value)


class TestProjectUpdate(BaseModel):
  name: str | None = Field(default=None, min_length=1, max_length=160)
  description: str | None = Field(default=None, max_length=2000)
  owner_operator_id: int | None = None
  version: int | None = Field(default=None, ge=1)


class TestProjectRead(BaseModel):
  model_config = ConfigDict(from_attributes=True)
  id: int
  access_project_id: int
  name: str
  code: str
  description: str | None
  status: str
  owner_operator_id: int | None
  created_by: int
  created_at: datetime
  updated_at: datetime
  archived_at: datetime | None
  version: int


class TestProjectList(BaseModel):
  items: list[TestProjectRead]
  page: Page


class TestModuleCreate(BaseModel):
  project_id: int
  name: str = Field(min_length=1, max_length=160)
  code: str = Field(min_length=1, max_length=40)
  description: str | None = Field(default=None, max_length=2000)
  sort_order: int = 0

  @field_validator('name', 'code')
  @classmethod
  def strip_required(cls, value: str) -> str:
    return _strip(value)


class TestModuleUpdate(BaseModel):
  name: str | None = Field(default=None, min_length=1, max_length=160)
  description: str | None = Field(default=None, max_length=2000)
  sort_order: int | None = None


class TestModuleRead(BaseModel):
  model_config = ConfigDict(from_attributes=True)
  id: int
  project_id: int
  name: str
  code: str
  description: str | None
  sort_order: int
  status: str
  created_by: int
  created_at: datetime
  updated_at: datetime
  archived_at: datetime | None


class TestSuiteCreate(BaseModel):
  project_id: int
  module_id: int
  name: str = Field(min_length=1, max_length=160)
  code: str = Field(min_length=1, max_length=40)
  description: str | None = Field(default=None, max_length=2000)
  suite_type: str = Field(default='MANUAL', max_length=40)
  owner_operator_id: int | None = None

  @field_validator('name', 'code', 'suite_type')
  @classmethod
  def strip_required(cls, value: str) -> str:
    return _strip(value).upper() if value else value


class TestSuiteUpdate(BaseModel):
  name: str | None = Field(default=None, min_length=1, max_length=160)
  description: str | None = Field(default=None, max_length=2000)
  owner_operator_id: int | None = None


class TestSuiteRead(BaseModel):
  model_config = ConfigDict(from_attributes=True)
  id: int
  project_id: int
  module_id: int
  name: str
  code: str
  description: str | None
  suite_type: str
  status: str
  owner_operator_id: int | None
  created_by: int
  created_at: datetime
  updated_at: datetime
  archived_at: datetime | None


class TestCaseStepInput(BaseModel):
  step_number: int = Field(ge=1, le=500)
  action: str = Field(min_length=1, max_length=5000)
  expected_result: str = Field(min_length=1, max_length=5000)
  test_data: str | None = Field(default=None, max_length=5000)

  @field_validator('action', 'expected_result')
  @classmethod
  def strip_required(cls, value: str) -> str:
    return _strip(value)


class TestCaseCreate(BaseModel):
  project_id: int
  module_id: int
  suite_id: int
  case_key: str = Field(min_length=3, max_length=60)
  title: str = Field(min_length=1, max_length=220)
  objective: str | None = Field(default=None, max_length=5000)
  preconditions: str | None = Field(default=None, max_length=5000)
  test_type: TestType = TestType.FUNCTIONAL
  priority: Priority = Priority.MEDIUM
  severity: Priority = Priority.MEDIUM
  owner_operator_id: int | None = None
  tags: list[str] = Field(default_factory=list, max_length=20)
  steps: list[TestCaseStepInput] = Field(min_length=1, max_length=500)

  @field_validator('case_key', 'title')
  @classmethod
  def strip_required(cls, value: str) -> str:
    return _strip(value)


class TestCaseUpdate(BaseModel):
  title: str | None = Field(default=None, min_length=1, max_length=220)
  objective: str | None = Field(default=None, max_length=5000)
  preconditions: str | None = Field(default=None, max_length=5000)
  test_type: TestType | None = None
  priority: Priority | None = None
  severity: Priority | None = None
  owner_operator_id: int | None = None
  tags: list[str] | None = Field(default=None, max_length=20)
  steps: list[TestCaseStepInput] | None = Field(default=None, min_length=1, max_length=500)


class TestCaseStepRead(BaseModel):
  model_config = ConfigDict(from_attributes=True)
  id: int
  step_number: int
  action: str
  expected_result: str
  test_data: str | None


class TagRead(BaseModel):
  model_config = ConfigDict(from_attributes=True)
  id: int
  name: str
  normalized_name: str


class TestCaseRead(BaseModel):
  model_config = ConfigDict(from_attributes=True)
  id: int
  project_id: int
  module_id: int
  suite_id: int
  case_key: str
  title: str
  objective: str | None
  preconditions: str | None
  test_type: str
  priority: str
  severity: str
  status: str
  lifecycle_state: str
  owner_operator_id: int | None
  created_by: int
  reviewed_by: int | None
  approved_by: int | None
  created_at: datetime
  updated_at: datetime
  reviewed_at: datetime | None
  approved_at: datetime | None
  archived_at: datetime | None
  current_version: int
  steps: list[TestCaseStepRead] = []
  tags: list[str] = []


class TestCaseList(BaseModel):
  items: list[TestCaseRead]
  page: Page


class LifecycleReason(BaseModel):
  reason: str | None = Field(default=None, max_length=500)


class TestCaseVersionRead(BaseModel):
  model_config = ConfigDict(from_attributes=True)
  id: int
  test_case_id: int
  version_number: int
  snapshot_json: str
  change_summary: str | None
  created_by: int
  created_at: datetime
  source_state: str


class ManualRunCreate(BaseModel):
  project_id: int
  suite_id: int
  name: str = Field(min_length=1, max_length=180)
  description: str | None = Field(default=None, max_length=2000)
  assigned_to: int | None = None
  case_ids: list[int] = Field(default_factory=list, min_length=1, max_length=200)


class ManualRunRead(BaseModel):
  model_config = ConfigDict(from_attributes=True)
  id: int
  run_key: str
  project_id: int
  suite_id: int
  name: str
  description: str | None
  status: str
  created_by: int
  assigned_to: int | None
  started_at: datetime | None
  completed_at: datetime | None
  created_at: datetime
  updated_at: datetime
  progress: str | None = None


class ManualRunCaseRead(BaseModel):
  model_config = ConfigDict(from_attributes=True)
  id: int
  run_id: int
  test_case_id: int
  test_case_version: int
  status: str
  assigned_to: int | None
  started_at: datetime | None
  completed_at: datetime | None
  actual_result: str | None
  notes: str | None
  executed_by: int | None


class ManualRunCaseAdd(BaseModel):
  case_ids: list[int] = Field(min_length=1, max_length=200)
  assigned_to: int | None = None


class ManualRunCaseUpdate(BaseModel):
  status: ManualResultStatus
  actual_result: str | None = Field(default=None, max_length=5000)
  notes: str | None = Field(default=None, max_length=2000)


class ManualStepResultUpdate(BaseModel):
  status: ManualResultStatus
  actual_result: str | None = Field(default=None, max_length=5000)
  notes: str | None = Field(default=None, max_length=2000)


class ManualStepResultRead(BaseModel):
  model_config = ConfigDict(from_attributes=True)
  id: int
  run_case_id: int
  step_number: int
  status: str
  actual_result: str | None
  notes: str | None
  executed_at: datetime | None
  executed_by: int | None


class ManualEvidenceRead(BaseModel):
  model_config = ConfigDict(from_attributes=True)
  id: int
  run_case_id: int
  step_result_id: int | None
  evidence_type: str
  original_filename: str
  mime_type: str
  size_bytes: int
  sha256: str
  uploaded_by: int
  created_at: datetime
