"""Phase 16 API Router: Requirements."""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.requirement_intelligence import RequirementIntelligenceService

req_router = APIRouter(prefix="/api/requirements", tags=["Requirements"])

class AnalyzeReqRequest(BaseModel):
    requirement_code: str
    title: str
    description: str

@req_router.post("/seed")
def seed_requirements(db: Session = Depends(get_db)):
    return RequirementIntelligenceService(db).seed_requirements()

@req_router.get("/list")
def list_requirements(req_type: Optional[str] = Query(None), db: Session = Depends(get_db)):
    service = RequirementIntelligenceService(db)
    service.seed_requirements()
    return service.fetch_requirements(req_type=req_type)

@req_router.post("/analyze")
def analyze_requirement(body: AnalyzeReqRequest, db: Session = Depends(get_db)):
    return RequirementIntelligenceService(db).analyze_requirement(
        req_code=body.requirement_code, title=body.title, description=body.description
    )
