from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.auth import AuthContext, get_auth_context, require_csrf
from app.database import get_db
from app.models.defect import Defect, DefectComment, DefectEvidenceLink, DefectHistory, DefectRetest
from app.models.test_management import ManagedTestCase, ManualTestRun, TestProject
from app.schemas.defect import (
  DefectCommentCreate,
  DefectCommentRead,
  DefectCreate,
  DefectEvidenceLinkRead,
  DefectFromRunCreate,
  DefectHistoryRead,
  DefectList,
  DefectRead,
  DefectRetestCreate,
  DefectRetestRead,
  DefectTransition,
  DefectUpdate,
)
from app.schemas.test_management import Page
from app.services.audit_service import append_event
from app.services.defect_service import (
  add_comment,
  can_create,
  create_defect,
  create_from_run,
  create_retest,
  safe_text,
  traceability,
  transition_defect,
  update_defect,
)
from app.services.project_access import ProjectAccessService, ProjectAction

router = APIRouter(tags=['defects'], dependencies=[Depends(get_auth_context)])


def _page(limit: int, offset: int, total: int) -> Page:
  return Page(limit=limit, offset=offset, total=total)


def _get_defect(db: Session, defect_id: int, context: AuthContext | None = None, action: ProjectAction = ProjectAction.READ) -> Defect:
  item = db.scalar(select(Defect).options(selectinload(Defect.evidence_links), selectinload(Defect.retests)).where(Defect.id == defect_id))
  if item is None:
    raise HTTPException(status_code=404, detail='Defect not found.')
  if context is not None:
    ProjectAccessService(db, context.operator.id).require(item.access_project_id, action)
  return item


def _sort_column(sort: str):
  allowed = {
    'updated_at': Defect.updated_at,
    'created_at': Defect.created_at,
    'defect_key': Defect.defect_key,
    'status': Defect.status,
    'severity': Defect.severity,
    'priority': Defect.priority,
  }
  if sort not in allowed:
    raise HTTPException(status_code=422, detail='Unsupported sort column.')
  return allowed[sort]


@router.get('/defects', response_model=DefectList)
def list_defects(
  search: str | None = None,
  project_id: int | None = None,
  module_id: int | None = None,
  suite_id: int | None = None,
  status: str | None = None,
  severity: str | None = None,
  priority: str | None = None,
  assignee_id: int | None = None,
  sort: str = 'updated_at',
  direction: str = 'desc',
  limit: int = Query(50, ge=1, le=200),
  offset: int = Query(0, ge=0),
  context: AuthContext = Depends(get_auth_context),
  db: Session = Depends(get_db),
):
  project_ids = ProjectAccessService(db, context.operator.id).project_ids()
  statement = select(Defect).where(Defect.access_project_id.in_(project_ids))
  count_statement = select(func.count(Defect.id)).where(Defect.access_project_id.in_(project_ids))
  filters = []
  if search:
    term = f'%{search.strip().lower()}%'
    filters.append(func.lower(Defect.title).like(term) | func.lower(Defect.defect_key).like(term))
  if project_id is not None: filters.append(Defect.project_id == project_id)
  if module_id is not None: filters.append(Defect.module_id == module_id)
  if suite_id is not None: filters.append(Defect.suite_id == suite_id)
  if status: filters.append(Defect.status == status.upper())
  if severity: filters.append(Defect.severity == severity.upper())
  if priority: filters.append(Defect.priority == priority.upper())
  if assignee_id is not None: filters.append(Defect.assigned_to == assignee_id)
  for item in filters:
    statement = statement.where(item)
    count_statement = count_statement.where(item)
  order = _sort_column(sort).asc() if direction.lower() == 'asc' else _sort_column(sort).desc()
  total = db.scalar(count_statement) or 0
  rows = list(db.scalars(statement.order_by(order, Defect.id.desc()).offset(offset).limit(limit)))
  return DefectList(items=rows, page=_page(limit, offset, total))


@router.post('/defects', response_model=DefectRead, status_code=201)
def create_defect_endpoint(payload: DefectCreate, context: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)):
  if not can_create(context.operator.role):
    raise HTTPException(status_code=403, detail='You do not have permission to perform this action.')
  test_project = db.get(TestProject, payload.project_id)
  if test_project is None:
    raise HTTPException(status_code=404, detail='Project not found.')
  ProjectAccessService(db, context.operator.id).require(test_project.access_project_id, ProjectAction.TEST)
  item = create_defect(db, payload, context.operator.id)
  append_event(db, 'defect_created', operator_id=context.operator.id, resource_type='DEFECT', resource_id=str(item.id), metadata={'defect_key': item.defect_key})
  db.commit(); db.refresh(item); return item


