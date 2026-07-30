from datetime import datetime

from app.models.test_run import TestRun as TestRunModel
from app.models.project import Project


def test_dashboard_summary_empty(client):
  summary = client.get('/api/dashboard/summary').json()
  assert summary['total_runs'] == 0
  assert summary['pass_rate'] == 0
  assert summary['average_duration_seconds'] == 0
  assert summary['recent_runs'] == []


def test_dashboard_summary_calculations(client, db, project_payload):
  project = client.post('/api/projects', json=project_payload).json()
  for index, status in enumerate(('PASSED', 'FAILED', 'QUEUED')):
    db.add(TestRunModel(
      run_code=f'RUN-CALC-{index}', project_id=project['id'], suite_name='Calculation', status=status,
      browser='chromium', environment='local', total_tests=10, passed_tests=8,
      failed_tests=2, skipped_tests=0, duration_seconds=30 + index, created_at=datetime.utcnow(),
    ))
  db.commit()
  summary = client.get('/api/dashboard/summary').json()
  assert summary['total_projects'] == 1
  assert summary['total_runs'] == 3
  assert summary['passed_runs'] == 1
  assert summary['failed_runs'] == 1
  assert summary['queued_runs'] == 1
  assert summary['pass_rate'] == 50
  assert summary['total_tests'] == 30
  assert summary['average_duration_seconds'] == 31


def test_seed_is_idempotent(db):
  from app.seed import seed_local_projects

  assert seed_local_projects(db) == 8
  assert seed_local_projects(db) == 0
  assert len(db.query(Project).all()) == 8
