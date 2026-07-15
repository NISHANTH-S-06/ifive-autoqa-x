from datetime import datetime, timedelta

import pytest
from sqlalchemy import text

from app.models.audit_event import AuditEvent
from app.models.operator import Operator
from app.models.operator_session import OperatorSession
from app.models.test_management import ManagedTestCase, ManualEvidence, TestCaseVersion
from app.services.audit_service import verify_chain
from app.services.password_service import hash_password, hash_secret

PASSWORD_HASH = hash_password('Manual!Fixture987')


def operator(db, username: str, role: str = 'VIEWER', active: bool = True, must_change: bool = False):
  item = Operator(username=username, display_name=username.title(), password_hash=PASSWORD_HASH, role=role, is_active=active, must_change_password=must_change)
  db.add(item); db.commit(); db.refresh(item); return item


def session_login(client, db, item, token: str, csrf: str = 'stage8-csrf'):
  session = OperatorSession(operator_id=item.id, token_hash=hash_secret(token), csrf_hash=hash_secret(csrf), created_at=datetime.utcnow(), expires_at=datetime.utcnow() + timedelta(hours=1), last_seen_at=datetime.utcnow(), password_version_at_login=item.password_version)
  db.add(session); db.commit(); client.cookies.clear(); client.cookies.set('autoqa_session', token); return {'X-CSRF-Token': csrf}


def create_structure(client, db):
  admin = operator(db, 'stage8-admin', 'ADMIN')
  headers = session_login(client, db, admin, 'admin-token')
  project = client.post('/api/test-projects', json={'name': 'Stage 8 Project', 'code': 'S8'}, headers=headers)
  assert project.status_code == 201
  duplicate = client.post('/api/test-projects', json={'name': 'Duplicate', 'code': 'S8'}, headers=headers)
  assert duplicate.status_code == 409
  module = client.post('/api/test-modules', json={'project_id': project.json()['id'], 'name': 'Login', 'code': 'LOGIN'}, headers=headers)
  assert module.status_code == 201
  suite = client.post('/api/test-suites', json={'project_id': project.json()['id'], 'module_id': module.json()['id'], 'name': 'Manual Smoke', 'code': 'SMOKE'}, headers=headers)
  assert suite.status_code == 201
  other_project = client.post('/api/test-projects', json={'name': 'Other Stage 8', 'code': 'S8B'}, headers=headers).json()
  cross = client.post('/api/test-suites', json={'project_id': other_project['id'], 'module_id': module.json()['id'], 'name': 'Bad', 'code': 'BAD'}, headers=headers)
  assert cross.status_code == 422
  return admin, headers, project.json(), module.json(), suite.json()


def case_payload(project, module, suite, title='Manual Login Works', case_key='S8-TC-001'):
  return {
    'project_id': project['id'],
    'module_id': module['id'],
    'suite_id': suite['id'],
    'case_key': case_key,
    'title': title,
    'objective': 'Validate a local manual workflow.',
    'preconditions': 'Operator is signed in.',
    'test_type': 'FUNCTIONAL',
    'priority': 'HIGH',
    'severity': 'MEDIUM',
    'tags': ['smoke', 'manual'],
    'steps': [
      {'step_number': 1, 'action': 'Open the local dashboard.', 'expected_result': 'Dashboard is visible.', 'test_data': 'local user only'},
      {'step_number': 2, 'action': 'Inspect the status cards.', 'expected_result': 'Cards render without overflow.', 'test_data': None},
    ],
  }


def approve_case(client, db, project, module, suite):
  tester = operator(db, 'stage8-tester', 'TESTER')
  tester_headers = session_login(client, db, tester, 'tester-token')
  created = client.post('/api/test-cases', json=case_payload(project, module, suite), headers=tester_headers)
  assert created.status_code == 201
  case_id = created.json()['id']
  assert client.post(f'/api/test-cases/{case_id}/submit', headers=tester_headers).status_code == 200
  assert client.post(f'/api/test-cases/{case_id}/approve', headers=tester_headers).status_code == 403
  approver = operator(db, 'stage8-approver', 'APPROVER')
  approver_headers = session_login(client, db, approver, 'approver-token')
  approved = client.post(f'/api/test-cases/{case_id}/approve', headers=approver_headers)
  assert approved.status_code == 200
  assert approved.json()['lifecycle_state'] == 'APPROVED'
  return tester, tester_headers, approver, approver_headers, approved.json()


