"""Phase 16 API Router: Customer Experience Intelligence."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.customer_experience_intelligence import CustomerExperienceIntelligenceService

customer_router = APIRouter(prefix="/api/customer-intelligence", tags=["Customer Intelligence"])

@customer_router.post("/seed")
def seed_customer_intelligence(db: Session = Depends(get_db)):
    return CustomerExperienceIntelligenceService(db).seed_feedback()

@customer_router.get("/feedback")
def get_customer_feedback(db: Session = Depends(get_db)):
    service = CustomerExperienceIntelligenceService(db)
    service.seed_feedback()
    return service.fetch_feedback()
