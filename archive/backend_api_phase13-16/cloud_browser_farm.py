"""Phase 13 – Cloud Browser Farm API router."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth import get_auth_context, AuthContext
from app.database import get_db
from app.services.cloud_browser_farm import CloudBrowserFarmService

router = APIRouter(prefix='/browser-farm', tags=['Phase13-BrowserFarm'])


class ReserveRequest(BaseModel):
    browser_type: str
    job_id: str


class ActivateRequest(BaseModel):
    recording_url: str | None = None


class UpdateMetricsRequest(BaseModel):
    cpu_pct: float = 0.0
    memory_mb: int = 0
    network_requests: int = 0
    page_load_ms: int = 0


@router.post('/provision')
def provision_pool(db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return CloudBrowserFarmService(db).provision_pool()


@router.get('/pool')
def get_pool(db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return CloudBrowserFarmService(db).get_pool_status()


@router.post('/reserve')
def reserve_session(body: ReserveRequest, db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return CloudBrowserFarmService(db).reserve_session(body.browser_type, body.job_id)


@router.post('/sessions/{session_id}/activate')
def activate_session(session_id: str, body: ActivateRequest, db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return CloudBrowserFarmService(db).activate_session(session_id, body.recording_url)


@router.post('/sessions/{session_id}/release')
def release_session(session_id: str, db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return CloudBrowserFarmService(db).release_session(session_id)


@router.post('/sessions/{session_id}/metrics')
def update_metrics(session_id: str, body: UpdateMetricsRequest, db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return CloudBrowserFarmService(db).update_session_metrics(session_id, body.model_dump())


@router.get('/sessions/live')
def live_sessions(db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return CloudBrowserFarmService(db).get_live_sessions()


@router.get('/health')
def session_health(db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return CloudBrowserFarmService(db).get_session_health()


@router.post('/cleanup')
def auto_cleanup(db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return CloudBrowserFarmService(db).auto_cleanup()


@router.get('/metrics')
def farm_metrics(db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return CloudBrowserFarmService(db).get_farm_metrics()
