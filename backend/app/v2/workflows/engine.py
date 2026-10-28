"""Workflow Engine and Agent Orchestrator for Version 2.0 (Enhanced for Phase 17.3 Workflow Intelligence)."""
import asyncio
import time
import uuid
from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from app.v2.agents import (
    BaseAgent,
    AgentContext,
    AgentResult,
    AgentRegistry,
    PlannerAgent,
    ExecutionAgent,
    ReviewAgent,
    HealingAgent,
    ReportingAgent,
    CoordinatorAgent,
)
from app.v2.decision import DecisionEngine, DecisionContext
from app.v2.events import EventBus, WorkflowStarted, WorkflowCompleted, TaskCreated, TaskCompleted


class WorkflowMode(str, Enum):
    SEQUENTIAL = "SEQUENTIAL"
    PARALLEL = "PARALLEL"
    CONDITIONAL = "CONDITIONAL"


class WorkflowStep(BaseModel):
    step_id: str
    name: str
    agent_id: str
    step_type: str = Field("AGENT", description="AGENT or DECISION")
    parameters: Dict[str, Any] = Field(default_factory=dict)
    depends_on: List[str] = Field(default_factory=list)
    fallback_step_id: Optional[str] = Field(None, description="Fallback step ID if primary fails")


class WorkflowDefinition(BaseModel):
    workflow_id: str = Field(default_factory=lambda: f"wf-{uuid.uuid4().hex[:8]}")
    name: str
    mode: WorkflowMode = WorkflowMode.SEQUENTIAL
    steps: List[WorkflowStep] = Field(default_factory=list)


class WorkflowEngine:
    def __init__(self, registry: AgentRegistry, event_bus: Optional[EventBus] = None):
        self.registry = registry
        self.event_bus = event_bus or EventBus()
        self.decision_engine = DecisionEngine()
        self._cancelled_workflows: set[str] = set()

    def cancel_workflow(self, workflow_id: str) -> None:
        self._cancelled_workflows.add(workflow_id)

    async def execute_workflow(
        self,
        definition: WorkflowDefinition,
        initial_context: AgentContext,
        max_retries: int = 2,
        timeout_sec: float = 30.0,
    ) -> Dict[str, Any]:
        workflow_id = definition.workflow_id
        start_time = time.time()
        
        await self.event_bus.publish(WorkflowStarted(payload={"workflow_id": workflow_id, "name": definition.name}))

        step_results: Dict[str, AgentResult] = {}
        accumulated_params = dict(initial_context.parameters)

        try:
            async with asyncio.timeout(timeout_sec):
                for step in definition.steps:
                    if workflow_id in self._cancelled_workflows:
                        return {
                            "workflow_id": workflow_id,
                            "status": "CANCELLED",
                            "step_results": step_results,
                            "error": "Workflow execution was cancelled",
                        }

                    # Intelligence check: Decision Node vs Standard Agent Step
                    if step.step_type == "DECISION":
                        dec_ctx = DecisionContext(
                            options=[{"id": "opt-1", "name": "Proceed"}, {"id": "opt-2", "name": "Fallback"}],
                            parameters=accumulated_params,
                        )
                        dec_res = self.decision_engine.evaluate_options(dec_ctx)
                        step_results[step.step_id] = AgentResult(
                            agent_id="decision_engine",
                            status="SUCCESS",
                            output={"decision_result": dec_res.model_dump()},
                        )
                        accumulated_params["decision_result"] = dec_res.model_dump()
                        continue

                    agent_cls = self.registry.get(step.agent_id)
                    if not agent_cls:
                        raise KeyError(f"Agent '{step.agent_id}' not found in registry")

                    agent: BaseAgent = agent_cls(agent_id=step.agent_id, name=step.name)
                    await agent.initialize({})

                    step_ctx = AgentContext(
                        run_id=initial_context.run_id,
                        project_id=initial_context.project_id,
                        task_id=initial_context.task_id,
                        parameters={**accumulated_params, **step.parameters},
                    )

                    # Retry loop with fallback execution path support
                    res: Optional[AgentResult] = None
                    for attempt in range(1 + max_retries):
                        res = await agent.execute_task(step_ctx)
                        if res.status == "SUCCESS":
                            break

                    step_results[step.step_id] = res or AgentResult(agent_id=step.agent_id, status="FAILED")
                    if res and res.status == "SUCCESS":
                        accumulated_params.update(res.output)
                    else:
                        # Fallback recovery route check
                        if step.fallback_step_id:
                            accumulated_params["fallback_triggered"] = True
                        else:
                            break

                    await agent.shutdown()

        except TimeoutError:
            return {
                "workflow_id": workflow_id,
                "status": "TIMEOUT",
                "step_results": step_results,
                "error": f"Workflow timed out after {timeout_sec}s",
            }

        elapsed = (time.time() - start_time) * 1000
        overall_status = "SUCCESS" if all(r.status == "SUCCESS" for r in step_results.values()) else "FAILED"

        await self.event_bus.publish(WorkflowCompleted(payload={"workflow_id": workflow_id, "status": overall_status}))

        return {
            "workflow_id": workflow_id,
            "status": overall_status,
            "duration_ms": elapsed,
            "step_results": {k: v.model_dump() for k, v in step_results.items()},
            "final_output": accumulated_params,
        }


class AgentOrchestrator:
    def __init__(self, event_bus: Optional[EventBus] = None):
        self.registry = AgentRegistry()
        self.event_bus = event_bus or EventBus()
        self.engine = WorkflowEngine(self.registry, self.event_bus)
        self._register_default_agents()

    def _register_default_agents(self) -> None:
        self.registry.register("planner", PlannerAgent)
        self.registry.register("executor", ExecutionAgent)
        self.registry.register("reviewer", ReviewAgent)
        self.registry.register("healer", HealingAgent)
        self.registry.register("reporter", ReportingAgent)
        self.registry.register("coordinator", CoordinatorAgent)

    def register_agent(self, agent_id: str, agent_cls: Any) -> None:
        self.registry.register(agent_id, agent_cls)

    def list_agents(self) -> List[str]:
        return self.registry.list_registered()

    async def execute_full_qa_pipeline(self, project_id: int, task_description: str) -> Dict[str, Any]:
        """Execute default autonomous QA pipeline (Planner -> Executor -> Reviewer -> Reporter)."""
        run_id = f"run-{uuid.uuid4().hex[:8]}"
        wf_def = WorkflowDefinition(
            name="Autonomous QA Pipeline",
            steps=[
                WorkflowStep(step_id="step-1", name="Task Planning", agent_id="planner"),
                WorkflowStep(step_id="step-2", name="Simulated Execution", agent_id="executor"),
                WorkflowStep(step_id="step-3", name="Execution Review", agent_id="reviewer"),
                WorkflowStep(step_id="step-4", name="Report Generation", agent_id="reporter"),
            ],
        )
        initial_ctx = AgentContext(
            run_id=run_id,
            project_id=project_id,
            parameters={"task_description": task_description},
        )
        return await self.engine.execute_workflow(wf_def, initial_ctx)
