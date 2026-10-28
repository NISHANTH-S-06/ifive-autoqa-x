def test_project_crud_and_validation(client, project_payload):
  created = client.post('/api/projects', json=project_payload)
  assert created.status_code == 201
  project_id = created.json()['id']
  assert client.get('/api/projects').json()[0]['product_code'] == 'AUTOQA'
  assert client.get(f'/api/projects/{project_id}').json()['name'] == project_payload['name']

  duplicate = client.post('/api/projects', json=project_payload)
  assert duplicate.status_code == 409
  invalid = client.post('/api/projects', json={**project_payload, 'name': 'Invalid', 'environment': 'INVALID_ENV'})
  assert invalid.status_code == 400


def test_project_404(client):
  assert client.get('/api/projects/999').status_code == 404
