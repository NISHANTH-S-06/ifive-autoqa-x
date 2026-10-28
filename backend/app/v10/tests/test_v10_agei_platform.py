"""Pytest Integration Test Suite — Phase 28 Artificial General Enterprise Intelligence (AGEI) v10.0."""
from __future__ import annotations

import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI

# AGEI Core
from app.v10.agei_core import (
    UnifiedIntelligenceEngine, EnterpriseMemory, GoalManager, AdvancedReasoning,
    REASONING_MODES, AGEI_VERSION,
)
# Strategic
from app.v10.strategic import (
    StrategicIntelligenceHub, StrategicPlanner, LongTermDecisionMaker, MultiDomainReasoner,
)
# Learning
from app.v10.learning import (
    EnterpriseLearningHub, ContinuousLearner, KnowledgeEvolver, PatternDiscoverer,
)
# Coordination
from app.v10.coordination import (
    AutonomousCoordinationHub, ModuleCoordinator, TaskDelegator, SelfOptimiser,
)
# API
from app.v10.api.v10_router import router as v10_router


# ===========================================================================
# AGEI Core — Enterprise Memory
# ===========================================================================

@pytest.mark.anyio
async def test_enterprise_memory_store_and_recall():
    memory = EnterpriseMemory()
    record = memory.store("AI", "test_context", "AGEI test content", importance=0.9, tags=["test"])
    assert record.domain == "AI"
    assert record.content == "AGEI test content"
    assert record.importance == 0.9
    recalled = memory.recall(domain="AI", top_k=5)
    assert any(r.record_id == record.record_id for r in recalled)


@pytest.mark.anyio
async def test_enterprise_memory_tag_recall():
    memory = EnterpriseMemory()
    memory.store("ENGINEERING", "arch", "Microservices pattern", tags=["architecture"])
    records = memory.recall(tags=["architecture"])
    assert len(records) >= 1


@pytest.mark.anyio
async def test_enterprise_memory_consolidation():
    memory = EnterpriseMemory()
    memory.store("FINANCE", "budget", "Q4 budget allocation", importance=0.88)
    result = memory.consolidate()
    assert result["consolidation_status"] == "COMPLETE"
    assert result["total_records"] >= 5
    assert "FINANCE" in result["domains"]


@pytest.mark.anyio
async def test_enterprise_memory_stats():
    memory = EnterpriseMemory()
    stats = memory.get_stats()
    assert stats["total_records"] >= 4
    assert stats["unique_domains"] >= 3
    assert 0.0 <= stats["avg_importance"] <= 1.0


# ===========================================================================
# AGEI Core — Goal Manager
# ===========================================================================

@pytest.mark.anyio
async def test_goal_create_and_list():
    gm = GoalManager()
    goal = gm.create_goal(
        title="Expand APAC market", domain="BUSINESS", priority=8,
        target_kpi="25% revenue growth", description="Enter 3 new APAC markets",
    )
    assert goal.title == "Expand APAC market"
    assert goal.state == "PENDING"
    goals = gm.list_goals()
    assert any(g.goal_id == goal.goal_id for g in goals)


@pytest.mark.anyio
async def test_goal_activate():
    gm = GoalManager()
    goal = gm.create_goal("Activate Test Goal", domain="AI", priority=7)
    activated = gm.activate(goal.goal_id)
    assert activated is not None
    assert activated.state == "ACTIVE"


@pytest.mark.anyio
async def test_goal_progress_update():
    gm = GoalManager()
    goal = gm.create_goal("Progress Test Goal", domain="ENGINEERING", priority=6)
    updated = gm.update_progress(goal.goal_id, 75.0)
    assert updated is not None
    assert updated.progress_pct == 75.0
    assert updated.state != "ACHIEVED"  # not yet 100%


@pytest.mark.anyio
async def test_goal_achievement():
    gm = GoalManager()
    goal = gm.create_goal("Achievable Goal", priority=5)
    gm.activate(goal.goal_id)
    achieved = gm.update_progress(goal.goal_id, 100.0)
    assert achieved is not None
    assert achieved.state == "ACHIEVED"


