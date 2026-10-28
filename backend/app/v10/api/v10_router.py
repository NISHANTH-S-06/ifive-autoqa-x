"""FastAPI Version 10.0 REST API Router — Artificial General Enterprise Intelligence (AGEI)."""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.v10.agei_core import (
    UnifiedIntelligenceEngine, EnterpriseMemory, GoalManager, AdvancedReasoning,
    REASONING_MODES,
)
from app.v10.strategic import (
    StrategicIntelligenceHub, StrategicPlanner, LongTermDecisionMaker, MultiDomainReasoner,
)
from app.v10.learning import EnterpriseLearningHub
from app.v10.coordination import AutonomousCoordinationHub

router = APIRouter(
    prefix="/api/v10",
    tags=["Version 10.0 — Artificial General Enterprise Intelligence (AGEI)"],
)

# ---------------------------------------------------------------------------
# Platform singletons
# ---------------------------------------------------------------------------
_agei = UnifiedIntelligenceEngine()
_strategic_hub = StrategicIntelligenceHub()
_learning_hub = EnterpriseLearningHub()
_coordination_hub = AutonomousCoordinationHub()


# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------

class ThinkRequest(BaseModel):
    prompt: str = Field("Optimise global enterprise performance")
    reasoning_mode: str = Field("Deductive")
    store_result: bool = Field(True)


class MemoryStoreRequest(BaseModel):
    domain: str = Field("ENTERPRISE")
    context: str = Field("general")
    content: str = Field("")
    importance: float = Field(0.85)
    tags: List[str] = Field(default_factory=list)


class MemoryRecallRequest(BaseModel):
    domain: Optional[str] = None
    tags: Optional[List[str]] = None
    top_k: int = Field(10)


class GoalCreateRequest(BaseModel):
    title: str = Field("New Enterprise Goal")
    domain: str = Field("ENTERPRISE")
    priority: int = Field(5)
    target_kpi: str = Field("")
    description: str = Field("")


class GoalProgressRequest(BaseModel):
    goal_id: str
    progress_pct: float = Field(0.0)


class ReasonRequest(BaseModel):
    premise: str = Field("Analyse enterprise performance")
    mode: str = Field("Deductive")


class MultiReasonRequest(BaseModel):
    premise: str = Field("Analyse enterprise performance")
    modes: List[str] = Field(default_factory=lambda: ["Deductive", "Inductive", "Causal"])


class StrategicPlanRequest(BaseModel):
    objective: str = Field("Platform modernisation")
    horizon_months: int = Field(12)
    domain: str = Field("PLATFORM")


class LongTermDecisionRequest(BaseModel):
    context: str = Field("Global expansion strategy")
    horizon_months: int = Field(24)
    domain: str = Field("STRATEGIC")


class MultiDomainRequest(BaseModel):
    premise: str = Field("Enterprise performance optimisation")
    domains: Optional[List[str]] = None


class LearningCycleRequest(BaseModel):
    domain: str = Field("ENTERPRISE")
    data_points: int = Field(10_000)


class KnowledgeEvolveRequest(BaseModel):
    trigger: str = Field("NEW_DOMAIN_DATA")
    evolution_type: str = Field("INCREMENTAL")
    new_triples: int = Field(150)


class PatternDiscoverRequest(BaseModel):
    domain: Optional[str] = None
    min_significance: float = Field(0.99)
    top_k: int = Field(10)


class DelegateTaskRequest(BaseModel):
    name: str = Field("AnalysisTask")
    required_capability: str = Field("ai_analysis")
    priority: int = Field(5)


class DelegateBatchRequest(BaseModel):
    tasks: List[Dict[str, Any]] = Field(
        default_factory=lambda: [{"name": "task-1", "capability": "ai_analysis"}]
    )


class OptimiseRequest(BaseModel):
    target: str = Field("execution_fabric")


# ---------------------------------------------------------------------------
# Platform / health endpoints
# ---------------------------------------------------------------------------

@router.get("/platform/status")
@router.get("/platform/health")
@router.get("/health")
async def get_v10_platform_status() -> Dict[str, Any]:
    return {
        "status": "ok",
        "system": "iFive AutoQA X — Artificial General Enterprise Intelligence (AGEI)",
        "version": "10.0",
        "phase": "28",
        "maturity": "ARTIFICIAL_GENERAL_ENTERPRISE_INTELLIGENCE",
        "codename": "UNIVERSAL_MIND",
    }


