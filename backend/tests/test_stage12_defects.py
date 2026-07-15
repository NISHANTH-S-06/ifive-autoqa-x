from datetime import datetime, timedelta
import hashlib
import json

import pytest
from sqlalchemy import text

from app.models.automated_execution import AutomatedRun, AutomatedRunCase, AutomatedStepResult, ExecutionArtifact
from app.models.connection_target import ConnectionTarget
from app.models.defect import DefectComment, DefectHistory, DefectRetest
from app.models.operator import Operator
from app.models.operator_session import OperatorSession
from app.models.test_management import (
  ManagedTestCase,
  ManagedTestSuite,
  ManualEvidence,
  ManualStepResult,
  ManualTestRun,
  ManualTestRunCase,
  TestCaseStep,
  TestModule,
  TestProject,
)
from app.services.audit_service import verify_chain
from app.services.password_service import hash_password, hash_secret
from app.services.test_management import create_version

PASSWORD_HASH = hash_password('Stage12!Fixture987')


def operator(db, username: str, role: str = 'VIEWER', active: bool = True, must_change: bool = False):
  item = Operator(username=username, display_name=username.title(), password_hash=PASSWORD_HASH, role=role, is_active=active, must_change_password=must_change)
  db.add(item); db.commit(); db.refresh(item); return item


def session_login(client, db, item, token: str, csrf: str = 'stage12-csrf'):
  session = OperatorSession(operator_id=item.id, token_hash=hash_secret(token), csrf_hash=hash_secret(csrf), created_at=datetime.utcnow(), expires_at=datetime.utcnow() + timedelta(hours=1), last_seen_at=datetime.utcnow(), password_version_at_login=item.password_version)
  db.add(session); db.commit(); client.cookies.clear(); client.cookies.set('autoqa_session', token); return {'X-CSRF-Token': csrf}


def approved_case(db, tester: Operator, approver: Operator, key='S12-CASE', suite_type='MANUAL'):
  project = TestProject(name=f'{key} Project', code=f'{key}-P', created_by=approver.id)
  db.add(project); db.flush()
  module = TestModule(project_id=project.id, name='Defect Module', code='DEF', created_by=approver.id)
  db.add(module); db.flush()
  suite = ManagedTestSuite(project_id=project.id, module_id=module.id, name='Defect Suite', code=key[-8:], suite_type=suite_type, created_by=approver.id)
  db.add(suite); db.flush()
  case = ManagedTestCase(project_id=project.id, module_id=module.id, suite_id=suite.id, case_key=key, title='Approved defect source case', lifecycle_state='APPROVED', status='ACTIVE', created_by=tester.id, reviewed_by=approver.id, approved_by=approver.id, approved_at=datetime.utcnow(), current_version=1)
  db.add(case); db.flush()
  case.steps.append(TestCaseStep(step_number=1, action='Inspect local mock page', expected_result='Expected text appears.', test_data='local only'))
  db.flush()
  create_version(db, case, approver.id, 'Approved for defect traceability', 'APPROVED')
  db.commit(); db.refresh(case)
  return project, module, suite, case


def manual_failure(db, tester: Operator, approver: Operator):
  project, module, suite, case = approved_case(db, tester, approver, 'S12-MANUAL')
  run = ManualTestRun(run_key='MRUN-S12-FAIL', project_id=project.id, suite_id=suite.id, name='Stage 12 Manual Failure', status='COMPLETED', created_by=tester.id, assigned_to=tester.id, completed_at=datetime.utcnow())
  db.add(run); db.flush()
  run_case = ManualTestRunCase(run_id=run.id, test_case_id=case.id, test_case_version=case.current_version, status='FAILED', actual_result='Observed safe validation mismatch.', notes='Reproduce by opening the local dashboard.', executed_by=tester.id, completed_at=datetime.utcnow())
  db.add(run_case); db.flush()
  step = ManualStepResult(run_case_id=run_case.id, step_number=1, status='FAILED', actual_result='Expected banner was missing.', notes='Expected banner should appear.', executed_by=tester.id, executed_at=datetime.utcnow())
  db.add(step); db.flush()
  digest = hashlib.sha256(b'stage12 manual evidence').hexdigest()
  db.add(ManualEvidence(run_case_id=run_case.id, step_result_id=step.id, evidence_type='TEXT', original_filename='stage12-note.txt', stored_filename='stage12-note.txt', relative_path='stage8_evidence/stage12-note.txt', mime_type='text/plain', size_bytes=23, sha256=digest, uploaded_by=tester.id))
  db.commit()
  return project, module, suite, case, run, run_case, step


