"""Tasks API router — all task CRUD and lifecycle endpoints."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth import AuthContext, get_auth_context
from app.database import get_db
from app.models.task import Task
from app.models.task_history import TaskHistory
from app.schemas.history import HistoryOut
from app.schemas.tasks import (
    DeveloperNotesRequest,
    QAResultRequest,
    ReworkRemarksRequest,
    StatusTransitionRequest,
    TaskCreate,
    TaskOut,
    TaskUpdate,
    TestingL2TaskOut,
)
from app.services.task_service import apply_qa_result, transition_status

router = APIRouter(prefix='/api/tasks', tags=['tasks'])


def _get_task_or_404(task_id: int, db: Session) -> Task:
    task = db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Task {task_id} not found')
    return task


@router.post('/reset-testing-l2')
def reset_testing_l2_tasks(db: Session = Depends(get_db)) -> dict:
    tasks = db.query(Task).all()
    for t in tasks:
        t.status = 'TESTING_L2'
        t.testing_l2_at = datetime.utcnow()
        t.updated_at = datetime.utcnow()
    db.commit()
    return {'status': 'ok', 'reset_count': len(tasks)}


def _assert_task_access(task: Task, ctx: AuthContext) -> None:
    """VIEWER and SUPERADMIN see everything; DEVELOPER sees only their assigned tasks;
    TESTER sees TESTING_L2+ tasks; DELIVERY sees DELIVERY_READY tasks."""
    if ctx.role == 'SUPERADMIN':
        return
    if ctx.role == 'VIEWER':
        return
    if ctx.role == 'DEVELOPER':
        if task.assigned_developer != ctx.username:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Access denied: not your task')
        return
    if ctx.role == 'TESTER':
        if task.status not in {
            'TESTING_L2', 'QA_RUNNING', 'QA_PASSED', 'QA_FAILED', 'REWORK',
            'DELIVERY_READY', 'DELIVERY_COMPLETED',
        }:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Task not in testable state')
        return
    if ctx.role == 'DELIVERY':
        if task.status not in {'DELIVERY_READY', 'DELIVERY_COMPLETED'}:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Task not in delivery state')
        return


# ─── POST /api/tasks ────────────────────────────────────────────────────────

@router.post('', response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(
    payload: TaskCreate,
    ctx: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db),
) -> TaskOut:
    ctx.require_role('SUPERADMIN')
    existing = db.query(Task).filter_by(task_code=payload.task_code).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f'task_code {payload.task_code!r} already exists',
        )
    task = Task(**payload.model_dump(), status='CREATED', revision=0, created_at=datetime.utcnow(), updated_at=datetime.utcnow())
    db.add(task)
    db.flush()
    db.add(TaskHistory(
        task_id=task.id,
        previous_status=None,
        new_status='CREATED',
        changed_by=ctx.username,
        reason='Task created',
        timestamp=datetime.utcnow(),
    ))
    db.commit()
    db.refresh(task)
    return TaskOut.model_validate(task)


# ─── GET /api/tasks ──────────────────────────────────────────────────────────

@router.get('', response_model=List)
def list_tasks(
    status_filter: Optional[str] = Query(None, alias='status'),
    project: Optional[str] = Query(None),
    developer: Optional[str] = Query(None),
    tester: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    ctx: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db),
) -> list:
    q = db.query(Task)

    # Role-based filtering
    if ctx.role == 'DEVELOPER':
        q = q.filter(Task.assigned_developer == ctx.username)
    elif ctx.role == 'TESTER':
        q = q.filter(Task.status.in_([
            'TESTING_L2', 'QA_RUNNING', 'QA_PASSED', 'QA_FAILED', 'REWORK',
        ]))
    elif ctx.role == 'DELIVERY':
        q = q.filter(Task.status.in_(['DELIVERY_READY', 'DELIVERY_COMPLETED']))

    if status_filter:
        q = q.filter(Task.status == status_filter)
    if project:
        q = q.filter(Task.project_name == project)
    if developer:
        q = q.filter(Task.assigned_developer == developer)
    if tester:
        q = q.filter(Task.assigned_tester == tester)
    if priority:
        q = q.filter(Task.priority == priority)

    tasks = q.order_by(Task.id.desc()).all()

    # Use connector contract for TESTING_L2 filtered responses
    if status_filter == 'TESTING_L2':
        return [
            TestingL2TaskOut(
                source_task_id=t.id,
                source_revision=t.revision,
                **{f: getattr(t, f) for f in [
                    'project_name', 'module_name', 'title', 'description',
                    'application_url', 'page_path', 'environment',
                    'expected_result', 'acceptance_criteria', 'test_data',
                    'assigned_developer', 'assigned_tester', 'priority',
                    'developer_notes', 'status', 'testing_l2_at',
                ]},
            ).model_dump()
            for t in tasks
        ]
    return [TaskOut.model_validate(t).model_dump() for t in tasks]


# ─── GET /api/tasks/{task_id} ────────────────────────────────────────────────

@router.get('/{task_id}', response_model=TaskOut)
def get_task(
    task_id: int,
    ctx: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db),
) -> TaskOut:
    task = _get_task_or_404(task_id, db)
    _assert_task_access(task, ctx)
    return TaskOut.model_validate(task)


# ─── PATCH /api/tasks/{task_id} ──────────────────────────────────────────────

@router.patch('/{task_id}', response_model=TaskOut)
def update_task(
    task_id: int,
    payload: TaskUpdate,
    ctx: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db),
) -> TaskOut:
    ctx.require_role('SUPERADMIN')
    task = _get_task_or_404(task_id, db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    task.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(task)
    return TaskOut.model_validate(task)


# ─── PATCH /api/tasks/{task_id}/status ───────────────────────────────────────

@router.patch('/{task_id}/status', response_model=TaskOut)
def change_status(
    task_id: int,
    payload: StatusTransitionRequest,
    ctx: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db),
) -> TaskOut:
    task = _get_task_or_404(task_id, db)
    transition_status(db, task, payload.new_status, ctx, payload.reason)
    db.commit()
    db.refresh(task)
    return TaskOut.model_validate(task)


# ─── POST /api/tasks/{task_id}/developer-notes ───────────────────────────────

@router.post('/{task_id}/developer-notes', response_model=TaskOut)
def add_developer_notes(
    task_id: int,
    payload: DeveloperNotesRequest,
    ctx: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db),
) -> TaskOut:
    ctx.require_role('DEVELOPER', 'SUPERADMIN')
    task = _get_task_or_404(task_id, db)
    if ctx.role == 'DEVELOPER' and task.assigned_developer != ctx.username:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not your task')
    task.developer_notes = payload.notes
    task.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(task)
    return TaskOut.model_validate(task)


# ─── POST /api/tasks/{task_id}/rework-remarks ────────────────────────────────

@router.post('/{task_id}/rework-remarks', response_model=TaskOut)
def add_rework_remarks(
    task_id: int,
    payload: ReworkRemarksRequest,
    ctx: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db),
) -> TaskOut:
    ctx.require_role('TESTER', 'SUPERADMIN')
    task = _get_task_or_404(task_id, db)
    task.rework_remarks = payload.remarks
    task.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(task)
    return TaskOut.model_validate(task)


# ─── GET /api/tasks/{task_id}/history ────────────────────────────────────────

@router.get('/{task_id}/history', response_model=List[HistoryOut])
def get_history(
    task_id: int,
    ctx: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db),
) -> List[HistoryOut]:
    _get_task_or_404(task_id, db)
    records = db.query(TaskHistory).filter_by(task_id=task_id).order_by(TaskHistory.timestamp).all()
    return [HistoryOut.model_validate(r) for r in records]


# ─── POST /api/tasks/{task_id}/qa-result ─────────────────────────────────────

@router.post('/{task_id}/qa-result', response_model=TaskOut)
def record_qa_result(
    task_id: int,
    payload: QAResultRequest,
    ctx: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db),
) -> TaskOut:
    task = _get_task_or_404(task_id, db)
    apply_qa_result(db, task, payload.result, ctx, payload.reason)
    db.commit()
    db.refresh(task)
    return TaskOut.model_validate(task)


# ─── DELETE /api/tasks/{task_id} ─────────────────────────────────────────────

@router.delete('/{task_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    ctx: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db),
) -> None:
    """Delete a task and all its history. SUPERADMIN only."""
    ctx.require_role('SUPERADMIN')
    task = _get_task_or_404(task_id, db)
    db.query(TaskHistory).filter_by(task_id=task.id).delete()
    db.delete(task)
    db.commit()

