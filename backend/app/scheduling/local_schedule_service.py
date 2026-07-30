import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.advanced_validation import AdvancedValidationProfile, LocalSchedule
from app.models.test_plan import TestPlan


def parse_next_run(cron_expr: str, base_time: Optional[datetime] = None) -> datetime:
    """
    Standard simple cron calculator for local hourly/daily expressions.
    Enforces minimum 1 hour frequency requirement.
    """
    base_time = base_time or datetime.utcnow()
    # Simple hourly expression e.g. "0 * * * *" or "0 0 * * *"
    parts = cron_expr.strip().split()
    if len(parts) != 5:
        raise HTTPException(status_code=422, detail="Invalid cron expression format. Must have 5 fields.")

    minute, hour, dom, month, dow = parts

    # Enforce minimum frequency check: minute field e.g. '*/5' or '*' is rejected if under 60 mins
    if minute.startswith("*/") or minute == "*":
        if minute.startswith("*/"):
            try:
                step = int(minute.replace("*/", ""))
                if step < 60:
                    raise HTTPException(status_code=422, detail="Minimum schedule frequency is once per hour (60 minutes).")
            except ValueError:
                pass
        else:
            raise HTTPException(status_code=422, detail="Minimum schedule frequency is once per hour (60 minutes).")

    # Default next run calculation: 1 hour from base_time
    return base_time + timedelta(hours=1)


class LocalScheduleService:
    def create_schedule(
        self,
        db: Session,
        project_id: int,
        name: str,
        cron_expression: str,
        approved_test_plan_id: int,
        validation_profile_id: int,
        created_by: int,
        browser: str = "chromium",
        timezone: str = "UTC"
    ) -> LocalSchedule:
        # 1. Verify approved test plan exists and is approved
        plan = db.get(TestPlan, approved_test_plan_id)
        if not plan:
            raise HTTPException(status_code=404, detail="TestPlan not found.")
        if plan.status != "APPROVED" or not plan.approved_version_number:
            raise HTTPException(status_code=409, detail="Schedules cannot use draft or rejected plans. Approved TestPlan required.")
        if plan.project_id != project_id:
            raise HTTPException(status_code=403, detail="Cross-project test plan reference is prohibited.")

        # 2. Verify validation profile
        profile = db.get(AdvancedValidationProfile, validation_profile_id)
        if not profile:
            raise HTTPException(status_code=404, detail="Validation profile not found.")
        if profile.project_id != project_id:
            raise HTTPException(status_code=403, detail="Cross-project profile reference is prohibited.")

        # 3. Calculate next run
        next_run = parse_next_run(cron_expression)

        schedule = LocalSchedule(
            project_id=project_id,
            name=name.strip(),
            enabled=True,
            cron_expression=cron_expression,
            timezone=timezone,
            approved_test_plan_id=plan.id,
            approved_version_number=plan.approved_version_number,
            validation_profile_id=profile.id,
            browser=browser,
            created_by=created_by,
            next_run_at=next_run
        )
        db.add(schedule)
        db.commit()
        db.refresh(schedule)
        return schedule

    def toggle_schedule(self, db: Session, schedule_id: int, project_id: int, enable: bool) -> LocalSchedule:
        schedule = db.get(LocalSchedule, schedule_id)
        if not schedule or schedule.project_id != project_id:
            raise HTTPException(status_code=404, detail="Local schedule not found.")

        schedule.enabled = enable
        schedule.updated_at = datetime.utcnow()
        if enable:
            schedule.next_run_at = parse_next_run(schedule.cron_expression)
        else:
            schedule.next_run_at = None

        db.commit()
        db.refresh(schedule)
        return schedule

    def run_now(self, db: Session, schedule_id: int, project_id: int, operator_id: int) -> Dict[str, Any]:
        schedule = db.get(LocalSchedule, schedule_id)
        if not schedule or schedule.project_id != project_id:
            raise HTTPException(status_code=404, detail="Local schedule not found.")

        if not schedule.enabled:
            raise HTTPException(status_code=409, detail="Schedule is disabled.")

        # Verify plan is still approved
        plan = db.get(TestPlan, schedule.approved_test_plan_id)
        if not plan or plan.status != "APPROVED":
            raise HTTPException(status_code=409, detail="TestPlan is no longer approved.")

        schedule.last_run_at = datetime.utcnow()
        schedule.next_run_at = parse_next_run(schedule.cron_expression, schedule.last_run_at)
        schedule.updated_at = datetime.utcnow()

        db.commit()

        return {
            "schedule_id": schedule.id,
            "status": "QUEUED",
            "approved_test_plan_id": schedule.approved_test_plan_id,
            "approved_version_number": schedule.approved_version_number,
            "triggered_at": schedule.last_run_at.isoformat()
        }
