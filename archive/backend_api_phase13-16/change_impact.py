"""Phase 15 – AI Change Impact Intelligence API router."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth import get_auth_context, AuthContext
from app.database import get_db
from app.services.change_impact_intelligence import ChangeImpactService

router = APIRouter(prefix='/change-impact', tags=['Phase15-ChangeImpact'])


class AnalyzeCommitRequest(BaseModel):
    commit_hash: str
    author: str
    changed_files: list[str]


@router.post('/analyze', status_code=201)
def analyze_commit(body: AnalyzeCommitRequest, db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return ChangeImpactService(db).analyze_commit(body.commit_hash, body.author, body.changed_files)


@router.get('/history')
def list_records(limit: int = 20, db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return ChangeImpactService(db).list_records(limit=limit)
