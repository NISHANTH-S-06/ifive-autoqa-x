from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import threading

import pytest
from sqlalchemy import text

from app.models.connection_target import ConnectionCheck, ConnectionTargetVersion
from app.models.operator import Operator
from app.models.operator_session import OperatorSession
from app.models.operator_session import OperatorSession
from app.services.audit_service import verify_chain
from app.services.password_service import hash_password, hash_secret
from app.services.target_policy import normalize_url, resolve_host

PASSWORD_HASH = hash_password('Stage9!Fixture987')


def operator(db, username: str, role: str = 'VIEWER', active: bool = True, must_change: bool = False):
  item = Operator(username=username, display_name=username.title(), password_hash=PASSWORD_HASH, role=role, is_active=active, must_change_password=must_change)
  db.add(item); db.commit(); db.refresh(item); return item


def session_login(client, db, item, token: str, csrf: str = 'stage9-csrf'):
  session = OperatorSession(operator_id=item.id, token_hash=hash_secret(token), csrf_hash=hash_secret(csrf), created_at=datetime.utcnow(), expires_at=datetime.utcnow() + timedelta(hours=1), last_seen_at=datetime.utcnow(), password_version_at_login=item.password_version)
  db.add(session); db.commit(); client.cookies.clear(); client.cookies.set('autoqa_session', token); return {'X-CSRF-Token': csrf}


class MockHandler(BaseHTTPRequestHandler):
  seen_headers = []

  def log_message(self, *_):
    return

  def _common(self, status=200, body=b'ok'):
    MockHandler.seen_headers.append(dict(self.headers))
    self.send_response(status)
    self.send_header('Content-Type', 'text/plain')
    self.send_header('Set-Cookie', 'unsafe=session')
    self.send_header('X-Visible', 'safe')
    self.end_headers()
    if self.command == 'GET':
      self.wfile.write(body)

  def do_HEAD(self):
    if self.path == '/redirect':
      self.send_response(302); self.send_header('Location', 'http://example.com/unsafe'); self.send_header('Set-Cookie', 'unsafe=session'); self.end_headers(); return
    self._common()

  def do_GET(self):
    if self.path == '/large':
      self._common(body=b'a' * 70000); return
    if self.path == '/error':
      self._common(status=503, body=b'fail'); return
    self._common(body=b'response body must not persist')


@pytest.fixture
def mock_target():
  server = ThreadingHTTPServer(('127.0.0.1', 0), MockHandler)
  thread = threading.Thread(target=server.serve_forever, daemon=True)
  thread.start()
  try:
    yield f'http://127.0.0.1:{server.server_port}'
  finally:
    server.shutdown(); thread.join(timeout=5); server.server_close()


def target_payload(base_url: str, key='S9-LOCAL'):
  return {
    'target_key': key,
    'name': 'Stage 9 Local Mock',
    'environment_type': 'LOCAL',
    'base_url': base_url,
    'allowed_probe_paths': ['/', '/health', '/redirect', '/large', '/error', '/'],
    'tls_required': False,
    'tls_verify': True,
    'connection_timeout_seconds': 3,
  }


def approve_target(client, db, mock_target):
  tester = operator(db, 'stage9-tester', 'TESTER')
  tester_headers = session_login(client, db, tester, 'stage9-tester-token')
  created = client.post('/api/connection-targets', json=target_payload(mock_target), headers=tester_headers)
  assert created.status_code == 201
  assert created.json()['allowed_probe_paths'].count('/') == 1
  target_id = created.json()['id']
  assert client.post(f'/api/connection-targets/{target_id}/checks', json={'method': 'HEAD', 'probe_path': '/'}, headers=tester_headers).status_code == 403
  assert client.post(f'/api/connection-targets/{target_id}/submit', headers=tester_headers).status_code == 200
  assert client.post(f'/api/connection-targets/{target_id}/approve', headers=tester_headers).status_code in {400, 403}
  approver = operator(db, 'stage9-approver', 'APPROVER')
  approver_headers = session_login(client, db, approver, 'stage9-approver-token')
  approved = client.post(f'/api/connection-targets/{target_id}/approve', headers=approver_headers)
  assert approved.status_code == 200
  assert approved.json()['lifecycle_state'] == 'APPROVED' and approved.json()['enabled'] is True
  return tester, tester_headers, approver, approver_headers, approved.json()


