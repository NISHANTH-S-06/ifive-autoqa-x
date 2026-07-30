import pytest
from app.ai.agents.agent_registry import AgentRegistry
from app.ai.agents.orchestrator import AgentOrchestrator
from app.ai.memory import AIMemoryService
from app.ai.knowledge_graph import KnowledgeGraphService
from app.ai.risk_engine import SmartRiskEngine
from app.services.release_readiness import ReleaseReadinessService
from app.services.autonomous_regression import AutonomousRegressionService
from app.ai.copilot import AICopilotEngine
from app.models.company_task import CompanyTask
from app.models.defect import Defect


def test_13_specialized_agents_registry():
    registry = AgentRegistry()
    agents = registry.list_agents()
    assert len(agents) == 13
    
    agent_ids = {a['id'] for a in agents}
    expected = {'task', 'discovery', 'context', 'planning', 'execution', 'validation', 'visual', 'decision', 'bug_analysis', 'recommendation', 'learning', 'reporting', 'release'}
    assert expected == agent_ids


def test_agent_orchestrator_pipeline():
    orchestrator = AgentOrchestrator()
    res = orchestrator.run_pipeline('FULL_AUTONOMOUS_QA', {'url': 'https://example.com', 'title': 'Test'})
    assert res['status'] == 'SUCCESS'
    assert 'task' in res['agent_results']
    assert 'discovery' in res['agent_results']
    assert 'release_verdict' in res['agent_results']


def test_ai_memory_and_locator_persistence(db):
    memory_service = AIMemoryService(db)
    rec = memory_service.store_memory('RUN', 'https://example.com/login', {'status': 'PASSED'})
    assert rec.id is not None

    recalled = memory_service.recall_memory('RUN', 'https://example.com/login')
    assert len(recalled) == 1
    assert recalled[0]['status'] == 'PASSED'

    loc = memory_service.record_locator_result('https://example.com/login', 'submit_btn', 'button.submit', success=True)
    assert loc.success_count == 1
    best = memory_service.get_best_locator('https://example.com/login', 'submit_btn')
    assert best == 'button.submit'


def test_knowledge_graph_service(db):
    graph = KnowledgeGraphService(db)
    node1 = graph.add_node('COMPANY', 'comp_1', 'iFive Tech')
    node2 = graph.add_node('PROJECT', 'proj_1', 'ERP System')

    assert node1.id is not None
    assert node2.id is not None

    edge = graph.add_edge(node1.id, node2.id, 'OWNS_PROJECT')
    assert edge.id is not None

    topology = graph.get_topology_graph()
    assert topology['total_nodes'] >= 2
    assert topology['total_edges'] >= 1


def test_smart_risk_engine():
    engine = SmartRiskEngine()
    risk = engine.calculate_risk({
        'open_critical_bugs': 0,
        'open_total_bugs': 2,
        'pass_rate': 98.0,
        'automation_coverage': 96.0
    })

    assert 'overall_risk_score' in risk
    assert risk['overall_risk_score'] < 20.0


def test_release_readiness_service(db):
    service = ReleaseReadinessService(db)
    eval_res = service.evaluate_release(1, 'v1.0.0', 1)
    assert eval_res.id is not None
    assert eval_res.readiness_status in ['READY', 'NOT_READY', 'BLOCKED']


def test_autonomous_regression_service(db):
    task = CompanyTask(
        project_id=1,
        title="Update Sales Order Form",
        module="Sales",
        created_by=1
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    service = AutonomousRegressionService(db)
    report = service.analyze_impact_and_plan(task.id)
    assert report['target_module'] == 'Sales'
    assert 'Inventory' in report['impacted_modules']
    assert len(report['regression_plan']) >= 2


def test_ai_copilot_engine(db):
    defect = Defect(
        access_project_id=1,
        project_id=1,
        defect_key="DEF-001",
        title="Button submit not clickable",
        severity="HIGH",
        reporter_id=1,
        created_by=1,
        actual_result="Element button.submit not visible"
    )
    db.add(defect)
    db.commit()

    engine = AICopilotEngine()
    res1 = engine.answer_query("Why did this test fail?", None, db)
    assert "Root Cause" in res1['answer']

    res2 = engine.answer_query("Predict release quality", None, db)
    assert "Release Quality Forecast" in res2['answer']
