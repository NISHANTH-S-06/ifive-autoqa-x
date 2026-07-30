"""Phase 14 – Enterprise Autonomous AI QA Operating System (AI QA OS) Integration Tests."""
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def auth_headers():
    return {}


# ─── Module 1: AI Enterprise Command Brain ───────────────────────────────────

def test_enterprise_brain_orchestration(client: TestClient, auth_headers: dict):
    res = client.post('/api/enterprise-brain/orchestrate', json={
        'goal_description': 'Run full autonomous regression for ERP release v3.0',
        'priority': 8,
    }, headers=auth_headers)
    assert res.status_code == 201
    data = res.json()
    assert 'run_id' in data
    assert len(data['dag_tasks']) >= 5
    assert 'decision_tree' in data
    assert data['resource_allocation']['allocated_workers'] >= 2

    # List runs & get status
    res2 = client.get('/api/enterprise-brain/runs', headers=auth_headers)
    assert res2.status_code == 200
    assert len(res2.json()) >= 1

    run_id = data['run_id']
    res3 = client.get(f'/api/enterprise-brain/runs/{run_id}', headers=auth_headers)
    assert res3.status_code == 200
    assert res3.json()['run_id'] == run_id


def test_enterprise_brain_priority_allocation(client: TestClient, auth_headers: dict):
    res = client.post('/api/enterprise-brain/orchestrate', json={
        'goal_description': 'High priority P1 hotfix verification',
        'priority': 10,
    }, headers=auth_headers)
    assert res.status_code == 201
    assert res.json()['priority'] == 10


# ─── Module 2: Autonomous Workflow Composer ────────────────────────────────

def test_workflow_composer_seed_and_list(client: TestClient, auth_headers: dict):
    res = client.post('/api/workflows/templates/seed', headers=auth_headers)
    assert res.status_code == 200
    templates = res.json()
    assert len(templates) >= 2

    res2 = client.get('/api/workflows/templates', headers=auth_headers)
    assert res2.status_code == 200
    assert len(res2.json()) >= 2


def test_workflow_composer_create_template(client: TestClient, auth_headers: dict):
    res = client.post('/api/workflows/templates', json={
        'template_name': 'Custom Smoke Flow',
        'category': 'QA_PIPELINE',
        'description': 'Custom smoke validation',
        'graph_definition': {'nodes': [{'id': 'n1', 'label': 'Login', 'type': 'ACTION'}]},
    }, headers=auth_headers)
    assert res.status_code == 201
    assert res.json()['template_name'] == 'Custom Smoke Flow'


def test_workflow_composer_execute(client: TestClient, auth_headers: dict):
    # Seed templates first
    client.post('/api/workflows/templates/seed', headers=auth_headers)
    res_list = client.get('/api/workflows/templates', headers=auth_headers)
    template_id = res_list.json()[0]['id']

    res = client.post('/api/workflows/execute', json={
        'template_id': template_id,
        'execution_name': 'Test Execution Run 1',
    }, headers=auth_headers)
    assert res.status_code == 201
    assert res.json()['execution_status'] == 'RUNNING'

    res2 = client.get('/api/workflows/executions', headers=auth_headers)
    assert res2.status_code == 200
    assert len(res2.json()) >= 1


# ─── Module 3: Enterprise AI Agents Marketplace ──────────────────────────────

def test_ai_agents_marketplace_flow(db):
    from app.services.ai_agents_marketplace import AIAgentsMarketplaceService
    svc = AIAgentsMarketplaceService(db)
    agents = svc.seed_agents()
    assert len(agents) == 10

    agent_id = agents[0]['id']
    installed = svc.install_agent(agent_id)
    assert installed['install_status'] == 'INSTALLED'

    updated = svc.update_agent(agent_id)
    assert updated['version'] != agents[0]['version']

    uninstalled = svc.uninstall_agent(agent_id)
    assert uninstalled['install_status'] == 'AVAILABLE'


def test_ai_agents_marketplace_categories(db):
    from app.services.ai_agents_marketplace import AIAgentsMarketplaceService
    svc = AIAgentsMarketplaceService(db)
    svc.seed_agents()
    sec_agents = svc.list_agents(category='SECURITY')
    assert len(sec_agents) >= 1
    assert sec_agents[0]['agent_category'] == 'SECURITY'


# ─── Module 4: AI Business Process Understanding ─────────────────────────────

def test_business_process_seed_and_list(client: TestClient, auth_headers: dict):
    res = client.post('/api/business-process/seed', headers=auth_headers)
    assert res.status_code == 200
    processes = res.json()
    assert len(processes) >= 3

    res2 = client.get('/api/business-process/processes', headers=auth_headers)
    assert res2.status_code == 200
    assert len(res2.json()) >= 3


def test_business_process_create(client: TestClient, auth_headers: dict):
    res = client.post('/api/business-process/processes', json={
        'process_name': 'Healthcare Patient Admission',
        'domain_type': 'HEALTHCARE',
        'risk_score': 92.0,
        'is_critical_path': True,
        'flow_graph': {'nodes': ['Register', 'Triage', 'Admit']},
    }, headers=auth_headers)
    assert res.status_code == 201
    assert res.json()['domain_type'] == 'HEALTHCARE'


# ─── Module 5 & 10: Release Simulation & Optimization V2 ─────────────────────

