from datetime import datetime, timedelta
import json

from app.models.automated_execution import AutomatedRun, AutomatedRunCase, ExecutionWorker
from app.models.connection_target import ConnectionCheck, ConnectionTarget
from app.models.defect import Defect, DefectRetest
from app.models.operator import Operator
from app.models.reporting import ReportExport
from app.models.test_management import ManagedTestCase, ManagedTestSuite, ManualTestRun, ManualTestRunCase, TestModule, TestProject
from app.services.audit_service import verify_chain
from app.services.test_management import create_version
from tests.test_stage12_defects import operator, session_login


def make_report_data(db):
  tester = operator(db, 'stage13-tester', 'TESTER')
  approver = operator(db, 'stage13-approver', 'APPROVER')
  admin = operator(db, 'stage13-admin', 'ADMIN')
  now = datetime.utcnow()
  project = TestProject(name='Stage 13 Project', code='=S13', created_by=admin.id)
  db.add(project); db.flush()
  module = TestModule(project_id=project.id, name='Reports Module', code='RPT', created_by=admin.id)
  db.add(module); db.flush()
  suite = ManagedTestSuite(project_id=project.id, module_id=module.id, name='Reports Suite', code='RPT-S', suite_type='MIXED', created_by=admin.id)
  db.add(suite); db.flush()
  approved = ManagedTestCase(project_id=project.id, module_id=module.id, suite_id=suite.id, case_key='S13-APPROVED', title='Approved report case', lifecycle_state='APPROVED', status='ACTIVE', created_by=tester.id, approved_by=approver.id, approved_at=now, current_version=1)
  draft = ManagedTestCase(project_id=project.id, module_id=module.id, suite_id=suite.id, case_key='S13-DRAFT', title='Draft report case', lifecycle_state='DRAFT', status='ACTIVE', created_by=tester.id)
  db.add_all([approved, draft]); db.flush()
  create_version(db, approved, approver.id, 'Approved report fixture', 'APPROVED')
  manual_run = ManualTestRun(run_key='MRUN-S13', project_id=project.id, suite_id=suite.id, name='Manual Report Run', status='COMPLETED', created_by=tester.id, assigned_to=tester.id, created_at=now - timedelta(days=1), completed_at=now)
  db.add(manual_run); db.flush()
  db.add_all([
    ManualTestRunCase(run_id=manual_run.id, test_case_id=approved.id, test_case_version=1, status='PASSED', executed_by=tester.id, completed_at=now),
    ManualTestRunCase(run_id=manual_run.id, test_case_id=draft.id, test_case_version=1, status='BLOCKED', executed_by=tester.id, completed_at=now),
    ManualTestRunCase(run_id=manual_run.id, test_case_id=draft.id, test_case_version=2, status='SKIPPED', executed_by=tester.id, completed_at=now),
  ])
  cancelled = ManualTestRun(run_key='MRUN-S13-CANCEL', project_id=project.id, suite_id=suite.id, name='Cancelled Manual', status='CANCELLED', created_by=tester.id, assigned_to=tester.id, created_at=now, completed_at=now)
  db.add(cancelled)
  target = ConnectionTarget(target_key='S13-LOCAL', name='Stage 13 Local', environment_type='LOCAL', base_url='http://127.0.0.1:45555', normalized_scheme='http', normalized_host='127.0.0.1', normalized_port=45555, normalized_origin='http://127.0.0.1:45555', allowed_probe_paths_json='["/"]', tls_required=False, tls_verify=True, lifecycle_state='APPROVED', enabled=True, execution_enabled=True, created_by=tester.id, approved_by=approver.id, execution_approved_by=approver.id, version=1)
  db.add(target); db.flush()
  automated = AutomatedRun(run_key='ARUN-S13', name='Automated Report Run', target_id=target.id, target_version=1, target_origin=target.normalized_origin, status='PASSED', created_by=tester.id, approved_by=approver.id, total_steps=2, completed_steps=2, failed_steps=0, attempt_count=2, max_retries=2, created_at=now, completed_at=now)
  failed = AutomatedRun(run_key='ARUN-S13-FAIL', name='Failed Automated Report Run', target_id=target.id, target_version=1, target_origin=target.normalized_origin, status='FAILED', created_by=tester.id, approved_by=approver.id, failure_classification='ASSERTION', total_steps=1, completed_steps=1, failed_steps=1, created_at=now, completed_at=now)
  db.add_all([automated, failed]); db.flush()
  db.add_all([
    AutomatedRunCase(run_id=automated.id, test_case_id=approved.id, test_case_version=1, case_snapshot_json='{}', status='PASSED'),
    AutomatedRunCase(run_id=failed.id, test_case_id=approved.id, test_case_version=1, case_snapshot_json='{}', status='FAILED', failure_classification='ASSERTION'),
  ])
  db.add_all([
    Defect(defect_key='DEF-S13-OPEN', title='Open report defect', project_id=project.id, module_id=module.id, suite_id=suite.id, test_case_id=approved.id, test_case_version=1, automated_run_id=failed.id, severity='HIGH', priority='HIGH', status='NEW', reporter_id=tester.id, created_by=tester.id, target_id=target.id, target_version=1, created_at=now),
    Defect(defect_key='DEF-S13-CLOSED', title='Closed report defect', project_id=project.id, module_id=module.id, suite_id=suite.id, test_case_id=approved.id, test_case_version=1, severity='LOW', priority='MEDIUM', status='CLOSED', reporter_id=tester.id, created_by=tester.id, created_at=now - timedelta(days=2), closed_at=now),
    Defect(defect_key='DEF-S13-DUP', title='Duplicate report defect', project_id=project.id, severity='MEDIUM', priority='LOW', status='DUPLICATE', reporter_id=tester.id, created_by=tester.id, created_at=now),
    Defect(defect_key='DEF-S13-REOPEN', title='Reopened report defect', project_id=project.id, severity='CRITICAL', priority='CRITICAL', status='REOPENED', reporter_id=tester.id, created_by=tester.id, created_at=now),
  ])
  db.add_all([
    DefectRetest(defect_id=1, test_case_id=approved.id, test_case_version=1, result_status='PASSED', created_by=tester.id, created_at=now),
    DefectRetest(defect_id=1, test_case_id=approved.id, test_case_version=1, result_status='FAILED', created_by=tester.id, created_at=now),
    ConnectionCheck(check_key='CHK-S13', target_id=target.id, target_version=1, probe_path='/', method='HEAD', requested_origin=target.normalized_origin, resolved_addresses_json='["127.0.0.1"]', started_at=now, completed_at=now, status='REACHABLE', response_headers_json='{}', initiated_by=approver.id, created_at=now),
    ExecutionWorker(worker_key='stage13-worker', status='IDLE', max_concurrency=1, heartbeat_at=now),
  ])
  db.commit()
  return admin, tester, approver, project, module, suite, target


