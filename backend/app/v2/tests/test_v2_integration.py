"""Pytest Integration Test Suite for Phase 17.4 Enterprise Autonomous AI Platform Integration."""
import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI

from app.v2.runtime import RuntimeManager, RuntimeState
from app.v2.orchestration import AutonomousCoordinator, ExecutionPipeline
from app.v2.workflows.enterprise_engine import EnterpriseWorkflowEngine
from app.v2.plugins.runtime import PluginRuntime
from app.v2.knowledge.runtime import KnowledgeRuntime
from app.v2.metrics import MetricsCollector
from app.v2.events import EventBus, BaseEvent
from app.v2.api.v2_router import router as v2_router


@pytest.mark.anyio
async def test_agent_runtime_manager_lifecycle():
    manager = RuntimeManager()
    status_initial = manager.get_status()
    assert status_initial["state"] == "STOPPED"

    started = await manager.start_all()
    assert started is True
    assert manager.context.state == RuntimeState.RUNNING

    manager.pause_all()
    assert manager.context.state == RuntimeState.PAUSED

    manager.resume_all()
    assert manager.context.state == RuntimeState.RUNNING

    stopped = await manager.stop_all()
    assert stopped is True
    assert manager.context.state == RuntimeState.STOPPED


@pytest.mark.anyio
async def test_autonomous_execution_pipeline_11_stages():
    coordinator = AutonomousCoordinator()
    res = await coordinator.execute_autonomous_pipeline(project_id=1, task_description="Verify Sales Order Workflow")
    assert res.overall_status == "SUCCESS"
    assert len(res.stages) == 11
    assert "decision_trace" in res.traces


@pytest.mark.anyio
async def test_enterprise_workflow_engine_collaboration_chain():
    engine = EnterpriseWorkflowEngine()
    res = await engine.execute_enterprise_collaboration_chain(project_id=1, task_description="Create Purchase Order Flow")
    assert res["status"] == "SUCCESS"
    assert res["collaboration_chain_complete"] is True
    assert res["checkpoints_count"] >= 1


@pytest.mark.anyio
async def test_plugin_runtime_auto_registration():
    runtime = PluginRuntime()
    plugins = runtime.list_plugins()
    assert len(plugins) == 9
    systems = [p["system"] for p in plugins]
    assert "Jira" in systems
    assert "GitHub" in systems
    assert "SAP" in systems
    assert "Salesforce" in systems


@pytest.mark.anyio
async def test_knowledge_runtime_unified_interface():
    runtime = KnowledgeRuntime()
    res = runtime.query_unified_knowledge("Authenticate User and Create Sales Order")
    assert res["status"] == "success"
    assert res["matched_pattern"]["matched"] is True


@pytest.mark.anyio
async def test_enterprise_metrics_collector():
    collector = MetricsCollector()
    metrics = collector.collect_all_metrics()
    assert "platform_uptime_seconds" in metrics
    assert len(metrics["dimensions"]) == 10


@pytest.mark.anyio
async def test_enterprise_event_bus_publishing():
    bus = EventBus()
    event = await bus.publish_platform_event("DecisionEngine", "DECISION_MADE", {"decision_id": "dec-101"})
    assert event.payload["source_engine"] == "DecisionEngine"
    assert len(bus.store.get_all()) >= 1


@pytest.mark.anyio
async def test_fastapi_v2_platform_dashboard_router():
    app = FastAPI()
    app.include_router(v2_router)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        # Runtime endpoints
        res = await client.get("/api/v2/runtime/status")
        assert res.status_code == 200

        res = await client.post("/api/v2/runtime/start")
        assert res.status_code == 200

        res = await client.get("/api/v2/runtime/metrics")
        assert res.status_code == 200
        assert "dimensions" in res.json()

        # Platform endpoints
        res = await client.get("/api/v2/platform/status")
        assert res.status_code == 200
        assert res.json()["platform_status"] == "ONLINE"

        res = await client.get("/api/v2/platform/health")
        assert res.status_code == 200
        assert res.json()["status"] == "HEALTHY"

        res = await client.get("/api/v2/platform/agents")
        assert res.status_code == 200

        res = await client.get("/api/v2/platform/workflows")
        assert res.status_code == 200
        assert len(res.json()["workflows"]) >= 3
