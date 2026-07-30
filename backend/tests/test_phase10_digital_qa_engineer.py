import pytest
from app.ai.reasoning_engine import AIDigitalQAReasoningEngine
from app.ai.autonomous_exploration import AutonomousExplorationEngine
from app.ai.strategy_generator import AITestStrategyGenerator
from app.ai.execution_intelligence import AIExecutionIntelligence
from app.ai.root_cause_intelligence import EnterpriseRootCauseIntelligence
from app.ai.business_impact_engine import BusinessImpactEngine
from app.ai.learning_engine_v2 import AILearningEngineV2
from app.ai.predictive_quality import PredictiveQualityEngine
from app.ai.digital_twin import DigitalTwinService
from app.services.continuous_monitoring import ContinuousMonitoringService
from app.services.self_optimization import SelfOptimizationService
from app.services.multi_format_reports import MultiFormatReportEngine


def test_ai_digital_qa_reasoning_engine():
    engine = AIDigitalQAReasoningEngine()
    res = engine.generate_page_reasoning("https://app.example.com/checkout", "Sales")
    assert res["overall_confidence"] >= 0.95
    assert len(res["reasoning_tree"]["nodes"]) == 5


def test_autonomous_exploration_engine():
    engine = AutonomousExplorationEngine()
    res = engine.explore_application_graph("https://app.example.com")
    assert res["total_discovered_elements"] >= 8
    assert len(res["application_graph"]["nodes"]) >= 4


def test_16_category_strategy_generator():
    generator = AITestStrategyGenerator()
    res = generator.generate_all_strategies("ERP Platform", "https://app.example.com")
    assert res["total_strategies"] == 16
    assert "smoke" in res["strategies"]
    assert "disaster" in res["strategies"]


def test_ai_execution_intelligence():
    intel = AIExecutionIntelligence()
    res = intel.evaluate_step_execution({"error_message": "Element not found selector button.submit"})
    assert res["recommended_action"] == "HEAL_LOCATOR"


def test_enterprise_root_cause_intelligence():
    rca = EnterpriseRootCauseIntelligence()
    res = rca.diagnose_failure({"error_message": "500 Internal Server Error", "http_code": 500})
    assert res["failure_dimension"] == "BACKEND_ISSUE"


def test_business_impact_engine():
    engine = BusinessImpactEngine()
    impact = engine.evaluate_business_impact({"severity": "CRITICAL", "module": "Sales"})
    assert impact["business_severity"] == "CRITICAL"
    assert impact["priority"] == "P0"


def test_predictive_quality_engine():
    engine = PredictiveQualityEngine()
    forecast = engine.generate_quality_forecast(1)
    assert forecast["release_quality_forecast_score"] > 90.0
    assert len(forecast["unstable_modules"]) >= 1


def test_digital_twin_service(db):
    twin = DigitalTwinService(db)
    entity = twin.sync_entity(1, 1, "PAGE", "/checkout", "Checkout Page", {"route": "/checkout"})
    assert entity.id is not None
    mirror = twin.get_digital_twin_mirror(1)
    assert mirror["total_twin_entities"] >= 1


def test_continuous_monitoring_service(db):
    mon = ContinuousMonitoringService(db)
    alert = mon.create_alert(1, "https://app.example.com", "UI_DRIFT", "HIGH", {"diff": "0.15%"})
    assert alert.id is not None
    alerts = mon.get_active_alerts(1)
    assert len(alerts) >= 1


def test_multi_format_report_engine():
    engine = MultiFormatReportEngine()
    rep = engine.generate_report("EXECUTIVE", "HTML", {"name": "ERP"})
    assert rep["report_type"] == "EXECUTIVE"
    assert rep["export_format"] == "HTML"
