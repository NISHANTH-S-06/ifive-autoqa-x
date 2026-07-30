"""Phase 15 – Enterprise Software Intelligence Graph API router."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth import get_auth_context, AuthContext
from app.database import get_db
from app.services.software_graph import SoftwareGraphService

router = APIRouter(prefix='/software-graph', tags=['Phase15-SoftwareGraph'])


@router.post('/seed')
def seed_graph(db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return SoftwareGraphService(db).seed_graph()


@router.get('/graph')
def get_graph(node_type: str | None = None, db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return SoftwareGraphService(db).get_graph(node_type=node_type)


@router.get('/impact/{node_key}')
def analyze_impact(node_key: str, db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return SoftwareGraphService(db).analyze_impact(node_key)
