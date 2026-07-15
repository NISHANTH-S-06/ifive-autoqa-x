from datetime import datetime, timedelta

import pytest
from sqlalchemy import text

from app.models.audit_event import AuditEvent
from app.models.operator import Operator
from app.models.operator_session import OperatorSession
from app.models.password_history import PasswordHistory
from app.services.audit_service import verify_chain
from app.services.password_service import hash_password, hash_secret, validate_password

TEMP_PASSWORD = 'Temp!Strong9876'
NEW_PASSWORD = 'Fresh!Strong9876'
NEXT_PASSWORD = 'Next!Strong9876'
ADMIN_PASSWORD = 'Admin!Strong9876'


def add_operator(db, username='stage6-user', role='TESTER', password=TEMP_PASSWORD, must_change=False):
  operator = Operator(username=username, display_name=username.replace('-', ' ').title(), password_hash=hash_password(password), role=role, is_active=True, must_change_password=must_change, password_version=1)
  db.add(operator); db.commit(); db.refresh(operator); return operator


def login(client, username, password):
  response = client.post('/api/auth/login', json={'username': username, 'password': password})
  assert response.status_code == 200
  return {'X-CSRF-Token': response.json()['csrf_token']}


def test_stage6_password_policy_rules():
  validate_password('Valid!Strong9876', 'policy-user', 'Policy User')
  cases = [
    'Short!1',
    'missinguppercase!1',
    'MISSINGLOWERCASE!1',
    'MissingNumber!',
    'MissingSpecial987',
    'PolicyUser!9876',
    'Password123!456',
    'aaaaaaaaaaaa',
    '123456789012',
  ]
  for password in cases:
    with pytest.raises(ValueError):
      validate_password(password, 'policy-user', 'Policy User')


def test_required_password_change_blocks_resources_and_then_allows_access(auth_client, db):
  operator = add_operator(db, must_change=True)
  headers = login(auth_client, operator.username, TEMP_PASSWORD)
  assert auth_client.get('/api/dashboard/summary').status_code == 403
  assert auth_client.post('/api/auth/change-required-password', json={'current_password': 'wrong', 'new_password': NEW_PASSWORD, 'confirm_password': NEW_PASSWORD}, headers=headers).json()['detail'] == 'Current password is incorrect.'
  assert auth_client.post('/api/auth/change-required-password', json={'current_password': TEMP_PASSWORD, 'new_password': NEW_PASSWORD, 'confirm_password': 'Mismatch!9876'}, headers=headers).status_code == 400
  changed = auth_client.post('/api/auth/change-required-password', json={'current_password': TEMP_PASSWORD, 'new_password': NEW_PASSWORD, 'confirm_password': NEW_PASSWORD}, headers=headers)
  assert changed.status_code == 200
  db.refresh(operator)
  assert operator.must_change_password is False and operator.password_version == 2
  assert db.query(PasswordHistory).filter_by(operator_id=operator.id, change_reason='FIRST_LOGIN_CHANGE').count() == 1
  assert auth_client.get('/api/dashboard/summary').status_code == 200
  assert auth_client.post('/api/auth/login', json={'username': operator.username, 'password': TEMP_PASSWORD}).status_code == 401


def test_self_service_change_rejects_reuse_and_revokes_other_sessions(auth_client, db):
  operator = add_operator(db, must_change=False)
  first_headers = login(auth_client, operator.username, TEMP_PASSWORD)
  first_session = db.query(OperatorSession).filter_by(operator_id=operator.id).order_by(OperatorSession.id.desc()).first()
  auth_client.cookies.clear()
  second_headers = login(auth_client, operator.username, TEMP_PASSWORD)
  second_session = db.query(OperatorSession).filter_by(operator_id=operator.id).order_by(OperatorSession.id.desc()).first()
  reused = auth_client.post('/api/auth/change-password', json={'current_password': TEMP_PASSWORD, 'new_password': TEMP_PASSWORD, 'confirm_password': TEMP_PASSWORD}, headers=second_headers)
  assert reused.status_code == 400
  changed = auth_client.post('/api/auth/change-password', json={'current_password': TEMP_PASSWORD, 'new_password': NEW_PASSWORD, 'confirm_password': NEW_PASSWORD}, headers=second_headers)
  assert changed.status_code == 200
  db.refresh(operator); db.refresh(first_session); db.refresh(second_session)
  assert operator.password_version == 2
  assert first_session.revoked_at is not None
  assert second_session.revoked_at is None and second_session.password_version_at_login == 2
  auth_client.cookies.set('autoqa_session', 'unused-old-token')
  assert first_headers['X-CSRF-Token']


