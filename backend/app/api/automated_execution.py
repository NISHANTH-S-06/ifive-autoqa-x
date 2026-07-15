from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.auth import AuthContext, get_auth_context, require_csrf
from app.database import get_db
from app.models.automated_execution import AutomatedRun, AutomatedRunCase, AutomatedStepResult, ExecutionArtifact, ExecutionEvent, ExecutionJob, ExecutionWorker
from app.models.connection_target import ConnectionTarget
from app.models.operator import Operator
from app.schemas.automated_execution import (
  AcceptanceReadinessRead,
  AutomatedRunCaseRead,
  AutomatedRunCreate,
  AutomatedRunList,
  AutomatedRunRead,
  AutomatedStepResultRead,
  ExecutionArtifactRead,
  ExecutionEventRead,
  ExecutionPreflightRead,
  ExecutionWorkerRead,
  WorkerHeartbeat,
)
from app.schemas.test_management import Page
from app.services.audit_service import append_event
from app.services.automated_execution import (
  add_event,
  artifact_path,
  create_run,
  execute_next_job,
  heartbeat,
  preflight_run,
  progress,
  recover_stale_jobs,
)
from app.services.project_access import ProjectAccessService, ProjectAction

router = APIRouter(tags=['automated-execution'], dependencies=[Depends(get_auth_context)])


def _can_author(context: AuthContext) -> bool:
  return context.operator.role in {'TESTER', 'ADMIN'}


def _can_review(context: AuthContext) -> bool:
  return context.operator.role in {'APPROVER', 'ADMIN'}


def _get_run(db: Session, run_id: int, context: AuthContext | None = None, action: ProjectAction = ProjectAction.READ) -> AutomatedRun:
  run = db.scalar(select(AutomatedRun).options(selectinload(AutomatedRun.cases), selectinload(AutomatedRun.jobs)).where(AutomatedRun.id == run_id))
  if run is None:
    raise HTTPException(status_code=404, detail='Automated run not found.')
  run.progress = progress(run)
  return run


def _get_target(db: Session, target_id: int) -> ConnectionTarget:
  target = db.get(ConnectionTarget, target_id)
  if target is None:
    raise HTTPException(status_code=404, detail='Connection target not found.')
  return target


def _page(limit: int, offset: int, total: int) -> Page:
  return Page(limit=limit, offset=offset, total=total)


@router.get('/automated-runs', response_model=AutomatedRunList)
def list_automated_runs(status: str | None = None, limit: int = Query(50, ge=1, le=200), offset: int = Query(0, ge=0), context: AuthContext = Depends(get_auth_context), db: Session = Depends(get_db)):
  project_ids = ProjectAccessService(db, context.operator.id).project_ids()
  statement = select(AutomatedRun).where(AutomatedRun.project_id.in_(project_ids))
  count_statement = select(func.count(AutomatedRun.id)).where(AutomatedRun.project_id.in_(project_ids))
  if status:
    statement = statement.where(AutomatedRun.status == status.upper())
    count_statement = count_statement.where(AutomatedRun.status == status.upper())
  total = db.scalar(count_statement) or 0
  items = list(db.scalars(statement.order_by(AutomatedRun.created_at.desc(), AutomatedRun.id.desc()).offset(offset).limit(limit)))
  for item in items:
    item.progress = progress(item)
  return AutomatedRunList(items=items, page=_page(limit, offset, total))


@router.get('/automated-runs/readiness', response_model=AcceptanceReadinessRead)
def automated_acceptance_readiness(db: Session = Depends(get_db)):
  active_admin_count = db.scalar(select(func.count(Operator.id)).where(Operator.role == 'ADMIN', Operator.is_active.is_(True))) or 0
  return {
    'active_admin_count': active_admin_count,
    'admin_prerequisite_met': active_admin_count > 0,
    'real_target_authorized': False,
    'real_target_status': 'PENDING_EXPLICIT_NON_PRODUCTION_AUTHORIZATION',
    'dns_pinning_status': 'ENFORCED',
    'runtime_secret_status': 'PENDING_SAFE_EPHEMERAL_INPUT',
    'allowed_risk_levels': ['READ_ONLY', 'SAFE_INTERACTION'],
    'blocked_risk_levels': ['MUTATING', 'DESTRUCTIVE'],
  }


