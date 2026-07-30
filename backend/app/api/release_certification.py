"""Phase 16 API Router: Autonomous Release Certification."""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.release_certification_service import ReleaseCertificationService

release_cert_router = APIRouter(prefix="/api/release-certification", tags=["Release Certification"])

class CertifyRequest(BaseModel):
    release_version: str

@release_cert_router.post("/certify")
def certify_release(body: CertifyRequest, db: Session = Depends(get_db)):
    return ReleaseCertificationService(db).certify_release(release_version=body.release_version)

@release_cert_router.get("/history")
def get_certifications_history(db: Session = Depends(get_db)):
    return ReleaseCertificationService(db).fetch_certifications()