def automated_failure(db, tester: Operator, approver: Operator):
  project, module, suite, case = approved_case(db, tester, approver, 'S12-AUTO', 'AUTOMATED')
  target = ConnectionTarget(target_key='S12-LOCAL', name='Stage 12 Local Mock', environment_type='LOCAL', base_url='http://127.0.0.1:43210', normalized_scheme='http', normalized_host='127.0.0.1', normalized_port=43210, normalized_origin='http://127.0.0.1:43210', allowed_probe_paths_json='["/"]', tls_required=False, tls_verify=True, connection_timeout_seconds=3, lifecycle_state='APPROVED', enabled=True, owner_operator_id=tester.id, created_by=tester.id, reviewed_by=approver.id, approved_by=approver.id, approved_at=datetime.utcnow(), execution_enabled=True, execution_submitted_by=tester.id, execution_submitted_at=datetime.utcnow(), execution_approved_by=approver.id, execution_approved_at=datetime.utcnow(), version=1)
  db.add(target); db.flush()
  run = AutomatedRun(run_key='ARUN-S12-FAIL', name='Stage 12 Automated Failure', target_id=target.id, target_version=1, target_origin=target.normalized_origin, status='FAILED', risk_level='READ_ONLY', preflight_status='PASSED', dns_pinning_status='PINNED', created_by=tester.id, approved_by=approver.id, total_steps=1, completed_steps=1, failed_steps=1, failure_classification='ASSERTION', safe_error_message='Expected safe text was not visible.', completed_at=datetime.utcnow())
  db.add(run); db.flush()
  run_case = AutomatedRunCase(run_id=run.id, test_case_id=case.id, test_case_version=case.current_version, case_snapshot_json=json.dumps({'case_key': case.case_key}), sort_order=1, status='FAILED', failure_classification='ASSERTION', safe_error_message='Case failed safely.', completed_at=datetime.utcnow())
  db.add(run_case); db.flush()
  step = AutomatedStepResult(run_case_id=run_case.id, step_number=1, action_type='ASSERT_TEXT', selector='#ready', expected_redacted='Ready', status='FAILED', failure_classification='ASSERTION', safe_error_message='Expected safe text was not visible.', duration_ms=12, completed_at=datetime.utcnow())
  db.add(step); db.flush()
  db.add(ExecutionArtifact(run_id=run.id, run_case_id=run_case.id, step_result_id=step.id, artifact_type='SUMMARY', original_filename='summary.json', stored_filename='stage12-summary.json', relative_path='stage10_artifacts/stage12-summary.json', mime_type='application/json', size_bytes=18, sha256=hashlib.sha256(b'stage12 artifact').hexdigest(), safe=True))
  db.commit()
  return target, run, run_case, step


