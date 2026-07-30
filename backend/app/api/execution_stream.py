"""Phase 13 – Execution Stream API router."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth import get_auth_context, AuthContext
from app.database import get_db
from app.services.execution_stream import ExecutionStreamService

router = APIRouter(prefix='/stream', tags=['Phase13-ExecutionStream'])


class EmitEventRequest(BaseModel):
    job_id: str
    event_type: str
    payload: dict[str, Any] = {}


@router.post('/events', status_code=201)
def emit_event(body: EmitEventRequest, db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    event = ExecutionStreamService(db).emit_event(body.job_id, body.event_type, body.payload)
    return {'id': event.id, 'job_id': event.job_id, 'event_type': event.event_type, 'sequence_num': event.sequence_num}


@router.get('/events')
def recent_events(limit: int = 50, db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return ExecutionStreamService(db).get_recent_events(limit=limit)


@router.get('/execution/{job_id}')
def execution_events(job_id: str, event_type: str | None = None, limit: int = 100, db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return ExecutionStreamService(db).get_execution_events(job_id, event_type=event_type, limit=limit)


@router.get('/execution/{job_id}/summary')
def execution_summary(job_id: str, db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return ExecutionStreamService(db).get_stream_summary(job_id)