def test_project_module_suite_rbac_archive_and_audit(auth_client, db):
  viewer = operator(db, 'stage8-viewer')
  viewer_headers = session_login(auth_client, db, viewer, 'viewer-token')
  assert auth_client.post('/api/test-projects', json={'name': 'Denied', 'code': 'DENIED'}, headers=viewer_headers).status_code == 403
  assert auth_client.post('/api/test-projects', json={'name': 'No CSRF', 'code': 'NOCSRF'}).status_code == 403
  _, admin_headers, project, module, suite = create_structure(auth_client, db)
  assert auth_client.post(f"/api/test-suites/{suite['id']}/archive", headers=admin_headers).json()['status'] == 'ARCHIVED'
  assert auth_client.post('/api/test-cases', json=case_payload(project, module, suite), headers=admin_headers).status_code == 409
  assert db.query(AuditEvent).filter(AuditEvent.action == 'test_suite_archived').count() == 1


def test_case_lifecycle_versions_tags_search_and_exports(auth_client, db):
  _, _, project, module, suite = create_structure(auth_client, db)
  tester, tester_headers, approver, approver_headers, approved = approve_case(auth_client, db, project, module, suite)
  case_id = approved['id']
  assert auth_client.patch(f'/api/test-cases/{case_id}', json={'title': 'Silent overwrite'}, headers=tester_headers).status_code == 409
  versions = auth_client.get(f'/api/test-cases/{case_id}/versions').json()
  assert len(versions) >= 3
  assert versions[-1]['source_state'] == 'APPROVED'
  snapshot = versions[-1]['snapshot_json']
  assert 'Open the local dashboard.' in snapshot and 'password' not in snapshot.lower()
  assert auth_client.get('/api/test-cases?tag=smoke&search=login&sort=case_key').json()['page']['total'] == 1
  csv_export = auth_client.get('/api/test-cases/export?format=csv').text
  assert 'S8-TC-001' in csv_export

  with pytest.raises(Exception):
    db.execute(text("UPDATE test_case_versions SET change_summary='tamper' WHERE id=:id"), {'id': versions[0]['id']}); db.commit()
  db.rollback()
  with pytest.raises(Exception):
    db.execute(text('DELETE FROM test_case_versions WHERE id=:id'), {'id': versions[0]['id']}); db.commit()
  db.rollback()

  tester_headers = session_login(auth_client, db, tester, 'tester-token-return')
  revision = auth_client.post(f'/api/test-cases/{case_id}/revision', json={'reason': 'Need a revised draft.'}, headers=tester_headers)
  assert revision.status_code == 200 and revision.json()['lifecycle_state'] == 'DRAFT'
  assert revision.json()['current_version'] == approved['current_version'] + 1
  assert auth_client.post(f'/api/test-cases/{case_id}/archive', headers=tester_headers).json()['lifecycle_state'] == 'ARCHIVED'


def test_rejection_requires_reason_and_rejected_returns_to_draft(auth_client, db):
  _, _, project, module, suite = create_structure(auth_client, db)
  tester = operator(db, 'reject-tester', 'TESTER')
  tester_headers = session_login(auth_client, db, tester, 'reject-tester-token')
  created = auth_client.post('/api/test-cases', json=case_payload(project, module, suite, case_key='S8-TC-REJ'), headers=tester_headers).json()
  auth_client.post(f"/api/test-cases/{created['id']}/submit", headers=tester_headers)
  approver = operator(db, 'reject-approver', 'APPROVER')
  approver_headers = session_login(auth_client, db, approver, 'reject-approver-token')
  assert auth_client.post(f"/api/test-cases/{created['id']}/reject", json={}, headers=approver_headers).status_code == 422
  rejected = auth_client.post(f"/api/test-cases/{created['id']}/reject", json={'reason': 'Expected result needs detail.'}, headers=approver_headers)
  assert rejected.json()['lifecycle_state'] == 'REJECTED'
  tester_headers = session_login(auth_client, db, tester, 'reject-tester-token-return')
  updated = auth_client.patch(f"/api/test-cases/{created['id']}", json={'title': 'Manual Login Works Updated'}, headers=tester_headers)
  assert updated.status_code == 200 and updated.json()['title'].endswith('Updated')


