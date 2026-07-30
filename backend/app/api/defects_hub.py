"""Phase 15 – AI Defect Intelligence Hub API router."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth import get_auth_context, AuthContext
from app.database import get_db
from app.services.defect_intelligence_hub import DefectIntelligenceHubService

router = APIRouter(prefix='/defects-hub', tags=['Phase15-DefectsHub'])


class PredictDuplicateRequest(BaseModel):
    defect_description: str


@router.post('/seed')
def seed_clusters(db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return DefectIntelligenceHubService(db).seed_clusters()


@router.get('/clusters')
def list_clusters(db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return DefectIntelligenceHubService(db).list_clusters()


@router.post('/predict-duplicate')
def predict_duplicates(body: PredictDuplicateRequest, db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return DefectIntelligenceHubService(db).predict_duplicates(body.defect_description)
