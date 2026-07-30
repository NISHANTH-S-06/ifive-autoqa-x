"""Module 7 – Enterprise Engineering Analytics service."""
from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.models.phase15_models import EngineeringMetric

METRIC_PROFILES = [
    {'name': 'CYCLE_TIME_HOURS', 'val': 18.4, 'unit': 'hours', 'trend': [26.0, 22.5, 20.0, 18.4]},
    {'name': 'LEAD_TIME_HOURS', 'val': 42.0, 'unit': 'hours', 'trend': [58.0, 50.0, 45.0, 42.0]},
    {'name': 'MTTR_MINUTES', 'val': 35.0, 'unit': 'minutes', 'trend': [65.0, 52.0, 40.0, 35.0]},
    {'name': 'BUG_LEAKAGE_PCT', 'val': 1.2, 'unit': '% leakage', 'trend': [3.5, 2.8, 1.9, 1.2]},
    {'name': 'DEV_PRODUCTIVITY_SCORE', 'val': 91.5, 'unit': 'score', 'trend': [82.0, 85.5, 88.0, 91.5]},
    {'name': 'QA_PRODUCTIVITY_SCORE', 'val': 95.0, 'unit': 'score', 'trend': [86.0, 89.0, 92.0, 95.0]},
    {'name': 'AUTOMATION_GROWTH_PCT', 'val': 94.2, 'unit': '% coverage', 'trend': [80.0, 85.0, 90.0, 94.2]},
]


class EngineeringAnalyticsService:
    """Engineering productivity, Cycle Time, Lead Time, MTTR, and Bug Leakage analytics."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def compute_metrics(self) -> list[dict[str, Any]]:
        metrics = []
        for p in METRIC_PROFILES:
            em = EngineeringMetric(
                metric_name=p['name'],
                metric_value=p['val'],
                unit=p['unit'],
                trend_json=json.dumps({'weeks': ['W-3', 'W-2', 'W-1', 'Now'], 'values': p['trend']}),
            )
            self.db.add(em)
            metrics.append(em)
        self.db.commit()
        return [self._em_dict(m) for m in metrics]

    def list_metrics(self) -> list[dict[str, Any]]:
        metrics = self.db.query(EngineeringMetric).order_by(EngineeringMetric.created_at.desc()).limit(20).all()
        if not metrics:
            return self.compute_metrics()
        return [self._em_dict(m) for m in metrics]

    def _em_dict(self, e: EngineeringMetric) -> dict[str, Any]:
        return {
            'id': e.id,
            'metric_name': e.metric_name,
            'metric_value': e.metric_value,
            'unit': e.unit,
            'trend': json.loads(e.trend_json),
            'created_at': e.created_at.isoformat(),
        }
