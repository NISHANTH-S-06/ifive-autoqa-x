"""Pytest Test Suite for Phase 20 Self-Evolving Autonomous QA Ecosystem (Version 3.0)."""
import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI

from app.v2.evolution import EvolutionEngine, EvolutionManager
from app.v2.improvement import ImprovementEngine
from app.v2.workflows import AdaptiveWorkflowEngine
from app.v2.knowledge import KnowledgeEvolutionManager
from app.v2.governance import GovernanceEngine
from app.v2.experiments import ExperimentEngine
from app.v2.orchestration import EnterpriseLifecycleCoordinator
from app.v2.api.v2_router import router as v2_router


@pytest.mark.anyio
async def test_self_evolution_engine():
    engine = EvolutionEngine()
    res = engine.run_evolution_cycle()
    assert res["status"] == "SUCCESS"
    assert res["cycle"]["cycle_number"] >= 1
    assert res["applied_candidate"]["status"] == "APPLIED"


@pytest.mark.anyio
async def test_autonomous_improvement_engine():
    engine = ImprovementEngine()
    res = engine.run_improvement_cycle()
    assert res["status"] == "SUCCESS"
    assert len(res["validated_improvements"]) >= 3


@pytest.mark.anyio
async def test_adaptive_workflow_engine():
    engine = AdaptiveWorkflowEngine()
    route = engine.adapt_workflow("wf-purchase", feedback_score=95.0)
    assert "OptimizedCacheLookup" in route.adapted_steps


@pytest.mark.anyio
async def test_knowledge_evolution_manager():
    mgr = KnowledgeEvolutionManager()
    res = mgr.evolve_all_knowledge()
    assert res["status"] == "EVOLVED"
    assert res["pattern_evolution"]["confidence_score"] >= 99.0


@pytest.mark.anyio
async def test_ai_governance_engine():
    engine = GovernanceEngine()
    res = engine.authorize_action("Deploy Autonomous Execution Candidate", risk_level="LOW")
    assert res["authorized"] is True
    assert res["approval_gate"]["status"] == "APPROVED"
    assert len(engine.audits) == 1


@pytest.mark.anyio
async def test_autonomous_experiment_engine():
    engine = ExperimentEngine()
    res = engine.run_experiment("Pipeline Parallelism A/B")
    assert res["status"] == "COMPLETED"
    assert res["comparison"]["winner"] == "variant-b-optimized"


@pytest.mark.anyio
async def test_enterprise_intelligence_lifecycle_coordinator():
    coord = EnterpriseLifecycleCoordinator()
    res = await coord.execute_autonomous_lifecycle(project_id=1, task_description="Execute Sales Order ERP Workflow")
    assert res.overall_status == "SUCCESS"
    assert res.passed_stages_count == 14
    assert len(res.stage_traces) == 14


@pytest.mark.anyio
async def test_fastapi_v2_evolution_router_endpoints():
    app = FastAPI()
    app.include_router(v2_router)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        # Evolution status & history
        res = await client.get("/api/v2/evolution/status")
        assert res.status_code == 200
        assert res.json()["status"] == "ONLINE"

        res = await client.get("/api/v2/evolution/history")
        assert res.status_code == 200

        res = await client.post("/api/v2/evolution/run")
        assert res.status_code == 200
        assert res.json()["status"] == "SUCCESS"

        # Improvement
        res = await client.get("/api/v2/improvement")
        assert res.status_code == 200

        # Governance
        res = await client.get("/api/v2/governance")
        assert res.status_code == 200

        res = await client.post("/api/v2/governance/authorize?action=Deploy&risk_level=LOW")
        assert res.status_code == 200
        assert res.json()["authorized"] is True

        # Experiments
        res = await client.get("/api/v2/experiments")
        assert res.status_code == 200

        res = await client.post("/api/v2/experiments/run?name=Test")
        assert res.status_code == 200

        # Self-learning
        res = await client.get("/api/v2/self-learning")
        assert res.status_code == 200

        # Platform health
        res = await client.get("/api/v2/platform/health")
        assert res.status_code == 200
        assert res.json()["phase"] == "20"