@pytest.mark.anyio
async def test_goal_summary():
    gm = GoalManager()
    summary = gm.get_summary()
    assert summary["total_goals"] >= 3
    assert "active_goals" in summary
    assert summary["active_goals"] >= 3


# ===========================================================================
# AGEI Core — Advanced Reasoning
# ===========================================================================

@pytest.mark.anyio
async def test_reasoning_deductive():
    ar = AdvancedReasoning()
    trace = ar.reason("All enterprise systems must be resilient", mode="Deductive")
    assert trace.mode == "Deductive"
    assert len(trace.steps) >= 4
    assert trace.confidence >= 0.90
    assert trace.conclusion != ""


@pytest.mark.anyio
async def test_reasoning_all_modes():
    ar = AdvancedReasoning()
    for mode in REASONING_MODES:
        trace = ar.reason(f"Test premise for {mode}", mode=mode)
        assert trace.mode == mode
        assert trace.confidence >= 0.90
        assert len(trace.steps) >= 4


@pytest.mark.anyio
async def test_multi_mode_reasoning():
    ar = AdvancedReasoning()
    results = ar.multi_mode_reason("Optimise API performance", modes=["Deductive", "Causal"])
    assert "Deductive" in results
    assert "Causal" in results
    assert all(t.confidence >= 0.90 for t in results.values())


@pytest.mark.anyio
async def test_reasoning_capabilities():
    ar = AdvancedReasoning()
    caps = ar.get_capabilities()
    assert len(caps["supported_modes"]) == 7
    assert caps["cross_domain_enabled"] is True
    assert caps["contradiction_detection"] is True


# ===========================================================================
# AGEI Core — Unified Intelligence Engine
# ===========================================================================

@pytest.mark.anyio
async def test_unified_engine_think():
    engine = UnifiedIntelligenceEngine()
    result = engine.think("How to improve enterprise resilience?", reasoning_mode="Deductive")
    assert result["confidence"] >= 0.90
    assert "conclusion" in result
    assert result["relevant_memories_retrieved"] >= 1


@pytest.mark.anyio
async def test_unified_engine_intelligence_profile():
    engine = UnifiedIntelligenceEngine()
    engine.think("Test thought", store_result=True)
    profile = engine.get_intelligence_profile()
    assert profile.agei_version == AGEI_VERSION
    assert profile.reasoning_accuracy >= 0.98
    assert profile.memory_records >= 4
    assert profile.maturity_level == "ARTIFICIAL_GENERAL_ENTERPRISE_INTELLIGENCE"


@pytest.mark.anyio
async def test_unified_engine_platform_summary():
    engine = UnifiedIntelligenceEngine()
    summary = engine.get_platform_summary()
    assert summary["agei_version"] == "10.0"
    assert summary["overall_health"] == "GREEN"
    assert "goals" in summary
    assert "memory" in summary


# ===========================================================================
# Strategic Intelligence
# ===========================================================================

@pytest.mark.anyio
async def test_strategic_planner():
    planner = StrategicPlanner()
    plan = planner.plan("Global AI leadership", horizon_months=12, domain="PLATFORM")
    assert plan.objective == "Global AI leadership"
    assert len(plan.initiatives) >= 1
    assert plan.confidence >= 0.90
    assert len(plan.success_kpis) >= 2
    assert plan.expected_total_roi_pct > 0


@pytest.mark.anyio
async def test_strategic_roadmap():
    planner = StrategicPlanner()
    roadmap = planner.get_roadmap(horizon_months=12)
    assert roadmap["quarters"] == 4
    assert len(roadmap["milestones"]) >= 4


@pytest.mark.anyio
async def test_long_term_decision_maker():
    ltdm = LongTermDecisionMaker()
    decision = ltdm.decide("Adopt universal AI architecture", horizon_months=24)
    assert decision.horizon_months == 24
    assert decision.confidence >= 0.90
    assert len(decision.expected_outcomes) >= 3
    assert decision.recommended_action != ""


@pytest.mark.anyio
async def test_scenario_comparison():
    ltdm = LongTermDecisionMaker()
    comparison = ltdm.compare_scenarios("Platform expansion strategy")
    assert len(comparison["scenarios"]) >= 3
    assert comparison["recommended_scenario"] == "Balanced"
    assert any(s["recommended"] for s in comparison["scenarios"])


