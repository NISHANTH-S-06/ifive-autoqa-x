"""Dashboard API — summary counts and filtered lists."""
from __future__ import annotations

from typing import Dict

from fastapi import APIRouter, Depends
from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.auth import AuthContext, get_auth_context
from app.database import get_db
from app.models.task import VALID_STATUSES, Task

router = APIRouter(prefix='/api/dashboard', tags=['dashboard'])

ALL_STATUS_KEYS = [
    'CREATED', 'ASSIGNED', 'IN_PROGRESS', 'TESTING_L1', 'TESTING_L2',
    'QA_RUNNING', 'QA_PASSED', 'QA_FAILED', 'REWORK',
    'DELIVERY_READY', 'DELIVERY_COMPLETED',
    'NEED_CLARITY', 'HOLD', 'CANCELLED',
]


@router.get('/summary')
def dashboard_summary(
    ctx: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db),
) -> dict:
    rows = db.query(Task.status, func.count(Task.id)).group_by(Task.status).all()
    counts: Dict[str, int] = {s: 0 for s in ALL_STATUS_KEYS}
    for s, cnt in rows:
        counts[s] = cnt
    return {'counts': counts, 'total': sum(counts.values())}
