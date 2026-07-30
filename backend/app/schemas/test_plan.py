from typing import Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
# ── Steps ────────────────────────────────────────────────────────────────

class TestStepBase(BaseModel):
    step_order: int
    action: str
    locator_json: Optional[str] = None
    input_value_reference: Optional[str] = None
    expected_value: Optional[str] = None
    timeout_ms: int = 10000
    continue_on_failure: bool = False
    metadata_json: Optional[str] = None

class TestStepCreate(TestStepBase):
    pass

class TestStepOut(TestStepBase):
    id: int
    scenario_id: int

    model_config = ConfigDict(from_attributes=True)

# ── Scenarios ────────────────────────────────────────────────────────────

class TestScenarioBase(BaseModel):
    scenario_type: str = Field(..., description="PRIMARY, NEGATIVE, REGRESSION, BOUNDARY")
    title: str
    description: Optional[str] = None
    priority: str = "P1"
    risk: str = "MEDIUM"
    enabled: bool = True
    mandatory: bool = True
    order_index: int = 0

class TestScenarioCreate(TestScenarioBase):
    steps: List[TestStepCreate] = []

class TestScenarioOut(TestScenarioBase):
    id: int
    test_plan_version_id: int
    steps: List[TestStepOut] = []

    model_config = ConfigDict(from_attributes=True)

# ── Versions ─────────────────────────────────────────────────────────────

class TestPlanVersionBase(BaseModel):
    version_number: int
    source_revision: int
    provider: Optional[str] = None
    model: Optional[str] = None
    prompt_version: Optional[str] = None
    schema_version: Optional[str] = None
    input_hash: Optional[str] = None
    output_hash: Optional[str] = None
    plan_hash: str

class TestPlanVersionOut(TestPlanVersionBase):
    id: int
    test_plan_id: int
    created_by: int
    created_at: datetime
    immutable_snapshot_json: str
    scenarios: List[TestScenarioOut] = []

    model_config = ConfigDict(from_attributes=True)

# ── Test Plan ────────────────────────────────────────────────────────────

class TestPlanBase(BaseModel):
    source_task_id: str
    source_revision: int
    analysis_id: Optional[str] = None
    title: str
    status: str = "DRAFT"
    execution_enabled: bool = False
    optional_regression_enabled: bool = False

class TestPlanCreate(TestPlanBase):
    external_task_import_id: int
    project_id: int
    plan_code: str

class TestPlanOut(TestPlanBase):
    id: int
    project_id: int
    external_task_import_id: int
    plan_code: str
    current_version: int
    approved_version_number: Optional[int] = None
    
    created_by: int
    submitted_by: Optional[int] = None
    approved_by: Optional[int] = None
    rejected_by: Optional[int] = None
    
    created_at: datetime
    updated_at: datetime
    submitted_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    rejected_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    
    versions: List[TestPlanVersionOut] = []

    model_config = ConfigDict(from_attributes=True)

class TestPlanUpdate(BaseModel):
    title: Optional[str] = None
    optional_regression_enabled: Optional[bool] = None
    scenarios: Optional[List[TestScenarioCreate]] = None

class TestPlanReject(BaseModel):
    reason: str
