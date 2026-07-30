"""Module 1 – Distributed Execution Orchestrator service."""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.models.phase13_models import (
    ExecutionQueueItem,
    ExecutionWorkerNode,
)


BROWSER_TYPES = ['CHROMIUM', 'FIREFOX', 'WEBKIT', 'EDGE', 'CHROME', 'MOBILE_CHROME', 'MOBILE_SAFARI']


class DistributedExecutionService:
    """Manages distributed test execution across worker nodes."""

    def __init__(self, db: Session) -> None:
        self.db = db

    # ── Worker Management ─────────────────────────────────────────────────────

    def register_worker(
        self,
        worker_name: str,
        region: str = 'local',
        capacity: int = 5,
        browser_types: list[str] | None = None,
    ) -> ExecutionWorkerNode:
        browsers = browser_types or ['CHROMIUM']
        worker = ExecutionWorkerNode(
            worker_name=worker_name,
            region=region,
            capacity=capacity,
            browser_types_json=json.dumps(browsers),
            worker_status='IDLE',
            last_heartbeat=datetime.utcnow(),
        )
        self.db.add(worker)
        self.db.commit()
        self.db.refresh(worker)
        return worker

    def list_workers(self) -> list[dict[str, Any]]:
        workers = self.db.query(ExecutionWorkerNode).order_by(ExecutionWorkerNode.id).all()
        result = []
        for w in workers:
            result.append({
                'id': w.id,
                'worker_name': w.worker_name,
                'worker_status': w.worker_status,
                'region': w.region,
                'capacity': w.capacity,
                'active_jobs': w.active_jobs,
                'browser_types': json.loads(w.browser_types_json),
                'jobs_completed': w.jobs_completed,
                'jobs_failed': w.jobs_failed,
                'avg_job_duration_ms': w.avg_job_duration_ms,
                'total_cost_usd': w.total_cost_usd,
                'last_heartbeat': w.last_heartbeat.isoformat() if w.last_heartbeat else None,
            })
        return result

    def update_worker_heartbeat(self, worker_id: int) -> dict[str, Any]:
        worker = self.db.query(ExecutionWorkerNode).filter_by(id=worker_id).first()
        if not worker:
            return {'error': 'Worker not found'}
        worker.last_heartbeat = datetime.utcnow()
        if worker.worker_status == 'OFFLINE':
            worker.worker_status = 'IDLE'
        self.db.commit()
        return {'worker_id': worker_id, 'last_heartbeat': worker.last_heartbeat.isoformat()}

    def get_worker_health(self) -> dict[str, Any]:
        workers = self.db.query(ExecutionWorkerNode).all()
        total = len(workers)
        idle = sum(1 for w in workers if w.worker_status == 'IDLE')
        busy = sum(1 for w in workers if w.worker_status == 'BUSY')
        unhealthy = sum(1 for w in workers if w.worker_status == 'UNHEALTHY')
        return {
            'total_workers': total,
            'idle': idle,
            'busy': busy,
            'unhealthy': unhealthy,
            'health_pct': round((total - unhealthy) / max(total, 1) * 100, 1),
        }

    # ── Queue Management ──────────────────────────────────────────────────────

    def submit_job(
        self,
        project_id: int | None,
        browser_type: str = 'CHROMIUM',
        priority: int = 5,
        payload: dict[str, Any] | None = None,
        estimated_duration_ms: int = 60000,
    ) -> ExecutionQueueItem:
        job = ExecutionQueueItem(
            job_id=f'JOB-{uuid.uuid4().hex[:12].upper()}',
            project_id=project_id,
            browser_type=browser_type,
            priority=max(1, min(10, priority)),
            payload_json=json.dumps(payload or {}),
            estimated_duration_ms=estimated_duration_ms,
            queue_status='QUEUED',
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        # Auto-assign if idle worker available
        self._try_assign(job)
        return job

    def _try_assign(self, job: ExecutionQueueItem) -> None:
        worker = (
            self.db.query(ExecutionWorkerNode)
            .filter(
                ExecutionWorkerNode.worker_status == 'IDLE',
                ExecutionWorkerNode.active_jobs < ExecutionWorkerNode.capacity,
            )
            .first()
        )
        if worker:
            job.queue_status = 'ASSIGNED'
            job.worker_id = worker.id
            job.started_at = datetime.utcnow()
            worker.active_jobs += 1
            if worker.active_jobs >= worker.capacity:
                worker.worker_status = 'BUSY'
            self.db.commit()

    def get_queue_status(self, project_id: int | None = None) -> dict[str, Any]:
        q = self.db.query(ExecutionQueueItem)
        if project_id:
            q = q.filter_by(project_id=project_id)
        items = q.order_by(ExecutionQueueItem.priority, ExecutionQueueItem.queued_at).all()
        by_status: dict[str, int] = {}
        for item in items:
            by_status[item.queue_status] = by_status.get(item.queue_status, 0) + 1
        return {
            'total': len(items),
            'by_status': by_status,
            'queued': [
                {
                    'job_id': i.job_id,
                    'priority': i.priority,
                    'browser_type': i.browser_type,
                    'queue_status': i.queue_status,
                    'queued_at': i.queued_at.isoformat(),
                }
                for i in items[:20]
            ],
        }

    def complete_job(self, job_id: str, success: bool = True, duration_ms: int = 0) -> dict[str, Any]:
        job = self.db.query(ExecutionQueueItem).filter_by(job_id=job_id).first()
        if not job:
            return {'error': 'Job not found'}
        job.queue_status = 'COMPLETED' if success else 'FAILED'
        job.completed_at = datetime.utcnow()
        job.actual_duration_ms = duration_ms
        job.cost_usd = round(duration_ms / 1000 * 0.002, 4)  # $0.002/sec

        if job.worker_id:
            worker = self.db.query(ExecutionWorkerNode).filter_by(id=job.worker_id).first()
            if worker:
                worker.active_jobs = max(0, worker.active_jobs - 1)
                if success:
                    worker.jobs_completed += 1
                else:
                    worker.jobs_failed += 1
                worker.total_cost_usd += job.cost_usd
                if worker.active_jobs == 0:
                    worker.worker_status = 'IDLE'
                # Rolling avg duration
                total = worker.jobs_completed + worker.jobs_failed
                if total > 0:
                    worker.avg_job_duration_ms = (
                        (worker.avg_job_duration_ms * (total - 1) + duration_ms) / total
                    )
        self.db.commit()
        return {'job_id': job_id, 'status': job.queue_status, 'cost_usd': job.cost_usd}

    def retry_failed_jobs(self) -> dict[str, Any]:
        failed = (
            self.db.query(ExecutionQueueItem)
            .filter(
                ExecutionQueueItem.queue_status == 'FAILED',
                ExecutionQueueItem.retry_count < ExecutionQueueItem.max_retries,
            )
            .all()
        )
        retried = 0
        for job in failed:
            job.queue_status = 'RETRYING'
            job.retry_count += 1
            retried += 1
            self.db.commit()
            self._try_assign(job)
        return {'retried_count': retried}

    # ── Analytics & Cost Tracking ─────────────────────────────────────────────

    def get_queue_analytics(self) -> dict[str, Any]:
        items = self.db.query(ExecutionQueueItem).all()
        total_cost = sum(i.cost_usd for i in items)
        completed = [i for i in items if i.queue_status == 'COMPLETED']
        avg_duration = (
            sum(i.actual_duration_ms or 0 for i in completed) / len(completed)
            if completed else 0
        )
        by_browser: dict[str, int] = {}
        for i in items:
            by_browser[i.browser_type] = by_browser.get(i.browser_type, 0) + 1
        return {
            'total_jobs': len(items),
            'completed': len(completed),
            'failed': sum(1 for i in items if i.queue_status == 'FAILED'),
            'avg_duration_ms': round(avg_duration, 0),
            'total_cost_usd': round(total_cost, 4),
            'by_browser': by_browser,
        }

    def get_cost_report(self) -> dict[str, Any]:
        workers = self.db.query(ExecutionWorkerNode).all()
        items = self.db.query(ExecutionQueueItem).all()
        by_region: dict[str, float] = {}
        for w in workers:
            by_region[w.region] = round(by_region.get(w.region, 0) + w.total_cost_usd, 4)
        by_browser: dict[str, float] = {}
        for i in items:
            by_browser[i.browser_type] = round(by_browser.get(i.browser_type, 0) + i.cost_usd, 4)
        return {
            'total_cost_usd': round(sum(i.cost_usd for i in items), 4),
            'by_region': by_region,
            'by_browser': by_browser,
            'cost_per_execution_avg': round(
                sum(i.cost_usd for i in items) / max(len(items), 1), 6
            ),
        }

    def auto_scale_workers(self) -> dict[str, Any]:
        """Recommend scaling decisions based on queue depth."""
        queued = self.db.query(ExecutionQueueItem).filter_by(queue_status='QUEUED').count()
        workers = self.db.query(ExecutionWorkerNode).filter_by(worker_status='IDLE').count()
        recommendation = 'NO_ACTION'
        if queued > workers * 3:
            recommendation = 'SCALE_UP'
        elif queued == 0 and workers > 2:
            recommendation = 'SCALE_DOWN'
        return {
            'queued_jobs': queued,
            'idle_workers': workers,
            'recommendation': recommendation,
        }
