"""Phase 14 – AI Business Process Understanding API router."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth import get_auth_context, AuthContext
from app.database import get_db
from app.services.business_process_center import BusinessProcessCenterService

router = APIRouter(prefix='/business-process', tags=['Phase14-BusinessProcess'])


class CreateProcessRequest(BaseModel):
    process_name: str
    domain_type: str
    risk_score: float = 50.0
    is_critical_path: bool = True
    flow_graph: dict[str, Any] = {}
    project_id: int | None = None


@router.post('/seed')
def seed_processes(db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return BusinessProcessCenterService(db).seed_processes()


@router.get('/processes')
def list_processes(domain_type: str | None = None, db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return BusinessProcessCenterService(db).list_processes(domain_type=domain_type)


@router.post('/processes', status_code=201)
def create_process(body: CreateProcessRequest, db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return BusinessProcessCenterService(db).create_process(
        process_name=body.process_name,
        domain_type=body.domain_type,
        risk_score=body.risk_score,
        is_critical_path=body.is_critical_path,
        flow_graph=body.flow_graph,
        project_id=body.project_id,
    )
