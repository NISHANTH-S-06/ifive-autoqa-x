from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import hashlib
import base64
import json
import threading
import time

from sqlalchemy import text
from sqlalchemy.orm import sessionmaker

from app.models.automated_execution import AutomatedRun, ExecutionArtifact, ExecutionJob, ExecutionWorker
from app.models.connection_target import ConnectionTarget
from app.models.operator import Operator
from app.models.operator_session import OperatorSession
from app.models.test_management import ManagedTestCase, ManagedTestSuite, TestCaseStep, TestModule, TestProject
from app.services.audit_service import verify_chain
from app.services.automated_execution import claim_next_job, execute_next_job, store_artifact
from app.services.password_service import hash_password, hash_secret
from app.services.test_management import create_version

PASSWORD_HASH = hash_password('Stage10!Fixture987')
ONE_PIXEL_PNG = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADGAWjR9awAAAABJRU5ErkJggg==')


def operator(db, username: str, role: str = 'VIEWER', active: bool = True, must_change: bool = False):
  item = Operator(username=username, display_name=username.title(), password_hash=PASSWORD_HASH, role=role, is_active=active, must_change_password=must_change)
  db.add(item); db.commit(); db.refresh(item); return item


def session_login(client, db, item, token: str, csrf: str = 'stage10-csrf'):
  session = OperatorSession(operator_id=item.id, token_hash=hash_secret(token), csrf_hash=hash_secret(csrf), created_at=datetime.utcnow(), expires_at=datetime.utcnow() + timedelta(hours=1), last_seen_at=datetime.utcnow(), password_version_at_login=item.password_version)
  db.add(session); db.commit(); client.cookies.clear(); client.cookies.set('autoqa_session', token); return {'X-CSRF-Token': csrf}


class MockHandler(BaseHTTPRequestHandler):
  def log_message(self, *_):
    return

  def do_GET(self):
    if self.path == '/redirect':
      self.send_response(302); self.send_header('Location', 'http://example.com/escape'); self.end_headers(); return
    if self.path == '/slow':
      time.sleep(6)
    self.send_response(200)
    self.send_header('Content-Type', 'text/html')
    self.end_headers()
    self.wfile.write(b'''<html><head><title>Stage10 Mock</title></head><body>
      <main id="ready">Ready local target</main>
      <form id="fixture"><input id="fixture-input"/><button id="fixture-submit" type="button">Submit</button></form>
      <div id="fixture-result" hidden></div>
      <button id="go">Go</button>
      <script>document.querySelector('#fixture-submit').onclick=()=>{const value=document.querySelector('#fixture-input').value;const result=document.querySelector('#fixture-result');result.textContent='Result: '+value;result.hidden=false;};</script>
    </body></html>''')


def mock_target_url():
  server = ThreadingHTTPServer(('127.0.0.1', 0), MockHandler)
  thread = threading.Thread(target=server.serve_forever, daemon=True)
  thread.start()
  return server, thread, f'http://127.0.0.1:{server.server_port}'


def target_payload(base_url: str, key='S10-LOCAL'):
  return {
    'target_key': key,
    'name': 'Stage 10 Local Mock',
    'environment_type': 'LOCAL',
    'base_url': base_url,
    'allowed_probe_paths': ['/', '/redirect', '/slow'],
    'tls_required': False,
    'tls_verify': True,
    'connection_timeout_seconds': 3,
  }


def approve_stage9_target(client, db, base_url):
  tester = operator(db, 'stage10-target-author', 'TESTER')
  approver = operator(db, 'stage10-target-approver', 'APPROVER')
  tester_headers = session_login(client, db, tester, 'stage10-target-author-token')
  created = client.post('/api/connection-targets', json=target_payload(base_url), headers=tester_headers)
  assert created.status_code == 201
  target_id = created.json()['id']
  assert client.post(f'/api/connection-targets/{target_id}/submit', headers=tester_headers).status_code == 200
  approver_headers = session_login(client, db, approver, 'stage10-target-approver-token')
  approved = client.post(f'/api/connection-targets/{target_id}/approve', headers=approver_headers)
  assert approved.status_code == 200
  return tester, tester_headers, approver, approver_headers, approved.json()