def test_target_registry_lifecycle_rbac_and_versions(auth_client, db, mock_target):
  viewer = operator(db, 'stage9-viewer')
  viewer_headers = session_login(auth_client, db, viewer, 'stage9-viewer-token')
  assert auth_client.post('/api/connection-targets', json=target_payload(mock_target), headers=viewer_headers).status_code == 403
  tester, tester_headers, _, _, target = approve_target(auth_client, db, mock_target)
  tester_headers = session_login(auth_client, db, tester, 'stage9-tester-token-return')
  duplicate = auth_client.post('/api/connection-targets', json=target_payload(mock_target), headers=tester_headers)
  assert duplicate.status_code == 409
  versions = auth_client.get(f"/api/connection-targets/{target['id']}/versions").json()
  assert len(versions) >= 3 and versions[-1]['source_state'] == 'APPROVED'
  assert 'password' not in versions[-1]['snapshot_json'].lower()
  with pytest.raises(Exception):
    db.execute(text("UPDATE connection_target_versions SET change_summary='tamper' WHERE id=:id"), {'id': versions[0]['id']}); db.commit()
  db.rollback()
  with pytest.raises(Exception):
    db.execute(text('DELETE FROM connection_target_versions WHERE id=:id'), {'id': versions[0]['id']}); db.commit()
  db.rollback()
  admin = operator(db, 'stage9-admin', 'ADMIN')
  admin_headers = session_login(auth_client, db, admin, 'stage9-admin-token')
  disabled = auth_client.post(f"/api/connection-targets/{target['id']}/disable", headers=admin_headers)
  assert disabled.status_code == 200 and disabled.json()['lifecycle_state'] == 'DISABLED'
  assert auth_client.post(f"/api/connection-targets/{target['id']}/checks", json={'method': 'HEAD', 'probe_path': '/'}, headers=admin_headers).status_code == 409
  assert auth_client.post(f"/api/connection-targets/{target['id']}/archive", headers=admin_headers).json()['lifecycle_state'] == 'ARCHIVED'
  assert db.query(ConnectionTargetVersion).count() >= 5


def test_url_probe_and_ssrf_policy(auth_client, db, mock_target):
  tester = operator(db, 'stage9-policy-tester', 'TESTER')
  headers = session_login(auth_client, db, tester, 'stage9-policy-token')
  invalid_urls = ['file:///etc/passwd', 'ftp://example.test', 'javascript:alert(1)', 'data:text/plain,x', '//example.test', 'http://user:pass@example.test', 'http://127.0.0.1/#frag', 'http://0x7f000001/']
  for index, url in enumerate(invalid_urls):
    assert auth_client.post('/api/connection-targets', json=target_payload(url, f'S9-BAD-{index}'), headers=headers).status_code in {403, 422}
  assert auth_client.post('/api/connection-targets', json={**target_payload(mock_target, 'S9-PROD'), 'environment_type': 'PRODUCTION'}, headers=headers).status_code == 403
  assert auth_client.post('/api/connection-targets', json={**target_payload(mock_target, 'S9-TRAV'), 'allowed_probe_paths': ['/../admin']}, headers=headers).status_code == 422
  assert auth_client.post('/api/connection-targets', json={**target_payload(mock_target, 'S9-MANY'), 'allowed_probe_paths': [f'/p{i}' for i in range(11)]}, headers=headers).status_code == 422
  assert normalize_url('HTTP://LOCALHOST:80').origin == 'http://localhost'
  with pytest.raises(Exception):
    resolve_host('169.254.169.254', 80, 'LOCAL')
  with pytest.raises(Exception):
    resolve_host('127.0.0.1', 80, 'QA')