def test_manual_defect_from_failed_result_lifecycle_traceability_and_immutability(auth_client, db):
  tester = operator(db, 'stage12-tester', 'TESTER')
  approver = operator(db, 'stage12-approver', 'APPROVER')
  _, _, _, _, run, run_case, step = manual_failure(db, tester, approver)
  tester_headers = session_login(auth_client, db, tester, 'stage12-manual-token')

  warning = auth_client.post('/api/defects/from-run', json={'source_type': 'MANUAL_STEP', 'manual_run_case_id': run_case.id, 'manual_step_result_id': step.id, 'severity': 'HIGH'}, headers=tester_headers)
  assert warning.status_code == 200 and warning.json()['requires_confirmation'] is True
  created = auth_client.post('/api/defects/from-run', json={'source_type': 'MANUAL_STEP', 'manual_run_case_id': run_case.id, 'manual_step_result_id': step.id, 'severity': 'HIGH', 'confirm': True}, headers=tester_headers)
  assert created.status_code == 200
  defect = created.json()
  assert defect['defect_key'].startswith('DEF-')
  assert defect['manual_run_id'] == run.id and defect['manual_step_result_id'] == step.id
  duplicate = auth_client.post('/api/defects/from-run', json={'source_type': 'MANUAL_STEP', 'manual_run_case_id': run_case.id, 'manual_step_result_id': step.id, 'confirm': True}, headers=tester_headers)
  assert duplicate.status_code == 409
  assert auth_client.get(f"/api/defects/{defect['id']}/evidence").json()[0]['manual_evidence_id'] is not None

  assert auth_client.post(f"/api/defects/{defect['id']}/triage", headers=tester_headers).status_code == 403
  approver_headers = session_login(auth_client, db, approver, 'stage12-approver-token')
  assert auth_client.post(f"/api/defects/{defect['id']}/triage", headers=approver_headers).json()['status'] == 'TRIAGED'
  assert auth_client.post(f"/api/defects/{defect['id']}/assign", json={'assigned_to': tester.id}, headers=approver_headers).json()['status'] == 'ASSIGNED'
  assert auth_client.post(f"/api/defects/{defect['id']}/close", json={'resolution': 'skip'}, headers=approver_headers).status_code == 409
  tester_headers = session_login(auth_client, db, tester, 'stage12-tester-start')
  assert auth_client.post(f"/api/defects/{defect['id']}/start", headers=tester_headers).json()['status'] == 'IN_PROGRESS'
  approver_headers = session_login(auth_client, db, approver, 'stage12-approver-fix')
  assert auth_client.post(f"/api/defects/{defect['id']}/fix", headers=approver_headers).json()['status'] == 'FIXED'
  assert auth_client.post(f"/api/defects/{defect['id']}/ready-for-retest", headers=approver_headers).json()['status'] == 'READY_FOR_RETEST'
  tester_headers = session_login(auth_client, db, tester, 'stage12-tester-retest')
  retest = auth_client.post(f"/api/defects/{defect['id']}/retest", json={'result_status': 'PASSED', 'notes': 'Local safe retest passed.'}, headers=tester_headers)
  assert retest.status_code == 201 and retest.json()['manual_run_id'] is not None
  approver_headers = session_login(auth_client, db, approver, 'stage12-approver-close')
  closed = auth_client.post(f"/api/defects/{defect['id']}/close", json={'resolution': 'Fixed and retested with local data.'}, headers=approver_headers)
  assert closed.status_code == 200 and closed.json()['status'] == 'CLOSED'

  assert auth_client.post(f"/api/defects/{defect['id']}/comments", json={'body': 'Clean local note.'}, headers=approver_headers).status_code == 201
  assert auth_client.post(f"/api/defects/{defect['id']}/comments", json={'body': 'password=never'}, headers=approver_headers).status_code == 422
  trace = auth_client.get(f"/api/defects/{defect['id']}/traceability").json()
  assert trace['manual_run_id'] == run.id and trace['test_case']['case_key'] == 'S12-MANUAL'
  assert auth_client.get(f"/api/traceability/runs/{run.id}?run_type=manual").json()['defects'][0]['status'] == 'CLOSED'

  comment = db.query(DefectComment).one()
  history = db.query(DefectHistory).first()
  retest_row = db.query(DefectRetest).one()
  for statement, params in [
    ('UPDATE defect_comments SET body=:body WHERE id=:id', {'body': 'tamper', 'id': comment.id}),
    ('DELETE FROM defect_history WHERE id=:id', {'id': history.id}),
    ('UPDATE defect_retests SET safe_notes=:body WHERE id=:id', {'body': 'tamper', 'id': retest_row.id}),
  ]:
    with pytest.raises(Exception):
      db.execute(text(statement), params); db.commit()
    db.rollback()
  valid, total, invalid = verify_chain(db)
  assert valid and total > 0 and invalid is None