def approve_execution_target(client, db, target_id, tester, approver):
  tester_headers = session_login(client, db, tester, f'{tester.username}-execution-submit')
  submitted = client.post(f'/api/connection-targets/{target_id}/execution-submit', headers=tester_headers)
  assert submitted.status_code == 200 and submitted.json()['execution_enabled'] is False
  self_approval = client.post(f'/api/connection-targets/{target_id}/execution-approve', headers=tester_headers)
  assert self_approval.status_code in {400, 403}
  approver_headers = session_login(client, db, approver, f'{approver.username}-execution-approve')
  approved = client.post(f'/api/connection-targets/{target_id}/execution-approve', headers=approver_headers)
  assert approved.status_code == 200 and approved.json()['execution_enabled'] is True
  return approved.json()


def create_approved_case(db, creator: Operator, approver: Operator, key='S10-CASE', steps=None):
  project = TestProject(name='Stage10 Project', code=f'{key}-P', created_by=approver.id)
  db.add(project); db.flush()
  module = TestModule(project_id=project.id, name='Module', code='MOD', created_by=approver.id)
  db.add(module); db.flush()
  suite = ManagedTestSuite(project_id=project.id, module_id=module.id, name='Suite', code='AUTO', suite_type='AUTOMATED', created_by=approver.id)
  db.add(suite); db.flush()
  case = ManagedTestCase(project_id=project.id, module_id=module.id, suite_id=suite.id, case_key=key, title='Structured automation case', lifecycle_state='APPROVED', status='ACTIVE', created_by=creator.id, reviewed_by=approver.id, approved_by=approver.id, approved_at=datetime.utcnow())
  db.add(case); db.flush()
  for index, payload in enumerate(steps or [
    {'action': 'NAVIGATE', 'path': '/'},
    {'action': 'ASSERT_VISIBLE', 'selector': '#ready'},
    {'action': 'ASSERT_TEXT', 'selector': '#ready', 'expected': 'Ready local target'},
    {'action': 'SCREENSHOT'},
  ], start=1):
    case.steps.append(TestCaseStep(step_number=index, action=json.dumps(payload), expected_result='Structured action passes', test_data=json.dumps(payload)))
  db.flush()
  create_version(db, case, approver.id, 'Approved for automation', 'APPROVED')
  db.commit(); db.refresh(case); return case


def create_run(client, target_id, case_id, headers, name='Stage 10 Run', timeout=30, retries=1):
  return client.post('/api/automated-runs', json={'name': name, 'target_id': target_id, 'case_ids': [case_id], 'timeout_seconds': timeout, 'max_retries': retries}, headers=headers)


def test_execution_target_approval_queue_worker_artifacts_and_audit(auth_client, db):
  server, thread, base_url = mock_target_url()
  try:
    tester, tester_headers, approver, approver_headers, target = approve_stage9_target(auth_client, db, base_url)
    case = create_approved_case(db, tester, approver)
    tester_headers = session_login(auth_client, db, tester, 'stage10-run-blocked-token')
    blocked = create_run(auth_client, target['id'], case.id, tester_headers)
    assert blocked.status_code == 409 and 'separately approved' in blocked.json()['detail']
    target = approve_execution_target(auth_client, db, target['id'], tester, approver)
    tester_headers = session_login(auth_client, db, tester, 'stage10-run-create-token')
    created = create_run(auth_client, target['id'], case.id, tester_headers)
    assert created.status_code == 201 and created.json()['status'] == 'DRAFT'
    run_id = created.json()['id']
    assert auth_client.post(f'/api/automated-runs/{run_id}/submit', headers=tester_headers).status_code == 200
    assert auth_client.post(f'/api/automated-runs/{run_id}/approve', headers=tester_headers).status_code == 403
    approver_headers = session_login(auth_client, db, approver, 'stage10-run-approve-token')
    assert auth_client.post(f'/api/automated-runs/{run_id}/approve', headers=approver_headers).status_code == 200
    assert auth_client.post('/api/execution-workers/heartbeat', json={'worker_key': 'stage10-worker'}, headers=approver_headers).status_code == 200
    assert auth_client.post(f'/api/automated-runs/{run_id}/queue', headers=approver_headers).status_code == 200
    executed = auth_client.post('/api/execution-workers/run-next', json={'worker_key': 'stage10-worker'}, headers=approver_headers)
    assert executed.status_code == 200 and executed.json()['status'] == 'PASSED'
    assert executed.json()['progress'] == '4/4'
    assert auth_client.get(f'/api/automated-runs/{run_id}/steps').json()[-1]['status'] == 'PASSED'
    artifacts = auth_client.get(f'/api/automated-runs/{run_id}/artifacts').json()
    assert {item['artifact_type'] for item in artifacts} >= {'SUMMARY', 'SCREENSHOT'}
    assert all('password' not in str(item).lower() and 'token' not in str(item).lower() for item in artifacts)
    assert db.query(ExecutionWorker).filter_by(worker_key='stage10-worker').one().status == 'IDLE'
    valid, total, invalid = verify_chain(db)
    assert valid and total > 0 and invalid is None
  finally:
    server.shutdown(); thread.join(timeout=5); server.server_close()


