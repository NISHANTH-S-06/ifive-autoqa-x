from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.auth import AuthContext, get_auth_context
from app.database import get_db
from app.services.release_readiness import ReleaseReadinessService
import json

router = APIRouter(prefix='/release-readiness', tags=['release-readiness'], dependencies=[Depends(get_auth_context)])


@router.get('/eval', summary='Evaluate Release Readiness')
def evaluate_release(
    project_id: int = Query(1),
    release_version: str = Query('v1.0.0'),
    context: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db)
):
    service = ReleaseReadinessService(db)
    evaluation = service.evaluate_release(project_id, release_version, context.operator.id)

    return {
        'id': evaluation.id,
        'project_id': evaluation.project_id,
        'release_version': evaluation.release_version,
        'release_score': evaluation.release_score,
        'readiness_status': evaluation.readiness_status,
        'automation_coverage': evaluation.automation_coverage,
        'pass_rate': evaluation.pass_rate,
        'open_critical_bugs': evaluation.open_critical_bugs,
        'risk_score': evaluation.risk_score,
        'breakdown': json.loads(evaluation.breakdown_json or '{}'),
        'created_at': evaluation.created_at
    }
