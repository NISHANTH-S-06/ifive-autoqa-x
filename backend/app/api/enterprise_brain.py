"""Phase 14 – AI Enterprise Command Brain API router."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.auth import get_auth_context, AuthContext
from app.database import get_db
from app.ai.enterprise_brain import EnterpriseBrainEngine

router = APIRouter(prefix='/enterprise-brain', tags=['Phase14-Brain'])


class OrchestrateGoalRequest(BaseModel):
    goal_description: str
    project_id: int | None = None
    priority: int = Field(default=5, ge=1, le=10)


@router.post('/orchestrate', status_code=201)
def orchestrate_goal(body: OrchestrateGoalRequest, db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return EnterpriseBrainEngine(db).orchestrate_goal(
        goal_description=body.goal_description,
        project_id=body.project_id,
        priority=body.priority,
    )


@router.get('/runs')
def list_runs(limit: int = 20, db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return EnterpriseBrainEngine(db).list_runs(limit=limit)


@router.get('/runs/{run_id}')
def get_run(run_id: str, db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return EnterpriseBrainEngine(db).get_run_status(run_id)
