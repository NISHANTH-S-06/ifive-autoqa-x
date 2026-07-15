import socket

from app.models.automated_execution import ExecutionArtifact
from app.models.connection_target import ConnectionTarget
from app.services.audit_service import verify_chain
from app.services.pinned_http import PinnedTargetSession
from tests.test_stage10_automated_execution import (
  approve_execution_target,
  approve_stage9_target,
  create_approved_case,
  create_run,
  mock_target_url,
  operator,
  session_login,
)


def test_stage11_readiness_admin_pending_and_real_target_pending(auth_client, db):
  tester = operator(db, 'stage11-readiness-user', 'TESTER')
  headers = session_login(auth_client, db, tester, 'stage11-readiness-token')
  response = auth_client.get('/api/automated-runs/readiness', headers=headers)
  assert response.status_code == 200
  payload = response.json()
  assert payload['active_admin_count'] == 0
  assert payload['admin_prerequisite_met'] is False
  assert payload['real_target_authorized'] is False
  assert payload['dns_pinning_status'] == 'ENFORCED'
  assert payload['blocked_risk_levels'] == ['MUTATING', 'DESTRUCTIVE']


def test_stage11_worker_preflight_and_read_only_execution(auth_client, db):
  server, thread, base_url = mock_target_url()
  try:
    tester, tester_headers, approver, approver_headers, target = approve_stage9_target(auth_client, db, base_url)
    target = approve_execution_target(auth_client, db, target['id'], tester, approver)
    case = create_approved_case(db, tester, approver, 'S11-READ')
    tester_headers = session_login(auth_client, db, tester, 'stage11-read-create')
    run = create_run(auth_client, target['id'], case.id, tester_headers, 'Stage 11 Read Only').json()
    run_id = run['id']
    assert run['risk_level'] == 'READ_ONLY'
    auth_client.post(f'/api/automated-runs/{run_id}/submit', headers=tester_headers)
    approver_headers = session_login(auth_client, db, approver, 'stage11-read-approve')
    assert auth_client.post(f'/api/automated-runs/{run_id}/approve', headers=approver_headers).status_code == 200
    blocked_queue = auth_client.post(f'/api/automated-runs/{run_id}/queue', headers=approver_headers)
    assert blocked_queue.status_code == 409 and 'preflight' in blocked_queue.json()['detail'].lower()
    assert auth_client.post('/api/execution-workers/heartbeat', json={'worker_key': 'stage11-worker'}, headers=approver_headers).status_code == 200
    preflight = auth_client.get(f'/api/automated-runs/{run_id}/preflight', headers=approver_headers).json()
    assert preflight['status'] == 'PASS'
    assert preflight['checks']['worker_available'] is True
    assert preflight['checks']['dns_pinning_enforced'] is True
    assert auth_client.post(f'/api/automated-runs/{run_id}/queue', headers=approver_headers).status_code == 200
    executed = auth_client.post('/api/execution-workers/run-next', json={'worker_key': 'stage11-worker'}, headers=approver_headers)
    assert executed.status_code == 200 and executed.json()['status'] == 'PASSED'
    assert executed.json()['dns_pinning_status'] == 'ENFORCED'
    for artifact in db.query(ExecutionArtifact).all():
      assert 'password' not in artifact.original_filename.lower()
      assert 'token' not in artifact.original_filename.lower()
    valid, _, invalid = verify_chain(db)
    assert valid and invalid is None
  finally:
    server.shutdown(); thread.join(timeout=5); server.server_close()


def test_stage11_validated_pin_and_dns_rebinding_blocked(auth_client, db, monkeypatch):
  server, thread, base_url = mock_target_url()
  try:
    tester, tester_headers, approver, approver_headers, target_payload = approve_stage9_target(auth_client, db, base_url)
    target_payload = approve_execution_target(auth_client, db, target_payload['id'], tester, approver)
    target = db.get(ConnectionTarget, target_payload['id'])
    session = PinnedTargetSession(target, 'stage11-test', 3, 4096)
    assert session.pinned_address == '127.0.0.1'
    response = session.request('GET', '/')
    assert response.status_code == 200
    assert b'Stage10 Mock' in response.body

    original_getaddrinfo = socket.getaddrinfo

    def rebound(host, port, *args, **kwargs):
      if host == target.normalized_host and port == target.normalized_port:
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, '', ('10.0.0.1', port))]
      return original_getaddrinfo(host, port, *args, **kwargs)

    monkeypatch.setattr(socket, 'getaddrinfo', rebound)
    try:
      session.assert_current_resolution()
      assert False, 'DNS rebinding should be blocked'
    except Exception as exc:
      assert 'blocked' in str(exc).lower()
  finally:
    server.shutdown(); thread.join(timeout=5); server.server_close()


def test_stage11_runtime_secret_and_dangerous_actions_blocked(auth_client, db):
  server, thread, base_url = mock_target_url()
  try:
    tester, tester_headers, approver, approver_headers, target = approve_stage9_target(auth_client, db, base_url)
    target = approve_execution_target(auth_client, db, target['id'], tester, approver)
    dangerous = create_approved_case(db, tester, approver, 'S11-DEL', [{'action': 'CLICK', 'selector': '#delete', 'risk_level': 'DESTRUCTIVE'}])
    mutating = create_approved_case(db, tester, approver, 'S11-POST', [{'action': 'CLICK', 'selector': '#post'}])
    safe = create_approved_case(db, tester, approver, 'S11-SECRET', [{'action': 'NAVIGATE', 'path': '/'}])
    tester_headers = session_login(auth_client, db, tester, 'stage11-policy-create')
    assert create_run(auth_client, target['id'], dangerous.id, tester_headers, 'Destructive').status_code == 422
    assert create_run(auth_client, target['id'], mutating.id, tester_headers, 'Mutating Wording').status_code == 422
    secret = auth_client.post('/api/automated-runs', json={'name': 'Secret Login Pending', 'target_id': target['id'], 'case_ids': [safe.id], 'timeout_seconds': 30, 'max_retries': 0, 'runtime_secret_required': True}, headers=tester_headers)
    assert secret.status_code == 409
    assert 'Runtime-secret input is not available' in secret.json()['detail']
  finally:
    server.shutdown(); thread.join(timeout=5); server.server_close()
