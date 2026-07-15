from datetime import datetime, timedelta

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.models.audit_event import AuditEvent
from app.models.automated_execution import AutomatedRun, ExecutionArtifact
from app.models.connection_target import ConnectionTarget
from app.models.defect import Defect
from app.models.operator import Operator
from app.models.operator_session import OperatorSession
from app.models.project import Project
from app.models.project_membership import ProjectMember
from app.models.reporting import ReportExport
from app.models.test_management import ManualEvidence
from app.services.password_service import hash_password, hash_secret
from app.services.project_access import ACTION_ROLES, ProjectAccessService, ProjectAction
from app.database import get_db
from app.main import app
from app.config import settings
from app.migration_safety import schema_snapshot


PASSWORD_HASH = hash_password('Isolation!Fixture987')


def test_isolated_testclient_request_cannot_mutate_active_schema(db):
  before = schema_snapshot(settings.database_url, allow_active=True)
  def override_db():
    yield db
  app.dependency_overrides[get_db] = override_db
  test_client = TestClient(app)
  try:
    assert test_client.get('/health').status_code == 200
  finally:
    test_client.close()
    app.dependency_overrides.clear()
  assert schema_snapshot(settings.database_url, allow_active=True) == before


def _operator(db, username: str, global_role: str = 'TESTER') -> Operator:
  item = Operator(
    username=username,
    display_name=username,
    password_hash=PASSWORD_HASH,
    role=global_role,
    is_active=True,
  )
  db.add(item); db.commit(); db.refresh(item)
  return item


def _project(db, name: str) -> Project:
  item = Project(name=name, product_code='AUTOQA', environment='local', is_active=True)
  db.add(item); db.commit(); db.refresh(item)
  return item


def _member(db, project: Project, operator: Operator, role: str) -> ProjectMember:
  item = ProjectMember(
    project_id=project.id,
    operator_id=operator.id,
    role=role,
    status='ACTIVE',
    created_by=operator.id,
  )
  db.add(item); db.commit(); db.refresh(item)
  return item


def _login(client, db, operator: Operator, token: str) -> dict[str, str]:
  csrf = f'{token}-csrf'
  db.add(OperatorSession(
    operator_id=operator.id,
    token_hash=hash_secret(token),
    csrf_hash=hash_secret(csrf),
    created_at=datetime.utcnow(),
    expires_at=datetime.utcnow() + timedelta(hours=1),
    last_seen_at=datetime.utcnow(),
    password_version_at_login=operator.password_version,
  ))
  db.commit()
  client.cookies.clear(); client.cookies.set('autoqa_session', token)
  return {'X-CSRF-Token': csrf}


def _target(db, project: Project, creator: Operator, key: str) -> ConnectionTarget:
  item = ConnectionTarget(
    project_id=project.id,
    target_key=key,
    name=f'{key} target',
    environment_type='LOCAL',
    base_url='http://127.0.0.1:5173',
    normalized_scheme='http',
    normalized_host='127.0.0.1',
    normalized_port=5173,
    normalized_origin='http://127.0.0.1:5173',
    allowed_probe_paths_json='["/"]',
    tls_required=False,
    tls_verify=True,
    connection_timeout_seconds=3,
    created_by=creator.id,
  )
  db.add(item); db.commit(); db.refresh(item)
  return item


def test_project_role_matrix_is_fail_closed_and_audited(db):
  project = _project(db, 'Isolation Role Matrix')
  for role in ('OWNER', 'ADMIN', 'APPROVER', 'TESTER', 'VIEWER'):
    operator = _operator(db, f'isolation-{role.lower()}')
    _member(db, project, operator, role)
    access = ProjectAccessService(db, operator.id)
    for action in ProjectAction:
      if role in ACTION_ROLES[action]:
        assert access.require(project.id, action).role == role
      else:
        with pytest.raises(HTTPException) as denied:
          access.require(project.id, action)
        assert denied.value.status_code == 403

  outsider = _operator(db, 'isolation-outsider')
  with pytest.raises(HTTPException) as hidden:
    ProjectAccessService(db, outsider.id).require(project.id)
  assert hidden.value.status_code == 404
  assert db.scalar(select(AuditEvent).where(AuditEvent.action == 'PROJECT_ACCESS_DENIED')) is not None


