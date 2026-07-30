"""Phase 13 – Observability Platform API router."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth import get_auth_context, AuthContext
from app.database import get_db
from app.services.observability_platform import ObservabilityPlatformService

router = APIRouter(prefix='/observability', tags=['Phase13-Observability'])


class MetricRequest(BaseModel):
    metric_name: str
    value: float
    unit: str = 'ms'
    source: str = 'SYSTEM'
    labels: dict[str, Any] = {}
    project_id: int | None = None
    trace_id: str | None = None


class BatchMetricRequest(BaseModel):
    metrics: list[MetricRequest]


@router.post('/metrics', status_code=201)
def ingest_metric(body: MetricRequest, db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    m = ObservabilityPlatformService(db).ingest_metric(
        metric_name=body.metric_name,
        value=body.value,
        unit=body.unit,
        source=body.source,
        labels=body.labels,
        project_id=body.project_id,
        trace_id=body.trace_id,
    )
    return {'id': m.id, 'metric_name': m.metric_name, 'metric_value': m.metric_value}


@router.post('/metrics/batch', status_code=201)
def ingest_batch(body: BatchMetricRequest, db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    svc = ObservabilityPlatformService(db)
    return svc.ingest_batch([m.model_dump() for m in body.metrics])


@router.get('/metrics')
def query_metrics(
    metric_name: str | None = None,
    source: str | None = None,
    project_id: int | None = None,
    since_hours: int = 24,
    limit: int = 200,
    db: Session = Depends(get_db),
    _: AuthContext = Depends(get_auth_context),
):
    return ObservabilityPlatformService(db).query_metrics(
        metric_name=metric_name, source=source, project_id=project_id,
        since_hours=since_hours, limit=limit,
    )


@router.get('/dashboard')
def dashboard(db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return ObservabilityPlatformService(db).get_dashboard()


@router.get('/traces')
def traces(trace_id: str | None = None, limit: int = 50, db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return ObservabilityPlatformService(db).get_traces(trace_id=trace_id, limit=limit)


@router.get('/failures')
def failure_metrics(db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return ObservabilityPlatformService(db).get_failure_metrics()
