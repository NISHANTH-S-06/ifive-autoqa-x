import json
import re
from datetime import datetime
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.automated_execution import AutomatedRun, AutomatedRunCase, AutomatedStepResult, ExecutionArtifact
from app.models.connection_target import ConnectionTarget
from app.models.defect import Defect, DefectComment, DefectEvidenceLink, DefectHistory, DefectRetest
from app.models.operator import Operator
from app.models.test_management import (
  ManagedTestCase,
  ManagedTestSuite,
  ManualEvidence,
  ManualStepResult,
  ManualTestRun,
  ManualTestRunCase,
  TestCaseVersion,
  TestModule,
  TestProject,
)
from app.schemas.defect import DefectCreate, DefectFromRunCreate, DefectTransition, DefectUpdate
from app.services.test_management import next_run_key, reject_secret_like

OPEN_DUPLICATE_STATES = {'NEW', 'TRIAGED', 'ASSIGNED', 'IN_PROGRESS', 'FIXED', 'READY_FOR_RETEST', 'REOPENED'}
VALID_TRANSITIONS = {
  'NEW': {'TRIAGED', 'REJECTED', 'DUPLICATE'},
  'TRIAGED': {'ASSIGNED', 'REJECTED', 'DUPLICATE'},
  'ASSIGNED': {'IN_PROGRESS', 'REJECTED', 'DUPLICATE'},
  'IN_PROGRESS': {'FIXED', 'REJECTED', 'DUPLICATE'},
  'FIXED': {'READY_FOR_RETEST', 'REJECTED', 'DUPLICATE'},
  'READY_FOR_RETEST': {'RETEST_PASSED', 'REOPENED', 'REJECTED', 'DUPLICATE'},
  'RETEST_PASSED': {'CLOSED', 'REJECTED', 'DUPLICATE'},
  'REOPENED': {'ASSIGNED', 'IN_PROGRESS', 'REJECTED', 'DUPLICATE'},
  'CLOSED': set(),
  'REJECTED': set(),
  'DUPLICATE': set(),
}
SECRET_PATTERN = re.compile(r'(?i)(bearer\s+[a-z0-9._-]+|password\s*[:=]|token\s*[:=]|csrf|autoqa_session|authorization\s*[:=]|secret\s*[:=]|cookie\s*[:=])')


def next_defect_key(db: Session) -> str:
  return f'DEF-{(db.scalar(select(func.count(Defect.id))) or 0) + 1:05d}-{uuid4().hex[:6].upper()}'


def safe_text(value, max_length: int = 5000) -> str | None:
  if value is None:
    return None
  text = str(value).strip()[:max_length]
  if SECRET_PATTERN.search(text):
    raise HTTPException(status_code=422, detail='Defect content must not contain credential-like content.')
  return text


def ensure_operator(db: Session, operator_id: int | None) -> Operator | None:
  if operator_id is None:
    return None
  operator = db.get(Operator, operator_id)
  if operator is None or not operator.is_active:
    raise HTTPException(status_code=422, detail='Assigned operator must be active.')
  return operator


def can_create(role: str) -> bool:
  return role in {'TESTER', 'ADMIN'}


def can_review(role: str) -> bool:
  return role in {'APPROVER', 'ADMIN'}


def add_history(db: Session, defect: Defect, event_type: str, operator_id: int, old_value=None, new_value=None, message: str | None = None) -> DefectHistory:
  item = DefectHistory(project_id=defect.access_project_id, defect_id=defect.id, event_type=event_type, old_value=safe_text(old_value, 500), new_value=safe_text(new_value, 500), safe_message=safe_text(message, 500), created_by=operator_id)
  db.add(item)
  return item


