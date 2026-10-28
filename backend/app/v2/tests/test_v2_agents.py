"""Pytest Unit Test Suite for Phase 17.2 AI Agents, Orchestrator, Workflows & API."""
import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI

from app.v2.agents import (
    PlannerAgent,
    ExecutionAgent,
    ReviewAgent,
    HealingAgent,
    ReportingAgent,
    CoordinatorAgent,
    AgentContext,
    AgentRegistry,
)
from app.v2.workflows import WorkflowEngine, WorkflowDefinition, WorkflowStep, AgentOrchestrator
from app.v2.memory import AgentMemory, SessionMemory, WorkflowMemory, ExecutionMemory
from app.v2.api.v2_router import router as v2_router


@pytest.mark.anyio
async def test_all_six_core_agents():
    ctx = AgentContext(run_id="run-1", project_id=1, parameters={"task_description": "Create Purchase Order"})

    # 1. PlannerAgent
    planner = PlannerAgent()
    await planner.initialize({})
    plan_res = await planner.execute_task(ctx)
    assert plan_res.status == "SUCCESS"
    plan = plan_res.output["execution_plan"]
    assert len(plan["subtasks"]) == 4

    # 2. ExecutionAgent
    executor = ExecutionAgent()
    await executor.initialize({})
    exec_ctx = AgentContext(run_id="run-1", project_id=1, parameters={"execution_plan": plan})
    exec_res = await executor.execute_task(exec_ctx)
    assert exec_res.status == "SUCCESS"
    executed_steps = exec_res.output["executed_steps"]

    # 3. ReviewAgent
    reviewer = ReviewAgent()
    await reviewer.initialize({})
    rev_ctx = AgentContext(run_id="run-1", project_id=1, parameters={"executed_steps": executed_steps})
    rev_res = await reviewer.execute_task(rev_ctx)
    assert rev_res.status == "SUCCESS"
    assert rev_res.output["review_summary"]["review_verdict"] == "PASSED"

    # 4. HealingAgent
    healer = HealingAgent()
    await healer.initialize({})
    heal_ctx = AgentContext(run_id="run-1", project_id=1, parameters={"failed_step": {"name": "Fill Form"}})
    heal_res = await healer.execute_task(heal_ctx)
    assert heal_res.status == "SUCCESS"
    assert heal_res.output["suggestion_count"] == 1

    # 5. ReportingAgent
    reporter = ReportingAgent()
    await reporter.initialize({})
    rep_ctx = AgentContext(run_id="run-1", project_id=1, parameters={"execution_plan": plan, "review_summary": rev_res.output["review_summary"]})
    rep_res = await reporter.execute_task(rep_ctx)
    assert rep_res.status == "SUCCESS"
    assert "report" in rep_res.output

    # 6. CoordinatorAgent
    coord = CoordinatorAgent()
    await coord.initialize({})
    coord_res = await coord.execute_task(ctx)
    assert coord_res.status == "SUCCESS"


@pytest.mark.anyio
async def test_agent_memory_systems():
    mem = AgentMemory("planner")
    mem.set("plan_cache", {"steps": 4})
    assert mem.get("plan_cache")["steps"] == 4

    sess_mem = SessionMemory("sess-1")
    sess_mem.set("user", "admin")
    assert sess_mem.get("user") == "admin"

    wf_mem = WorkflowMemory("wf-1")
    wf_mem.record_step("st-1", {"status": "PASSED"})
    assert len(wf_mem.get_step_results()) == 1

    exec_mem = ExecutionMemory()
    exec_mem.record_run("run-1", {"verdict": "PASSED"})
    assert exec_mem.get_run("run-1")["verdict"] == "PASSED"


@pytest.mark.anyio
async def test_orchestrator_and_workflow_engine():
    orchestrator = AgentOrchestrator()
    assert len(orchestrator.list_agents()) >= 6

    res = await orchestrator.execute_full_qa_pipeline(project_id=1, task_description="Verify Sales Order Workflow")
    assert res["status"] == "SUCCESS"
    assert "step-1" in res["step_results"]
    assert "step-4" in res["step_results"]


@pytest.mark.anyio
async def test_fastapi_v2_router_endpoints():
    app = FastAPI()
    app.include_router(v2_router)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        # Health endpoint
        res = await client.get("/api/v2/health")
        assert res.status_code == 200
        assert res.json()["status"] == "ok"

        # Agents endpoint
        res = await client.get("/api/v2/agents")
        assert res.status_code == 200
        assert res.json()["total_agents"] >= 6

        # Orchestrator status
        res = await client.get("/api/v2/orchestrator/status")
        assert res.status_code == 200
        assert res.json()["orchestrator_ready"] is True

        # Orchestrator execute
        res = await client.post("/api/v2/orchestrator/execute", json={"project_id": 1, "task_description": "Test Flow"})
        assert res.status_code == 200
        assert res.json()["execution_result"]["status"] == "SUCCESS"

        # Reports endpoint
        res = await client.get("/api/v2/reports")
        assert res.status_code == 200
        assert len(res.json()["reports"]) >= 1
