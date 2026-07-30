from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class AIStepRecommendation(BaseModel):
    step_number: int
    action: str = Field(..., description="Action type like NAVIGATE, FILL, CLICK, ASSERT_VISIBLE, etc.")
    selector: Optional[str] = Field(None, description="UI Element selector")
    value: Optional[str] = Field(None, description="Value to type or select")
    path: Optional[str] = Field(None, description="URL path for navigation")
    risk_level: str = Field("SAFE_INTERACTION", description="Assessed risk level for this step")
    expected_result: str = Field("Step executed successfully")

class AIScenarioMock(BaseModel):
    scenario_type: str
    title: str
    description: str
    priority: str = "P1"
    risk: str = "MEDIUM"
    enabled: bool = True
    mandatory: bool = True
    steps: List[AIStepRecommendation] = []

class AIAnalysisResponse(BaseModel):
    plan_title: str = Field(..., description="Title of the test plan")
    task_type: str = Field(..., description="Type of task (e.g. FEATURE, BUGFIX)")
    module: str = Field(..., description="System module (e.g. ERP, HRMS)")
    risk_classification: str = Field(..., description="HIGH, MEDIUM, LOW, or SAFE")
    preconditions: str = Field(..., description="Required initial state")
    cleanup_policy: str = Field(..., description="Cleanup instructions")
    test_plan_strategy: str = Field(..., description="Brief explanation of the proposed automated testing strategy")
    scenarios: List[AIScenarioMock] = Field(default_factory=list, description="List of generated test scenarios")
    missing_information: List[str] = Field(default_factory=list, description="List of ambiguities or missing requirements in the task description")
    confidence_score: int = Field(..., description="0-100 integer score of how confident the AI is in the generated plan")
    template_type: str = Field("GENERATED_BY_AI", description="Type of template used")

    @property
    def recommended_steps(self) -> List[AIStepRecommendation]:
        steps = []
        for sc in self.scenarios:
            steps.extend(sc.steps)
        return steps

class AIContextJSON(BaseModel):
    page_title: str
    url: str
    navigation: List[Dict[str, Any]] = Field(default_factory=list)
    buttons: List[Dict[str, Any]] = Field(default_factory=list)
    links: List[Dict[str, Any]] = Field(default_factory=list)
    forms: List[Dict[str, Any]] = Field(default_factory=list)
    inputs: List[Dict[str, Any]] = Field(default_factory=list)
    tables: List[Dict[str, Any]] = Field(default_factory=list)
    console_errors: List[str] = Field(default_factory=list)
    network_requests: List[Dict[str, Any]] = Field(default_factory=list)
    api_calls: List[Dict[str, Any]] = Field(default_factory=list)
    dom: Dict[str, Any] = Field(default_factory=dict)
    storage: Dict[str, Any] = Field(default_factory=dict)
    cookies: List[Dict[str, Any]] = Field(default_factory=list)
    meta: Dict[str, Any] = Field(default_factory=dict)

class ValidationStep(BaseModel):
    step_number: int
    action: str
    validations: List[str]

class ValidationExecutionPlan(BaseModel):
    plan_title: str
    steps: List[ValidationStep]

class ExecutionFailure(BaseModel):
    step_number: int
    action: str
    selector: Optional[str] = None
    error_message: str
    current_dom: Dict[str, Any] = Field(default_factory=dict)
    original_context: Optional[Dict[str, Any]] = None

class DecisionResponse(BaseModel):
    decision: str = Field(..., description="CONTINUE, HEAL, or ABORT")
    reason: str
    confidence_score: int

class HealingResponse(BaseModel):
    original_selector: str
    healed_selector: Optional[str]
    strategy_used: str
    confidence_score: int
    success: bool
