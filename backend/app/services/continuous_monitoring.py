import json
import logging
from typing import Dict, Any, List
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.phase10_models import ContinuousMonitorAlert

logger = logging.getLogger('autoqa.services.continuous_monitoring')

class ContinuousMonitoringService:
    """
    Module 11: Continuous Autonomous Monitoring
    Auto-monitors connected company products for UI drift, broken links,
    performance degradation, API failures, cert expiry, security header changes, and accessibility issues.
    """

    def __init__(self, db: Session):
        self.db = db

    def create_alert(self, company_id: int, target_url: str, alert_type: str, severity: str, details: Dict[str, Any]) -> ContinuousMonitorAlert:
        alert = ContinuousMonitorAlert(
            company_id=company_id,
            target_url=target_url,
            alert_type=alert_type.upper(),
            severity=severity.upper(),
            details_json=json.dumps(details)
        )
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)
        return alert

    def get_active_alerts(self, company_id: int) -> List[Dict[str, Any]]:
        stmt = select(ContinuousMonitorAlert).where(
            ContinuousMonitorAlert.company_id == company_id,
            ContinuousMonitorAlert.is_resolved == False
        ).order_by(ContinuousMonitorAlert.created_at.desc())

        alerts = list(self.db.scalars(stmt).all())
        return [
            {
                'id': a.id,
                'target_url': a.target_url,
                'alert_type': a.alert_type,
                'severity': a.severity,
                'details': json.loads(a.details_json or '{}'),
                'created_at': a.created_at
            }
            for a in alerts
        ]
