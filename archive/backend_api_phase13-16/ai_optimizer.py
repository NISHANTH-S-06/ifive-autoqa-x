"""Phase 13 – AI Execution Optimizer API router."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth import get_auth_context, AuthContext
from app.database import get_db
from app.services.ai_execution_optimizer import AIExecutionOptimizerService

router = APIRouter(prefix='/ai-optimizer', tags=['Phase13-AIOptimizer'])


@router.get('/logs')
def optimization_logs(
    project_id: int | None = None,
    limit: int = 50,
    db: Session = Depends(get_db),
    _: AuthContext = Depends(get_auth_context),
):
    return AIExecutionOptimizerService(db).get_optimization_logs(project_id=project_id, limit=limit)


@router.post('/optimize')
def trigger_optimization(
    project_id: int | None = None,
    db: Session = Depends(get_db),
    _: AuthContext = Depends(get_auth_context),
):
    return AIExecutionOptimizerService(db).trigger_full_optimization(project_id=project_id)


@router.get('/recommendations')
def get_recommendations(
    project_id: int | None = None,
    db: Session = Depends(get_db),
    _: AuthContext = Depends(get_auth_context),
):
    return AIExecutionOptimizerService(db).get_recommendations(project_id=project_id)