def test_release_simulation_run(client: TestClient, auth_headers: dict):
    res = client.post('/api/optimization-v2/simulation/run', json={
        'release_version': 'v4.0.0-RC1',
    }, headers=auth_headers)
    assert res.status_code == 201
    data = res.json()
    assert 'rollback_probability_pct' in data
    assert data['release_version'] == 'v4.0.0-RC1'

    res2 = client.get('/api/optimization-v2/simulation/history', headers=auth_headers)
    assert res2.status_code == 200
    assert len(res2.json()) >= 1


def test_optimization_v2_tuning(client: TestClient, auth_headers: dict):
    res = client.post('/api/optimization-v2/tune', headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data['total_subsystems_tuned'] == 8
    assert data['overall_gain_pct'] > 0

    res2 = client.get('/api/optimization-v2/history', headers=auth_headers)
    assert res2.status_code == 200
    assert len(res2.json()) >= 8


# ─── Module 7: Autonomous Incident Commander ───────────────────────────────

def test_incident_commander_flow(client: TestClient, auth_headers: dict):
    res = client.post('/api/incidents/trigger', json={
        'title': 'Production Checkout Latency Spike',
        'severity': 'SEV-1',
        'evidence': {'latency_p99_ms': 4500},
    }, headers=auth_headers)
    assert res.status_code == 201
    inc = res.json()
    assert inc['severity'] == 'SEV-1'
    assert len(inc['timeline']) >= 1
    incident_id = inc['id']

    # Get incident
    res2 = client.get(f'/api/incidents/{incident_id}', headers=auth_headers)
    assert res2.status_code == 200

    # Resolve incident
    res3 = client.post(f'/api/incidents/{incident_id}/resolve', json={
        'summary': 'DB index applied to resolve latency.',
    }, headers=auth_headers)
    assert res3.status_code == 200
    assert res3.json()['incident_status'] == 'RESOLVED'


def test_incident_list_filtering(client: TestClient, auth_headers: dict):
    res = client.get('/api/incidents?status=RESOLVED', headers=auth_headers)
    assert res.status_code == 200


# ─── Module 8: Enterprise Knowledge Universe ────────────────────────────────

def test_knowledge_universe_flow(client: TestClient, auth_headers: dict):
    res = client.post('/api/knowledge-universe/seed', headers=auth_headers)
    assert res.status_code == 200
    graph = res.json()
    assert len(graph['nodes']) >= 10
    assert len(graph['edges']) >= 8

    res2 = client.get('/api/knowledge-universe/graph', headers=auth_headers)
    assert res2.status_code == 200

    res3 = client.post('/api/knowledge-universe/nodes', json={
        'label': 'New Microservice',
        'node_type': 'INFRASTRUCTURE',
    }, headers=auth_headers)
    assert res3.status_code == 201
    assert res3.json()['label'] == 'New Microservice'


# ─── Module 9: AI Executive Advisor ─────────────────────────────────────────

def test_executive_advisor_queries(client: TestClient, auth_headers: dict):
    queries = [
        'Can I release today?',
        "What are today's risks?",
        'Which developer introduces most defects?',
        'Predict next sprint quality',
    ]
    for q in queries:
        res = client.post('/api/executive-advisor/ask', json={'query': q}, headers=auth_headers)
        assert res.status_code == 201
        assert res.json()['confidence_score'] > 0.8

    res_hist = client.get('/api/executive-advisor/history', headers=auth_headers)
    assert res_hist.status_code == 200
    assert len(res_hist.json()) >= 4


# ─── Module 11: Enterprise Governance Center ─────────────────────────────────

def test_governance_center_policies(client: TestClient, auth_headers: dict):
    res = client.post('/api/governance-v2/policies/seed', headers=auth_headers)
    assert res.status_code == 200
    policies = res.json()
    assert len(policies) >= 4

    policy_id = policies[0]['id']
    res2 = client.post(f'/api/governance-v2/policies/{policy_id}/toggle', headers=auth_headers)
    assert res2.status_code == 200
    assert res2.json()['is_enforced'] is False


def test_governance_center_create(client: TestClient, auth_headers: dict):
    res = client.post('/api/governance-v2/policies', json={
        'policy_name': 'HIPAA Patient Privacy Lock',
        'policy_type': 'SECURITY_POLICY',
        'rules': {'patient_data_encrypted': True},
    }, headers=auth_headers)
    assert res.status_code == 201
    assert res.json()['policy_name'] == 'HIPAA Patient Privacy Lock'


# ─── Module 12: AI Forecast Center ───────────────────────────────────────────

def test_forecast_center_generation(client: TestClient, auth_headers: dict):
    res = client.post('/api/forecast/generate?horizon_days=30', headers=auth_headers)
    assert res.status_code == 201
    forecasts = res.json()
    assert len(forecasts) >= 7

    res2 = client.get('/api/forecast/metrics', headers=auth_headers)
    assert res2.status_code == 200
    assert len(res2.json()) >= 7


# ─── Module 13: Enterprise Report Factory V2 ─────────────────────────────────

def test_report_factory_v2_generation(client: TestClient, auth_headers: dict):
    personas = ['EXECUTIVE', 'TECHNICAL', 'DEVELOPER', 'COMPLIANCE']
    for p in personas:
        res = client.post('/api/report-factory/generate', json={
            'report_title': f'{p} Quarterly Report',
            'report_persona': p,
            'export_format': 'PDF',
        }, headers=auth_headers)
        assert res.status_code == 201
        assert res.json()['report_persona'] == p

    res2 = client.get('/api/report-factory/reports', headers=auth_headers)
    assert res2.status_code == 200
    assert len(res2.json()) >= 4