def test_stage13_dashboard_execution_defect_trends_quality_and_filters(auth_client, db):
  admin, tester, approver, project, module, suite, target = make_report_data(db)
  headers = session_login(auth_client, db, tester, 'stage13-tester-token')
  dashboard = auth_client.get('/api/reports/dashboard?date_range=last_7_days', headers=headers).json()
  assert dashboard['summary']['test_projects'] == 1
  assert dashboard['summary']['approved_test_cases'] == 1
  assert dashboard['summary']['manual_runs'] == 2
  assert dashboard['summary']['automated_runs'] == 2
  assert dashboard['summary']['result_counts']['PASSED'] == 2
  assert dashboard['summary']['result_counts']['BLOCKED'] == 1
  assert dashboard['summary']['result_counts']['SKIPPED'] == 1
  assert dashboard['summary']['open_defects'] == 2
  assert dashboard['summary']['closed_defects'] == 1
  assert dashboard['summary']['duplicate_defects'] == 1
  assert dashboard['summary']['target_health']['REACHABLE'] == 1
  executions = auth_client.get(f'/api/reports/executions?project_id={project.id}&suite_id={suite.id}&date_range=last_7_days', headers=headers).json()
  assert executions['manual']['case_statuses']['PASSED'] == 1
  assert executions['automated']['case_statuses']['FAILED'] == 1
  assert executions['automated']['failure_categories']['ASSERTION'] == 1
  defects = auth_client.get(f'/api/reports/defects?project_id={project.id}&severity=HIGH&date_range=last_7_days', headers=headers).json()
  assert defects['by_severity']['HIGH'] == 1
  trends = auth_client.get('/api/reports/trends?date_range=last_7_days', headers=headers).json()
  assert trends['defects_created']
  quality = auth_client.get('/api/reports/quality?date_range=last_7_days', headers=headers).json()
  assert quality['pass_percentage'] > 0
  assert quality['approved_test_case_percentage'] == 50.0
  assert quality['automation_coverage'] == 50.0
  assert quality['retest_success_rate'] == 50.0
  traceability = auth_client.get('/api/reports/traceability?date_range=last_7_days', headers=headers).json()
  assert any(item['defect_key'] == 'DEF-S13-OPEN' and item['automated_run_id'] for item in traceability['items'])
  targets = auth_client.get(f'/api/reports/targets?target_id={target.id}&environment=LOCAL&date_range=last_7_days', headers=headers).json()
  assert targets['targets'][0]['target_key'] == 'S13-LOCAL'
  workers = auth_client.get('/api/reports/workers', headers=headers).json()
  assert workers['status_counts']['IDLE'] == 1


