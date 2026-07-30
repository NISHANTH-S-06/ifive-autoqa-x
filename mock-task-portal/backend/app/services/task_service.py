"""Task service — business logic, transition validation, history recording."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.auth import AuthContext
from app.models.task import ALLOWED_TRANSITIONS, TERMINAL_STATUSES, Task
from app.models.task_history import TaskHistory


def _record_history(
    db: Session,
    task: Task,
    previous_status: Optional[str],
    new_status: str,
    changed_by: str,
    reason: Optional[str] = None,
) -> None:
    db.add(TaskHistory(
        task_id=task.id,
        previous_status=previous_status,
        new_status=new_status,
        changed_by=changed_by,
        reason=reason,
        timestamp=datetime.utcnow(),
    ))


def transition_status(
    db: Session,
    task: Task,
    new_status: str,
    ctx: AuthContext,
    reason: Optional[str] = None,
) -> Task:
    """Validate and apply a status transition, recording history."""
    current = task.status
    allowed = ALLOWED_TRANSITIONS.get(current, {})
    if new_status not in allowed:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f'Transition {current} → {new_status} is not allowed.',
        )
    permitted_roles = allowed[new_status]
    if ctx.role not in permitted_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f'Role {ctx.role} cannot perform {current} → {new_status}.',
        )

    previous = task.status
    task.status = new_status
    task.updated_at = datetime.utcnow()

    if new_status == 'TESTING_L2':
        task.testing_l2_at = datetime.utcnow()
        task.revision += 1

    if new_status in {'DELIVERY_COMPLETED', 'CANCELLED'}:
        task.completed_at = datetime.utcnow()

    if new_status == 'REWORK':
        task.revision += 1

    _record_history(db, task, previous, new_status, ctx.username, reason)
    return task


def apply_qa_result(
    db: Session,
    task: Task,
    result: str,
    ctx: AuthContext,
    reason: Optional[str] = None,
) -> Task:
    """Apply a QA result from TESTING_L2 or QA_RUNNING states."""
    ctx.require_role('TESTER', 'SUPERADMIN')
    if task.status not in {'TESTING_L2', 'QA_RUNNING'}:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f'QA result can only be recorded in TESTING_L2 or QA_RUNNING state, not {task.status}.',
        )

    if result == 'PASS':
        target = 'QA_PASSED'
    elif result == 'FAIL':
        target = 'QA_FAILED'
    elif result == 'BLOCKED':
        target = 'NEED_CLARITY'
    else:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='result must be PASS, FAIL, or BLOCKED')

    # Move to QA_RUNNING first if still in TESTING_L2
    if task.status == 'TESTING_L2':
        _record_history(db, task, 'TESTING_L2', 'QA_RUNNING', ctx.username, 'Auto-advanced to QA_RUNNING on qa-result')
        task.status = 'QA_RUNNING'
        task.updated_at = datetime.utcnow()

    previous = task.status
    task.status = target
    task.updated_at = datetime.utcnow()

    if target == 'QA_FAILED':
        task.rework_remarks = reason or task.rework_remarks
        # revision increments at REWORK state, not at QA_FAILED

    _record_history(db, task, previous, target, ctx.username, reason)
    return task
