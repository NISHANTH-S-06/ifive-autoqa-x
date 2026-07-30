"""Phase 14 – AI Executive Advisor API router."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth import get_auth_context, AuthContext
from app.database import get_db
from app.services.executive_advisor import ExecutiveAdvisorService

router = APIRouter(prefix='/executive-advisor', tags=['Phase14-ExecutiveAdvisor'])


class AskAdvisorRequest(BaseModel):
    query: str


@router.post('/ask', status_code=201)
def ask_advisor(body: AskAdvisorRequest, db: Session = Depends(get_db), ctx: AuthContext = Depends(get_auth_context)):
    return ExecutiveAdvisorService(db).ask_advisor(body.query, asked_by=ctx.operator.id)


@router.get('/history')
def list_insights(limit: int = 20, db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return ExecutiveAdvisorService(db).list_insights(limit=limit)
