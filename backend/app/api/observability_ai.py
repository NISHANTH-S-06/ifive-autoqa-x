"""Phase 16 API Router: Production Observability AI."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.production_observability_ai import ProductionObservabilityAIService

observability_router = APIRouter(prefix="/api/observability-ai", tags=["Observability AI"])

@observability_router.post("/seed")
def seed_observability(db: Session = Depends(get_db)):
    return ProductionObservabilityAIService(db).seed_metrics()

@observability_router.get("/metrics")
def get_observability_metrics(db: Session = Depends(get_db)):
    service = ProductionObservabilityAIService(db)
    service.seed_metrics()
    return service.fetch_metrics()
