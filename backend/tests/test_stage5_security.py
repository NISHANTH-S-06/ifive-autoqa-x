from datetime import datetime, timedelta

import pytest
from sqlalchemy import text

from app.models.audit_event import AuditEvent
from app.models.operator import Operator
from app.models.operator_session import OperatorSession
from app.models.project import Project
from app.models.test_run import TestRun as RunModel
from app.services.audit_service import append_event, verify_chain
from app.services.password_service import hash_password, hash_secret

PASSWORD = 'Strong!Local9876'
PASSWORD_HASH = hash_password(PASSWORD)


def operator(db, username, role='VIEWER', active=True):
  item = Operator(username=username, display_name=username.title(), password_hash=PASSWORD_HASH, role=role, is_active=active)
  db.add(item); db.commit(); db.refresh(item); return item


def session_login(client, db, item, token='session-token', csrf='csrf-value', expires=None, revoked=None):
  session = OperatorSession(operator_id=item.id, token_hash=hash_secret(token), csrf_hash=hash_secret(csrf), created_at=datetime.utcnow(), expires_at=expires or datetime.utcnow() + timedelta(hours=1), last_seen_at=datetime.utcnow(), revoked_at=revoked)
  db.add(session); db.commit(); client.cookies.set('autoqa_session', token); return {'X-CSRF-Token': csrf}, session


def test_login_success_session_cookie_and_safe_profile(auth_client, db):
  item = operator(db, 'login-user')
  response = auth_client.post('/api/auth/login', json={'username': 'LOGIN-USER', 'password': PASSWORD})
  assert response.status_code == 200
  assert response.json()['operator']['username'] == 'login-user'
  assert 'password_hash' not in str(response.json()).lower()
  assert response.cookies.get('autoqa_session')
  assert db.query(OperatorSession).one().token_hash != response.cookies.get('autoqa_session')
  assert auth_client.get('/api/auth/me').status_code == 200
  assert db.query(AuditEvent).filter_by(action='LOGIN_SUCCESS').count() == 1


def test_invalid_login_inactive_and_lockout(auth_client, db):
  item = operator(db, 'locked-user')
  assert auth_client.post('/api/auth/login', json={'username': 'missing-user', 'password': PASSWORD}).json()['detail'] == 'Invalid username or password.'
  assert auth_client.post('/api/auth/login', json={'username': item.username, 'password': 'wrong'}).json()['detail'] == 'Invalid username or password.'
  for _ in range(4): auth_client.post('/api/auth/login', json={'username': item.username, 'password': 'wrong'})
  db.refresh(item); assert item.locked_until is not None
  assert auth_client.post('/api/auth/login', json={'username': item.username, 'password': PASSWORD}).status_code == 401
  item.locked_until = datetime.utcnow() - timedelta(seconds=1); item.failed_login_count = 0; db.commit()
  assert auth_client.post('/api/auth/login', json={'username': item.username, 'password': PASSWORD}).status_code == 200
  inactive = operator(db, 'inactive-user', active=False)
  assert auth_client.post('/api/auth/login', json={'username': inactive.username, 'password': PASSWORD}).status_code == 401


def test_expired_revoked_logout_and_csrf(auth_client, db):
  expired = operator(db, 'expired-user'); session_login(auth_client, db, expired, expires=datetime.utcnow() - timedelta(seconds=1))
  assert auth_client.get('/api/auth/me').status_code == 401
  active = operator(db, 'active-user'); headers, session = session_login(auth_client, db, active, token='active-token')
  assert auth_client.post('/api/auth/logout').status_code == 403
  assert auth_client.post('/api/auth/logout', headers=headers).status_code == 200
  db.refresh(session); assert session.revoked_at is not None
  assert auth_client.get('/api/auth/me').status_code == 401


def test_rbac_viewer_tester_and_approver(auth_client, db):
  project = Project(name='RBAC AutoQA', product_code='AUTOQA', environment='local', is_active=True); db.add(project); db.commit()
  viewer = operator(db, 'viewer-user'); headers, _ = session_login(auth_client, db, viewer)
  assert auth_client.get('/api/projects').status_code == 200
  payload = {'project_id': project.id, 'suite_name': 'dashboard-smoke', 'browser': 'chromium', 'environment': 'local'}
  assert auth_client.post('/api/test-runs', json=payload, headers=headers).status_code == 403
  tester = operator(db, 'tester-user', 'TESTER'); headers, _ = session_login(auth_client, db, tester, 'tester-token', 'tester-csrf')
  created = auth_client.post('/api/test-runs', json=payload, headers=headers)
  assert created.status_code == 201 and created.json()['created_by_operator_id'] == tester.id
  assert auth_client.post(f"/api/test-runs/{created.json()['id']}/approve", json={'confirmation': 'APPROVE LOCAL TEST EXECUTION'}, headers=headers).status_code == 403
  approver = operator(db, 'approver-user', 'APPROVER'); headers, _ = session_login(auth_client, db, approver, 'approver-token', 'approver-csrf')
  approved = auth_client.post(f"/api/test-runs/{created.json()['id']}/approve", json={'confirmation': 'APPROVE LOCAL TEST EXECUTION'}, headers=headers)
  assert approved.status_code == 200 and approved.json()['approved_by_operator_id'] == approver.id


