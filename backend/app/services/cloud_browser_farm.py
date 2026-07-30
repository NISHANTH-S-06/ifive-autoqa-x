"""Module 2 – Cloud Browser Farm service."""
from __future__ import annotations

import json
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.models.phase13_models import BrowserFarmSession

BROWSER_POOL_SIZES: dict[str, int] = {
    'CHROMIUM': 10,
    'FIREFOX': 8,
    'WEBKIT': 6,
    'EDGE': 4,
    'CHROME': 8,
    'MOBILE_CHROME': 5,
    'MOBILE_SAFARI': 4,
}


class CloudBrowserFarmService:
    """Manages the cloud browser farm pool."""

    def __init__(self, db: Session) -> None:
        self.db = db

    # ── Pool provisioning ─────────────────────────────────────────────────────

    def provision_pool(self) -> dict[str, Any]:
        """Seed one session per browser type if pool is empty."""
        existing = self.db.query(BrowserFarmSession).count()
        if existing > 0:
            return {'status': 'ALREADY_PROVISIONED', 'sessions': existing}
        created = 0
        for browser, count in BROWSER_POOL_SIZES.items():
            for i in range(count):
                session = BrowserFarmSession(
                    session_id=f'BFS-{browser[:3]}-{uuid.uuid4().hex[:8].upper()}',
                    browser_type=browser,
                    session_status='AVAILABLE',
                    health_score=100.0,
                    metrics_json=json.dumps({
                        'cpu_pct': 0.0,
                        'memory_mb': 0,
                        'network_requests': 0,
                        'page_load_ms': 0,
                    }),
                )
                self.db.add(session)
                created += 1
        self.db.commit()
        return {'status': 'PROVISIONED', 'sessions_created': created}

    # ── Pool status ───────────────────────────────────────────────────────────

    def get_pool_status(self) -> dict[str, Any]:
        sessions = self.db.query(BrowserFarmSession).all()
        by_browser: dict[str, dict[str, int]] = {}
        for s in sessions:
            b = s.browser_type
            if b not in by_browser:
                by_browser[b] = {'total': 0, 'available': 0, 'reserved': 0, 'active': 0, 'unhealthy': 0}
            by_browser[b]['total'] += 1
            status_key = s.session_status.lower()
            if status_key in by_browser[b]:
                by_browser[b][status_key] += 1
        total = len(sessions)
        available = sum(1 for s in sessions if s.session_status == 'AVAILABLE')
        return {
            'total_sessions': total,
            'available': available,
            'utilization_pct': round((total - available) / max(total, 1) * 100, 1),
            'by_browser': by_browser,
        }

    # ── Reservation ───────────────────────────────────────────────────────────

    def reserve_session(self, browser_type: str, job_id: str) -> dict[str, Any]:
        session = (
            self.db.query(BrowserFarmSession)
            .filter_by(browser_type=browser_type, session_status='AVAILABLE')
            .first()
        )
        if not session:
            return {'error': f'No available {browser_type} session', 'status': 'UNAVAILABLE'}
        session.session_status = 'RESERVED'
        session.reserved_by_job_id = job_id
        session.reserved_at = datetime.utcnow()
        self.db.commit()
        return {
            'session_id': session.session_id,
            'browser_type': session.browser_type,
            'status': 'RESERVED',
            'reserved_at': session.reserved_at.isoformat(),
        }

    def activate_session(self, session_id: str, recording_url: str | None = None) -> dict[str, Any]:
        session = self.db.query(BrowserFarmSession).filter_by(session_id=session_id).first()
        if not session:
            return {'error': 'Session not found'}
        session.session_status = 'ACTIVE'
        session.recording_url = recording_url
        self.db.commit()
        return {'session_id': session_id, 'status': 'ACTIVE'}

    def release_session(self, session_id: str) -> dict[str, Any]:
        session = self.db.query(BrowserFarmSession).filter_by(session_id=session_id).first()
        if not session:
            return {'error': 'Session not found'}
        session.session_status = 'AVAILABLE'
        session.reserved_by_job_id = None
        session.released_at = datetime.utcnow()
        metrics = json.loads(session.metrics_json)
        metrics = {'cpu_pct': 0.0, 'memory_mb': 0, 'network_requests': 0, 'page_load_ms': 0}
        session.metrics_json = json.dumps(metrics)
        self.db.commit()
        return {'session_id': session_id, 'status': 'RELEASED'}

    # ── Health monitoring ─────────────────────────────────────────────────────

    def get_session_health(self) -> dict[str, Any]:
        sessions = self.db.query(BrowserFarmSession).all()
        unhealthy = [s for s in sessions if s.session_status == 'UNHEALTHY']
        avg_health = sum(s.health_score for s in sessions) / max(len(sessions), 1)
        return {
            'overall_health_pct': round(avg_health, 1),
            'unhealthy_count': len(unhealthy),
            'unhealthy_sessions': [s.session_id for s in unhealthy],
        }

    def update_session_metrics(self, session_id: str, metrics: dict[str, Any]) -> dict[str, Any]:
        session = self.db.query(BrowserFarmSession).filter_by(session_id=session_id).first()
        if not session:
            return {'error': 'Session not found'}
        existing = json.loads(session.metrics_json)
        existing.update(metrics)
        session.metrics_json = json.dumps(existing)
        # Health score: penalise high CPU/memory
        cpu = metrics.get('cpu_pct', 0)
        health = max(0.0, 100.0 - cpu * 0.5)
        session.health_score = round(health, 1)
        if health < 30:
            session.session_status = 'UNHEALTHY'
        self.db.commit()
        return {'session_id': session_id, 'health_score': health}

    # ── Auto-cleanup ──────────────────────────────────────────────────────────

    def auto_cleanup(self) -> dict[str, Any]:
        """Reset unhealthy sessions back to AVAILABLE."""
        unhealthy = self.db.query(BrowserFarmSession).filter_by(session_status='UNHEALTHY').all()
        healed = 0
        for s in unhealthy:
            s.session_status = 'AVAILABLE'
            s.health_score = 100.0
            s.reserved_by_job_id = None
            s.metrics_json = json.dumps({'cpu_pct': 0.0, 'memory_mb': 0, 'network_requests': 0, 'page_load_ms': 0})
            healed += 1
        self.db.commit()
        return {'healed_count': healed}

    # ── Live sessions ─────────────────────────────────────────────────────────

    def get_live_sessions(self) -> list[dict[str, Any]]:
        sessions = (
            self.db.query(BrowserFarmSession)
            .filter(BrowserFarmSession.session_status.in_(['RESERVED', 'ACTIVE']))
            .all()
        )
        return [
            {
                'session_id': s.session_id,
                'browser_type': s.browser_type,
                'session_status': s.session_status,
                'reserved_by_job_id': s.reserved_by_job_id,
                'health_score': s.health_score,
                'recording_url': s.recording_url,
                'metrics': json.loads(s.metrics_json),
                'reserved_at': s.reserved_at.isoformat() if s.reserved_at else None,
            }
            for s in sessions
        ]

    # ── Farm metrics ──────────────────────────────────────────────────────────

    def get_farm_metrics(self) -> dict[str, Any]:
        sessions = self.db.query(BrowserFarmSession).all()
        total = len(sessions)
        available = sum(1 for s in sessions if s.session_status == 'AVAILABLE')
        active = sum(1 for s in sessions if s.session_status == 'ACTIVE')
        reserved = sum(1 for s in sessions if s.session_status == 'RESERVED')
        return {
            'total_sessions': total,
            'available': available,
            'active': active,
            'reserved': reserved,
            'utilization_pct': round((active + reserved) / max(total, 1) * 100, 1),
            'avg_health_score': round(sum(s.health_score for s in sessions) / max(total, 1), 1),
        }