@router.post('/automated-runs', response_model=AutomatedRunRead, status_code=201)
def create_automated_run(payload: AutomatedRunCreate, context: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)):
  if not _can_author(context):
    raise HTTPException(status_code=403, detail='You do not have permission to perform this action.')
  target = _get_target(db, payload.target_id)
  ProjectAccessService(db, context.operator.id).require(target.project_id, ProjectAction.TEST)
  run = create_run(db, target, payload.name, payload.description, payload.case_ids, payload.timeout_seconds, payload.max_retries, context.operator.id, payload.runtime_secret_required)
  append_event(db, 'automated_run_created', operator_id=context.operator.id, resource_type='AUTOMATED_RUN', resource_id=str(run.id), metadata={'run_key': run.run_key})
  db.commit()
  return _get_run(db, run.id)


@router.get('/automated-runs/{run_id}', response_model=AutomatedRunRead)
def get_automated_run(run_id: int, context: AuthContext = Depends(get_auth_context), db: Session = Depends(get_db)):
  return _get_run(db, run_id, context)


@router.get('/automated-runs/{run_id}/preflight', response_model=ExecutionPreflightRead)
def get_automated_run_preflight(run_id: int, context: AuthContext = Depends(get_auth_context), db: Session = Depends(get_db)):
  run = _get_run(db, run_id, context)
  result = preflight_run(db, run, require_worker=True)
  db.commit()
  return result


@router.post('/automated-runs/{run_id}/submit', response_model=AutomatedRunRead)
def submit_automated_run(run_id: int, context: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)):
  run = _get_run(db, run_id, context, ProjectAction.TEST)
  if run.status != 'DRAFT':
    raise HTTPException(status_code=409, detail='Only draft automated runs can be submitted.')
  if context.operator.role != 'ADMIN' and run.created_by != context.operator.id:
    raise HTTPException(status_code=403, detail='Only the creator or ADMIN can submit this run.')
  run.status = 'SUBMITTED'; run.submitted_by = context.operator.id; run.submitted_at = datetime.utcnow()
  add_event(db, run.id, 'automated_run_submitted')
  append_event(db, 'automated_run_submitted', operator_id=context.operator.id, resource_type='AUTOMATED_RUN', resource_id=str(run.id), metadata={'run_key': run.run_key})
  db.commit()
  return _get_run(db, run.id)


@router.post('/automated-runs/{run_id}/approve', response_model=AutomatedRunRead)
def approve_automated_run(run_id: int, context: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)):
  if not _can_review(context):
    raise HTTPException(status_code=403, detail='You do not have permission to perform this action.')
  run = _get_run(db, run_id, context, ProjectAction.APPROVE)
  if run.status != 'SUBMITTED':
    raise HTTPException(status_code=409, detail='Only submitted automated runs can be approved.')
  if run.created_by == context.operator.id:
    append_event(db, 'automated_run_approval_denied', 'DENIED', context.operator.id, resource_type='AUTOMATED_RUN', resource_id=str(run.id), metadata={'reason': 'creator_separation'})
    db.commit()
    raise HTTPException(status_code=400, detail='Run creators cannot approve their own automated run.')
  target = _get_target(db, run.target_id)
  if target.version != run.target_version or not target.execution_enabled or target.environment_type == 'PRODUCTION':
    raise HTTPException(status_code=409, detail='Execution target is no longer approved for this run.')
  preflight = preflight_run(db, run, require_worker=False)
  if preflight['status'] != 'PASS':
    raise HTTPException(status_code=409, detail='Stage 11 preflight failed before run approval.')
  run.status = 'APPROVED'; run.approved_by = context.operator.id; run.approved_at = datetime.utcnow()
  add_event(db, run.id, 'automated_run_approved')
  append_event(db, 'automated_run_approved', operator_id=context.operator.id, resource_type='AUTOMATED_RUN', resource_id=str(run.id), metadata={'run_key': run.run_key})
  db.commit()
  return _get_run(db, run.id)


