"""Phase 13 – Multi-Region Cloud API router."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth import get_auth_context, AuthContext
from app.database import get_db
from app.services.multi_region_cloud import MultiRegionCloudService

router = APIRouter(prefix='/cloud', tags=['Phase13-Cloud'])


class AddRegionRequest(BaseModel):
    cloud_provider: str
    region_name: str
    region_display: str
    failover_priority: int = 9
    config: dict[str, Any] = {}


class FailoverRequest(BaseModel):
    from_region_id: int
    to_region_id: int


@router.post('/regions/seed')
def seed_regions(db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return MultiRegionCloudService(db).seed_regions()


@router.get('/regions')
def list_regions(db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return MultiRegionCloudService(db).list_regions()


@router.post('/regions', status_code=201)
def add_region(body: AddRegionRequest, db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    r = MultiRegionCloudService(db).add_region(
        cloud_provider=body.cloud_provider,
        region_name=body.region_name,
        region_display=body.region_display,
        failover_priority=body.failover_priority,
        config=body.config,
    )
    return {'id': r.id, 'region_name': r.region_name, 'region_status': r.region_status}


@router.get('/health')
def cloud_health(db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return MultiRegionCloudService(db).get_cloud_health()


@router.post('/failover')
def trigger_failover(body: FailoverRequest, db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return MultiRegionCloudService(db).trigger_failover(body.from_region_id, body.to_region_id)


@router.get('/backup')
def backup_status(db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return MultiRegionCloudService(db).get_backup_status()
