"""FastAPI Version 12.0 REST API Router — Autonomous Digital Civilization Platform."""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.v12.civilization import (
    CivilizationEngine, GovernancePolicy, CivilizationEpoch, CivilizationStatus
)
from app.v12.society import (
    AgentSociety, AgentProfile, AICommunity, InterCommunityLink
)
from app.v12.economy import (
    DigitalEconomy, ResourceListing, TradeTransaction, ValueContribution
)
from app.v12.coordination import (
    PlanetCoordinator, CrisisIncident, ScheduledGlobalTask, PlanetaryTelemetry
)

router = APIRouter(
    prefix="/api/v12",
    tags=["Version 12.0 — Autonomous Digital Civilization Platform"],
)

# ---------------------------------------------------------------------------
# Platform Singletons
# ---------------------------------------------------------------------------
_civilization = CivilizationEngine()
_society = AgentSociety()
_economy = DigitalEconomy()
_planet = PlanetCoordinator()

# ---------------------------------------------------------------------------
# Request Models
# ---------------------------------------------------------------------------

class ProposePolicyRequest(BaseModel):
    title: str = Field("Universal Energy Sustainability Standard")
    category: str = Field("ECONOMY")
    description: str = Field("All nodes must prioritize renewable green grid compute windows.")

class CreateCommunityRequest(BaseModel):
    name: str = Field("Autonomous Quantum Research Guild")
    specialization: str = Field("QUANTUM_COMPUTING")

class RegisterAgentRequest(BaseModel):
    name: str = Field("Quantum AI")
    role: str = Field("RESEARCHER")
    community_id: str

class EstablishLinkRequest(BaseModel):
    source_community_id: str
    target_community_id: str
    collaboration_topic: str = Field("Quantum Encryption Benchmarks")

class CreateListingRequest(BaseModel):
    seller_org_id: str = Field("org-alpha")
    resource_type: str = Field("MODEL_INFERENCE_RIGHTS")
    quantity: float = Field(1000.0)
    price_per_unit: float = Field(2.5)

class TradeRequest(BaseModel):
    listing_id: str
    buyer_org_id: str = Field("org-beta")
    quantity: float = Field(100.0)

class ContributeValueRequest(BaseModel):
    org_id: str = Field("org-alpha")
    activity_type: str = Field("THREAT_MITIGATION")
    value_score: float = Field(99.0)

class TriggerIncidentRequest(BaseModel):
    category: str = Field("LATENCY_SPIKE")
    description: str = Field("Transatlantic fiber latency increase")
    severity: str = Field("MEDIUM")

class ScheduleTaskRequest(BaseModel):
    name: str = Field("Global Planetary Sync")
    target_region: str = Field("global-mesh")
    priority: int = Field(8)

# ---------------------------------------------------------------------------
# Platform & Health Endpoints
# ---------------------------------------------------------------------------

@router.get("/platform/status")
@router.get("/platform/health")
@router.get("/health")
async def get_v12_platform_status() -> Dict[str, Any]:
    return {
        "status": "ok",
        "system": "iFive AutoQA X — Autonomous Digital Civilization Platform",
        "version": "12.0",
        "phase": "30",
        "maturity": "AUTONOMOUS_DIGITAL_CIVILIZATION_PLATFORM",
        "codename": "PLANETARY_CIVILIZATION",
        "roadmap_status": "ROADMAP_COMPLETE",
    }

@router.get("/dashboard")
async def get_v12_dashboard() -> Dict[str, Any]:
    return {
        "platform": "iFive AutoQA X v12.0 — Autonomous Digital Civilization Platform",
        "civilization": _civilization.get_summary(),
        "society": _society.get_society_summary(),
        "economy": _economy.get_economic_summary(),
        "planet": _planet.get_summary(),
        "overall_health": "GREEN",
        "civilization_score": 100.0,
    }

# ---------------------------------------------------------------------------
# Digital Civilization Core Endpoints
# ---------------------------------------------------------------------------

@router.get("/civilization")
async def get_civilization_summary() -> Dict[str, Any]:
    return _civilization.get_summary()

@router.get("/civilization/status")
async def get_civilization_status() -> Dict[str, Any]:
    return _civilization.get_status().model_dump()

@router.get("/civilization/policies")
async def list_policies(category: Optional[str] = None) -> Dict[str, Any]:
    policies = _civilization.governance.list_policies(category=category)
    return {"status": "success", "policies": [p.model_dump() for p in policies], "count": len(policies)}

@router.post("/civilization/policies/propose")
async def propose_policy(req: ProposePolicyRequest) -> Dict[str, Any]:
    policy = _civilization.governance.propose_policy(req.title, req.category, req.description)
    return {"status": "success", "policy": policy.model_dump()}

@router.get("/civilization/audit")
async def audit_governance_compliance() -> Dict[str, Any]:
    return _civilization.governance.audit_compliance()

@router.get("/civilization/epoch")
async def get_current_epoch() -> Dict[str, Any]:
    return _civilization.manager.get_current_epoch().model_dump()

@router.post("/civilization/epoch/advance")
async def advance_epoch() -> Dict[str, Any]:
    new_epoch = _civilization.manager.advance_epoch()
    return {"status": "success", "new_epoch": new_epoch.model_dump()}