@router.post('/automated-runs/{run_id}/queue', response_model=AutomatedRunRead)
def queue_automated_run(run_id: int, context: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)):
  if not _can_review(context):
    raise HTTPException(status_code=403, detail='You do not have permission to perform this action.')
  recover_stale_jobs(db)
  run = _get_run(db, run_id, context, ProjectAction.APPROVE)
  if run.status != 'APPROVED':
    raise HTTPException(status_code=409, detail='Only approved automated runs can be queued.')
  target = _get_target(db, run.target_id)
  if target.environment_type == 'PRODUCTION' or not target.execution_enabled or target.version != run.target_version:
    raise HTTPException(status_code=409, detail='Execution target is not valid for queueing.')
  preflight = preflight_run(db, run, require_worker=True)
  if preflight['status'] != 'PASS':
    raise HTTPException(status_code=409, detail='Stage 11 preflight failed before queueing.')
  run.status = 'QUEUED'; run.queued_by = context.operator.id; run.queued_at = datetime.utcnow()
  db.add(ExecutionJob(project_id=run.project_id, run_id=run.id, status='QUEUED'))
  try:
    db.flush()
  except IntegrityError:
    db.rollback()
    raise HTTPException(status_code=409, detail='Automated run is already queued.') from None
  add_event(db, run.id, 'automated_run_queued')
  append_event(db, 'automated_run_queued', operator_id=context.operator.id, resource_type='AUTOMATED_RUN', resource_id=str(run.id), metadata={'run_key': run.run_key})
  db.commit()
  return _get_run(db, run.id)


@router.post('/automated-runs/{run_id}/cancel', response_model=AutomatedRunRead)
def cancel_automated_run(run_id: int, context: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)):
  if context.operator.role not in {'TESTER', 'APPROVER', 'ADMIN'}:
    raise HTTPException(status_code=403, detail='You do not have permission to perform this action.')
  run = _get_run(db, run_id, context, ProjectAction.TEST)
  if run.status in {'PASSED', 'FAILED', 'CANCELLED', 'TIMED_OUT', 'BLOCKED'}:
    raise HTTPException(status_code=409, detail='Terminal automated runs cannot be cancelled.')
  run.status = 'CANCELLED'; run.cancelled_by = context.operator.id; run.cancelled_at = datetime.utcnow(); run.completed_at = datetime.utcnow(); run.failure_classification = 'CANCELLED'; run.safe_error_message = 'Automated run was cancelled.'
  for job in run.jobs:
    if job.status in {'QUEUED', 'RUNNING'}:
      job.status = 'CANCELLED'; job.lease_owner = None; job.lease_expires_at = None
  add_event(db, run.id, 'automated_run_cancelled', 'WARN')
  append_event(db, 'automated_run_cancelled', operator_id=context.operator.id, resource_type='AUTOMATED_RUN', resource_id=str(run.id), metadata={'run_key': run.run_key})
  db.commit()
  return _get_run(db, run.id)


@router.post('/automated-runs/{run_id}/retry', response_model=AutomatedRunRead)
def retry_automated_run(run_id: int, context: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)):
  if not _can_review(context):
    raise HTTPException(status_code=403, detail='You do not have permission to perform this action.')
  run = _get_run(db, run_id, context, ProjectAction.APPROVE)
  if run.status not in {'FAILED', 'TIMED_OUT', 'BLOCKED'}:
    raise HTTPException(status_code=409, detail='Only failed, blocked, or timed-out automated runs can be retried.')
  if run.attempt_count > run.max_retries:
    raise HTTPException(status_code=409, detail='Automated run retry limit reached.')
  run.status = 'QUEUED'; run.completed_at = None; run.failure_classification = None; run.safe_error_message = None; run.completed_steps = 0; run.failed_steps = 0
  for run_case in run.cases:
    run_case.status = 'NOT_RUN'; run_case.failure_classification = None; run_case.safe_error_message = None; run_case.started_at = None; run_case.completed_at = None
  job = run.jobs[0] if run.jobs else None
  if job is None:
    job = ExecutionJob(project_id=run.project_id, run_id=run.id)
    db.add(job)
  job.status = 'QUEUED'; job.lease_owner = None; job.lease_expires_at = None
  add_event(db, run.id, 'automated_run_retry_queued')
  append_event(db, 'automated_run_retry_queued', operator_id=context.operator.id, resource_type='AUTOMATED_RUN', resource_id=str(run.id), metadata={'run_key': run.run_key})
  db.commit()
  return _get_run(db, run.id)