def test_cross_project_lists_ids_artifacts_and_relationships_are_isolated(auth_client, db):
  project_a = _project(db, 'Isolation Project A')
  project_b = _project(db, 'Isolation Project B')
  operator_a = _operator(db, 'isolation-user-a')
  operator_b = _operator(db, 'isolation-user-b')
  _member(db, project_a, operator_a, 'OWNER')
  _member(db, project_b, operator_b, 'OWNER')
  target_a = _target(db, project_a, operator_a, 'ISOLATION-A')
  target_b = _target(db, project_b, operator_b, 'ISOLATION-B')
  run_b = AutomatedRun(
    project_id=project_b.id,
    run_key='ISOLATION-RUN-B',
    name='Private B run',
    target_id=target_b.id,
    target_version=1,
    target_origin=target_b.normalized_origin,
    created_by=operator_b.id,
  )
  defect_b = Defect(
    access_project_id=project_b.id,
    defect_key='ISOLATION-DEFECT-B',
    title='Private B defect',
    project_id=0,
    reporter_id=operator_b.id,
    created_by=operator_b.id,
  )
  report_b = ReportExport(
    project_id=project_b.id,
    export_key='ISOLATION-REPORT-B',
    report_type='dashboard',
    export_format='json',
    original_filename='isolation-b-report.json',
    stored_filename='isolation-b-report-private.json',
    relative_path='private/isolation-b-report-private.json',
    mime_type='application/json',
    size_bytes=2,
    sha256='1' * 64,
    row_count=0,
    created_by=operator_b.id,
  )
  evidence_b = ManualEvidence(
    access_project_id=project_b.id,
    run_case_id=0,
    evidence_type='SCREENSHOT',
    original_filename='isolation-b-private.png',
    stored_filename='isolation-b-evidence-private.png',
    relative_path='private/isolation-b-evidence-private.png',
    mime_type='image/png',
    size_bytes=8,
    sha256='2' * 64,
    uploaded_by=operator_b.id,
  )
  db.add_all([run_b, defect_b, report_b, evidence_b]); db.flush()
  artifact_b = ExecutionArtifact(
    project_id=project_b.id,
    run_id=run_b.id,
    artifact_type='TRACE',
    original_filename='isolation-b-secret-token.txt',
    stored_filename='isolation-b-private.txt',
    relative_path='private/isolation-b-private.txt',
    mime_type='text/plain',
    size_bytes=8,
    sha256='0' * 64,
    safe=True,
  )
  db.add(artifact_b); db.commit(); db.refresh(artifact_b)
  headers = _login(auth_client, db, operator_a, 'isolation-a-token')

  project_ids = {item['id'] for item in auth_client.get('/api/projects').json()}
  assert project_a.id in project_ids
  assert project_b.id not in project_ids
  targets = auth_client.get('/api/connection-targets').json()['items']
  assert {item['id'] for item in targets} == {target_a.id}
  assert run_b.id not in {item['id'] for item in auth_client.get('/api/automated-runs').json()['items']}
  assert defect_b.id not in {item['id'] for item in auth_client.get('/api/defects').json()['items']}
  assert report_b.id not in {item['id'] for item in auth_client.get('/api/reports/exports').json()['items']}
  assert auth_client.get(f'/api/connection-targets/{target_b.id}').status_code == 404
  artifact_response = auth_client.get(f'/api/execution-artifacts/{artifact_b.id}/download')
  assert artifact_response.status_code == 404
  assert 'isolation-b-secret-token' not in artifact_response.text.lower()
  evidence_response = auth_client.get(f'/api/manual-evidence/{evidence_b.id}/download')
  assert evidence_response.status_code == 404
  assert 'isolation-b-private' not in evidence_response.text.lower()

  with pytest.raises(HTTPException) as relationship_denied:
    ProjectAccessService(db, operator_a.id).assert_same_project(project_a.id, project_b.id, 'TEST_PARENT')
  assert relationship_denied.value.status_code == 400
  assert db.scalar(select(AuditEvent).where(AuditEvent.action == 'PROJECT_RELATIONSHIP_DENIED')) is not None

  new_member = _operator(db, 'isolation-new-member', 'VIEWER')
  created = auth_client.post(
    f'/api/projects/{project_a.id}/members',
    json={'operator_id': new_member.id, 'role': 'VIEWER'},
    headers=headers,
  )
  assert created.status_code == 201
  updated = auth_client.patch(
    f'/api/projects/{project_a.id}/members/{created.json()["id"]}',
    json={'role': 'TESTER'},
    headers=headers,
  )
  assert updated.status_code == 200
  actions = set(db.scalars(select(AuditEvent.action).where(AuditEvent.action.like('PROJECT_MEMBERSHIP_%'))))
  assert {'PROJECT_MEMBERSHIP_CREATED', 'PROJECT_MEMBERSHIP_UPDATED'} <= actions