@router.get("/dashboard")
async def get_v10_dashboard() -> Dict[str, Any]:
    profile = _agei.get_intelligence_profile()
    return {
        "platform": "iFive AutoQA X v10.0 — AGEI",
        "intelligence_profile": profile.model_dump(),
        "strategic_hub": _strategic_hub.get_hub_summary(),
        "learning": _learning_hub.get_learning_summary(),
        "coordination": _coordination_hub.get_hub_summary(),
        "overall_health": "GREEN",
        "ai_maturity_score": 99.9,
        "platform_maturity_level": "ARTIFICIAL_GENERAL_ENTERPRISE_INTELLIGENCE",
    }


# ---------------------------------------------------------------------------
# AGEI Core endpoints
# ---------------------------------------------------------------------------

@router.get("/agei")
async def get_agei_summary() -> Dict[str, Any]:
    return _agei.get_platform_summary()


@router.post("/agei/think")
async def agei_think(req: ThinkRequest) -> Dict[str, Any]:
    result = _agei.think(req.prompt, reasoning_mode=req.reasoning_mode, store_result=req.store_result)
    return {"status": "success", "result": result}


@router.get("/agei/profile")
async def get_intelligence_profile() -> Dict[str, Any]:
    return _agei.get_intelligence_profile().model_dump()


# ---------------------------------------------------------------------------
# Memory endpoints
# ---------------------------------------------------------------------------

@router.get("/memory")
async def get_memory_stats() -> Dict[str, Any]:
    return _agei.memory.get_stats()


@router.post("/memory/store")
async def store_memory(req: MemoryStoreRequest) -> Dict[str, Any]:
    record = _agei.memory.store(
        domain=req.domain, context=req.context, content=req.content,
        importance=req.importance, tags=req.tags,
    )
    return {"status": "success", "record": record.model_dump()}


@router.post("/memory/recall")
async def recall_memory(req: MemoryRecallRequest) -> Dict[str, Any]:
    records = _agei.memory.recall(domain=req.domain, tags=req.tags, top_k=req.top_k)
    return {"status": "success", "records": [r.model_dump() for r in records], "count": len(records)}


@router.post("/memory/consolidate")
async def consolidate_memory() -> Dict[str, Any]:
    return _agei.memory.consolidate()


# ---------------------------------------------------------------------------
# Goal endpoints
# ---------------------------------------------------------------------------

@router.get("/goals")
async def list_goals(state: Optional[str] = None, domain: Optional[str] = None) -> Dict[str, Any]:
    goals = _agei.goal_manager.list_goals(state=state, domain=domain)
    return {"status": "success", "goals": [g.model_dump() for g in goals], "count": len(goals)}


@router.get("/goals/summary")
async def get_goals_summary() -> Dict[str, Any]:
    return _agei.goal_manager.get_summary()


@router.post("/goals/create")
async def create_goal(req: GoalCreateRequest) -> Dict[str, Any]:
    goal = _agei.goal_manager.create_goal(
        title=req.title, domain=req.domain, priority=req.priority,
        target_kpi=req.target_kpi, description=req.description,
    )
    return {"status": "success", "goal": goal.model_dump()}


@router.post("/goals/progress")
async def update_goal_progress(req: GoalProgressRequest) -> Dict[str, Any]:
    goal = _agei.goal_manager.update_progress(req.goal_id, req.progress_pct)
    if not goal:
        return {"status": "error", "detail": f"Goal {req.goal_id} not found"}
    return {"status": "success", "goal": goal.model_dump()}


# ---------------------------------------------------------------------------
# Reasoning endpoints
# ---------------------------------------------------------------------------

@router.get("/reasoning/capabilities")
async def get_reasoning_capabilities() -> Dict[str, Any]:
    return _agei.reasoning.get_capabilities()


@router.post("/reasoning/reason")
async def reason(req: ReasonRequest) -> Dict[str, Any]:
    trace = _agei.reasoning.reason(req.premise, mode=req.mode)
    return {"status": "success", "trace": trace.model_dump()}


@router.post("/reasoning/multi")
async def multi_reason(req: MultiReasonRequest) -> Dict[str, Any]:
    results = _agei.reasoning.multi_mode_reason(req.premise, modes=req.modes)
    return {"status": "success", "traces": {k: v.model_dump() for k, v in results.items()}}


# ---------------------------------------------------------------------------
# Strategic Intelligence endpoints
# ---------------------------------------------------------------------------

@router.get("/strategic")
async def get_strategic_summary() -> Dict[str, Any]:
    return _strategic_hub.get_hub_summary()


@router.post("/strategic/plan")
async def create_strategic_plan(req: StrategicPlanRequest) -> Dict[str, Any]:
    plan = _strategic_hub.planner.plan(
        objective=req.objective, horizon_months=req.horizon_months, domain=req.domain,
    )
    return {"status": "success", "plan": plan.model_dump()}


@router.get("/strategic/roadmap")
async def get_roadmap(horizon_months: int = 36) -> Dict[str, Any]:
    return _strategic_hub.planner.get_roadmap(horizon_months=horizon_months)