def _project_scope(db: Session, project_id: int, module_id: int | None, suite_id: int | None, case_id: int | None) -> None:
  project = db.get(TestProject, project_id)
  if project is None:
    raise HTTPException(status_code=404, detail='Project not found.')
  if module_id is not None:
    module = db.get(TestModule, module_id)
    if module is None or module.project_id != project_id:
      raise HTTPException(status_code=422, detail='Module does not belong to the selected project.')
  if suite_id is not None:
    suite = db.get(ManagedTestSuite, suite_id)
    if suite is None or suite.project_id != project_id or (module_id is not None and suite.module_id != module_id):
      raise HTTPException(status_code=422, detail='Suite does not belong to the selected project/module.')
  if case_id is not None:
    case = db.get(ManagedTestCase, case_id)
    if case is None or case.project_id != project_id or (module_id is not None and case.module_id != module_id) or (suite_id is not None and case.suite_id != suite_id):
      raise HTTPException(status_code=422, detail='Test case does not belong to the selected project/module/suite.')


def create_defect(db: Session, payload: DefectCreate, reporter_id: int) -> Defect:
  ensure_operator(db, payload.assigned_to)
  _project_scope(db, payload.project_id, payload.module_id, payload.suite_id, payload.test_case_id)
  if payload.test_case_id and payload.test_case_version:
    version = db.scalar(select(TestCaseVersion).where(TestCaseVersion.test_case_id == payload.test_case_id, TestCaseVersion.version_number == payload.test_case_version))
    if version is None:
      raise HTTPException(status_code=422, detail='Frozen test-case version does not exist.')
  defect = Defect(
    access_project_id=db.get(TestProject, payload.project_id).access_project_id,
    defect_key=next_defect_key(db),
    title=safe_text(payload.title, 220) or '',
    description=safe_text(payload.description),
    project_id=payload.project_id,
    module_id=payload.module_id,
    suite_id=payload.suite_id,
    test_case_id=payload.test_case_id,
    test_case_version=payload.test_case_version,
    severity=payload.severity.value,
    priority=payload.priority.value,
    assigned_to=payload.assigned_to,
    reporter_id=reporter_id,
    created_by=reporter_id,
    environment=safe_text(payload.environment, 80),
    failure_category=safe_text(payload.failure_category, 80),
    expected_result=safe_text(payload.expected_result),
    actual_result=safe_text(payload.actual_result),
    reproduction_steps=safe_text(payload.reproduction_steps),
  )
  db.add(defect); db.flush()
  add_history(db, defect, 'CREATED', reporter_id, new_value=defect.status)
  return defect


def possible_duplicates(db: Session, **keys) -> list[Defect]:
  filters = [Defect.status.in_(OPEN_DUPLICATE_STATES)]
  source_filters = []
  for field in ['manual_step_result_id', 'automated_step_result_id', 'manual_run_case_id', 'automated_run_case_id', 'automated_run_id']:
    value = keys.get(field)
    if value is not None:
      source_filters.append(getattr(Defect, field) == value)
      break
  if not source_filters:
    return []
  return list(db.scalars(select(Defect).where(*filters).where(or_(*source_filters)).order_by(Defect.updated_at.desc()).limit(5)))


