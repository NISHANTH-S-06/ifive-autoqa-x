def create_project(client, payload):
  return client.post('/api/projects', json=payload).json()['id']


def test_run_creation_detail_filters_and_404(client, project_payload):
  project_id = create_project(client, project_payload)
  payload = {'project_id': project_id, 'suite_name': 'Smoke Pack', 'browser': 'chromium', 'environment': 'qa'}
  response = client.post('/api/test-runs', json=payload)
  assert response.status_code == 201
  run = response.json()
  assert run['status'] == 'QUEUED'
  assert run['run_code'].startswith('RUN-')
  assert client.get(f"/api/test-runs/{run['id']}").status_code == 200
  assert len(client.get(f'/api/test-runs?project_id={project_id}&status=QUEUED&limit=1').json()) == 1
  assert client.get('/api/test-runs?status=PASSED').json() == []
  assert client.get('/api/test-runs/999').status_code == 404


def test_run_rejects_missing_project_and_production(client):
  payload = {'project_id': 999, 'suite_name': 'Smoke Pack', 'browser': 'chromium', 'environment': 'local'}
  assert client.post('/api/test-runs', json=payload).status_code == 404
  response = client.post('/api/test-runs', json={**payload, 'environment': 'production'})
  assert response.status_code == 400
  assert response.json()['detail'] == 'Production test execution is disabled.'