@router.post("/strategic/decide")
async def long_term_decide(req: LongTermDecisionRequest) -> Dict[str, Any]:
    decision = _strategic_hub.ltdm.decide(
        context=req.context, horizon_months=req.horizon_months, domain=req.domain,
    )
    return {"status": "success", "decision": decision.model_dump()}


@router.post("/strategic/scenarios")
async def compare_scenarios(req: LongTermDecisionRequest) -> Dict[str, Any]:
    return _strategic_hub.ltdm.compare_scenarios(context=req.context)


@router.post("/strategic/synthesise")
async def multi_domain_synthesise(req: MultiDomainRequest) -> Dict[str, Any]:
    alignment = _strategic_hub.mdr.synthesise(req.premise, domains=req.domains)
    return {"status": "success", "alignment": alignment.model_dump()}


@router.get("/strategic/domain-health")
async def get_domain_health() -> Dict[str, Any]:
    return _strategic_hub.mdr.get_domain_health()


# ---------------------------------------------------------------------------
# Learning endpoints
# ---------------------------------------------------------------------------

@router.get("/learning")
async def get_learning_summary() -> Dict[str, Any]:
    return _learning_hub.get_learning_summary()


@router.post("/learning/cycle")
async def run_learning_cycle(req: LearningCycleRequest) -> Dict[str, Any]:
    cycle = _learning_hub.continuous_learner.run_cycle(
        domain=req.domain, data_points=req.data_points,
    )
    return {"status": "success", "cycle": cycle.model_dump()}


@router.post("/learning/full-cycle")
async def run_full_learning_cycle() -> Dict[str, Any]:
    result = _learning_hub.run_full_learning_cycle()
    # Ensure top-level status is "success" (inner result contains status="COMPLETE")
    return {"status": "success", **{k: v for k, v in result.items() if k != "status"}}


@router.post("/learning/evolve")
async def evolve_knowledge(req: KnowledgeEvolveRequest) -> Dict[str, Any]:
    event = _learning_hub.knowledge_evolver.evolve(
        trigger=req.trigger, evolution_type=req.evolution_type, new_triples=req.new_triples,
    )
    return {"status": "success", "evolution": event.model_dump()}


@router.post("/learning/discover")
async def discover_patterns(req: PatternDiscoverRequest) -> Dict[str, Any]:
    patterns = _learning_hub.pattern_discoverer.discover(
        domain=req.domain, min_significance=req.min_significance, top_k=req.top_k,
    )
    return {"status": "success", "patterns": [p.model_dump() for p in patterns]}


@router.get("/learning/patterns")
async def get_pattern_stats() -> Dict[str, Any]:
    return _learning_hub.pattern_discoverer.get_pattern_stats()


# ---------------------------------------------------------------------------
# Coordination endpoints
# ---------------------------------------------------------------------------

@router.get("/coordination")
async def get_coordination_summary() -> Dict[str, Any]:
    return _coordination_hub.get_hub_summary()


@router.get("/coordination/modules")
async def list_modules(health: Optional[str] = None) -> Dict[str, Any]:
    modules = _coordination_hub.module_coordinator.list_modules(health=health)
    return {"status": "success", "modules": [m.model_dump() for m in modules]}


@router.get("/coordination/report")
async def get_coordination_report() -> Dict[str, Any]:
    return _coordination_hub.module_coordinator.get_coordination_report().model_dump()


@router.post("/coordination/delegate")
async def delegate_task(req: DelegateTaskRequest) -> Dict[str, Any]:
    task = _coordination_hub.task_delegator.delegate(
        task_name=req.name, required_capability=req.required_capability, priority=req.priority,
    )
    return {"status": "success", "task": task.model_dump()}


@router.post("/coordination/delegate-batch")
async def delegate_batch(req: DelegateBatchRequest) -> Dict[str, Any]:
    tasks = _coordination_hub.task_delegator.delegate_batch(req.tasks)
    return {"status": "success", "tasks": [t.model_dump() for t in tasks]}


@router.post("/coordination/optimise")
async def apply_optimisation(req: OptimiseRequest) -> Dict[str, Any]:
    action = _coordination_hub.self_optimiser.apply_optimisation(req.target)
    return {"status": "success", "action": action.model_dump()}


@router.post("/coordination/auto-optimise")
async def auto_optimise_all() -> Dict[str, Any]:
    actions = _coordination_hub.self_optimiser.auto_optimise_all()
    return {"status": "success", "actions_applied": len(actions), "actions": [a.model_dump() for a in actions]}


@router.post("/coordination/full-cycle")
async def coordination_full_cycle() -> Dict[str, Any]:
    return _coordination_hub.coordinate_full_cycle()
