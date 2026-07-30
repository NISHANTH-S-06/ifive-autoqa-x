"""Phase 15 – Enterprise Release Intelligence API router."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth import get_auth_context, AuthContext
from app.database import get_db
from app.services.release_intelligence import ReleaseIntelligenceService

router = APIRouter(prefix='/release-intelligence', tags=['Phase15-ReleaseIntel'])


class EvaluateReleaseRequest(BaseModel):
    release_version: str


@router.post('/evaluate', status_code=201)
def evaluate_release(body: EvaluateReleaseRequest, db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return ReleaseIntelligenceService(db).evaluate_release(body.release_version)


@router.get('/evaluations')
def list_evaluations(limit: int = 20, db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return ReleaseIntelligenceService(db).list_evaluations(limit=limit)
