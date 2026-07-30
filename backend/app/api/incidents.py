"""Phase 14 – Autonomous Incident Commander API router."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth import get_auth_context, AuthContext
from app.database import get_db
from app.services.incident_commander import IncidentCommanderService

router = APIRouter(prefix='/incidents', tags=['Phase14-Incidents'])


class TriggerIncidentRequest(BaseModel):
    title: str
    severity: str = 'SEV-2'
    evidence: dict[str, Any] = {}


class ResolveIncidentRequest(BaseModel):
    summary: str = ''


@router.post('/trigger', status_code=201)
def trigger_incident(body: TriggerIncidentRequest, db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return IncidentCommanderService(db).trigger_incident(body.title, body.severity, body.evidence)


@router.get('')
def list_incidents(status: str | None = None, db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return IncidentCommanderService(db).list_incidents(status=status)


@router.get('/{incident_id}')
def get_incident(incident_id: int, db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return IncidentCommanderService(db).get_incident(incident_id)


@router.post('/{incident_id}/resolve')
def resolve_incident(incident_id: int, body: ResolveIncidentRequest, db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return IncidentCommanderService(db).resolve_incident(incident_id, body.summary)
