from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth import AuthContext, get_auth_context
from app.database import get_db
from app.services.autonomous_regression import AutonomousRegressionService

router = APIRouter(prefix='/regression', tags=['autonomous-regression'], dependencies=[Depends(get_auth_context)])


class RegressionRequest(BaseModel):
    task_id: int


@router.post('/analyze-and-run', summary='Analyze Developer Task Change & Execute Regression')
def analyze_and_run_regression(
    payload: RegressionRequest,
    context: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db)
):
    service = AutonomousRegressionService(db)
    report = service.analyze_impact_and_plan(payload.task_id)
    if 'error' in report:
        raise HTTPException(status_code=404, detail=report['error'])
    return report
