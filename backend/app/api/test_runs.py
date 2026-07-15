from datetime import datetime
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import AuthContext, get_auth_context, require_csrf
from app.repositories.project_repository import ProjectRepository
from app.repositories.result_repository import ResultRepository
from app.repositories.run_repository import RunRepository
from app.schemas.result import EvidenceRead
from app.schemas.test_run import ApprovalRequest, ExecuteRequest, TestRunDetail, TestRunRead, TestRunRequest, TestRunStatus
from app.security import SafetyViolation, validate_environment
from app.services.playwright_runner import PROJECT_ROOT, RUNS_ROOT, PlaywrightRunner, RunnerValidationError, get_runner, sanitize_run_code
from app.services.suite_registry import get_allowed_suite
from app.services.audit_service import append_event

router = APIRouter(prefix='/test-runs', tags=['test-runs'], dependencies=[Depends(get_auth_context)])
TERMINAL = {TestRunStatus.PASSED.value, TestRunStatus.FAILED.value, TestRunStatus.CANCELLED.value}


def _get_run(run_id: int, db: Session):
  run = RunRepository(db).get(run_id)
  if run is None:
    raise HTTPException(status_code=404, detail='Test run not found.')
  return run


def _validate_local_scope(run) -> None:
  if run.project.product_code != 'AUTOQA' or run.environment != 'local':
    raise HTTPException(status_code=400, detail='Only local AutoQA suites can be executed in Stage 4.')
  if get_allowed_suite(run.suite_name) is None:
    raise HTTPException(status_code=400, detail='Test suite is not approved for local execution.')


@router.get('', response_model=list[TestRunRead])
def list_test_runs(project_id: int | None = None, status: TestRunStatus | None = None, limit: int = Query(default=50, ge=1, le=200), db: Session = Depends(get_db)):
  return RunRepository(db).list(project_id=project_id, status=status, limit=limit)


@router.get('/{run_id}', response_model=TestRunDetail)
def get_test_run(run_id: int, db: Session = Depends(get_db)):
  return _get_run(run_id, db)


@router.post('', response_model=TestRunRead, status_code=201)
def queue_test_run(request: TestRunRequest, context: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)):
  if context.operator.role not in ('TESTER', 'ADMIN'):
    raise HTTPException(status_code=403, detail='You do not have permission to perform this action.')
  if request.environment.strip().lower() == 'production':
    raise HTTPException(status_code=400, detail='Production test execution is disabled.')
  try: validate_environment(request.environment)
  except SafetyViolation as exc: raise HTTPException(status_code=400, detail=str(exc)) from None
  if ProjectRepository(db).get(request.project_id) is None:
    raise HTTPException(status_code=404, detail='Project not found.')
  run = RunRepository(db).create(request, f'RUN-{uuid4().hex[:12].upper()}', context.operator.id)
  append_event(db, 'TEST_RUN_CREATED', operator_id=context.operator.id, resource_type='TEST_RUN', resource_id=str(run.id), metadata={'suite': run.suite_name, 'environment': run.environment}); db.commit()
  return run


@router.post('/{run_id}/approve', response_model=TestRunDetail)
def approve_test_run(run_id: int, request: ApprovalRequest, context: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)):
  if context.operator.role not in ('APPROVER', 'ADMIN'):
    raise HTTPException(status_code=403, detail='You do not have permission to perform this action.')
  run = _get_run(run_id, db)
  if run.created_by_operator_id == context.operator.id:
    append_event(db, 'TEST_RUN_APPROVAL_DENIED', 'DENIED', context.operator.id, resource_type='TEST_RUN', resource_id=str(run.id), metadata={'reason': 'creator_separation'}); db.commit()
    raise HTTPException(status_code=400, detail='Run creators cannot approve their own test runs.')
  if request.confirmation != 'APPROVE LOCAL TEST EXECUTION':
    raise HTTPException(status_code=400, detail='Exact local execution confirmation is required.')
  if run.status != TestRunStatus.QUEUED.value:
    raise HTTPException(status_code=409, detail='Only queued test runs can be approved.')
  _validate_local_scope(run)
  approved = RunRepository(db).set_status(run, TestRunStatus.APPROVED, approved_at=datetime.utcnow(), approved_by_operator_id=context.operator.id)
  append_event(db, 'TEST_RUN_APPROVED', operator_id=context.operator.id, resource_type='TEST_RUN', resource_id=str(run.id)); db.commit(); return approved


