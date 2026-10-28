"""Pytest Integration Test Suite — Phase 30 Autonomous Digital Civilization Platform v12.0."""
from __future__ import annotations

import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI

# Civilization
from app.v12.civilization import (
    CivilizationEngine, GlobalGovernance, CivilizationManager
)
# Society
from app.v12.society import (
    AgentSociety, CommunityManager, CollaborationNetwork
)
# Economy
from app.v12.economy import (
    DigitalEconomy, ResourceExchange, ValueEngine
)
# Coordination
from app.v12.coordination import (
    PlanetCoordinator, CrisisManager, GlobalScheduler
)
# API
from app.v12.api.v12_router import router as v12_router

# ===========================================================================
# Digital Civilization Core Tests
# ===========================================================================

@pytest.mark.anyio
async def test_global_governance():
    gov = GlobalGovernance()
    pol = gov.propose_policy("AI Ethics Standard", "ETHICS", "Guarantee fair allocation")
    assert pol.title == "AI Ethics Standard"
    assert pol.enforced is True
    assert len(gov.list_policies()) == 5
    audit = gov.audit_compliance()
    assert audit["audit_status"] == "FULL_COMPLIANCE"

@pytest.mark.anyio
async def test_civilization_manager():
    mgr = CivilizationManager()
    current = mgr.get_current_epoch()
    assert current.epoch_number == 1
    advanced = mgr.advance_epoch()
    assert advanced.epoch_number == 2
    assert advanced.total_ai_agents > current.total_ai_agents
    demographics = mgr.get_demographics()
    assert demographics["epoch_number"] == 2

@pytest.mark.anyio
async def test_civilization_engine():
    engine = CivilizationEngine()
    status = engine.get_status()
    assert status.status == "STABLE_CIVILIZATION"
    summary = engine.get_summary()
    assert summary["compliance_audit"]["compliance_rate_pct"] == 100.0

# ===========================================================================
# Global AI Society Tests
# ===========================================================================

@pytest.mark.anyio
async def test_community_manager():
    cm = CommunityManager()
    guild = cm.create_community("Quantum AI Guild", "QUANTUM")
    agent = cm.register_agent("Q-Agent 1", "RESEARCHER", guild.community_id)
    assert guild.member_count == 1
    assert agent.community_id == guild.community_id
    assert len(cm.list_communities()) == 5
    assert len(cm.list_agents(guild.community_id)) == 1

@pytest.mark.anyio
async def test_collaboration_network():
    cn = CollaborationNetwork()
    link = cn.establish_link("comm-1", "comm-2", "Cross-Guild Research")
    assert link.status == "ESTABLISHED"
    assert len(cn.list_links()) == 1
    topology = cn.get_network_topology()
    assert topology["total_inter_community_links"] == 1

@pytest.mark.anyio
async def test_agent_society():
    society = AgentSociety()
    summary = society.get_society_summary()
    assert summary["society_status"] == "FLOURISHING"
    assert summary["total_communities"] >= 4
    assert summary["registered_lead_agents"] >= 4

# ===========================================================================
# Autonomous Economy Tests
# ===========================================================================

@pytest.mark.anyio
async def test_resource_exchange():
    rx = ResourceExchange()
    listing = rx.create_listing("org-alpha", "COMPUTE_CREDITS", 1000.0, 1.0)
    assert listing.quantity == 1000.0
    tx = rx.execute_trade(listing.listing_id, "org-beta", 500.0)
    assert tx.total_credits == 500.0
    assert len(rx.get_trade_history()) == 1

@pytest.mark.anyio
async def test_value_engine():
    ve = ValueEngine()
    contrib = ve.record_contribution("org-alpha", "CODE_GENERATION", 95.0)
    assert contrib.reward_credits_issued == 950.0
    assert ve.get_org_rewards("org-alpha") == 950.0
    stats = ve.get_value_stats()
    assert stats["economic_stability"] == "OPTIMAL_EQUILIBRIUM"

@pytest.mark.anyio
async def test_digital_economy():
    econ = DigitalEconomy()
    summary = econ.get_economic_summary()
    assert summary["economy_status"] == "THRIVING"
    assert summary["market_listings"]["available"] >= 2

# ===========================================================================
# Global Coordination Tests
# ===========================================================================

@pytest.mark.anyio
async def test_crisis_manager():
    cm = CrisisManager()
    incident = cm.trigger_incident("LATENCY_SPIKE", "High fiber optic latency")
    assert incident.resolved is True
    assert len(cm.list_incidents()) == 1
    summary = cm.get_crisis_summary()
    assert summary["open_crises"] == 0

@pytest.mark.anyio
async def test_global_scheduler():
    gs = GlobalScheduler()
    task = gs.schedule_task("Global Health Check", target_region="us-east", priority=8)
    assert task.status == "SCHEDULED"
    res = gs.execute_scheduled_tasks()
    assert res["status"] == "SUCCESS"
    assert task.status == "COMPLETED"

