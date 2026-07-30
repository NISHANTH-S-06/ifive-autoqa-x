from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import AuthContext, get_auth_context, require_csrf
from app.database import get_db
from app.models.advanced_validation import AdvancedValidationRun, LocalSchedule
from app.scheduling.local_schedule_service import LocalScheduleService

router = APIRouter(prefix='/local-schedules', tags=['local-schedules'])


class CreateScheduleRequest(BaseModel):
    project_id: int
    name: str = Field(min_length=1, max_length=120)
    cron_expression: str = Field(min_length=1, max_length=60)
    timezone: str = Field(default="UTC")
    approved_test_plan_id: int
    validation_profile_id: int
    browser: str = Field(default="chromium")


class UpdateScheduleRequest(BaseModel):
    name: Optional[str] = None
    cron_expression: Optional[str] = None
    timezone: Optional[str] = None
    browser: Optional[str] = None


def require_admin_or_approver(context: AuthContext) -> None:
    if context.operator.role not in ('ADMIN', 'APPROVER'):
        raise HTTPException(status_code=403, detail="ADMIN or APPROVER role is required for scheduling.")


@router.post('', status_code=201)
def create_schedule(
    payload: CreateScheduleRequest,
    context: AuthContext = Depends(require_csrf),
    db: Session = Depends(get_db)
):
    require_admin_or_approver(context)
    svc = LocalScheduleService()
    return svc.create_schedule(
        db=db,
        project_id=payload.project_id,
        name=payload.name,
        cron_expression=payload.cron_expression,
        approved_test_plan_id=payload.approved_test_plan_id,
        validation_profile_id=payload.validation_profile_id,
        created_by=context.operator.id,
        browser=payload.browser,
        timezone=payload.timezone
    )


@router.get('')
def list_schedules(
    project_id: int,
    context: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db)
):
    return db.scalars(select(LocalSchedule).where(LocalSchedule.project_id == project_id)).all()


@router.get('/{schedule_id}')
def get_schedule(
    schedule_id: int,
    context: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db)
):
    item = db.get(LocalSchedule, schedule_id)
    if not item:
        raise HTTPException(status_code=404, detail="Schedule not found.")
    return item


@router.patch('/{schedule_id}')
def update_schedule(
    schedule_id: int,
    payload: UpdateScheduleRequest,
    context: AuthContext = Depends(require_csrf),
    db: Session = Depends(get_db)
):
    require_admin_or_approver(context)
    item = db.get(LocalSchedule, schedule_id)
    if not item:
        raise HTTPException(status_code=404, detail="Schedule not found.")

    if payload.name is not None:
        item.name = payload.name.strip()
    if payload.cron_expression is not None:
        item.cron_expression = payload.cron_expression.strip()
    if payload.timezone is not None:
        item.timezone = payload.timezone.strip()
    if payload.browser is not None:
        item.browser = payload.browser.strip()

    db.commit()
    db.refresh(item)
    return item


@router.post('/{schedule_id}/enable')
def enable_schedule(
    schedule_id: int,
    context: AuthContext = Depends(require_csrf),
    db: Session = Depends(get_db)
):
    require_admin_or_approver(context)
    item = db.get(LocalSchedule, schedule_id)
    if not item:
        raise HTTPException(status_code=404, detail="Schedule not found.")

    svc = LocalScheduleService()
    return svc.toggle_schedule(db, schedule_id, item.project_id, enable=True)


@router.post('/{schedule_id}/disable')
def disable_schedule(
    schedule_id: int,
    context: AuthContext = Depends(require_csrf),
    db: Session = Depends(get_db)
):
    require_admin_or_approver(context)
    item = db.get(LocalSchedule, schedule_id)
    if not item:
        raise HTTPException(status_code=404, detail="Schedule not found.")

    svc = LocalScheduleService()
    return svc.toggle_schedule(db, schedule_id, item.project_id, enable=False)


@router.post('/{schedule_id}/run-now')
def run_now_schedule(
    schedule_id: int,
    context: AuthContext = Depends(require_csrf),
    db: Session = Depends(get_db)
):
    require_admin_or_approver(context)
    item = db.get(LocalSchedule, schedule_id)
    if not item:
        raise HTTPException(status_code=404, detail="Schedule not found.")

    svc = LocalScheduleService()
    return svc.run_now(db, schedule_id, item.project_id, context.operator.id)


@router.get('/{schedule_id}/history')
def get_schedule_history(
    schedule_id: int,
    context: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db)
):
    item = db.get(LocalSchedule, schedule_id)
    if not item:
        raise HTTPException(status_code=404, detail="Schedule not found.")

    # Returns advanced runs triggered for this approved test plan
    runs = db.scalars(
        select(AdvancedValidationRun)
        .where(
            AdvancedValidationRun.project_id == item.project_id,
            AdvancedValidationRun.test_plan_id == item.approved_test_plan_id,
            AdvancedValidationRun.validation_profile_id == item.validation_profile_id
        )
        .order_by(AdvancedValidationRun.started_at.desc())
        .limit(20)
    ).all()

    return runs