@router.post('/{run_id}/execute', status_code=202)
def execute_test_run(run_id: int, request: ExecuteRequest, context: AuthContext = Depends(require_csrf), db: Session = Depends(get_db), local_runner: PlaywrightRunner = Depends(get_runner)):
  if context.operator.role not in ('APPROVER', 'ADMIN'):
    raise HTTPException(status_code=403, detail='You do not have permission to perform this action.')
  run = _get_run(run_id, db)
  if not request.confirm_local_execution:
    raise HTTPException(status_code=400, detail='Local execution confirmation is required.')
  if run.status in TERMINAL:
    raise HTTPException(status_code=409, detail='Completed test runs cannot be executed again.')
  if run.status != TestRunStatus.APPROVED.value:
    raise HTTPException(status_code=409, detail='Run approval is required before execution.')
  _validate_local_scope(run)
  if RunRepository(db).running_count(exclude_run_id=run.id) or local_runner.is_active(run.id):
    raise HTTPException(status_code=409, detail='Another local test run is already executing.')
  try:
    local_runner.validate_run(run)
    run.executed_by_operator_id = context.operator.id; db.commit()
    local_runner.start(run.id)
  except RunnerValidationError as exc:
    raise HTTPException(status_code=409, detail=str(exc)) from None
  append_event(db, 'TEST_RUN_EXECUTION_STARTED', operator_id=context.operator.id, resource_type='TEST_RUN', resource_id=str(run.id)); db.commit()
  return {'run_id': run.id, 'status': 'ACCEPTED', 'message': 'Local execution accepted.'}


@router.post('/{run_id}/cancel', response_model=TestRunDetail)
def cancel_test_run(run_id: int, context: AuthContext = Depends(require_csrf), db: Session = Depends(get_db), local_runner: PlaywrightRunner = Depends(get_runner)):
  if context.operator.role not in ('APPROVER', 'ADMIN'):
    raise HTTPException(status_code=403, detail='You do not have permission to perform this action.')
  run = _get_run(run_id, db)
  if run.status not in (TestRunStatus.APPROVED.value, TestRunStatus.RUNNING.value):
    raise HTTPException(status_code=409, detail='Only approved or running test runs can be cancelled.')
  if run.status == TestRunStatus.RUNNING.value:
    local_runner.cancel(run.id)
  cancelled = RunRepository(db).set_status(run, TestRunStatus.CANCELLED, completed_at=datetime.utcnow(), error_summary=None, cancelled_by_operator_id=context.operator.id)
  append_event(db, 'TEST_RUN_CANCELLED', operator_id=context.operator.id, resource_type='TEST_RUN', resource_id=str(run.id)); db.commit(); return cancelled


@router.get('/{run_id}/evidence', response_model=list[EvidenceRead])
def list_evidence(run_id: int, context: AuthContext = Depends(get_auth_context), db: Session = Depends(get_db)):
  _get_run(run_id, db)
  items = ResultRepository(db).evidence_by_run(run_id); append_event(db, 'EVIDENCE_VIEWED', operator_id=context.operator.id, resource_type='TEST_RUN', resource_id=str(run_id)); db.commit(); return items


@router.get('/{run_id}/evidence/{evidence_id}')
def download_evidence(run_id: int, evidence_id: int, context: AuthContext = Depends(get_auth_context), db: Session = Depends(get_db)):
  run = _get_run(run_id, db)
  evidence = ResultRepository(db).get_evidence(run_id, evidence_id)
  if evidence is None:
    raise HTTPException(status_code=404, detail='Evidence not found for this test run.')
  try:
    run_root = (RUNS_ROOT / sanitize_run_code(run.run_code)).resolve()
    path = (PROJECT_ROOT / evidence.relative_path).resolve()
    path.relative_to(run_root)
  except (ValueError, RunnerValidationError):
    raise HTTPException(status_code=400, detail='Invalid evidence path.') from None
  if not path.is_file():
    raise HTTPException(status_code=404, detail='Evidence file is unavailable.')
  append_event(db, 'EVIDENCE_DOWNLOADED', operator_id=context.operator.id, resource_type='EVIDENCE', resource_id=str(evidence.id)); db.commit()
  return FileResponse(path, filename=path.name)
