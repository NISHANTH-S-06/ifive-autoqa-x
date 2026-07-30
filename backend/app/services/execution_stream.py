"""Module 3 – Real-Time Execution Stream service (REST event log)."""
from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.models.phase13_models import ExecutionStreamEvent

EVENT_TYPES = [
    'STATUS', 'STEP', 'SCREENSHOT', 'LOG', 'NETWORK',
    'CONSOLE', 'PERFORMANCE', 'AI_DECISION', 'VISUAL_COMPARE', 'BUG_CREATED',
]


class ExecutionStreamService:
    """REST-based real-time execution event log."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def emit_event(
        self,
        job_id: str,
        event_type: str,
        payload: dict[str, Any],
    ) -> ExecutionStreamEvent:
        last = (
            self.db.query(ExecutionStreamEvent)
            .filter_by(job_id=job_id)
            .order_by(ExecutionStreamEvent.sequence_num.desc())
            .first()
        )
        seq = (last.sequence_num + 1) if last else 1
        event = ExecutionStreamEvent(
            job_id=job_id,
            event_type=event_type,
            event_payload_json=json.dumps(payload),
            sequence_num=seq,
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def get_execution_events(
        self,
        job_id: str,
        event_type: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        q = self.db.query(ExecutionStreamEvent).filter_by(job_id=job_id)
        if event_type:
            q = q.filter_by(event_type=event_type)
        events = q.order_by(ExecutionStreamEvent.sequence_num).limit(limit).all()
        return [
            {
                'id': e.id,
                'job_id': e.job_id,
                'event_type': e.event_type,
                'payload': json.loads(e.event_payload_json),
                'sequence_num': e.sequence_num,
                'created_at': e.created_at.isoformat(),
            }
            for e in events
        ]

    def get_recent_events(self, limit: int = 50) -> list[dict[str, Any]]:
        events = (
            self.db.query(ExecutionStreamEvent)
            .order_by(ExecutionStreamEvent.id.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                'id': e.id,
                'job_id': e.job_id,
                'event_type': e.event_type,
                'sequence_num': e.sequence_num,
                'created_at': e.created_at.isoformat(),
            }
            for e in reversed(events)
        ]

    def get_stream_summary(self, job_id: str) -> dict[str, Any]:
        events = self.db.query(ExecutionStreamEvent).filter_by(job_id=job_id).all()
        by_type: dict[str, int] = {}
        for e in events:
            by_type[e.event_type] = by_type.get(e.event_type, 0) + 1
        return {
            'job_id': job_id,
            'total_events': len(events),
            'by_type': by_type,
            'last_event_at': events[-1].created_at.isoformat() if events else None,
        }