def test_manual_run_results_evidence_and_frozen_version(auth_client, db, monkeypatch, tmp_path):
  import app.services.test_management as management_service
  monkeypatch.setattr(management_service, 'EVIDENCE_ROOT', tmp_path / 'stage8_evidence')
  _, _, project, module, suite = create_structure(auth_client, db)
  tester, tester_headers, _, _, approved = approve_case(auth_client, db, project, module, suite)
  tester_headers = session_login(auth_client, db, tester, 'manual-tester-token-return')
  draft = auth_client.post('/api/test-cases', json=case_payload(project, module, suite, case_key='S8-DRAFT'), headers=tester_headers).json()
  bad_run = auth_client.post('/api/manual-test-runs', json={'project_id': project['id'], 'suite_id': suite['id'], 'name': 'Bad Run', 'case_ids': [draft['id']]}, headers=tester_headers)
  assert bad_run.status_code == 409
  run = auth_client.post('/api/manual-test-runs', json={'project_id': project['id'], 'suite_id': suite['id'], 'name': 'Manual Run', 'assigned_to': tester.id, 'case_ids': [approved['id']]}, headers=tester_headers)
  assert run.status_code == 201 and run.json()['status'] == 'PLANNED'
  assert auth_client.post(f"/api/manual-test-runs/{run.json()['id']}/cases", json={'case_ids': [approved['id']]}, headers=tester_headers).status_code == 409
  assert auth_client.post(f"/api/manual-test-runs/{run.json()['id']}/start", headers=tester_headers).json()['status'] == 'IN_PROGRESS'
  run_case = auth_client.get(f"/api/manual-test-runs/{run.json()['id']}/cases").json()[0]
  assert run_case['test_case_version'] == approved['current_version']
  assert auth_client.patch(f"/api/manual-test-runs/{run.json()['id']}/cases/{run_case['id']}/steps/1", json={'status': 'FAILED'}, headers=tester_headers).status_code == 422
  step = auth_client.patch(f"/api/manual-test-runs/{run.json()['id']}/cases/{run_case['id']}/steps/1", json={'status': 'PASSED', 'actual_result': 'Visible'}, headers=tester_headers)
  assert step.status_code == 200
  assert auth_client.patch(f"/api/manual-test-runs/{run.json()['id']}/cases/{run_case['id']}/steps/99", json={'status': 'PASSED'}, headers=tester_headers).status_code == 422
  result = auth_client.patch(f"/api/manual-test-runs/{run.json()['id']}/cases/{run_case['id']}", json={'status': 'PASSED', 'actual_result': 'All steps passed.'}, headers=tester_headers)
  assert result.status_code == 200 and result.json()['executed_by'] == tester.id
  done = auth_client.post(f"/api/manual-test-runs/{run.json()['id']}/complete", headers=tester_headers)
  assert done.status_code == 200 and done.json()['status'] == 'COMPLETED'

  upload = auth_client.post(f"/api/manual-test-runs/{run.json()['id']}/cases/{run_case['id']}/evidence?filename=..%2Fsafe-note.txt", content=b'manual evidence', headers={**tester_headers, 'Content-Type': 'text/plain'})
  assert upload.status_code == 201
  evidence = upload.json()
  assert evidence['sha256'] and 'D:\\' not in str(evidence)
  stored = db.get(ManualEvidence, evidence['id'])
  assert 'stage8_evidence/' in stored.relative_path and not stored.relative_path.startswith('D:')
  assert auth_client.post(f"/api/manual-test-runs/{run.json()['id']}/cases/{run_case['id']}/evidence?filename=bad.exe", content=b'MZ', headers={**tester_headers, 'Content-Type': 'application/octet-stream'}).status_code == 422
  assert auth_client.get(f"/api/manual-evidence/{evidence['id']}/download").status_code == 200
  assert auth_client.delete(f"/api/manual-evidence/{evidence['id']}", headers=tester_headers).status_code == 204


def test_export_formula_escape_and_security_regressions(auth_client, db):
  _, admin_headers, project, module, suite = create_structure(auth_client, db)
  tester = operator(db, 'formula-tester', 'TESTER')
  tester_headers = session_login(auth_client, db, tester, 'formula-token')
  created = auth_client.post('/api/test-cases', json=case_payload(project, module, suite, title='=HYPERLINK("x")', case_key='S8-FORMULA'), headers=tester_headers)
  assert created.status_code == 201
  export = auth_client.get('/api/test-cases/export?format=csv').text
  assert "'=HYPERLINK" in export
  assert auth_client.get('/api/test-cases?sort=unsafe').status_code == 422
  assert auth_client.post('/api/test-cases', json={**case_payload(project, module, suite, case_key='S8-SECRET'), 'steps': [{'step_number': 1, 'action': 'Do x', 'expected_result': 'See y', 'test_data': 'token=abc'}]}, headers=tester_headers).status_code == 422

  changing = operator(db, 'must-change-user', 'TESTER', must_change=True)
  session_login(auth_client, db, changing, 'must-change-token')
  assert auth_client.get('/api/test-projects').status_code == 403
  disabled = operator(db, 'disabled-user', 'TESTER', active=False)
  session_login(auth_client, db, disabled, 'disabled-token')
  assert auth_client.get('/api/test-projects').status_code == 403
  assert db.query(Operator).filter_by(role='ADMIN', username='default-admin').count() == 0
  valid, total, invalid = verify_chain(db)
  assert valid and total > 0 and invalid is None