def source_payload(db: Session, payload: DefectFromRunCreate) -> tuple[DefectCreate, dict, list[ManualEvidence], list[ExecutionArtifact]]:
  manual_evidence: list[ManualEvidence] = []
  execution_artifacts: list[ExecutionArtifact] = []
  if payload.source_type.value in {'MANUAL_RUN_CASE', 'MANUAL_STEP'}:
    run_case = db.get(ManualTestRunCase, payload.manual_run_case_id)
    if run_case is None:
      raise HTTPException(status_code=404, detail='Manual run case not found.')
    if run_case.status not in {'FAILED', 'BLOCKED'}:
      raise HTTPException(status_code=409, detail='Manual defects can only be created from failed or blocked results.')
    run = db.get(ManualTestRun, run_case.run_id)
    case = db.get(ManagedTestCase, run_case.test_case_id)
    step = db.get(ManualStepResult, payload.manual_step_result_id) if payload.manual_step_result_id else None
    if step and step.run_case_id != run_case.id:
      raise HTTPException(status_code=422, detail='Manual step result is outside the selected run case.')
    manual_evidence = list(db.scalars(select(ManualEvidence).where(ManualEvidence.run_case_id == run_case.id, ManualEvidence.deleted_at.is_(None))))
    create = DefectCreate(
      title=payload.title or f'Manual failure {run.run_key if run else run_case.id}',
      project_id=run.project_id,
      module_id=case.module_id if case else None,
      suite_id=run.suite_id,
      test_case_id=run_case.test_case_id,
      test_case_version=run_case.test_case_version,
      severity=payload.severity,
      priority=payload.priority,
      assigned_to=payload.assigned_to,
      environment='LOCAL',
      failure_category=run_case.status,
      expected_result=step.notes if step else None,
      actual_result=step.actual_result if step else run_case.actual_result,
      reproduction_steps=run_case.notes,
    )
    keys = {'manual_run_id': run.id if run else None, 'manual_run_case_id': run_case.id, 'manual_step_result_id': step.id if step else None}
    return create, keys, manual_evidence, execution_artifacts

  if payload.source_type.value in {'AUTOMATED_RUN', 'AUTOMATED_RUN_CASE', 'AUTOMATED_STEP'}:
    run = db.get(AutomatedRun, payload.automated_run_id)
    run_case = db.get(AutomatedRunCase, payload.automated_run_case_id) if payload.automated_run_case_id else None
    step = db.get(AutomatedStepResult, payload.automated_step_result_id) if payload.automated_step_result_id else None
    if run is None and run_case is not None:
      run = db.get(AutomatedRun, run_case.run_id)
    if run is None and step is not None:
      run_case = db.get(AutomatedRunCase, step.run_case_id)
      run = db.get(AutomatedRun, run_case.run_id) if run_case else None
    if run is None:
      raise HTTPException(status_code=404, detail='Automated run not found.')
    if run.status not in {'FAILED', 'TIMED_OUT', 'BLOCKED'} and not (run_case and run_case.status in {'FAILED', 'BLOCKED'}) and not (step and step.status in {'FAILED', 'BLOCKED'}):
      raise HTTPException(status_code=409, detail='Automated defects can only be created from failed, timed-out, or policy-blocked results.')
    if run_case and run_case.run_id != run.id:
      raise HTTPException(status_code=422, detail='Automated run case is outside the selected run.')
    if step and (run_case is None or step.run_case_id != run_case.id):
      raise HTTPException(status_code=422, detail='Automated step result is outside the selected run case.')
    case = db.get(ManagedTestCase, run_case.test_case_id) if run_case else None
    target = db.get(ConnectionTarget, run.target_id)
    execution_artifacts = list(db.scalars(select(ExecutionArtifact).where(ExecutionArtifact.run_id == run.id, ExecutionArtifact.safe.is_(True))))
    create = DefectCreate(
      title=payload.title or f'Automated failure {run.run_key}',
      project_id=case.project_id if case else 1,
      module_id=case.module_id if case else None,
      suite_id=case.suite_id if case else None,
      test_case_id=run_case.test_case_id if run_case else None,
      test_case_version=run_case.test_case_version if run_case else None,
      severity=payload.severity,
      priority=payload.priority,
      assigned_to=payload.assigned_to,
      environment=target.environment_type if target else 'LOCAL',
      failure_category=step.failure_classification if step else run.failure_classification or run.status,
      expected_result=step.expected_redacted if step else None,
      actual_result=step.safe_error_message if step else run.safe_error_message,
      reproduction_steps=json.dumps({'run_key': run.run_key, 'target_version': run.target_version}, separators=(',', ':')),
    )
    keys = {'automated_run_id': run.id, 'automated_run_case_id': run_case.id if run_case else None, 'automated_step_result_id': step.id if step else None}
    return create, keys, manual_evidence, execution_artifacts
  raise HTTPException(status_code=422, detail='Unsupported defect source.')