@router.post('/defects/from-run')
def create_defect_from_run_endpoint(payload: DefectFromRunCreate, context: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)):
  if not can_create(context.operator.role):
    raise HTTPException(status_code=403, detail='You do not have permission to perform this action.')
  result = create_from_run(db, payload, context.operator.id)
  if isinstance(result, dict):
    return result
  ProjectAccessService(db, context.operator.id).require(result.access_project_id, ProjectAction.TEST)
  if result.automated_run_id:
    from app.models.automated_execution import AutomatedRun
    run = db.get(AutomatedRun, result.automated_run_id)
    if run:
      result.target_id = run.target_id
      result.target_version = run.target_version
  append_event(db, 'defect_created_from_run', operator_id=context.operator.id, resource_type='DEFECT', resource_id=str(result.id), metadata={'defect_key': result.defect_key, 'source_type': payload.source_type.value})
  db.commit(); db.refresh(result); return DefectRead.model_validate(result)


@router.get('/defects/{defect_id}', response_model=DefectRead)
def get_defect(defect_id: int, context: AuthContext = Depends(get_auth_context), db: Session = Depends(get_db)):
  return _get_defect(db, defect_id, context)


@router.patch('/defects/{defect_id}', response_model=DefectRead)
def patch_defect(defect_id: int, payload: DefectUpdate, context: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)):
  item = _get_defect(db, defect_id, context, ProjectAction.TEST)
  if context.operator.role not in {'APPROVER', 'ADMIN'} and item.reporter_id != context.operator.id:
    raise HTTPException(status_code=403, detail='You do not have permission to perform this action.')
  update_defect(db, item, payload, context.operator.id)
  append_event(db, 'defect_updated', operator_id=context.operator.id, resource_type='DEFECT', resource_id=str(item.id))
  db.commit(); db.refresh(item); return item


def _transition(defect_id: int, status: str, payload: DefectTransition, context: AuthContext, db: Session) -> Defect:
  action = ProjectAction.APPROVE if status in {'TRIAGED', 'ASSIGNED', 'FIXED', 'READY_FOR_RETEST', 'CLOSED', 'REJECTED', 'DUPLICATE'} else ProjectAction.TEST
  item = _get_defect(db, defect_id, context, action)
  transition_defect(db, item, status, payload, context.operator)
  append_event(db, 'defect_status_changed', operator_id=context.operator.id, resource_type='DEFECT', resource_id=str(item.id), metadata={'status': item.status})
  db.commit(); db.refresh(item); return item


@router.post('/defects/{defect_id}/triage', response_model=DefectRead)
def triage_defect(defect_id: int, payload: DefectTransition | None = None, context: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)):
  return _transition(defect_id, 'TRIAGED', payload or DefectTransition(), context, db)


@router.post('/defects/{defect_id}/assign', response_model=DefectRead)
def assign_defect(defect_id: int, payload: DefectTransition, context: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)):
  return _transition(defect_id, 'ASSIGNED', payload, context, db)


@router.post('/defects/{defect_id}/start', response_model=DefectRead)
def start_defect(defect_id: int, payload: DefectTransition | None = None, context: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)):
  return _transition(defect_id, 'IN_PROGRESS', payload or DefectTransition(), context, db)


@router.post('/defects/{defect_id}/fix', response_model=DefectRead)
def fix_defect(defect_id: int, payload: DefectTransition | None = None, context: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)):
  return _transition(defect_id, 'FIXED', payload or DefectTransition(), context, db)


@router.post('/defects/{defect_id}/ready-for-retest', response_model=DefectRead)
def ready_for_retest(defect_id: int, payload: DefectTransition | None = None, context: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)):
  return _transition(defect_id, 'READY_FOR_RETEST', payload or DefectTransition(), context, db)


@router.post('/defects/{defect_id}/reopen', response_model=DefectRead)
def reopen_defect(defect_id: int, payload: DefectTransition, context: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)):
  return _transition(defect_id, 'REOPENED', payload, context, db)


@router.post('/defects/{defect_id}/close', response_model=DefectRead)
def close_defect(defect_id: int, payload: DefectTransition, context: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)):
  return _transition(defect_id, 'CLOSED', payload, context, db)


@router.post('/defects/{defect_id}/reject', response_model=DefectRead)
def reject_defect(defect_id: int, payload: DefectTransition, context: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)):
  return _transition(defect_id, 'REJECTED', payload, context, db)


@router.post('/defects/{defect_id}/duplicate', response_model=DefectRead)
def duplicate_defect(defect_id: int, payload: DefectTransition, context: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)):
  return _transition(defect_id, 'DUPLICATE', payload, context, db)


