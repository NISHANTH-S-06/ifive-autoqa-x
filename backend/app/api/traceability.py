"""Phase 16 API Router: Traceability Matrix."""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.traceability_matrix_service import TraceabilityMatrixService

trace_router = APIRouter(prefix="/api/traceability", tags=["Traceability"])

@trace_router.post("/seed")
def seed_traceability(db: Session = Depends(get_db)):
    return TraceabilityMatrixService(db).seed_traceability()

@trace_router.get("/matrix")
def get_traceability_matrix(release_version: Optional[str] = Query(None), db: Session = Depends(get_db)):
    service = TraceabilityMatrixService(db)
    service.seed_traceability()
    return service.fetch_matrix(release_version=release_version)

@trace_router.get("/gap-report")
def get_gap_report(db: Session = Depends(get_db)):
    service = TraceabilityMatrixService(db)
    service.seed_traceability()
    return service.compute_gap_report()