def test_stage10_policy_blocks_bad_targets_cases_actions_and_csrf(auth_client, db):
  server, thread, base_url = mock_target_url()
  try:
    tester, tester_headers, approver, approver_headers, target = approve_stage9_target(auth_client, db, base_url)
    target = approve_execution_target(auth_client, db, target['id'], tester, approver)
    tester_headers = session_login(auth_client, db, tester, 'stage10-policy-create-token')
    unapproved = create_approved_case(db, tester, approver, 'S10-DRAFT')
    unapproved.lifecycle_state = 'DRAFT'; db.commit()
    assert create_run(auth_client, target['id'], unapproved.id, tester_headers).status_code == 409
    external = create_approved_case(db, tester, approver, 'S10-EXT', [{'action': 'NAVIGATE', 'url': 'http://example.com'}])
    assert create_run(auth_client, target['id'], external.id, tester_headers).status_code == 422
    code = create_approved_case(db, tester, approver, 'S10-CODE', [{'action': 'FILL', 'selector': '#x', 'value': 'javascript:alert(1)'}])
    assert create_run(auth_client, target['id'], code.id, tester_headers).status_code == 422
    assert auth_client.post('/api/automated-runs', json={'name': 'No CSRF', 'target_id': target['id'], 'case_ids': []}).status_code == 403
    prod = db.get(ConnectionTarget, target['id'])
    prod.environment_type = 'PRODUCTION'; prod.execution_enabled = True; db.commit()
    assert create_run(auth_client, target['id'], create_approved_case(db, tester, approver, 'S10-PROD').id, tester_headers).status_code == 403
  finally:
    server.shutdown(); thread.join(timeout=5); server.server_close()


