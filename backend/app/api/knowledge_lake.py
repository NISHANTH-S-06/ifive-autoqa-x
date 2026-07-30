"""Phase 15 – Enterprise Knowledge Lake API router."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth import get_auth_context, AuthContext
from app.database import get_db
from app.services.executive_mission_control import KnowledgeLakeService

router = APIRouter(prefix='/knowledge-lake', tags=['Phase15-KnowledgeLake'])


@router.post('/seed')
def seed_lake(db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return KnowledgeLakeService(db).seed_lake()


@router.get('/search')
def search_lake(query: str = '', db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return KnowledgeLakeService(db).search_lake(query=query)
