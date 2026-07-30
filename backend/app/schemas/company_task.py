from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


# ── Enums ────────────────────────────────────────────────────────────────────

class TaskStatus(str, Enum):
  # Full Phase 2 pipeline
  NEW = 'NEW'
  ASSIGNED = 'ASSIGNED'
  IN_PROGRESS = 'IN_PROGRESS'
  DEVELOPER_COMPLETED = 'DEVELOPER_COMPLETED'
  TESTING_L2 = 'TESTING_L2'
  TEST_APPROVED = 'TEST_APPROVED'
  AUTOQA_RUNNING = 'AUTOQA_RUNNING'
  PASSED = 'PASSED'
  FAILED = 'FAILED'
  BACK_TO_DEVELOPER = 'BACK_TO_DEVELOPER'
  DELIVERY_COMPLETED = 'DELIVERY_COMPLETED'
  CLOSED = 'CLOSED'


class TaskPriority(str, Enum):
  LOW = 'LOW'
  MEDIUM = 'MEDIUM'
  HIGH = 'HIGH'
  CRITICAL = 'CRITICAL'


class TaskSeverity(str, Enum):
  LOW = 'LOW'
  MEDIUM = 'MEDIUM'
  HIGH = 'HIGH'
  CRITICAL = 'CRITICAL'


class TaskBrowser(str, Enum):
  CHROMIUM = 'CHROMIUM'
  FIREFOX = 'FIREFOX'
  WEBKIT = 'WEBKIT'


# ── Request bodies ────────────────────────────────────────────────────────────

class CompanyTaskCreate(BaseModel):
  title: str = Field(min_length=1, max_length=250)
  module: str | None = Field(default=None, max_length=100)
  feature: str | None = Field(default=None, max_length=150)
  description: str | None = None
  # AutoQA inputs
  target_url: str | None = Field(default=None, max_length=1000)
  expected_flow: str | None = None
  acceptance_criteria: str | None = None
  expected_result: str | None = None
  api_endpoint: str | None = Field(default=None, max_length=500)
  # Testing context
  browser: TaskBrowser = TaskBrowser.CHROMIUM
  environment: str = Field(default='local', max_length=50)
  reference_screenshot_url: str | None = Field(default=None, max_length=1000)
  # Priority / scheduling
  priority: TaskPriority = TaskPriority.MEDIUM
  severity: TaskSeverity = TaskSeverity.MEDIUM
  estimated_hours: float | None = Field(default=None, ge=0.5, le=200)
  target_date: datetime | None = None
  # Assignments
  project_id: int | None = None
  assigned_developer_id: int | None = None
  assigned_tester_id: int | None = None


class CompanyTaskUpdate(BaseModel):
  title: str | None = Field(default=None, min_length=1, max_length=250)
  module: str | None = Field(default=None, max_length=100)
  feature: str | None = Field(default=None, max_length=150)
  description: str | None = None
  target_url: str | None = Field(default=None, max_length=1000)
  expected_flow: str | None = None
  acceptance_criteria: str | None = None
  expected_result: str | None = None
  api_endpoint: str | None = Field(default=None, max_length=500)
  browser: TaskBrowser | None = None
  environment: str | None = Field(default=None, max_length=50)
  reference_screenshot_url: str | None = Field(default=None, max_length=1000)
  priority: TaskPriority | None = None
  severity: TaskSeverity | None = None
  estimated_hours: float | None = Field(default=None, ge=0.5, le=200)
  target_date: datetime | None = None
  project_id: int | None = None


class TaskAssignRequest(BaseModel):
  developer_id: int


class TaskAssignTesterRequest(BaseModel):
  tester_id: int


class TaskStatusTransition(BaseModel):
  status: TaskStatus
  notes: str | None = Field(default=None, max_length=2000)


class AutoQAPreviewStep(BaseModel):
  step_number: int
  action_type: str
  target: str
  risk_level: str
  expected_result: str


class ApproveAutoQARequest(BaseModel):
  steps: list[AutoQAPreviewStep] | None = None


# ── Response schemas ──────────────────────────────────────────────────────────

class OperatorSummary(BaseModel):
  model_config = ConfigDict(from_attributes=True)
  id: int
  username: str
  display_name: str
  role: str


class CompanyTaskRead(BaseModel):
  model_config = ConfigDict(from_attributes=True)
  id: int
  project_id: int | None
  # Core fields
  title: str
  module: str | None
  feature: str | None
  description: str | None
  # AutoQA inputs
  target_url: str | None
  expected_flow: str | None
  acceptance_criteria: str | None
  expected_result: str | None
  api_endpoint: str | None
  # Testing context
  browser: str
  environment: str
  reference_screenshot_url: str | None
  # Priority
  priority: str
  severity: str
  estimated_hours: float | None
  target_date: datetime | None
  # Status
  status: str
  retest_count: int
  # People
  assigned_developer_id: int | None
  assigned_developer: OperatorSummary | None
  assigned_tester_id: int | None
  assigned_tester: OperatorSummary | None
  created_by: int
  creator: OperatorSummary | None
  approved_by_tester_id: int | None
  approver: OperatorSummary | None
  # AutoQA results
  autoqa_run_id: int | None
  autoqa_result: str | None
  autoqa_notes: str | None
  # Timestamps
  created_at: datetime
  updated_at: datetime
  assigned_at: datetime | None
  in_progress_at: datetime | None
  developer_completed_at: datetime | None
  testing_l2_at: datetime | None
  test_approved_at: datetime | None
  autoqa_started_at: datetime | None
  autoqa_completed_at: datetime | None
  back_to_developer_at: datetime | None
  delivery_completed_at: datetime | None
  closed_at: datetime | None


class CompanyTaskListRead(BaseModel):
  """Lightweight version for list / kanban views."""
  model_config = ConfigDict(from_attributes=True)
  id: int
  project_id: int | None
  title: str
  module: str | None
  feature: str | None
  priority: str
  severity: str
  status: str
  browser: str
  environment: str
  retest_count: int
  assigned_developer: OperatorSummary | None
  assigned_tester: OperatorSummary | None
  creator: OperatorSummary | None
  target_date: datetime | None
  created_at: datetime
  updated_at: datetime
  autoqa_result: str | None
  autoqa_run_id: int | None


class AutoQARunStatusRead(BaseModel):
  """Live execution status for polling from frontend."""
  task_id: int
  task_status: str
  autoqa_run_id: int | None
  run_status: str | None           # AutomatedRun.status
  progress: str | None             # e.g. "5/12"
  completed_steps: int
  failed_steps: int
  total_steps: int
  autoqa_result: str | None
  autoqa_notes: str | None
  artifact_count: int
