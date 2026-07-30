"""Phase 16 API Router: Enterprise Policy Engine & Digital Twin V2."""
from typing import Any, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.digital_twin_v2 import DigitalTwinV2Service
from app.services.enterprise_policy_engine import EnterprisePolicyEngineService

policy_router = APIRouter(prefix="/api/policies", tags=["Policies & Digital Twin"])

@policy_router.post("/seed")
def seed_policies(db: Session = Depends(get_db)):
    return EnterprisePolicyEngineService(db).seed_policies()

@policy_router.get("/list")
def list_policies(category: Optional[str] = Query(None), db: Session = Depends(get_db)):
    service = EnterprisePolicyEngineService(db)
    service.seed_policies()
    return service.fetch_policies(category=category)

@policy_router.post("/evaluate")
def evaluate_policies(body: dict[str, Any], db: Session = Depends(get_db)):
    return EnterprisePolicyEngineService(db).evaluate_policies(context=body)

@policy_router.get("/digital-twin-v2")
def get_digital_twin_v2(db: Session = Depends(get_db)):
    return DigitalTwinV2Service(db).sync_digital_twin()
