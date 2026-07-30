"""Phase 16 API Routers Batch 1: Knowledge Lake V2, Requirements, Traceability, Architecture."""
from typing import Any, Optional
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.knowledge_lake_v2 import KnowledgeLakeV2Service
from app.services.requirement_intelligence import RequirementIntelligenceService
from app.services.traceability_matrix_service import TraceabilityMatrixService
from app.services.architecture_intelligence import ArchitectureIntelligenceService

# Router 1: Knowledge Lake V2
kl_v2_router = APIRouter(prefix="/api/knowledge-lake-v2", tags=["Knowledge Lake V2"])

@kl_v2_router.post("/seed")
def seed_knowledge_lake_v2(db: Session = Depends(get_db)):
    return KnowledgeLakeV2Service(db).seed_lake()

@kl_v2_router.get("/search")
def search_knowledge_lake_v2(
    query: str = Query("", description="Search term"),
    source_type: Optional[str] = Query(None, description="Filter source type"),
    db: Session = Depends(get_db)
):
    service = KnowledgeLakeV2Service(db)
    service.seed_lake()
    return service.search_lake(query=query, source_type=source_type)


# Router 2: Requirement Intelligence
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


# Router 3: Traceability Matrix
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


# Router 4: Architecture Intelligence
arch_router = APIRouter(prefix="/api/architecture", tags=["Architecture"])

@arch_router.post("/seed")
def seed_architecture(db: Session = Depends(get_db)):
    return ArchitectureIntelligenceService(db).seed_architecture()

@arch_router.get("/graph")
def get_architecture_graph(db: Session = Depends(get_db)):
    service = ArchitectureIntelligenceService(db)
    return service.seed_architecture()
