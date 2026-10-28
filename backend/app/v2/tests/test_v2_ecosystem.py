"""Pytest Test Suite for Phase 18 Enterprise Multi-Agent Ecosystem & Plugin Intelligence."""
import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI

from app.v2.ecosystem import AgentDirectory, AgentDiscoveryService, TaskDelegator, CollaborationEngine
from app.v2.communication import MessageBus, AgentMessage, MessageType
from app.v2.plugins import PluginMarketplace
from app.v2.integrations import IntegrationHub
from app.v2.knowledge import KnowledgeExchange
from app.v2.orchestration import AutonomousTeamCoordinator
from app.v2.api.v2_router import router as v2_router


@pytest.mark.anyio
async def test_multi_agent_registry_and_discovery():
    discovery = AgentDiscoveryService()
    agents = discovery.discover_by_capability("EXECUTION")
    assert len(agents) >= 1
    assert agents[0].agent_id == "executor"


@pytest.mark.anyio
async def test_message_bus_routing_and_pubsub():
    bus = MessageBus()
    received = []

    async def listener(msg: AgentMessage):
        received.append(msg)

    bus.subscribe("executor", listener)
    msg = await bus.send_direct("coordinator", "executor", {"action": "RUN"})
    assert len(received) == 1
    assert received[0].message_id == msg.message_id


@pytest.mark.anyio
async def test_task_delegation_engine():
    delegator = TaskDelegator()
    asgn = delegator.delegate_task("task-501", "PLANNING")
    assert asgn is not None
    assert asgn.assigned_agent_id == "planner"


@pytest.mark.anyio
async def test_collaboration_engine_planning():
    collab = CollaborationEngine()
    res = collab.run_collaborative_planning("Integrate SAP Purchase Order")
    assert res["status"] == "SUCCESS"
    assert len(res["team_assembled"]) >= 5


@pytest.mark.anyio
async def test_plugin_marketplace_install():
    marketplace = PluginMarketplace()
    res = marketplace.install("jira")
    assert res["status"] == "SUCCESS"


@pytest.mark.anyio
async def test_integration_hub_connectors_and_webhooks():
    hub = IntegrationHub()
    wh = hub.webhook_mgr.process_webhook("GitHub", "push", {"ref": "refs/heads/main"})
    assert wh.source_system == "GitHub"
    assert len(hub.webhook_mgr.list_webhooks()) == 1


@pytest.mark.anyio
async def test_knowledge_exchange_sharing():
    exchange = KnowledgeExchange()
    art = exchange.share_knowledge("planner", "PATTERN", {"pattern": "PO -> Invoice"})
    assert art.category == "PATTERN"
    queried = exchange.query_knowledge("PATTERN")
    assert len(queried) == 1


@pytest.mark.anyio
async def test_autonomous_team_pipeline_execution():
    team = AutonomousTeamCoordinator()
    res = await team.execute_team_pipeline(1, "Create Sales Order Flow")
    assert res.overall_status == "SUCCESS"
    assert res.messages_routed_count == 10
    assert len(res.stage_trace) == 10


@pytest.mark.anyio
async def test_fastapi_v2_ecosystem_router_endpoints():
    app = FastAPI()
    app.include_router(v2_router)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        # Ecosystem health & status
        res = await client.get("/api/v2/ecosystem/health")
        assert res.status_code == 200
        assert res.json()["status"] == "ONLINE"

        # Ecosystem agents
        res = await client.get("/api/v2/ecosystem/agents")
        assert res.status_code == 200
        assert len(res.json()["agents"]) >= 10

        # Discovery endpoint
        res = await client.get("/api/v2/ecosystem/discovery?capability=EXECUTION")
        assert res.status_code == 200
        assert len(res.json()["matched_agents"]) >= 1

        # Tasks delegation
        res = await client.post("/api/v2/ecosystem/tasks", json={"task_id": "task-99", "required_capability": "PLANNING"})
        assert res.status_code == 200
        assert res.json()["status"] == "success"

        # Collaboration
        res = await client.get("/api/v2/ecosystem/collaboration")
        assert res.status_code == 200
        assert res.json()["status"] == "SUCCESS"

        # Plugins catalog
        res = await client.get("/api/v2/plugins/catalog")
        assert res.status_code == 200
        assert len(res.json()["catalog"]) >= 10

        # Plugin install
        res = await client.post("/api/v2/plugins/install", json={"plugin_id": "jira"})
        assert res.status_code == 200

        # Integrations hub
        res = await client.get("/api/v2/integrations")
        assert res.status_code == 200
        assert res.json()["status"] == "ONLINE"

        # Integration sync
        res = await client.post("/api/v2/integrations/sync?system=Jira")
        assert res.status_code == 200
        assert res.json()["status"] == "SYNCED"