def test_creator_approver_separation_even_for_admin(auth_client, db):
  admin = operator(db, 'creator-admin', 'ADMIN'); headers, _ = session_login(auth_client, db, admin)
  project = Project(name='Separation AutoQA', product_code='AUTOQA', environment='local', is_active=True); db.add(project); db.commit()
  run = RunModel(run_code='RUN-SEPARATION', project_id=project.id, created_by_operator_id=admin.id, suite_name='dashboard-smoke', browser='chromium', environment='local', status='QUEUED'); db.add(run); db.commit()
  response = auth_client.post(f'/api/test-runs/{run.id}/approve', json={'confirmation': 'APPROVE LOCAL TEST EXECUTION'}, headers=headers)
  assert response.json()['detail'] == 'Run creators cannot approve their own test runs.'


def test_operator_management_and_final_admin_protection(auth_client, db):
  admin = operator(db, 'admin-user', 'ADMIN'); headers, _ = session_login(auth_client, db, admin)
  payload = {'username': 'new.tester', 'display_name': 'New Tester', 'role': 'TESTER', 'temporary_password': 'Another!Strong987'}
  created = auth_client.post('/api/operators', json=payload, headers=headers)
  assert created.status_code == 201 and 'password_hash' not in str(created.json()).lower()
  target = created.json()['id']
  assert auth_client.patch(f'/api/operators/{target}/role', json={'role': 'APPROVER'}, headers=headers).json()['role'] == 'APPROVER'
  assert auth_client.patch(f'/api/operators/{target}/status', json={'is_active': False}, headers=headers).json()['is_active'] is False
  assert auth_client.patch(f'/api/operators/{admin.id}/status', json={'is_active': False}, headers=headers).status_code == 400
  assert auth_client.patch(f'/api/operators/{admin.id}/role', json={'role': 'VIEWER'}, headers=headers).status_code == 400
  viewer = operator(db, 'management-viewer'); viewer_headers, _ = session_login(auth_client, db, viewer, 'viewer2-token', 'viewer2-csrf')
  assert auth_client.get('/api/operators').status_code == 403
  assert auth_client.post('/api/operators', json=payload, headers=viewer_headers).status_code == 403


def test_audit_append_only_chain_redaction_filters_and_permissions(auth_client, db):
  admin = operator(db, 'audit-admin', 'ADMIN'); headers, _ = session_login(auth_client, db, admin)
  append_event(db, 'SAFE_EVENT', operator_id=admin.id, resource_type='TEST', resource_id='1', metadata={'password': 'never-store', 'safe': 'visible'}); db.commit()
  event = db.query(AuditEvent).filter_by(action='SAFE_EVENT').one()
  assert 'never-store' not in event.metadata_json and '[REDACTED]' in event.metadata_json
  valid, total, invalid = verify_chain(db); assert valid and total >= 1 and invalid is None
  response = auth_client.get('/api/audit/events?action=SAFE_EVENT&limit=1')
  assert response.status_code == 200 and response.json()[0]['action'] == 'SAFE_EVENT'
  verification = auth_client.get('/api/audit/verify').json(); assert verification['valid'] is True
  with pytest.raises(Exception): db.execute(text("UPDATE audit_events SET action='EDITED' WHERE id=:id"), {'id': event.id}); db.commit()
  db.rollback()
  with pytest.raises(Exception): db.execute(text('DELETE FROM audit_events WHERE id=:id'), {'id': event.id}); db.commit()
  db.rollback()
  viewer = operator(db, 'audit-viewer'); session_login(auth_client, db, viewer, 'audit-view-token', 'audit-view-csrf')
  assert auth_client.get('/api/audit/verify').status_code == 403


def test_tampered_chain_detection(db):
  append_event(db, 'ONE', actor_type='SYSTEM'); append_event(db, 'TWO', actor_type='SYSTEM'); db.commit()
  db.execute(text('DROP TRIGGER audit_events_no_update')); db.execute(text("UPDATE audit_events SET action='TAMPERED' WHERE id=1")); db.commit()
  valid, _, invalid = verify_chain(db); assert valid is False and invalid == 1
