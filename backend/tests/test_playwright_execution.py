from pathlib import Path
import struct

from app.models.automated_execution import ExecutionArtifact
from app.services.automated_execution import artifact_path
from tests.test_stage10_automated_execution import (
  approve_execution_target,
  approve_stage9_target,
  create_approved_case,
  create_run,
  mock_target_url,
  operator,
  session_login,
)


def _queue_and_execute(client, db, target, case, tester, approver, name='Playwright fixture'):
  tester_headers = session_login(client, db, tester, f'{name}-tester')
  created = create_run(client, target['id'], case.id, tester_headers, name)
  assert created.status_code == 201, created.text
  run_id = created.json()['id']
  assert client.post(f'/api/automated-runs/{run_id}/submit', headers=tester_headers).status_code == 200
  approver_headers = session_login(client, db, approver, f'{name}-approver')
  assert client.post(f'/api/automated-runs/{run_id}/approve', headers=approver_headers).status_code == 200
  assert client.post('/api/execution-workers/heartbeat', json={'worker_key': name}, headers=approver_headers).status_code == 200
  assert client.post(f'/api/automated-runs/{run_id}/queue', headers=approver_headers).status_code == 200
  executed = client.post('/api/execution-workers/run-next', json={'worker_key': name}, headers=approver_headers)
  return run_id, executed, approver_headers


def _png_dimensions(content: bytes):
  assert content.startswith(b'\x89PNG\r\n\x1a\n')
  assert content[12:16] == b'IHDR'
  return struct.unpack('>II', content[16:24])


def test_real_playwright_fixture_actions_and_screenshot(auth_client, db):
  server, thread, base_url = mock_target_url()
  try:
    tester, _, approver, _, target = approve_stage9_target(auth_client, db, base_url)
    target = approve_execution_target(auth_client, db, target['id'], tester, approver)
    case = create_approved_case(db, tester, approver, 'PW-FIXTURE', [
      {'action': 'NAVIGATE', 'path': '/'},
      {'action': 'FILL', 'selector': '#fixture-input', 'value': 'Playwright'},
      {'action': 'CLICK', 'selector': '#fixture-submit'},
      {'action': 'ASSERT_VISIBLE', 'selector': '#fixture-result'},
      {'action': 'ASSERT_TEXT', 'selector': '#fixture-result', 'expected': 'Result: Playwright'},
      {'action': 'SCREENSHOT'},
    ])
    run_id, executed, headers = _queue_and_execute(auth_client, db, target, case, tester, approver)
    assert executed.status_code == 200 and executed.json()['status'] == 'PASSED'
    steps = auth_client.get(f'/api/automated-runs/{run_id}/steps', headers=headers).json()
    assert [step['status'] for step in steps] == ['PASSED'] * 6
    # runner auto-captures evidence after every step; expect at least one SCREENSHOT artifact
    artifacts = db.query(ExecutionArtifact).filter_by(run_id=run_id, artifact_type='SCREENSHOT').order_by(ExecutionArtifact.id).all()
    assert len(artifacts) >= 1
    artifact = artifacts[-1]
    width, height = _png_dimensions(Path(artifact_path(artifact)).read_bytes())
    assert width > 1 and height > 1
  finally:
    server.shutdown(); thread.join(timeout=5); server.server_close()


def test_playwright_negative_actions_and_origin_policy(auth_client, db):
  server, thread, base_url = mock_target_url()
  try:
    tester, _, approver, _, target = approve_stage9_target(auth_client, db, base_url)
    target = approve_execution_target(auth_client, db, target['id'], tester, approver)
    headers = session_login(auth_client, db, tester, 'pw-negative-create')
    missing_locator = create_approved_case(db, tester, approver, 'PW-MISSING', [{'action': 'FILL', 'value': 'x'}])
    assert create_run(auth_client, target['id'], missing_locator.id, headers).status_code == 422

    wrong_text = create_approved_case(db, tester, approver, 'PW-WRONG', [
      {'action': 'NAVIGATE', 'path': '/'},
      {'action': 'ASSERT_TEXT', 'selector': '#fixture-result', 'expected': 'not present'},
    ])
    run_id, executed, review_headers = _queue_and_execute(auth_client, db, target, wrong_text, tester, approver, 'pw-wrong')
    assert executed.status_code == 200 and executed.json()['status'] == 'FAILED'
    step = auth_client.get(f'/api/automated-runs/{run_id}/steps', headers=review_headers).json()[-1]
    assert step['status'] == 'FAILED'

    escape = create_approved_case(db, tester, approver, 'PW-ESCAPE', [{'action': 'NAVIGATE', 'path': '/redirect'}])
    run_id, executed, review_headers = _queue_and_execute(auth_client, db, target, escape, tester, approver, 'pw-escape')
    assert executed.status_code == 200 and executed.json()['status'] == 'BLOCKED'
    step = auth_client.get(f'/api/automated-runs/{run_id}/steps', headers=review_headers).json()[-1]
    assert step['status'] == 'BLOCKED'
  finally:
    server.shutdown(); thread.join(timeout=5); server.server_close()