def create_from_run(db: Session, payload: DefectFromRunCreate, reporter_id: int):
  create, keys, manual_evidence, execution_artifacts = source_payload(db, payload)
  duplicates = possible_duplicates(db, **keys)
  if not payload.confirm:
    return {'requires_confirmation': True, 'possible_existing': duplicates}
  if duplicates:
    raise HTTPException(status_code=409, detail='A possible existing defect already links this failure.')
  defect = create_defect(db, create, reporter_id)
  for key, value in keys.items():
    setattr(defect, key, value)
  for item in manual_evidence:
    db.add(DefectEvidenceLink(project_id=defect.access_project_id, defect_id=defect.id, manual_evidence_id=item.id, link_type='SOURCE', created_by=reporter_id))
  for item in execution_artifacts:
    db.add(DefectEvidenceLink(project_id=defect.access_project_id, defect_id=defect.id, execution_artifact_id=item.id, link_type='SOURCE', created_by=reporter_id))
  add_history(db, defect, 'SOURCE_LINKED', reporter_id, new_value=payload.source_type.value)
  return defect


def update_defect(db: Session, defect: Defect, payload: DefectUpdate, operator_id: int) -> Defect:
  for key, value in payload.model_dump(exclude_unset=True).items():
    old = getattr(defect, key)
    new = value.value if hasattr(value, 'value') else value
    if key == 'assigned_to':
      ensure_operator(db, new)
    if isinstance(new, str):
      new = safe_text(new)
    if old != new:
      setattr(defect, key, new)
      add_history(db, defect, f'{key.upper()}_CHANGED', operator_id, old, new)
  defect.updated_at = datetime.utcnow()
  return defect


def transition_defect(db: Session, defect: Defect, target_status: str, payload: DefectTransition, operator: Operator) -> Defect:
  if target_status not in VALID_TRANSITIONS.get(defect.status, set()):
    raise HTTPException(status_code=409, detail='Invalid defect lifecycle transition.')
  if target_status in {'TRIAGED', 'ASSIGNED', 'FIXED', 'READY_FOR_RETEST', 'CLOSED', 'REJECTED', 'DUPLICATE'} and not can_review(operator.role):
    raise HTTPException(status_code=403, detail='You do not have permission to perform this action.')
  if target_status == 'IN_PROGRESS' and operator.role not in {'TESTER', 'APPROVER', 'ADMIN'}:
    raise HTTPException(status_code=403, detail='You do not have permission to perform this action.')
  if target_status == 'CLOSED':
    if defect.reporter_id == operator.id and operator.role != 'ADMIN':
      raise HTTPException(status_code=400, detail='Reporters cannot close their own defect.')
    if not payload.resolution or not payload.resolution.strip():
      raise HTTPException(status_code=422, detail='Closing requires a resolution.')
    defect.resolution = safe_text(payload.resolution, 2000)
    defect.closed_at = datetime.utcnow()
  if target_status == 'REJECTED':
    if not payload.reason or not payload.reason.strip():
      raise HTTPException(status_code=422, detail='Rejection requires a reason.')
    defect.resolution = safe_text(payload.reason, 2000)
    defect.closed_at = datetime.utcnow()
  if target_status == 'DUPLICATE':
    if not payload.duplicate_of_defect_id:
      raise HTTPException(status_code=422, detail='Duplicate requires an original defect reference.')
    original = db.get(Defect, payload.duplicate_of_defect_id)
    if original is None or original.id == defect.id or original.project_id != defect.project_id:
      raise HTTPException(status_code=422, detail='Original defect must exist in the same project.')
    defect.duplicate_of_defect_id = original.id
    defect.closed_at = datetime.utcnow()
  if target_status == 'REOPENED':
    if not payload.reason or not payload.reason.strip():
      raise HTTPException(status_code=422, detail='Reopen requires a reason.')
    defect.resolution = safe_text(payload.reason, 2000)
  if target_status == 'ASSIGNED':
    ensure_operator(db, payload.assigned_to)
    defect.assigned_to = payload.assigned_to
  old = defect.status
  defect.status = target_status
  defect.updated_at = datetime.utcnow()
  add_history(db, defect, 'STATUS_CHANGED', operator.id, old, target_status, payload.reason or payload.resolution)
  return defect


def add_comment(db: Session, defect: Defect, body: str, operator_id: int) -> DefectComment:
  reject_secret_like(body, 'Defect comment')
  comment = DefectComment(project_id=defect.access_project_id, defect_id=defect.id, body=safe_text(body) or '', created_by=operator_id)
  db.add(comment)
  add_history(db, defect, 'COMMENT_ADDED', operator_id)
  defect.updated_at = datetime.utcnow()
  return comment


