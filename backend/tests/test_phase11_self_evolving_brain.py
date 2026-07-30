import pytest
from app.ai.experience_memory import AIExperienceMemoryService
from app.ai.pattern_recognition import PatternRecognitionEngine
from app.ai.predictive_quality_v2 import QualityPredictionEngineV2
from app.ai.test_evolution import AutonomousTestEvolutionEngine
from app.ai.root_cause_graph import AIRootCauseGraphService
from app.ai.self_improving_playwright import SelfImprovingPlaywrightEngine
from app.services.autonomous_monitoring_v2 import AutonomousMonitoringV2Service
from app.services.autonomous_optimization import AutonomousOptimizationService
from app.services.release_readiness import ReleaseReadinessService


def test_ai_experience_memory_service(db):
    service = AIExperienceMemoryService(db)
    rec = service.record_experience("EXECUTION", "https://example.com/checkout", {"status": "PASSED"})
    assert rec.id is not None
    mems = service.recall_experiences("EXECUTION")
    assert len(mems) >= 1
    global_pats = service.get_global_qa_patterns()
    assert global_pats["anonymized_tenant_count"] == 100


def test_pattern_recognition_engine(db):
    engine = PatternRecognitionEngine(db)
    res = engine.analyze_patterns(1)
    assert res["pattern_score"] > 0
    assert len(res["patterns"]) >= 1


def test_quality_prediction_engine_v2():
    engine = QualityPredictionEngineV2()
    forecast = engine.forecast_sprint_and_release(1)
    assert forecast["sprint_quality_score"] > 90.0
    assert forecast["confidence_percentage"] >= 95.0


def test_autonomous_test_evolution_engine(db):
    engine = AutonomousTestEvolutionEngine(db)
    res = engine.evolve_test_suite(1)
    assert res["total_evolved_actions"] >= 4


def test_ai_root_cause_graph_service(db):
    service = AIRootCauseGraphService(db)
    chain = service.build_root_cause_chain("DEF-101")
    assert chain["chain_depth"] >= 8
    assert "why" in chain["explanation"]


def test_self_improving_playwright_engine():
    engine = SelfImprovingPlaywrightEngine()
    opt = engine.optimize_playwright_runtime({"run_id": 1})
    assert opt["status"] == "PLAYWRIGHT_RUNTIME_OPTIMIZED"


def test_autonomous_monitoring_v2_service():
    service = AutonomousMonitoringV2Service()
    res = service.run_monitoring_pass("https://example.com")
    assert res["status"] == "ALL_CHECKS_HEALTHY"
    assert res["checks_count"] >= 6


def test_autonomous_optimization_service(db):
    service = AutonomousOptimizationService(db)
    opt = service.generate_optimizations(1)
    assert opt["total_recommendations"] >= 4