def test_connectivity_checks_are_read_only_and_sanitized(auth_client, db, mock_target):
  _, _, _, approver_headers, target = approve_target(auth_client, db, mock_target)
  head = auth_client.post(f"/api/connection-targets/{target['id']}/checks", json={'method': 'HEAD', 'probe_path': '/'}, headers=approver_headers)
  assert head.status_code == 201 and head.json()['status'] == 'REACHABLE'
  assert 'set-cookie' not in {key.lower() for key in head.json()['response_headers']}
  get = auth_client.post(f"/api/connection-targets/{target['id']}/checks", json={'method': 'GET', 'probe_path': '/large'}, headers=approver_headers)
  assert get.status_code == 201 and get.json()['response_size_bytes'] == 65536
  redirect = auth_client.post(f"/api/connection-targets/{target['id']}/checks", json={'method': 'HEAD', 'probe_path': '/redirect'}, headers=approver_headers)
  assert redirect.status_code == 201 and redirect.json()['status'] == 'REDIRECT_BLOCKED'
  assert auth_client.post(f"/api/connection-targets/{target['id']}/checks", json={'method': 'POST', 'probe_path': '/'}, headers=approver_headers).status_code == 422
  assert auth_client.post(f"/api/connection-targets/{target['id']}/checks", json={'method': 'GET', 'probe_path': '/not-approved'}, headers=approver_headers).status_code == 201
  stored = db.query(ConnectionCheck).filter_by(id=get.json()['id']).one()
  assert 'response body must not persist' not in str(stored.__dict__).lower()
  assert all('authorization' not in {key.lower() for key in item} for item in MockHandler.seen_headers)
  assert any(item.get('User-Agent') == 'iFive-AutoQA-Stage9-ConnectionCheck/1.0' for item in MockHandler.seen_headers)
  history = auth_client.get(f"/api/connection-targets/{target['id']}/checks").json()
  assert len(history) >= 3


def test_credential_metadata_and_security_regressions(auth_client, db, mock_target):
  tester, tester_headers, _, approver_headers, target = approve_target(auth_client, db, mock_target)
  tester_headers = session_login(auth_client, db, tester, 'stage9-profile-token')
  created = auth_client.post(f"/api/connection-targets/{target['id']}/credential-profiles", json={'profile_name': 'Prompt later', 'username_hint': 'qa-user', 'secret_source': 'PROMPT_AT_USE'}, headers=tester_headers)
  assert created.status_code == 201
  assert 'password' not in str(created.json()).lower()
  secret_payload = {'profile_name': 'Bad', 'secret_source': 'NONE', 'password': 'Never!Store123'}
  assert auth_client.post(f"/api/connection-targets/{target['id']}/credential-profiles", json=secret_payload, headers=tester_headers).status_code == 422
  assert auth_client.post(f"/api/connection-targets/{target['id']}/credential-profiles", json={'profile_name': 'Token', 'token': 'abc'}, headers=tester_headers).status_code == 422
  changing = operator(db, 'stage9-must-change', 'TESTER', must_change=True)
  session_login(auth_client, db, changing, 'stage9-must-change-token')
  assert auth_client.get('/api/connection-targets').status_code == 403
  disabled = operator(db, 'stage9-disabled', 'TESTER', active=False)
  session_login(auth_client, db, disabled, 'stage9-disabled-token')
  assert auth_client.get('/api/connection-targets').status_code == 403
  session_login(auth_client, db, operator(db, 'stage9-csrf-approver', 'APPROVER'), 'stage9-csrf-token')
  assert auth_client.post(f"/api/connection-targets/{target['id']}/checks", json={'method': 'GET', 'probe_path': '/'}).status_code == 403
  session_login(auth_client, db, tester, 'stage9-version-token')
  session = db.query(OperatorSession).filter_by(token_hash=hash_secret('stage9-version-token')).one()
  tester.password_version += 1; db.commit()
  assert auth_client.get('/api/connection-targets').status_code == 401
  assert session.password_version_at_login != tester.password_version
  assert db.query(Operator).filter_by(role='ADMIN', username='default-admin').count() == 0
  valid, total, invalid = verify_chain(db)
  assert valid and total > 0 and invalid is None
  for event in db.execute(text('SELECT metadata_json FROM audit_events')).scalars():
    assert 'password' not in (event or '').lower()
    assert 'token' not in (event or '').lower()
    assert 'cookie' not in (event or '').lower()