def create_retest(db: Session, defect: Defect, payload, operator: Operator) -> DefectRetest:
  if operator.role not in {'TESTER', 'ADMIN'}:
    raise HTTPException(status_code=403, detail='You do not have permission to perform this action.')
  if defect.status != 'READY_FOR_RETEST':
    raise HTTPException(status_code=409, detail='Retest evidence can only be recorded after the defect is ready for retest.')
  result_status = payload.result_status.upper()
  if result_status not in {'PLANNED', 'PASSED', 'FAILED', 'BLOCKED'}:
    raise HTTPException(status_code=422, detail='Unsupported retest result status.')
  reject_secret_like(payload.notes, 'Retest notes')
  version_number = defect.test_case_version
  if payload.use_latest_approved_version and defect.test_case_id:
    case = db.get(ManagedTestCase, defect.test_case_id)
    if case is None or case.lifecycle_state != 'APPROVED':
      raise HTTPException(status_code=409, detail='No approved newer test-case version is available.')
    version_number = case.current_version
  manual_run_id = None
  if defect.test_case_id and defect.suite_id:
    run = ManualTestRun(access_project_id=defect.access_project_id, run_key=next_run_key(db), project_id=defect.project_id, suite_id=defect.suite_id, name=f'Retest {defect.defect_key}', description='Defect retest run', assigned_to=operator.id, created_by=operator.id)
    db.add(run); db.flush()
    db.add(ManualTestRunCase(access_project_id=defect.access_project_id, run_id=run.id, test_case_id=defect.test_case_id, test_case_version=version_number or defect.test_case_version or 1, assigned_to=operator.id))
    manual_run_id = run.id
  retest = DefectRetest(project_id=defect.access_project_id, defect_id=defect.id, manual_run_id=manual_run_id, test_case_id=defect.test_case_id, test_case_version=version_number, target_id=defect.target_id, target_version=defect.target_version, result_status=result_status, safe_notes=safe_text(payload.notes, 2000), created_by=operator.id)
  db.add(retest)
  old = defect.status
  if retest.result_status == 'PASSED':
    defect.status = 'RETEST_PASSED'
  elif retest.result_status in {'FAILED', 'BLOCKED'}:
    defect.status = 'REOPENED'
  defect.updated_at = datetime.utcnow()
  add_history(db, defect, 'RETEST_RECORDED', operator.id, old, defect.status, payload.notes)
  return retest


def traceability(db: Session, defect: Defect) -> dict:
  return {
    'defect': {'id': defect.id, 'defect_key': defect.defect_key, 'status': defect.status},
    'project': _safe_row(db.get(TestProject, defect.project_id), ['id', 'code', 'name', 'status']),
    'module': _safe_row(db.get(TestModule, defect.module_id), ['id', 'code', 'name', 'status']) if defect.module_id else None,
    'suite': _safe_row(db.get(ManagedTestSuite, defect.suite_id), ['id', 'code', 'name', 'status']) if defect.suite_id else None,
    'test_case': _safe_row(db.get(ManagedTestCase, defect.test_case_id), ['id', 'case_key', 'title', 'status', 'lifecycle_state']) if defect.test_case_id else None,
    'test_case_version': defect.test_case_version,
    'manual_run_id': defect.manual_run_id,
    'manual_run_case_id': defect.manual_run_case_id,
    'manual_step_result_id': defect.manual_step_result_id,
    'automated_run_id': defect.automated_run_id,
    'automated_run_case_id': defect.automated_run_case_id,
    'automated_step_result_id': defect.automated_step_result_id,
    'evidence_links': [{'manual_evidence_id': item.manual_evidence_id, 'execution_artifact_id': item.execution_artifact_id} for item in defect.evidence_links],
    'retests': [{'manual_run_id': item.manual_run_id, 'result_status': item.result_status, 'test_case_version': item.test_case_version} for item in defect.retests],
  }


def _safe_row(item, fields: list[str]) -> dict | None:
  if item is None:
    return None
  return {field: getattr(item, field) for field in fields}
