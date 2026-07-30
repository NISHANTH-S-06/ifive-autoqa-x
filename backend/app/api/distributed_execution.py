"""Phase 13 – Distributed Execution API router."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.auth import get_auth_context, AuthContext
from app.database import get_db
from app.services.distributed_execution import DistributedExecutionService

router = APIRouter(prefix='/execution', tags=['Phase13-Execution'])


class RegisterWorkerRequest(BaseModel):
    worker_name: str
    region: str = 'local'
    capacity: int = Field(default=5, ge=1, le=50)
    browser_types: list[str] = ['CHROMIUM']


class SubmitJobRequest(BaseModel):
    project_id: int | None = None
    browser_type: str = 'CHROMIUM'
    priority: int = Field(default=5, ge=1, le=10)
    payload: dict[str, Any] = {}
    estimated_duration_ms: int = 60000


class CompleteJobRequest(BaseModel):
    success: bool = True
    duration_ms: int = 0


@router.get('/workers')
def list_workers(db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return DistributedExecutionService(db).list_workers()


@router.post('/workers/register', status_code=201)
def register_worker(body: RegisterWorkerRequest, db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return DistributedExecutionService(db).register_worker(
        worker_name=body.worker_name,
        region=body.region,
        capacity=body.capacity,
        browser_types=body.browser_types,
    )


@router.get('/workers/health')
def worker_health(db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return DistributedExecutionService(db).get_worker_health()


@router.post('/workers/{worker_id}/heartbeat')
def worker_heartbeat(worker_id: int, db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return DistributedExecutionService(db).update_worker_heartbeat(worker_id)


@router.get('/queue')
def get_queue(project_id: int | None = None, db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return DistributedExecutionService(db).get_queue_status(project_id=project_id)


@router.post('/queue/submit', status_code=201)
def submit_job(body: SubmitJobRequest, db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    job = DistributedExecutionService(db).submit_job(
        project_id=body.project_id,
        browser_type=body.browser_type,
        priority=body.priority,
        payload=body.payload,
        estimated_duration_ms=body.estimated_duration_ms,
    )
    return {'id': job.id, 'job_id': job.job_id, 'queue_status': job.queue_status, 'priority': job.priority}


@router.post('/queue/{job_id}/complete')
def complete_job(job_id: str, body: CompleteJobRequest, db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return DistributedExecutionService(db).complete_job(job_id, body.success, body.duration_ms)


@router.post('/queue/retry')
def retry_failed(db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return DistributedExecutionService(db).retry_failed_jobs()


@router.get('/analytics')
def queue_analytics(db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return DistributedExecutionService(db).get_queue_analytics()


@router.get('/cost')
def cost_report(db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return DistributedExecutionService(db).get_cost_report()


@router.get('/scale')
def auto_scale_recommendation(db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return DistributedExecutionService(db).auto_scale_workers()
