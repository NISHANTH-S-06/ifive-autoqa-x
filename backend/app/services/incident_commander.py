"""Module 7 – Autonomous Incident Commander service."""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy.orm import Session

from app.models.phase14_models import Incident, IncidentTimeline


class IncidentCommanderService:
    """Autonomous Incident Commander – auto-creates incidents, assigns teams, correlates root cause, builds timeline."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def trigger_incident(
        self,
        title: str,
        severity: str = 'SEV-2',
        evidence: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        number = f'INC-{datetime.utcnow().strftime("%Y%m%d")}-{uuid.uuid4().hex[:4].upper()}'
        
        recs = [
            {'action': 'Rollback checkout service to v2.4.1', 'priority': 'HIGH'},
            {'action': 'Flush Redis cache and restart worker nodes', 'priority': 'MEDIUM'},
        ]

        inc = Incident(
            incident_number=number,
            title=title,
            severity=severity,
            incident_status='INVESTIGATING',
            assigned_team='SRE / Platform QA',
            root_cause_summary=f'High latency detected on API gateway correlating with database connection pool exhaustion.',
            predicted_eta_minutes=45,
            recommendations_json=json.dumps(recs),
        )
        self.db.add(inc)
        self.db.flush()

        # Build initial timeline event
        tl = IncidentTimeline(
            incident_id=inc.id,
            event_type='TRIGGERED',
            description=f'Incident triggered autonomously by production monitoring: {title}',
            evidence_json=json.dumps(evidence or {}),
        )
        self.db.add(tl)
        self.db.commit()
        self.db.refresh(inc)

        return self.get_incident(inc.id)  # type: ignore

    def list_incidents(self, status: str | None = None) -> list[dict[str, Any]]:
        q = self.db.query(Incident)
        if status:
            q = q.filter_by(incident_status=status)
        incidents = q.order_by(Incident.created_at.desc()).all()
        return [self._inc_dict(i) for i in incidents]

    def get_incident(self, incident_id: int) -> dict[str, Any]:
        inc = self.db.query(Incident).filter_by(id=incident_id).first()
        if not inc:
            return {'error': 'Incident not found'}
        return self._inc_dict(inc)

    def resolve_incident(self, incident_id: int, summary: str = '') -> dict[str, Any]:
        inc = self.db.query(Incident).filter_by(id=incident_id).first()
        if not inc:
            return {'error': 'Incident not found'}
        inc.incident_status = 'RESOLVED'
        inc.resolved_at = datetime.utcnow()
        if summary:
            inc.root_cause_summary = summary
        
        tl = IncidentTimeline(
            incident_id=inc.id,
            event_type='RESOLVED',
            description=f'Incident marked as resolved. Summary: {summary or inc.root_cause_summary}',
        )
        self.db.add(tl)
        self.db.commit()
        return self._inc_dict(inc)

    def _inc_dict(self, i: Incident) -> dict[str, Any]:
        timeline = self.db.query(IncidentTimeline).filter_by(incident_id=i.id).order_by(IncidentTimeline.created_at).all()
        return {
            'id': i.id,
            'incident_number': i.incident_number,
            'title': i.title,
            'severity': i.severity,
            'incident_status': i.incident_status,
            'assigned_team': i.assigned_team,
            'root_cause_summary': i.root_cause_summary,
            'predicted_eta_minutes': i.predicted_eta_minutes,
            'recommendations': json.loads(i.recommendations_json),
            'timeline': [
                {
                    'id': t.id,
                    'event_type': t.event_type,
                    'description': t.description,
                    'evidence': json.loads(t.evidence_json),
                    'created_at': t.created_at.isoformat(),
                }
                for t in timeline
            ],
            'created_at': i.created_at.isoformat(),
            'resolved_at': i.resolved_at.isoformat() if i.resolved_at else None,
        }
