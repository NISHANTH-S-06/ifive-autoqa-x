"""Phase 15 – Enterprise Engineering Analytics API router."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth import get_auth_context, AuthContext
from app.database import get_db
from app.services.engineering_analytics import EngineeringAnalyticsService

router = APIRouter(prefix='/engineering', tags=['Phase15-Engineering'])


@router.post('/compute', status_code=201)
def compute_metrics(db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return EngineeringAnalyticsService(db).compute_metrics()


@router.get('/metrics')
def list_metrics(db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return EngineeringAnalyticsService(db).list_metrics()