def test_automated_defect_source_links_target_artifact_and_duplicate_warning(auth_client, db):
  tester = operator(db, 'stage12-auto-tester', 'TESTER')
  approver = operator(db, 'stage12-auto-approver', 'APPROVER')
  target, run, run_case, step = automated_failure(db, tester, approver)
  tester_headers = session_login(auth_client, db, tester, 'stage12-auto-token')

  created = auth_client.post('/api/defects/from-run', json={'source_type': 'AUTOMATED_STEP', 'automated_run_id': run.id, 'automated_run_case_id': run_case.id, 'automated_step_result_id': step.id, 'priority': 'CRITICAL', 'confirm': True}, headers=tester_headers)
  assert created.status_code == 200
  defect = created.json()
  assert defect['automated_run_id'] == run.id
  assert defect['target_id'] == target.id and defect['target_version'] == 1
  assert 'token' not in json.dumps(defect).lower()
  evidence = auth_client.get(f"/api/defects/{defect['id']}/evidence").json()
  assert evidence[0]['execution_artifact_id'] is not None
  warning = auth_client.post('/api/defects/from-run', json={'source_type': 'AUTOMATED_STEP', 'automated_run_id': run.id, 'automated_run_case_id': run_case.id, 'automated_step_result_id': step.id}, headers=tester_headers)
  assert warning.status_code == 200 and len(warning.json()['possible_existing']) == 1
  trace = auth_client.get(f"/api/traceability/runs/{run.id}?run_type=automated").json()
  assert trace['run']['run_key'] == 'ARUN-S12-FAIL' and trace['defects'][0]['defect_key'] == defect['defect_key']


def test_defect_rbac_csrf_cross_project_and_secret_rejection(auth_client, db):
  tester = operator(db, 'stage12-sec-tester', 'TESTER')
  approver = operator(db, 'stage12-sec-approver', 'APPROVER')
  viewer = operator(db, 'stage12-viewer', 'VIEWER')
  project, module, suite, case = approved_case(db, tester, approver, 'S12-SEC')
  other_project, _, _, _ = approved_case(db, tester, approver, 'S12-OTHER')
  tester_headers = session_login(auth_client, db, tester, 'stage12-sec-token')

  assert auth_client.post('/api/defects', json={'title': 'No csrf', 'project_id': project.id}).status_code == 403
  viewer_headers = session_login(auth_client, db, viewer, 'stage12-viewer-token')
  assert auth_client.post('/api/defects', json={'title': 'Denied', 'project_id': project.id}, headers=viewer_headers).status_code == 403
  tester_headers = session_login(auth_client, db, tester, 'stage12-sec-token-return')
  bad_scope = auth_client.post('/api/defects', json={'title': 'Bad cross scope', 'project_id': other_project.id, 'module_id': module.id, 'suite_id': suite.id, 'test_case_id': case.id}, headers=tester_headers)
  assert bad_scope.status_code == 422
  secret = auth_client.post('/api/defects', json={'title': 'Leaky defect', 'project_id': project.id, 'actual_result': 'authorization: bearer local'}, headers=tester_headers)
  assert secret.status_code == 422
  good = auth_client.post('/api/defects', json={'title': 'Standalone local defect', 'project_id': project.id, 'module_id': module.id, 'suite_id': suite.id, 'test_case_id': case.id, 'test_case_version': case.current_version}, headers=tester_headers)
  assert good.status_code == 201
  assert auth_client.get('/api/defects?search=standalone&status=NEW').json()['page']['total'] == 1
  assert auth_client.get('/api/defects?sort=unsafe').status_code == 422
  assert db.query(Operator).filter_by(role='ADMIN', username='default-admin').count() == 0