@router.get('/automated-runs/{run_id}/cases', response_model=list[AutomatedRunCaseRead])
def list_run_cases(run_id: int, context: AuthContext = Depends(get_auth_context), db: Session = Depends(get_db)):
  _get_run(db, run_id, context)
  return list(db.scalars(select(AutomatedRunCase).where(AutomatedRunCase.run_id == run_id).order_by(AutomatedRunCase.sort_order)))


@router.get('/automated-runs/{run_id}/steps', response_model=list[AutomatedStepResultRead])
def list_run_steps(run_id: int, context: AuthContext = Depends(get_auth_context), db: Session = Depends(get_db)):
  _get_run(db, run_id, context)
  return list(db.scalars(select(AutomatedStepResult).join(AutomatedRunCase).where(AutomatedRunCase.run_id == run_id).order_by(AutomatedRunCase.sort_order, AutomatedStepResult.step_number)))


@router.get('/automated-runs/{run_id}/events', response_model=list[ExecutionEventRead])
def list_run_events(run_id: int, context: AuthContext = Depends(get_auth_context), db: Session = Depends(get_db)):
  _get_run(db, run_id, context)
  return list(db.scalars(select(ExecutionEvent).where(ExecutionEvent.run_id == run_id).order_by(ExecutionEvent.created_at)))


@router.get('/automated-runs/{run_id}/artifacts', response_model=list[ExecutionArtifactRead])
def list_run_artifacts(run_id: int, context: AuthContext = Depends(get_auth_context), db: Session = Depends(get_db)):
  _get_run(db, run_id, context)
  return list(db.scalars(select(ExecutionArtifact).where(ExecutionArtifact.run_id == run_id).order_by(ExecutionArtifact.created_at.desc())))


@router.get('/execution-artifacts/{artifact_id}/download')
def download_execution_artifact(artifact_id: int, context: AuthContext = Depends(get_auth_context), db: Session = Depends(get_db)):
  item = db.get(ExecutionArtifact, artifact_id)
  if item is None or not item.safe:
    raise HTTPException(status_code=404, detail='Artifact not found.')
  ProjectAccessService(db, context.operator.id).require(item.project_id)
  path = artifact_path(item)
  if not path.is_file():
    raise HTTPException(status_code=404, detail='Artifact file is unavailable.')
  append_event(db, 'execution_artifact_downloaded', operator_id=context.operator.id, resource_type='EXECUTION_ARTIFACT', resource_id=str(item.id))
  db.commit()
  return FileResponse(path, media_type=item.mime_type, filename=item.original_filename)


@router.get('/execution-workers', response_model=list[ExecutionWorkerRead])
def list_workers(db: Session = Depends(get_db)):
  return list(db.scalars(select(ExecutionWorker).order_by(ExecutionWorker.heartbeat_at.desc())))


@router.post('/execution-workers/heartbeat', response_model=ExecutionWorkerRead)
def worker_heartbeat(payload: WorkerHeartbeat, context: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)):
  if context.operator.role not in {'APPROVER', 'ADMIN'}:
    raise HTTPException(status_code=403, detail='You do not have permission to perform this action.')
  worker = heartbeat(db, payload.worker_key)
  append_event(db, 'execution_worker_heartbeat', operator_id=context.operator.id, resource_type='EXECUTION_WORKER', resource_id=payload.worker_key)
  db.commit(); db.refresh(worker); return worker


@router.post('/execution-workers/run-next', response_model=AutomatedRunRead | None)
def run_next_worker_job(payload: WorkerHeartbeat, context: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)):
  if context.operator.role not in {'APPROVER', 'ADMIN'}:
    raise HTTPException(status_code=403, detail='You do not have permission to perform this action.')
  run = execute_next_job(db, payload.worker_key)
  append_event(db, 'execution_worker_run_next', operator_id=context.operator.id, resource_type='EXECUTION_WORKER', resource_id=payload.worker_key, metadata={'run_id': run.id if run else None})
  db.commit()
  return _get_run(db, run.id) if run else None
  if context is not None:
    ProjectAccessService(db, context.operator.id).require(run.project_id, action)
  ProjectAccessService(db, context.operator.id).require(item.project_id)
