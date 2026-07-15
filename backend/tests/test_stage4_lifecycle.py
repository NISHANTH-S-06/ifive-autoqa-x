import json
from datetime import datetime

import pytest

from app.models.evidence import Evidence
from app.models.project import Project
from app.models.test_result import TestResult as ResultModel
from app.models.test_run import TestRun as RunModel
from app.repositories.run_repository import RunRepository
from app.schemas.test_run import TestRunStatus
from app.services.playwright_runner import get_runner, parse_playwright_json, redact_secrets


class FakeRunner:
  def __init__(self):
    self.started = []
    self.cancelled = []
    self.active = False

  def validate_run(self, run):
    return None

  def start(self, run_id):
    self.started.append(run_id)

  def cancel(self, run_id):
    self.cancelled.append(run_id)
    return True

  def is_active(self, run_id):
    return self.active


@pytest.fixture
def fake_runner(client):
  runner = FakeRunner()
  from app.main import app
  app.dependency_overrides[get_runner] = lambda: runner
  yield runner
  app.dependency_overrides.pop(get_runner, None)


def add_project(db, code='AUTOQA', environment='local', name='Stage 4 Project'):
  project = Project(name=name, product_code=code, environment=environment, is_active=True)
  db.add(project); db.commit(); db.refresh(project)
  return project


def add_run(db, project, status='QUEUED', suite='dashboard-smoke', environment='local', code='RUN-STAGE4'):
  run = RunModel(run_code=code, project_id=project.id, suite_name=suite, browser='chromium', environment=environment, status=status)
  db.add(run); db.commit(); db.refresh(run)
  return run


def approve(client, run_id, confirmation='APPROVE LOCAL TEST EXECUTION'):
  return client.post(f'/api/test-runs/{run_id}/approve', json={'confirmation': confirmation})


def test_valid_approval_and_incorrect_confirmation(client, db):
  run = add_run(db, add_project(db))
  assert approve(client, run.id, 'wrong').status_code == 400
  response = approve(client, run.id)
  assert response.status_code == 200
  assert response.json()['status'] == 'APPROVED'
  assert response.json()['approved_at']
  assert approve(client, run.id).status_code == 409


def test_approval_missing_and_scope_rejections(client, db):
  assert approve(client, 999).status_code == 404
  non_autoqa = add_run(db, add_project(db, code='ERP', name='ERP'), code='RUN-ERP')
  assert approve(client, non_autoqa.id).json()['detail'] == 'Only local AutoQA suites can be executed in Stage 4.'
  non_local = add_run(db, add_project(db, name='Remote'), environment='qa', code='RUN-QA')
  assert approve(client, non_local.id).status_code == 400
  unknown = add_run(db, add_project(db, name='Unknown'), suite='../evil.spec.ts', code='RUN-EVIL')
  assert approve(client, unknown.id).json()['detail'] == 'Test suite is not approved for local execution.'


def test_execute_requires_approval_and_accepts_approved(client, db, fake_runner):
  run = add_run(db, add_project(db))
  assert client.post(f'/api/test-runs/{run.id}/execute', json={'confirm_local_execution': True}).status_code == 409
  assert approve(client, run.id).status_code == 200
  response = client.post(f'/api/test-runs/{run.id}/execute', json={'confirm_local_execution': True})
  assert response.status_code == 202
  assert fake_runner.started == [run.id]


def test_duplicate_completed_and_concurrent_execute_rejections(client, db, fake_runner):
  project = add_project(db)
  approved = add_run(db, project, status='APPROVED')
  fake_runner.active = True
  assert client.post(f'/api/test-runs/{approved.id}/execute', json={'confirm_local_execution': True}).status_code == 409
  fake_runner.active = False
  for index, status in enumerate(('PASSED', 'FAILED', 'CANCELLED')):
    run = add_run(db, project, status=status, code=f'RUN-DONE-{index}')
    response = client.post(f'/api/test-runs/{run.id}/execute', json={'confirm_local_execution': True})
    assert response.json()['detail'] == 'Completed test runs cannot be executed again.'
  running = add_run(db, project, status='RUNNING', code='RUN-BUSY')
  other = add_run(db, project, status='APPROVED', code='RUN-WAIT')
  assert client.post(f'/api/test-runs/{other.id}/execute', json={'confirm_local_execution': True}).json()['detail'] == 'Another local test run is already executing.'