@pytest.mark.anyio
async def test_multi_domain_reasoner_synthesise():
    mdr = MultiDomainReasoner()
    alignment = mdr.synthesise(
        "Improve enterprise efficiency",
        domains=["ENGINEERING", "BUSINESS", "AI"],
    )
    assert alignment.alignment_score >= 0.90
    assert alignment.conflict_count == 0
    assert len(alignment.cross_domain_opportunities) >= 1


@pytest.mark.anyio
async def test_multi_domain_health():
    mdr = MultiDomainReasoner()
    health = mdr.get_domain_health()
    assert len(health) >= 5
    assert all(v["health"] == "GREEN" for v in health.values())


@pytest.mark.anyio
async def test_strategic_hub_summary():
    hub = StrategicIntelligenceHub()
    summary = hub.get_hub_summary()
    assert "strategic_planning" in summary
    assert "long_term_decisions" in summary
    assert "multi_domain_reasoning" in summary


# ===========================================================================
# Enterprise Learning
# ===========================================================================

@pytest.mark.anyio
async def test_continuous_learner_single_cycle():
    learner = ContinuousLearner()
    cycle = learner.run_cycle(domain="AI", data_points=5_000)
    assert cycle.cycle_number == 1
    assert cycle.data_points_ingested == 5_000
    assert cycle.model_accuracy_after > cycle.model_accuracy_before
    assert cycle.improvement_pct > 0


@pytest.mark.anyio
async def test_continuous_learner_multi_domain():
    learner = ContinuousLearner()
    cycles = learner.run_multi_domain_cycles(["ENGINEERING", "BUSINESS", "AI"])
    assert len(cycles) == 3
    assert all(c.improvement_pct >= 0 for c in cycles)


@pytest.mark.anyio
async def test_continuous_learner_stats():
    learner = ContinuousLearner()
    learner.run_cycle(data_points=10_000)
    stats = learner.get_learning_stats()
    assert stats.total_cycles == 1
    assert stats.total_data_points == 10_000
    assert stats.current_model_accuracy > 0


@pytest.mark.anyio
async def test_knowledge_evolver():
    evolver = KnowledgeEvolver()
    event = evolver.evolve(trigger="TEST_TRIGGER", evolution_type="INCREMENTAL", new_triples=100)
    assert event.triples_added == 100
    assert event.validated is True
    assert event.knowledge_density_after > event.knowledge_density_before


@pytest.mark.anyio
async def test_knowledge_evolver_auto_prune():
    evolver = KnowledgeEvolver()
    result = evolver.auto_prune()
    assert result["status"] == "COMPLETE"
    assert "pruning_strategy" in result


@pytest.mark.anyio
async def test_pattern_discoverer():
    discoverer = PatternDiscoverer()
    patterns = discoverer.discover(min_significance=0.99, top_k=5)
    assert len(patterns) >= 1
    assert all(p.statistical_significance >= 0.99 for p in patterns)
    assert all(p.actionable for p in patterns)


@pytest.mark.anyio
async def test_pattern_discoverer_domain_filter():
    discoverer = PatternDiscoverer()
    patterns = discoverer.discover(domain="ENGINEERING", min_significance=0.0)
    assert all(p.domain == "ENGINEERING" for p in patterns)


@pytest.mark.anyio
async def test_enterprise_learning_hub_full_cycle():
    hub = EnterpriseLearningHub()
    result = hub.run_full_learning_cycle()
    assert result["status"] == "COMPLETE"
    assert result["overall_improvement_pct"] >= 0
    assert "learning_cycle" in result
    assert "knowledge_evolution" in result
    assert len(result["patterns_discovered"]) >= 1


@pytest.mark.anyio
async def test_enterprise_learning_hub_summary():
    hub = EnterpriseLearningHub()
    summary = hub.get_learning_summary()
    assert "continuous_learning" in summary
    assert "knowledge_evolution" in summary
    assert "pattern_library" in summary
    assert summary["learning_maturity"] == "AUTONOMOUS_CONTINUAL"


# ===========================================================================
# Autonomous Coordination
# ===========================================================================

