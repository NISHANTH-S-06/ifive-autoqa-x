"""Pytest Unit Test Suite for Phase 17.3 AI Reasoning, Decisions, Confidence & Policies."""
import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI

from app.v2.decision import DecisionEngine, DecisionContext, DecisionRule, DecisionPolicy
from app.v2.reasoning import ReasoningEngine, ReasoningRequest, ReasoningType
from app.v2.planner import TaskPlanner, TaskNode
from app.v2.agents import AgentVote, ConsensusManager
from app.v2.confidence import ConfidenceEngine
from app.v2.policies import PolicyEngine, PolicyRule, PolicyType
from app.v2.explanations import ExplanationEngine
from app.v2.workflows import WorkflowEngine, WorkflowDefinition, WorkflowStep, AgentOrchestrator
from app.v2.api.v2_router import router as v2_router


@pytest.mark.anyio
async def test_decision_engine_evaluation():
    engine = DecisionEngine()
    ctx = DecisionContext(
        options=[
            {"id": "opt-1", "name": "Option A", "review_verdict": "PASSED", "failure_count": 0, "is_complete": True},
            {"id": "opt-2", "name": "Option B", "review_verdict": "FAILED", "failure_count": 2, "is_complete": False},
        ],
        parameters={},
    )
    res = engine.evaluate_options(ctx)
    assert res.selected_option["id"] == "opt-1"
    assert res.confidence_score == 100.0
    assert len(res.rules_applied) >= 2


@pytest.mark.anyio
async def test_reasoning_engine_deductive_and_constraints():
    engine = ReasoningEngine()

    # Deductive
    req_ded = ReasoningRequest(
        reasoning_type=ReasoningType.DEDUCTIVE,
        premises=[{"name": "Step 1", "status": "PASSED"}, {"name": "Step 2", "status": "PASSED"}],
    )
    verdict_ded = engine.reason(req_ded)
    assert verdict_ded.confidence == 100.0
    assert verdict_ded.risk_level == "LOW"

    # Constraint
    req_con = ReasoningRequest(
        reasoning_type=ReasoningType.CONSTRAINT,
        context={"auth_valid": True, "db_connected": True},
        constraints=["auth_valid", "db_connected"],
    )
    verdict_con = engine.reason(req_con)
    assert verdict_con.risk_level == "LOW"


@pytest.mark.anyio
async def test_task_planner_and_dependency_resolver():
    planner = TaskPlanner()
    nodes = planner.split_work("Verify Sales Flow")
    assert len(nodes) == 4

    plan = planner.create_optimized_plan(nodes)
    assert len(plan.ordered_tasks) == 4
    assert plan.total_estimated_cost_ms > 0


@pytest.mark.anyio
async def test_consensus_manager_voting():
    mgr = ConsensusManager(threshold=0.50)
    votes = [
        AgentVote(agent_id="planner", option_id="opt-a", vote_weight=1.0),
        AgentVote(agent_id="executor", option_id="opt-a", vote_weight=1.0),
        AgentVote(agent_id="reviewer", option_id="opt-b", vote_weight=1.0),
    ]
    res = mgr.evaluate_consensus(votes)
    assert res.consensus_reached is True
    assert res.winning_option_id == "opt-a"


@pytest.mark.anyio
async def test_confidence_engine_scoring():
    engine = ConfidenceEngine()
    eval_res = engine.compute_execution_confidence([{"status": "PASSED"}, {"status": "PASSED"}])
    assert eval_res.overall_score == 100.0
    assert eval_res.confidence_level == "HIGH"


@pytest.mark.anyio
async def test_policy_engine_validation():
    engine = PolicyEngine()
    res_valid = engine.evaluate_context({"environment": "STAGING", "target_host": "127.0.0.1"})
    assert res_valid["is_compliant"] is True

    res_blocked = engine.evaluate_context({"environment": "STAGING", "target_host": "169.254.169.254"})
    assert res_blocked["is_compliant"] is False
    assert res_blocked["has_critical_violations"] is True


@pytest.mark.anyio
async def test_explanation_engine_trace_generation():
    engine = ExplanationEngine()
    trace = engine.explain_decision(
        decision_id="dec-1",
        selected_option={"id": "opt-1", "name": "Proceed"},
        confidence_score=90.0,
        ranked_options=[{"id": "opt-1", "name": "Proceed"}],
        rules_applied=["Rule 1"],
    )
    assert trace.confidence_score == 90.0
    assert "Proceed" in trace.why


@pytest.mark.anyio
async def test_workflow_intelligence_decision_nodes():
    orchestrator = AgentOrchestrator()
    wf_def = WorkflowDefinition(
        name="Dynamic Intelligence Workflow",
        steps=[
            WorkflowStep(step_id="step-dec", name="Evaluate Path", agent_id="planner", step_type="DECISION"),
            WorkflowStep(step_id="step-exec", name="Execute Plan", agent_id="executor"),
        ],
    )
    res = await orchestrator.engine.execute_workflow(
        wf_def,
        initial_context=pytest.importorskip("app.v2.agents").AgentContext(run_id="run-dec-1", project_id=1),
    )
    assert res["status"] == "SUCCESS"
    assert "step-dec" in res["step_results"]


@pytest.mark.anyio
async def test_fastapi_v2_reasoning_router_endpoints():
    app = FastAPI()
    app.include_router(v2_router)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        # Decision endpoint
        res = await client.post("/api/v2/decision", json={"options": [{"id": "opt-1", "review_verdict": "PASSED", "failure_count": 0, "is_complete": True}]})
        assert res.status_code == 200
        assert res.json()["decision"]["confidence_score"] == 100.0

        # Reasoning endpoint
        res = await client.post("/api/v2/reasoning", json={"reasoning_type": "DEDUCTIVE", "premises": [{"name": "P1", "status": "PASSED"}]})
        assert res.status_code == 200
        assert res.json()["reasoning_verdict"]["confidence"] == 100.0

        # Confidence endpoint
        res = await client.get("/api/v2/confidence")
        assert res.status_code == 200
        assert res.json()["confidence"]["overall_score"] == 100.0

        # Policies endpoint
        res = await client.get("/api/v2/policies")
        assert res.status_code == 200
        assert res.json()["policy_evaluation"]["is_compliant"] is True

        # Explanations endpoint
        res = await client.get("/api/v2/explanations")
        assert res.status_code == 200
        assert "decision_trace" in res.json()