def test_admin_reset_forces_change_and_revokes_target_sessions(auth_client, db):
  admin = add_operator(db, 'stage6-admin', 'ADMIN', ADMIN_PASSWORD)
  target = add_operator(db, 'stage6-target', 'TESTER', TEMP_PASSWORD)
  target_headers = login(auth_client, target.username, TEMP_PASSWORD)
  assert auth_client.get('/api/auth/me').status_code == 200
  auth_client.cookies.clear()
  admin_headers = login(auth_client, admin.username, ADMIN_PASSWORD)
  assert auth_client.post(f'/api/operators/{admin.id}/reset-password', json={'temporary_password': NEXT_PASSWORD, 'confirm_temporary_password': NEXT_PASSWORD, 'reason': 'self'}, headers=admin_headers).status_code == 400
  response = auth_client.post(f'/api/operators/{target.id}/reset-password', json={'temporary_password': NEXT_PASSWORD, 'confirm_temporary_password': NEXT_PASSWORD, 'reason': 'operator rotation'}, headers=admin_headers)
  assert response.status_code == 200
  assert response.json() == {'message': 'Operator password reset. Password change is required at next login.'}
  assert 'temporary_password' not in str(response.json())
  db.refresh(target)
  assert target.must_change_password is True and target.force_password_change_reason == 'ADMIN_RESET'
  assert db.query(PasswordHistory).filter_by(operator_id=target.id, change_reason='ADMIN_RESET').count() == 1
  auth_client.cookies.clear()
  auth_client.cookies.set('autoqa_session', 'unused')
  assert target_headers['X-CSRF-Token']
  assert all(session.revoked_at is not None for session in db.query(OperatorSession).filter_by(operator_id=target.id))
  reset_headers = login(auth_client, target.username, NEXT_PASSWORD)
  assert auth_client.get('/api/dashboard/summary').status_code == 403
  assert auth_client.post('/api/auth/change-required-password', json={'current_password': NEXT_PASSWORD, 'new_password': 'After!Reset9876', 'confirm_password': 'After!Reset9876'}, headers=reset_headers).status_code == 200


def test_session_apis_hide_hashes_and_revoke(auth_client, db):
  operator = add_operator(db, 'session-user', 'TESTER', TEMP_PASSWORD)
  headers = login(auth_client, operator.username, TEMP_PASSWORD)
  sessions = auth_client.get('/api/auth/sessions').json()
  assert sessions and sessions[0]['is_current'] is True
  assert 'token_hash' not in str(sessions) and 'csrf_hash' not in str(sessions)
  auth_client.cookies.clear()
  other_headers = login(auth_client, operator.username, TEMP_PASSWORD)
  assert auth_client.post('/api/auth/sessions/revoke-others', json={}, headers=other_headers).json()['revoked_count'] == 1
  session_id = auth_client.get('/api/auth/sessions').json()[0]['session_id']
  revoked = auth_client.post(f'/api/auth/sessions/{session_id}/revoke', json={'reason': 'done'}, headers=other_headers)
  assert revoked.status_code == 200
  assert auth_client.get('/api/auth/me').status_code == 401


def test_admin_session_reports_security_reports_and_history_append_only(auth_client, db):
  admin = add_operator(db, 'report-admin', 'ADMIN', ADMIN_PASSWORD)
  target = add_operator(db, 'report-target', 'TESTER', TEMP_PASSWORD)
  login(auth_client, target.username, TEMP_PASSWORD)
  auth_client.cookies.clear()
  admin_headers = login(auth_client, admin.username, ADMIN_PASSWORD)
  listed = auth_client.get(f'/api/operators/{target.id}/sessions')
  assert listed.status_code == 200 and 'token_hash' not in str(listed.json())
  assert auth_client.post(f'/api/operators/{target.id}/sessions/revoke-all', json={'reason': 'admin review'}, headers=admin_headers).json()['revoked_count'] == 1
  summary = auth_client.get('/api/security/summary')
  assert summary.status_code == 200 and summary.json()['audit_chain_valid'] is True
  operators = auth_client.get('/api/security/operators?role=TESTER')
  assert operators.status_code == 200 and operators.json()[0]['username'] == target.username
  history = PasswordHistory(operator_id=target.id, password_hash=target.password_hash, password_version=target.password_version, changed_at=datetime.utcnow(), change_reason='SECURITY_ROTATION')
  db.add(history); db.commit()
  with pytest.raises(Exception):
    db.execute(text("UPDATE password_history SET change_reason='EDITED' WHERE id=:id"), {'id': history.id}); db.commit()
  db.rollback()
  with pytest.raises(Exception):
    db.execute(text('DELETE FROM password_history WHERE id=:id'), {'id': history.id}); db.commit()
  db.rollback()
  assert verify_chain(db)[0] is True
  assert db.query(AuditEvent).filter(AuditEvent.action.in_(['SECURITY_SUMMARY_VIEWED', 'SECURITY_OPERATOR_REPORT_VIEWED'])).count() >= 2