@pytest.mark.anyio
async def test_planet_coordinator():
    planet = PlanetCoordinator()
    telemetry = planet.get_planetary_telemetry()
    assert telemetry.planetary_health == "OPTIMAL"
    summary = planet.get_summary()
    assert summary["coordinator_status"] == "PLANETARY_EQUILIBRIUM"

# ===========================================================================
# REST API — Full v12 Router Test
# ===========================================================================

@pytest.mark.anyio
async def test_v12_api_router_full():
    app = FastAPI()
    app.include_router(v12_router)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:

        # Platform status & health
        res = await client.get("/api/v12/platform/status")
        assert res.status_code == 200
        assert res.json()["version"] == "12.0"
        assert res.json()["roadmap_status"] == "ROADMAP_COMPLETE"

        res = await client.get("/api/v12/dashboard")
        assert res.status_code == 200
        assert res.json()["overall_health"] == "GREEN"

        # Civilization endpoints
        res = await client.get("/api/v12/civilization")
        assert res.status_code == 200

        res = await client.get("/api/v12/civilization/status")
        assert res.status_code == 200
        assert res.json()["status"] == "STABLE_CIVILIZATION"

        res = await client.get("/api/v12/civilization/policies")
        assert res.status_code == 200
        assert res.json()["count"] >= 4

        res = await client.post("/api/v12/civilization/policies/propose", json={
            "title": "Green Compute Policy", "category": "ECONOMY", "description": "Prioritize renewable grid energy"
        })
        assert res.status_code == 200
        assert res.json()["policy"]["title"] == "Green Compute Policy"

        res = await client.get("/api/v12/civilization/audit")
        assert res.status_code == 200
        assert res.json()["audit_status"] == "FULL_COMPLIANCE"

        res = await client.get("/api/v12/civilization/epoch")
        assert res.status_code == 200

        res = await client.post("/api/v12/civilization/epoch/advance")
        assert res.status_code == 200

        # Society endpoints
        res = await client.get("/api/v12/society")
        assert res.status_code == 200

        res = await client.get("/api/v12/society/communities")
        assert res.status_code == 200

        res = await client.post("/api/v12/society/communities/create", json={
            "name": "Robotics Guild", "specialization": "ROBOTICS"
        })
        assert res.status_code == 200
        cid = res.json()["community"]["community_id"]

        res = await client.get("/api/v12/society/agents")
        assert res.status_code == 200

        res = await client.post("/api/v12/society/agents/register", json={
            "name": "Robo-AI", "role": "OPERATOR", "community_id": cid
        })
        assert res.status_code == 200

        res = await client.get("/api/v12/society/links")
        assert res.status_code == 200

        res = await client.post("/api/v12/society/links/establish", json={
            "source_community_id": cid, "target_community_id": cid, "collaboration_topic": "Shared Telemetry"
        })
        assert res.status_code == 200

        # Economy endpoints
        res = await client.get("/api/v12/economy")
        assert res.status_code == 200

        res = await client.get("/api/v12/economy/listings")
        assert res.status_code == 200

        res = await client.post("/api/v12/economy/listings/create", json={
            "seller_org_id": "org-alpha", "resource_type": "COMPUTE_CREDITS", "quantity": 1000.0, "price_per_unit": 1.0
        })
        assert res.status_code == 200
        lid = res.json()["listing"]["listing_id"]

        res = await client.post("/api/v12/economy/trade", json={
            "listing_id": lid, "buyer_org_id": "org-beta", "quantity": 100.0
        })
        assert res.status_code == 200

        res = await client.get("/api/v12/economy/transactions")
        assert res.status_code == 200

        res = await client.post("/api/v12/economy/contribute", json={
            "org_id": "org-alpha", "activity_type": "CODE_GENERATION", "value_score": 95.0
        })
        assert res.status_code == 200

        res = await client.get("/api/v12/economy/value-stats")
        assert res.status_code == 200

        # Global Coordination endpoints
        res = await client.get("/api/v12/coordination")
        assert res.status_code == 200

        res = await client.get("/api/v12/coordination/telemetry")
        assert res.status_code == 200
        assert res.json()["planetary_health"] == "OPTIMAL"

        res = await client.get("/api/v12/coordination/incidents")
        assert res.status_code == 200

        res = await client.post("/api/v12/coordination/incidents/trigger", json={
            "category": "NETWORK_PARTITION", "description": "Simulated partition", "severity": "LOW"
        })
        assert res.status_code == 200

        res = await client.get("/api/v12/coordination/tasks")
        assert res.status_code == 200

        res = await client.post("/api/v12/coordination/tasks/schedule", json={
            "name": "Global Audit", "target_region": "global-mesh", "priority": 5
        })
        assert res.status_code == 200

        res = await client.post("/api/v12/coordination/tasks/execute")
        assert res.status_code == 200