def test_valid_and_invalid_cancellation(client, db, fake_runner):
  project = add_project(db)
  approved = add_run(db, project, status='APPROVED')
  assert client.post(f'/api/test-runs/{approved.id}/cancel').json()['status'] == 'CANCELLED'
  queued = add_run(db, project, code='RUN-QUEUE')
  assert client.post(f'/api/test-runs/{queued.id}/cancel').status_code == 409
  running = add_run(db, project, status='RUNNING', code='RUN-CANCEL')
  assert client.post(f'/api/test-runs/{running.id}/cancel').json()['status'] == 'CANCELLED'
  assert fake_runner.cancelled == [running.id]


def test_lifecycle_terminal_timeout_and_recovery(db):
  project = add_project(db)
  for index, status in enumerate((TestRunStatus.PASSED, TestRunStatus.FAILED, TestRunStatus.CANCELLED)):
    run = add_run(db, project, status='RUNNING', code=f'RUN-LIFE-{index}')
    RunRepository(db).set_status(run, status, completed_at=datetime.utcnow())
    assert run.status == status.value
  timeout = add_run(db, project, status='RUNNING', code='RUN-TIMEOUT')
  RunRepository(db).set_status(timeout, TestRunStatus.FAILED, error_summary='Test execution exceeded the configured timeout.', completed_at=datetime.utcnow())
  assert 'timeout' in timeout.error_summary
  interrupted = add_run(db, project, status='RUNNING', code='RUN-INTERRUPTED')
  assert RunRepository(db).recover_interrupted() == 1
  db.refresh(interrupted)
  assert interrupted.error_summary == 'Execution interrupted before completion.'


def test_result_parsing_and_secret_redaction(tmp_path):
  result_file = tmp_path / 'results.json'
  result_file.write_text(json.dumps({'suites': [{'file': 'tests/dashboard/dashboard.spec.ts', 'specs': [{'title': 'works', 'tests': [{'results': [{'status': 'passed', 'duration': 1250}]}]}]}]}), encoding='utf-8')
  parsed = parse_playwright_json(result_file)
  assert parsed[0]['status'] == 'PASSED'
  assert parsed[0]['duration_seconds'] == 1.25
  redacted = redact_secrets('token=abc password: xyz Authorization=Bearer123 safe=value')
  assert 'abc' not in redacted and 'xyz' not in redacted and 'Bearer123' not in redacted


def test_evidence_metadata_ownership_and_traversal(client, db, tmp_path, monkeypatch):
  import app.api.test_runs as routes
  project = add_project(db)
  run = add_run(db, project)
  other = add_run(db, project, code='RUN-OTHER')
  run_root = tmp_path / 'runs' / run.run_code
  run_root.mkdir(parents=True)
  safe_file = run_root / 'report.txt'; safe_file.write_text('safe', encoding='utf-8')
  monkeypatch.setattr(routes, 'PROJECT_ROOT', tmp_path)
  monkeypatch.setattr(routes, 'RUNS_ROOT', tmp_path / 'runs')
  safe = Evidence(test_run_id=run.id, evidence_type='STDOUT', relative_path=f'runs/{run.run_code}/report.txt', file_size_bytes=4)
  escaped = Evidence(test_run_id=run.id, evidence_type='STDERR', relative_path='../outside.txt', file_size_bytes=0)
  owned_elsewhere = Evidence(test_run_id=other.id, evidence_type='STDOUT', relative_path=f'runs/{run.run_code}/report.txt', file_size_bytes=4)
  db.add_all([safe, escaped, owned_elsewhere]); db.commit()
  assert len(client.get(f'/api/test-runs/{run.id}/evidence').json()) == 2
  assert client.get(f'/api/test-runs/{run.id}/evidence/{safe.id}').status_code == 200
  assert client.get(f'/api/test-runs/{run.id}/evidence/{escaped.id}').status_code == 400
  assert client.get(f'/api/test-runs/{run.id}/evidence/{owned_elsewhere.id}').status_code == 404


def test_detail_returns_results_and_evidence(client, db):
  run = add_run(db, add_project(db))
  result = ResultModel(test_run_id=run.id, test_name='local smoke', test_file='tests/dashboard/dashboard.spec.ts', status='PASSED', duration_seconds=1)
  db.add(result); db.flush()
  db.add(Evidence(test_run_id=run.id, test_result_id=result.id, evidence_type='JSON_RESULT', relative_path='qa/reports/runs/RUN-STAGE4/results/results.json', file_size_bytes=10))
  db.commit()
  detail = client.get(f'/api/test-runs/{run.id}').json()
  assert detail['results'][0]['test_name'] == 'local smoke'
  assert detail['evidence'][0]['evidence_type'] == 'JSON_RESULT'