# ---------------------------------------------------------------------------
# Global AI Society Endpoints
# ---------------------------------------------------------------------------

@router.get("/society")
async def get_society_summary() -> Dict[str, Any]:
    return _society.get_society_summary()

@router.get("/society/communities")
async def list_communities() -> Dict[str, Any]:
    comms = _society.community_manager.list_communities()
    return {"status": "success", "communities": [c.model_dump() for c in comms], "count": len(comms)}

@router.post("/society/communities/create")
async def create_community(req: CreateCommunityRequest) -> Dict[str, Any]:
    comm = _society.community_manager.create_community(req.name, req.specialization)
    return {"status": "success", "community": comm.model_dump()}

@router.get("/society/agents")
async def list_agents(community_id: Optional[str] = None) -> Dict[str, Any]:
    agents = _society.community_manager.list_agents(community_id=community_id)
    return {"status": "success", "agents": [a.model_dump() for a in agents], "count": len(agents)}

@router.post("/society/agents/register")
async def register_agent(req: RegisterAgentRequest) -> Dict[str, Any]:
    agent = _society.community_manager.register_agent(req.name, req.role, req.community_id)
    return {"status": "success", "agent": agent.model_dump()}

@router.get("/society/links")
async def list_inter_community_links() -> Dict[str, Any]:
    links = _society.collaboration_network.list_links()
    return {"status": "success", "links": [l.model_dump() for l in links], "count": len(links)}

@router.post("/society/links/establish")
async def establish_link(req: EstablishLinkRequest) -> Dict[str, Any]:
    link = _society.collaboration_network.establish_link(
        req.source_community_id, req.target_community_id, req.collaboration_topic
    )
    return {"status": "success", "link": link.model_dump()}

# ---------------------------------------------------------------------------
# Autonomous Economy Endpoints
# ---------------------------------------------------------------------------

@router.get("/economy")
async def get_economic_summary() -> Dict[str, Any]:
    return _economy.get_economic_summary()

@router.get("/economy/listings")
async def list_listings(status: Optional[str] = None) -> Dict[str, Any]:
    listings = _economy.exchange.list_listings(status=status)
    return {"status": "success", "listings": [l.model_dump() for l in listings], "count": len(listings)}

@router.post("/economy/listings/create")
async def create_listing(req: CreateListingRequest) -> Dict[str, Any]:
    listing = _economy.exchange.create_listing(
        req.seller_org_id, req.resource_type, req.quantity, req.price_per_unit
    )
    return {"status": "success", "listing": listing.model_dump()}

@router.post("/economy/trade")
async def execute_trade(req: TradeRequest) -> Dict[str, Any]:
    try:
        tx = _economy.exchange.execute_trade(req.listing_id, req.buyer_org_id, req.quantity)
        return {"status": "success", "transaction": tx.model_dump()}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/economy/transactions")
async def get_trade_history() -> Dict[str, Any]:
    history = _economy.exchange.get_trade_history()
    return {"status": "success", "transactions": [t.model_dump() for t in history], "count": len(history)}

@router.post("/economy/contribute")
async def record_contribution(req: ContributeValueRequest) -> Dict[str, Any]:
    contrib = _economy.value_engine.record_contribution(req.org_id, req.activity_type, req.value_score)
    return {"status": "success", "contribution": contrib.model_dump()}

@router.get("/economy/value-stats")
async def get_value_stats() -> Dict[str, Any]:
    return _economy.value_engine.get_value_stats()

# ---------------------------------------------------------------------------
# Global Coordination Endpoints
# ---------------------------------------------------------------------------

@router.get("/coordination")
async def get_coordination_summary() -> Dict[str, Any]:
    return _planet.get_summary()

@router.get("/coordination/telemetry")
async def get_planetary_telemetry() -> Dict[str, Any]:
    return _planet.get_planetary_telemetry().model_dump()

@router.get("/coordination/incidents")
async def list_crisis_incidents() -> Dict[str, Any]:
    incidents = _planet.crisis_manager.list_incidents()
    return {"status": "success", "incidents": [i.model_dump() for i in incidents], "count": len(incidents)}

@router.post("/coordination/incidents/trigger")
async def trigger_crisis_incident(req: TriggerIncidentRequest) -> Dict[str, Any]:
    incident = _planet.crisis_manager.trigger_incident(req.category, req.description, req.severity)
    return {"status": "success", "incident": incident.model_dump()}

@router.get("/coordination/tasks")
async def list_scheduled_tasks() -> Dict[str, Any]:
    tasks = _planet.global_scheduler.list_tasks()
    return {"status": "success", "tasks": [t.model_dump() for t in tasks], "count": len(tasks)}

@router.post("/coordination/tasks/schedule")
async def schedule_global_task(req: ScheduleTaskRequest) -> Dict[str, Any]:
    task = _planet.global_scheduler.schedule_task(req.name, req.target_region, req.priority)
    return {"status": "success", "task": task.model_dump()}

@router.post("/coordination/tasks/execute")
async def execute_scheduled_tasks() -> Dict[str, Any]:
    res = _planet.global_scheduler.execute_scheduled_tasks()
    return {"status": "success", "result": res}