@router.get('/defects/{defect_id}/comments', response_model=list[DefectCommentRead])
def list_comments(defect_id: int, context: AuthContext = Depends(get_auth_context), db: Session = Depends(get_db)):
  _get_defect(db, defect_id, context)
  return list(db.scalars(select(DefectComment).where(DefectComment.defect_id == defect_id).order_by(DefectComment.created_at)))


@router.post('/defects/{defect_id}/comments', response_model=DefectCommentRead, status_code=201)
def create_comment(defect_id: int, payload: DefectCommentCreate, context: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)):
  item = _get_defect(db, defect_id, context)
  if ProjectAccessService(db, context.operator.id).membership(item.access_project_id).role == 'VIEWER':
    raise HTTPException(status_code=403, detail='Viewer membership is read-only.')
  comment = add_comment(db, item, payload.body, context.operator.id)
  append_event(db, 'defect_comment_added', operator_id=context.operator.id, resource_type='DEFECT', resource_id=str(item.id))
  db.commit(); db.refresh(comment); return comment


@router.get('/defects/{defect_id}/history', response_model=list[DefectHistoryRead])
def list_history(defect_id: int, context: AuthContext = Depends(get_auth_context), db: Session = Depends(get_db)):
  _get_defect(db, defect_id, context)
  return list(db.scalars(select(DefectHistory).where(DefectHistory.defect_id == defect_id).order_by(DefectHistory.created_at)))


@router.get('/defects/{defect_id}/evidence', response_model=list[DefectEvidenceLinkRead])
def list_evidence(defect_id: int, context: AuthContext = Depends(get_auth_context), db: Session = Depends(get_db)):
  _get_defect(db, defect_id, context)
  return list(db.scalars(select(DefectEvidenceLink).where(DefectEvidenceLink.defect_id == defect_id).order_by(DefectEvidenceLink.created_at)))


@router.post('/defects/{defect_id}/retest', response_model=DefectRetestRead, status_code=201)
def retest_defect(defect_id: int, payload: DefectRetestCreate, context: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)):
  item = _get_defect(db, defect_id, context, ProjectAction.TEST)
  retest = create_retest(db, item, payload, context.operator)
  append_event(db, 'defect_retest_recorded', operator_id=context.operator.id, resource_type='DEFECT', resource_id=str(item.id), metadata={'result_status': retest.result_status})
  db.commit(); db.refresh(retest); return retest


@router.get('/defects/{defect_id}/traceability')
def defect_traceability(defect_id: int, context: AuthContext = Depends(get_auth_context), db: Session = Depends(get_db)):
  return traceability(db, _get_defect(db, defect_id, context))


@router.get('/traceability/test-cases/{case_id}')
def test_case_traceability(case_id: int, context: AuthContext = Depends(get_auth_context), db: Session = Depends(get_db)):
  case = db.get(ManagedTestCase, case_id)
  if case is None:
    raise HTTPException(status_code=404, detail='Test case not found.')
  ProjectAccessService(db, context.operator.id).require(case.access_project_id)
  defects = list(db.scalars(select(Defect).where(Defect.test_case_id == case_id).order_by(Defect.updated_at.desc())))
  return {'test_case': {'id': case.id, 'case_key': case.case_key, 'current_version': case.current_version, 'status': case.status}, 'defects': [{'id': item.id, 'defect_key': item.defect_key, 'status': item.status, 'test_case_version': item.test_case_version} for item in defects]}


@router.get('/traceability/runs/{run_id}')
def run_traceability(run_id: int, run_type: str = Query('manual', pattern='^(manual|automated)$'), context: AuthContext = Depends(get_auth_context), db: Session = Depends(get_db)):
  if run_type == 'manual':
    run = db.get(ManualTestRun, run_id)
    if run is None:
      raise HTTPException(status_code=404, detail='Manual run not found.')
    ProjectAccessService(db, context.operator.id).require(run.access_project_id)
    defects = list(db.scalars(select(Defect).where(Defect.manual_run_id == run_id).order_by(Defect.updated_at.desc())))
    return {'run': {'id': run.id, 'run_key': run.run_key, 'status': run.status}, 'defects': [{'id': item.id, 'defect_key': item.defect_key, 'status': item.status} for item in defects]}
  from app.models.automated_execution import AutomatedRun
  run = db.get(AutomatedRun, run_id)
  if run is None:
    raise HTTPException(status_code=404, detail='Automated run not found.')
  ProjectAccessService(db, context.operator.id).require(run.project_id)
  defects = list(db.scalars(select(Defect).where(Defect.automated_run_id == run_id).order_by(Defect.updated_at.desc())))
  return {'run': {'id': run.id, 'run_key': run.run_key, 'status': run.status}, 'defects': [{'id': item.id, 'defect_key': item.defect_key, 'status': item.status} for item in defects]}