def test_queue_claim_cancellation_timeout_retry_and_origin_escape(auth_client, db):
  server, thread, base_url = mock_target_url()
  try:
    tester, tester_headers, approver, approver_headers, target = approve_stage9_target(auth_client, db, base_url)
    target = approve_execution_target(auth_client, db, target['id'], tester, approver)
    tester_headers = session_login(auth_client, db, tester, 'stage10-cancel-create-token')
    case = create_approved_case(db, tester, approver, 'S10-CANCEL')
    created = create_run(auth_client, target['id'], case.id, tester_headers).json()
    run_id = created['id']
    auth_client.post(f'/api/automated-runs/{run_id}/submit', headers=tester_headers)
    approver_headers = session_login(auth_client, db, approver, 'stage10-cancel-approve-token')
    auth_client.post(f'/api/automated-runs/{run_id}/approve', headers=approver_headers)
    auth_client.post('/api/execution-workers/heartbeat', json={'worker_key': 'stage10-worker'}, headers=approver_headers)
    auth_client.post(f'/api/automated-runs/{run_id}/queue', headers=approver_headers)
    assert db.query(ExecutionJob).filter_by(run_id=run_id, status='QUEUED').count() == 1
    tester_headers = session_login(auth_client, db, tester, 'stage10-cancel-token')
    cancelled = auth_client.post(f'/api/automated-runs/{run_id}/cancel', headers=tester_headers)
    assert cancelled.status_code == 200 and cancelled.json()['status'] == 'CANCELLED'

    fail_case = create_approved_case(db, tester, approver, 'S10-FAIL', [{'action': 'NAVIGATE', 'path': '/'}, {'action': 'ASSERT_TEXT', 'selector': '#ready', 'expected': 'Missing text'}])
    tester_headers = session_login(auth_client, db, tester, 'stage10-fail-create-token')
    failed = create_run(auth_client, target['id'], fail_case.id, tester_headers, 'Failing Run').json()
    fail_id = failed['id']
    auth_client.post(f'/api/automated-runs/{fail_id}/submit', headers=tester_headers)
    approver_headers = session_login(auth_client, db, approver, 'stage10-fail-approve-token')
    auth_client.post(f'/api/automated-runs/{fail_id}/approve', headers=approver_headers)
    auth_client.post('/api/execution-workers/heartbeat', json={'worker_key': 'stage10-worker'}, headers=approver_headers)
    auth_client.post(f'/api/automated-runs/{fail_id}/queue', headers=approver_headers)
    assert auth_client.post('/api/execution-workers/run-next', json={'worker_key': 'stage10-worker'}, headers=approver_headers).json()['status'] == 'FAILED'
    retried = auth_client.post(f'/api/automated-runs/{fail_id}/retry', headers=approver_headers)
    assert retried.status_code == 200 and retried.json()['status'] == 'QUEUED'
    assert auth_client.post(f'/api/automated-runs/{fail_id}/cancel', headers=approver_headers).status_code == 200

    escape_case = create_approved_case(db, tester, approver, 'S10-ESCAPE', [{'action': 'NAVIGATE', 'path': '/redirect'}])
    tester_headers = session_login(auth_client, db, tester, 'stage10-escape-create-token')
    escape = create_run(auth_client, target['id'], escape_case.id, tester_headers, 'Escape Run').json()
    escape_id = escape['id']
    auth_client.post(f'/api/automated-runs/{escape_id}/submit', headers=tester_headers)
    approver_headers = session_login(auth_client, db, approver, 'stage10-escape-approve-token')
    auth_client.post(f'/api/automated-runs/{escape_id}/approve', headers=approver_headers)
    auth_client.post('/api/execution-workers/heartbeat', json={'worker_key': 'stage10-worker'}, headers=approver_headers)
    auth_client.post(f'/api/automated-runs/{escape_id}/queue', headers=approver_headers)
    assert auth_client.post('/api/execution-workers/run-next', json={'worker_key': 'stage10-worker'}, headers=approver_headers).json()['status'] == 'BLOCKED'

    slow_case = create_approved_case(db, tester, approver, 'S10-SLOW', [{'action': 'NAVIGATE', 'path': '/slow'}])
    tester_headers = session_login(auth_client, db, tester, 'stage10-slow-create-token')
    slow = create_run(auth_client, target['id'], slow_case.id, tester_headers, 'Slow Run', timeout=5).json()
    slow_id = slow['id']
    auth_client.post(f'/api/automated-runs/{slow_id}/submit', headers=tester_headers)
    approver_headers = session_login(auth_client, db, approver, 'stage10-slow-approve-token')
    auth_client.post(f'/api/automated-runs/{slow_id}/approve', headers=approver_headers)
    auth_client.post('/api/execution-workers/heartbeat', json={'worker_key': 'stage10-worker'}, headers=approver_headers)
    auth_client.post(f'/api/automated-runs/{slow_id}/queue', headers=approver_headers)
    timed = auth_client.post('/api/execution-workers/run-next', json={'worker_key': 'stage10-worker'}, headers=approver_headers)
    assert timed.json()['status'] in {'TIMED_OUT', 'FAILED'}

    for artifact in db.query(ExecutionArtifact).all():
      assert '..' not in artifact.relative_path and not artifact.relative_path.startswith('/')
      assert artifact.sha256 and artifact.size_bytes > 0
    for event in db.execute(text('SELECT metadata_json FROM audit_events')).scalars():
      assert 'password' not in (event or '').lower()
      assert 'token' not in (event or '').lower()
      assert 'cookie' not in (event or '').lower()
  finally:
    server.shutdown(); thread.join(timeout=5); server.server_close()


def test_atomic_worker_claim_prevents_duplicate_claim(auth_client, db):
  server, thread, base_url = mock_target_url()
  try:
    tester, tester_headers, approver, approver_headers, target = approve_stage9_target(auth_client, db, base_url)
    target = approve_execution_target(auth_client, db, target['id'], tester, approver)
    case = create_approved_case(db, tester, approver, 'S10-ATOMIC-CLAIM')
    tester_headers = session_login(auth_client, db, tester, 'stage10-atomic-claim-create-token')
    created = create_run(auth_client, target['id'], case.id, tester_headers, 'Atomic Claim Run').json()
    run_id = created['id']
    auth_client.post(f'/api/automated-runs/{run_id}/submit', headers=tester_headers)
    approver_headers = session_login(auth_client, db, approver, 'stage10-atomic-claim-approve-token')
    auth_client.post(f'/api/automated-runs/{run_id}/approve', headers=approver_headers)
    assert auth_client.post('/api/execution-workers/heartbeat', json={'worker_key': 'stage10-claim-worker-a'}, headers=approver_headers).status_code == 200
    assert auth_client.post(f'/api/automated-runs/{run_id}/queue', headers=approver_headers).status_code == 200

    Session = sessionmaker(bind=db.get_bind(), autocommit=False, autoflush=False)
    first = Session()
    second = Session()
    try:
      claimed = [claim_next_job(first, 'stage10-claim-worker-a')]
      first.commit()
      claimed.append(claim_next_job(second, 'stage10-claim-worker-b'))
      second.commit()
      assert sum(job is not None for job in claimed) == 1
      db.expire_all()
      job = db.query(ExecutionJob).filter_by(run_id=run_id).one()
      assert job.status == 'RUNNING'
      assert job.lease_owner in {'stage10-claim-worker-a', 'stage10-claim-worker-b'}
      assert job.attempts == 1
    finally:
      first.close()
      second.close()
  finally:
    server.shutdown(); thread.join(timeout=5); server.server_close()


