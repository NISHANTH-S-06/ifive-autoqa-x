"""Phase 15 – AI Test Coverage Intelligence API router."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth import get_auth_context, AuthContext
from app.database import get_db
from app.services.coverage_intelligence import CoverageIntelligenceService

router = APIRouter(prefix='/coverage', tags=['Phase15-Coverage'])


@router.post('/compute', status_code=201)
def compute_coverage(db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return CoverageIntelligenceService(db).compute_coverage()


@router.get('/metrics')
def list_metrics(db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return CoverageIntelligenceService(db).list_metrics()


@router.post('/generate-missing/{dimension_type}', status_code=200)
def generate_missing_tests(dimension_type: str, db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return CoverageIntelligenceService(db).generate_missing_tests(dimension_type)
