"""Phase 16 API Router: Architecture Intelligence."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.architecture_intelligence import ArchitectureIntelligenceService

arch_router = APIRouter(prefix="/api/architecture", tags=["Architecture"])

@arch_router.post("/seed")
def seed_architecture(db: Session = Depends(get_db)):
    return ArchitectureIntelligenceService(db).seed_architecture()

@arch_router.get("/graph")
def get_architecture_graph(db: Session = Depends(get_db)):
    service = ArchitectureIntelligenceService(db)
    return service.seed_architecture()