def test_cancelled_run_is_not_overwritten_by_stale_worker_completion(auth_client, db):
  from unittest.mock import patch

  server, thread, base_url = mock_target_url()
  try:
    tester, tester_headers, approver, approver_headers, target = approve_stage9_target(auth_client, db, base_url)
    target = approve_execution_target(auth_client, db, target['id'], tester, approver)
    case = create_approved_case(db, tester, approver, 'S10-STALE-CANCEL', [
      {'action': 'NAVIGATE', 'path': '/'},
      {'action': 'ASSERT_VISIBLE', 'selector': '#ready'},
    ])
    tester_headers = session_login(auth_client, db, tester, 'stage10-stale-cancel-create-token')
    created = create_run(auth_client, target['id'], case.id, tester_headers, 'Stale Completion Run').json()
    run_id = created['id']
    auth_client.post(f'/api/automated-runs/{run_id}/submit', headers=tester_headers)
    approver_headers = session_login(auth_client, db, approver, 'stage10-stale-cancel-approve-token')
    auth_client.post(f'/api/automated-runs/{run_id}/approve', headers=approver_headers)
    assert auth_client.post('/api/execution-workers/heartbeat', json={'worker_key': 'stage10-stale-worker'}, headers=approver_headers).status_code == 200
    assert auth_client.post(f'/api/automated-runs/{run_id}/queue', headers=approver_headers).status_code == 200

    Session = sessionmaker(bind=db.get_bind(), autocommit=False, autoflush=False)

    def cancel_during_browser(_db, _target, _run):
      cancelling = Session()
      try:
        cancelled = cancelling.get(AutomatedRun, run_id)
        cancelled.status = 'CANCELLED'
        cancelled.cancelled_by = tester.id
        cancelled.cancelled_at = datetime.utcnow()
        cancelled.completed_at = datetime.utcnow()
        for job in cancelling.query(ExecutionJob).filter_by(run_id=run_id):
          job.status = 'CANCELLED'
          job.lease_owner = None
          job.lease_expires_at = None
        cancelling.commit()
      finally:
        cancelling.close()
      return [
        {'execution_id': 1, 'status': 'PASSED', 'duration_ms': 1},
        {'execution_id': 2, 'status': 'PASSED', 'duration_ms': 1},
      ]

    with patch('app.services.automated_execution.run_playwright', side_effect=cancel_during_browser):
      result = execute_next_job(db, 'stage10-stale-worker')
      db.commit()

    db.expire_all()
    persisted = db.get(AutomatedRun, run_id)
    assert result.id == run_id
    assert persisted.status == 'CANCELLED'
    assert persisted.cancelled_by == tester.id
    assert db.query(ExecutionJob).filter_by(run_id=run_id).one().status == 'CANCELLED'
  finally:
    server.shutdown(); thread.join(timeout=5); server.server_close()


# ---------------------------------------------------------------------------
# Regression tests for the db.flush() fix (artifact id was None before patch)
# ---------------------------------------------------------------------------

