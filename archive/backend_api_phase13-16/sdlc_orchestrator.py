"""Phase 16 API Router: Autonomous SDLC Orchestrator & AI Executive Decision Engine."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.sdlc_orchestrator import ExecutiveDecisionEngineService, SDLCOrchestratorService

sdlc_router = APIRouter(prefix="/api/sdlc-orchestrator", tags=["SDLC & Executive Decision"])

@sdlc_router.post("/seed")
def seed_sdlc(db: Session = Depends(get_db)):
    return SDLCOrchestratorService(db).seed_sdlc()

@sdlc_router.get("/status")
def get_sdlc_status(db: Session = Depends(get_db)):
    service = SDLCOrchestratorService(db)
    service.seed_sdlc()
    return service.fetch_sdlc_status()

@sdlc_router.get("/executive-decisions")
def get_executive_decisions(db: Session = Depends(get_db)):
    service = ExecutiveDecisionEngineService(db)
    service.seed_decisions()
    return service.fetch_decisions()