@pytest.mark.anyio
async def test_module_coordinator_list():
    mc = ModuleCoordinator()
    modules = mc.list_modules()
    assert len(modules) >= 10  # v2.0 through v9.0
    assert all(m.health == "GREEN" for m in modules)


@pytest.mark.anyio
async def test_module_coordinator_register():
    mc = ModuleCoordinator()
    initial_count = len(mc.list_modules())
    new_mod = mc.register_module("AGEI v10.0", "10.0", ["general_intelligence", "reasoning"])
    assert new_mod.name == "AGEI v10.0"
    assert len(mc.list_modules()) == initial_count + 1


@pytest.mark.anyio
async def test_module_coordinator_report():
    mc = ModuleCoordinator()
    report = mc.get_coordination_report()
    assert report.modules_registered >= 10
    assert report.modules_healthy >= 10
    assert report.coordination_health == "GREEN"
    assert report.autonomous_decisions_today > 0


@pytest.mark.anyio
async def test_task_delegator_single():
    mc = ModuleCoordinator()
    td = TaskDelegator(mc)
    task = td.delegate("AnalyseCodeQuality", required_capability="code_analysis", priority=8)
    assert task.status == "COMPLETE"
    assert task.assigned_module != ""
    assert task.actual_duration_ms >= 0


@pytest.mark.anyio
async def test_task_delegator_batch():
    mc = ModuleCoordinator()
    td = TaskDelegator(mc)
    tasks_spec = [
        {"name": f"BatchTask-{i}", "capability": "ai_analysis", "priority": i}
        for i in range(1, 6)
    ]
    results = td.delegate_batch(tasks_spec)
    assert len(results) == 5
    assert all(t.status == "COMPLETE" for t in results)


@pytest.mark.anyio
async def test_self_optimiser_analyse():
    opt = SelfOptimiser()
    actions = opt.analyse()
    assert len(actions) >= 5
    assert all(a.risk_level == "LOW" for a in actions)


@pytest.mark.anyio
async def test_self_optimiser_apply():
    opt = SelfOptimiser()
    action = opt.apply_optimisation("execution_fabric")
    assert action.applied is True
    assert action.result == "SUCCESS"


@pytest.mark.anyio
async def test_self_optimiser_auto_all():
    opt = SelfOptimiser()
    actions = opt.auto_optimise_all()
    assert len(actions) == 5
    assert all(a.applied for a in actions)
    assert all(a.result == "SUCCESS" for a in actions)


@pytest.mark.anyio
async def test_coordination_hub_summary():
    hub = AutonomousCoordinationHub()
    summary = hub.get_hub_summary()
    assert summary["registered_modules"] >= 10
    assert summary["coordination_health"] == "GREEN"
    assert summary["autonomous_decisions_today"] > 0


@pytest.mark.anyio
async def test_coordination_full_cycle():
    hub = AutonomousCoordinationHub()
    result = hub.coordinate_full_cycle()
    assert result["coordination_health"] == "GREEN"
    assert result["total_modules"] >= 10
    assert result["optimisations_applied"] >= 5


# ===========================================================================
# REST API — Full v10 Router Test
# ===========================================================================