def test_store_artifact_returns_non_null_id(db, tmp_path):
  """store_artifact() must return an ExecutionArtifact whose .id is a non-None
  integer immediately after the call, without requiring a separate commit.

  Before the fix: db.add(item); return item  → item.id was None.
  After the fix:  db.add(item); db.flush(); return item  → item.id is an int.
  """
  from unittest.mock import patch, PropertyMock
  import app.services.automated_execution as _svc

  artifact_dir = tmp_path / 'artifacts'
  artifact_dir.mkdir(parents=True, exist_ok=True)

  # Build a fake Settings whose data_root and artifact_root point at tmp_path
  # so store_artifact() can compute relative paths without touching production.
  class _FakeSettings:
    data_root = tmp_path
    artifact_root = artifact_dir
    execution_max_artifact_bytes_per_run = 10 * 1024 * 1024

  with patch.object(_svc, 'ARTIFACT_ROOT', artifact_dir), \
       patch.object(_svc, 'settings', _FakeSettings()):
    run = AutomatedRun(
      run_key='ARUN-TEST-FLUSH',
      name='flush regression run',
      target_id=0,
      target_version=1,
      target_origin='http://localhost',
      timeout_seconds=30,
      max_retries=0,
      dns_pinning_status='ENFORCED',
      runtime_secret_status='NOT_REQUIRED',
      created_by=0,
    )
    db.add(run)
    db.flush()  # give run a real id so storage-limit query works

    content = ONE_PIXEL_PNG
    artifact = store_artifact(db, run, None, None, 'SCREENSHOT', 'step-1.png', content, 'image/png')

    # Core assertion: id must be a non-None integer immediately after the call.
    assert artifact.id is not None, 'artifact.id is None — db.flush() patch missing'
    assert isinstance(artifact.id, int), f'artifact.id has unexpected type {type(artifact.id)}'
    assert artifact.id > 0

    # Metadata integrity — unchanged by the patch.
    assert artifact.artifact_type == 'SCREENSHOT'
    assert artifact.original_filename == 'step-1.png'
    assert artifact.mime_type == 'image/png'
    assert artifact.size_bytes == len(content)
    assert artifact.sha256 == hashlib.sha256(content).hexdigest()
    assert artifact.relative_path and '..' not in artifact.relative_path
    assert not artifact.relative_path.startswith('/')


def test_screenshot_step_records_numeric_evidence_id(auth_client, db):
  """End-to-end: a SCREENSHOT step must store evidence:<numeric_id> in
  safe_error_message, never evidence:None.

  This is the exact user-visible symptom fixed by the db.flush() patch.
  """
  import re
  server, thread, base_url = mock_target_url()
  try:
    tester, tester_headers, approver, approver_headers, target = approve_stage9_target(auth_client, db, base_url)
    target = approve_execution_target(auth_client, db, target['id'], tester, approver)

    # Case with a single SCREENSHOT step so we can isolate the evidence field.
    screenshot_only_case = create_approved_case(
      db, tester, approver, 'S10-SCREENSHOT-FLUSH',
      steps=[
        {'action': 'NAVIGATE', 'path': '/'},
        {'action': 'SCREENSHOT'},
      ]
    )
    tester_headers = session_login(auth_client, db, tester, 'stage10-screenshot-flush-create-token')
    created = create_run(auth_client, target['id'], screenshot_only_case.id, tester_headers, 'Screenshot Flush Regression Run')
    assert created.status_code == 201
    run_id = created.json()['id']

    auth_client.post(f'/api/automated-runs/{run_id}/submit', headers=tester_headers)
    approver_headers = session_login(auth_client, db, approver, 'stage10-screenshot-flush-approve-token')
    auth_client.post(f'/api/automated-runs/{run_id}/approve', headers=approver_headers)
    auth_client.post('/api/execution-workers/heartbeat', json={'worker_key': 'stage10-flush-worker'}, headers=approver_headers)
    auth_client.post(f'/api/automated-runs/{run_id}/queue', headers=approver_headers)

    executed = auth_client.post('/api/execution-workers/run-next', json={'worker_key': 'stage10-flush-worker'}, headers=approver_headers)
    assert executed.status_code == 200

    steps = auth_client.get(f'/api/automated-runs/{run_id}/steps').json()
    screenshot_steps = [s for s in steps if s.get('action_type') == 'SCREENSHOT']
    assert screenshot_steps, 'No SCREENSHOT step result found in the run'

    for step in screenshot_steps:
      msg = step.get('safe_error_message') or ''
      # Must match evidence:<positive integer>, never evidence:None.
      assert re.fullmatch(r'evidence:\d+', msg), (
        f'SCREENSHOT step safe_error_message was {msg!r} — expected evidence:<numeric_id>'
      )
      numeric_id = int(msg.split(':')[1])
      assert numeric_id > 0, f'Artifact id in evidence message is not positive: {numeric_id}'
  finally:
    server.shutdown(); thread.join(timeout=5); server.server_close()
