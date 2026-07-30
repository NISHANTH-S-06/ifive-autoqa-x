"""API router for External Task Imports."""
from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session as DBSession

from app.auth import AuthContext, get_auth_context, require_csrf
from app.config import settings
from app.database import get_db
from app.models.external_task_import import ExternalTaskImport
from app.schemas.task_import import TaskImportOut
from app.services import task_import_service
from app.services.project_access import ProjectAccessService, ProjectAction
from app.models.test_plan import TestPlan
from app.schemas.test_plan import TestPlanOut
from app.services import test_plan_service

router = APIRouter(prefix='/task-imports', tags=['task-imports'])


def _check_import_access(db: DBSession, import_id: int, context: AuthContext, action: ProjectAction = ProjectAction.READ) -> ExternalTaskImport:
    item = db.get(ExternalTaskImport, import_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Import {import_id} not found.')
    ProjectAccessService(db, context.operator.id).require(item.project_id, action)
    return item


@router.post('/sync', response_model=List[TaskImportOut])
def sync_task_imports(context: AuthContext = Depends(require_csrf), db: DBSession = Depends(get_db)) -> List[TaskImportOut]:
    records = task_import_service.sync_tasks_from_portal(db)
    return [TaskImportOut.model_validate(r) for r in records]


@router.post('/reset-for-testing')
def reset_for_testing(
    context: AuthContext = Depends(get_auth_context),
    db: DBSession = Depends(get_db),
) -> dict:
    """Reset all imports to DRAFT + cancel queued runs. LOCAL E2E TESTING ONLY. Requires authenticated ADMIN."""
    if settings.app_env not in {'local', 'development', 'test'} or settings.allow_real_target_execution:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Reset endpoint is only available in local/test environments.",
        )
    if context.operator.role != 'ADMIN':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin operators can reset data for testing.",
        )
    count = task_import_service.reset_imports_for_testing(db)
    return {'reset_count': count}


@router.get('', response_model=List[TaskImportOut])
def list_task_imports(
    import_status: Optional[str] = Query(None),
    source_system: Optional[str] = Query(None),
    context: AuthContext = Depends(get_auth_context),
    db: DBSession = Depends(get_db),
) -> List[TaskImportOut]:
    query = select(ExternalTaskImport).order_by(ExternalTaskImport.id.desc())
    allowed_ids = ProjectAccessService(db, context.operator.id).project_ids()
    query = query.where(ExternalTaskImport.project_id.in_(allowed_ids))
    if import_status:
        query = query.where(ExternalTaskImport.import_status == import_status)
    if source_system:
        query = query.where(ExternalTaskImport.source_system == source_system)
    records = db.scalars(query).all()
    return [TaskImportOut.model_validate(r) for r in records]


@router.get('/{import_id}', response_model=TaskImportOut)
def get_task_import(import_id: int, context: AuthContext = Depends(get_auth_context), db: DBSession = Depends(get_db)) -> TaskImportOut:
    item = _check_import_access(db, import_id, context, ProjectAction.READ)
    return TaskImportOut.model_validate(item)


@router.post('/{import_id}/prepare-plan', response_model=TaskImportOut)
def prepare_plan(import_id: int, context: AuthContext = Depends(get_auth_context), db: DBSession = Depends(get_db)) -> TaskImportOut:
    _check_import_access(db, import_id, context, ProjectAction.TEST)
    item = task_import_service.prepare_test_plan(db, import_id)
    return TaskImportOut.model_validate(item)


@router.post('/{import_id}/analyze')
def analyze_task_import(import_id: int, context: AuthContext = Depends(get_auth_context), db: DBSession = Depends(get_db)) -> dict:
    item = _check_import_access(db, import_id, context, ProjectAction.READ)
    from app.services.task_analysis_service import analyze_imported_task
    response = analyze_imported_task(item.title, item.description or '', item.acceptance_criteria or '')
    
    # Store the template type on the task so we can use AI_GENERATED
    item.template_type = response.template_type
    db.commit()
    
    return response.model_dump()


@router.post('/{import_id}/generate-plan', response_model=TestPlanOut)
def generate_task_plan(import_id: int, context: AuthContext = Depends(get_auth_context), db: DBSession = Depends(get_db)):
    _check_import_access(db, import_id, context, ProjectAction.TEST)
    plan = test_plan_service.generate_plan_for_task(db, import_id, context.operator.id)
    return TestPlanOut.model_validate(plan)


@router.get('/{import_id}/plans', response_model=List[TestPlanOut])
def get_plans_for_import(import_id: int, context: AuthContext = Depends(get_auth_context), db: DBSession = Depends(get_db)):
    _check_import_access(db, import_id, context, ProjectAction.READ)
    plan = test_plan_service.get_plan_by_import_id(db, import_id)
    if not plan:
        return []
    return [TestPlanOut.model_validate(plan)]
@router.post('/{import_id}/approve', response_model=TaskImportOut)
def approve_plan(
    import_id: int,
    context: AuthContext = Depends(get_auth_context),
    db: DBSession = Depends(get_db),
) -> TaskImportOut:
    _check_import_access(db, import_id, context, ProjectAction.APPROVE)
    # Actor identity is derived only from the authenticated session; never trust caller-supplied identity.
    item = task_import_service.approve_test_plan(db, import_id, approver_username=context.operator.username)
    return TaskImportOut.model_validate(item)


@router.post('/{import_id}/run', response_model=TaskImportOut)
def run_task_import(import_id: int, context: AuthContext = Depends(get_auth_context), db: DBSession = Depends(get_db)) -> TaskImportOut:
    _check_import_access(db, import_id, context, ProjectAction.TEST)
    item = task_import_service.execute_and_callback(db, import_id)
    return TaskImportOut.model_validate(item)


@router.post('/{import_id}/callback/retry', response_model=TaskImportOut)
def retry_callback(import_id: int, context: AuthContext = Depends(get_auth_context), db: DBSession = Depends(get_db)) -> TaskImportOut:
    _check_import_access(db, import_id, context, ProjectAction.TEST)
    item = task_import_service.retry_callback(db, import_id)
    return TaskImportOut.model_validate(item)


@router.get('/{import_id}/status')
def get_task_import_status(import_id: int, context: AuthContext = Depends(get_auth_context), db: DBSession = Depends(get_db)) -> dict:
    item = _check_import_access(db, import_id, context, ProjectAction.READ)
    return {
        'import_id': item.id,
        'source_task_id': item.source_task_id,
        'source_revision': item.source_revision,
        'import_status': item.import_status,
        'linked_run_id': item.linked_run_id,
        'callback_status': item.callback_status,
        'callback_error': item.callback_error,
        'approved_by': item.approved_by,
        'approved_at': item.approved_at,
    }