@pytest.mark.anyio
async def test_v10_api_router_full():
    app = FastAPI()
    app.include_router(v10_router)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:

        # Platform status
        res = await client.get("/api/v10/platform/status")
        assert res.status_code == 200
        data = res.json()
        assert data["version"] == "10.0"
        assert data["maturity"] == "ARTIFICIAL_GENERAL_ENTERPRISE_INTELLIGENCE"

        # Dashboard
        res = await client.get("/api/v10/dashboard")
        assert res.status_code == 200
        body = res.json()
        assert body["overall_health"] == "GREEN"
        assert body["ai_maturity_score"] >= 99.0

        # AGEI summary
        res = await client.get("/api/v10/agei")
        assert res.status_code == 200
        assert res.json()["agei_version"] == "10.0"

        # Think
        res = await client.post("/api/v10/agei/think",
                                json={"prompt": "How to maximise ROI?", "reasoning_mode": "Inductive"})
        assert res.status_code == 200
        assert res.json()["result"]["confidence"] >= 0.90

        # Intelligence profile
        res = await client.get("/api/v10/agei/profile")
        assert res.status_code == 200
        assert res.json()["maturity_level"] == "ARTIFICIAL_GENERAL_ENTERPRISE_INTELLIGENCE"

        # Memory store
        res = await client.post("/api/v10/memory/store",
                                json={"domain": "TEST", "context": "api_test",
                                      "content": "API test record", "importance": 0.9})
        assert res.status_code == 200

        # Memory recall
        res = await client.post("/api/v10/memory/recall", json={"domain": "TEST", "top_k": 5})
        assert res.status_code == 200

        # Memory consolidate
        res = await client.post("/api/v10/memory/consolidate")
        assert res.status_code == 200
        assert res.json()["consolidation_status"] == "COMPLETE"

        # Goals
        res = await client.get("/api/v10/goals")
        assert res.status_code == 200
        assert res.json()["count"] >= 3

        # Create goal
        res = await client.post("/api/v10/goals/create",
                                json={"title": "API Test Goal", "domain": "ENGINEERING", "priority": 7})
        assert res.status_code == 200
        goal_id = res.json()["goal"]["goal_id"]

        # Update progress
        res = await client.post("/api/v10/goals/progress",
                                json={"goal_id": goal_id, "progress_pct": 50.0})
        assert res.status_code == 200

        # Reasoning
        res = await client.post("/api/v10/reasoning/reason",
                                json={"premise": "All systems must be reliable", "mode": "Deductive"})
        assert res.status_code == 200
        assert res.json()["trace"]["confidence"] >= 0.90

        # Multi-mode reasoning
        res = await client.post("/api/v10/reasoning/multi",
                                json={"premise": "Enterprise AI optimisation", "modes": ["Deductive", "Causal"]})
        assert res.status_code == 200
        assert "Deductive" in res.json()["traces"]

        # Strategic plan
        res = await client.post("/api/v10/strategic/plan",
                                json={"objective": "AI leadership", "horizon_months": 12, "domain": "PLATFORM"})
        assert res.status_code == 200
        plan = res.json()["plan"]
        assert plan["confidence"] >= 0.90

        # Roadmap
        res = await client.get("/api/v10/strategic/roadmap?horizon_months=12")
        assert res.status_code == 200
        assert res.json()["quarters"] == 4

        # Long-term decision
        res = await client.post("/api/v10/strategic/decide",
                                json={"context": "Global expansion", "horizon_months": 24})
        assert res.status_code == 200
        assert res.json()["decision"]["confidence"] >= 0.90

        # Synthesise
        res = await client.post("/api/v10/strategic/synthesise",
                                json={"premise": "Improve engineering", "domains": ["ENGINEERING", "AI"]})
        assert res.status_code == 200
        assert res.json()["alignment"]["alignment_score"] >= 0.90

        # Learning cycle
        res = await client.post("/api/v10/learning/cycle",
                                json={"domain": "AI", "data_points": 5000})
        assert res.status_code == 200
        assert res.json()["cycle"]["improvement_pct"] >= 0

        # Full learning cycle
        res = await client.post("/api/v10/learning/full-cycle")
        assert res.status_code == 200
        assert res.json()["status"] == "success"

        # Discover patterns
        res = await client.post("/api/v10/learning/discover",
                                json={"min_significance": 0.99, "top_k": 5})
        assert res.status_code == 200
        assert len(res.json()["patterns"]) >= 1

        # Coordination summary
        res = await client.get("/api/v10/coordination")
        assert res.status_code == 200
        assert res.json()["registered_modules"] >= 10

        # List modules
        res = await client.get("/api/v10/coordination/modules")
        assert res.status_code == 200
        assert len(res.json()["modules"]) >= 10

        # Delegate task
        res = await client.post("/api/v10/coordination/delegate",
                                json={"name": "TestTask", "required_capability": "ai_analysis", "priority": 5})
        assert res.status_code == 200
        assert res.json()["task"]["status"] == "COMPLETE"

        # Auto-optimise
        res = await client.post("/api/v10/coordination/auto-optimise")
        assert res.status_code == 200
        assert res.json()["actions_applied"] >= 5

        # Full coordination cycle
        res = await client.post("/api/v10/coordination/full-cycle")
        assert res.status_code == 200
        assert res.json()["coordination_health"] == "GREEN"