def test_stage13_zero_division_and_invalid_filters(auth_client, db):
  viewer = operator(db, 'stage13-empty-viewer', 'VIEWER')
  headers = session_login(auth_client, db, viewer, 'stage13-empty-viewer-token')
  quality = auth_client.get('/api/reports/quality?date_range=today', headers=headers).json()
  assert quality['pass_percentage'] == 0
  assert quality['defect_density'] == 0
  assert auth_client.get('/api/reports/dashboard?date_range=century', headers=headers).status_code == 422
  assert auth_client.get('/api/reports/defects?severity=SECRET', headers=headers).status_code == 422


def test_stage13_export_authorization_formula_safety_row_limit_and_audit(auth_client, db):
  admin, tester, _, _, _, _, _ = make_report_data(db)
  tester_headers = session_login(auth_client, db, tester, 'stage13-export-denied')
  assert auth_client.post('/api/reports/export', json={'report_type': 'executions', 'export_format': 'csv'}, headers=tester_headers).status_code == 403
  assert auth_client.post('/api/reports/export', json={'report_type': 'executions', 'export_format': 'csv'}).status_code == 403
  admin_headers = session_login(auth_client, db, admin, 'stage13-export-admin')
  created = auth_client.post('/api/reports/export', json={'report_type': 'executions', 'export_format': 'csv', 'filters': {'date_range': 'last_7_days'}}, headers=admin_headers)
  assert created.status_code == 201
  export = created.json()
  assert export['row_count'] <= 500 and export['sha256']
  assert db.query(ReportExport).filter_by(id=export['id']).one().relative_path.startswith('stage13_exports/')
  downloaded = auth_client.get(f"/api/reports/exports/{export['id']}/download")
  assert downloaded.status_code == 200
  text = downloaded.text
  assert "'=S13" in text
  lowered = text.lower()
  for forbidden in ['password', 'token', 'cookie', 'csrf', 'authorization', 'session', 'hash', 'd:\\']:
    assert forbidden not in lowered
  valid, total, invalid = verify_chain(db)
  assert valid and total > 0 and invalid is None


def test_stage13_report_definitions_are_admin_only_and_local_run(auth_client, db):
  admin, tester, _, _, _, _, _ = make_report_data(db)
  tester_headers = session_login(auth_client, db, tester, 'stage13-def-viewer')
  assert auth_client.get('/api/report-definitions', headers=tester_headers).status_code == 403
  admin_headers = session_login(auth_client, db, admin, 'stage13-def-admin')
  created = auth_client.post('/api/report-definitions', json={'name': 'Daily quality', 'report_type': 'quality', 'frequency': 'DAILY', 'filters': {'date_range': 'last_7_days'}}, headers=admin_headers)
  assert created.status_code == 201 and created.json()['next_run_at']
  run = auth_client.post(f"/api/report-definitions/{created.json()['id']}/run", headers=admin_headers)
  assert run.status_code == 200, run.text
  assert run.json()['report_type'] == 'quality'
  disabled = auth_client.post(f"/api/report-definitions/{created.json()['id']}/disable", headers=admin_headers)
  assert disabled.json()['enabled'] is False
  assert auth_client.post(f"/api/report-definitions/{created.json()['id']}/run", headers=admin_headers).status_code == 409
