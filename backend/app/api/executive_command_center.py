"""Phase 13 – Executive Command Center API router."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth import get_auth_context, AuthContext
from app.database import get_db
from app.services.executive_command_center import ExecutiveCommandCenterService

router = APIRouter(prefix='/executive', tags=['Phase13-Executive'])


@router.get('/kpis')
def all_kpis(db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return ExecutiveCommandCenterService(db).get_all_kpis()


@router.get('/companies')
def company_overview(db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return ExecutiveCommandCenterService(db).get_company_overview()


@router.get('/health')
def platform_health(db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return ExecutiveCommandCenterService(db).get_platform_health()


@router.get('/alerts')
def active_alerts(db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return ExecutiveCommandCenterService(db).get_active_alerts()


@router.get('/history')
def snapshot_history(limit: int = 20, db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return ExecutiveCommandCenterService(db).get_snapshot_history(limit=limit)
