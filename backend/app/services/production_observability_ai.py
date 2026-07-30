"""Module 7 – Production Observability AI service."""
from __future__ import annotations

import json
from typing import Any

from sqlalchemy.orm import Session

from app.models.phase16_models import ObservabilityMetricV2

DEFAULT_METRICS = [
    {
        'service_name': 'Payments Core Service',
        'error_rate_pct': 0.12,
        'latency_p99_ms': 88.4,
        'predicted_incident_risk': 0.15,
        'prediction_summary': 'Low error trend. P99 latency within 100ms threshold.',
        'metrics': {'throughput_rpm': 14200, 'cpu_pct': 38.2, 'mem_mb': 1024},
    },
    {
        'service_name': 'Search Indexer Microservice',
        'error_rate_pct': 2.45,
        'latency_p99_ms': 310.0,
        'predicted_incident_risk': 0.68,
        'prediction_summary': 'Elevated memory leakage detected. Incident predicted in 4.5 hours if unmitigated.',
        'metrics': {'throughput_rpm': 8500, 'cpu_pct': 84.1, 'mem_mb': 3890},
    },
]


class ProductionObservabilityAIService:
    """Production APM observability metrics, APM logs/exceptions correlation, and incident predictor."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def seed_metrics(self) -> list[dict[str, Any]]:
        count = self.db.query(ObservabilityMetricV2).count()
        if count > 0:
            return self.fetch_metrics()

        for m in DEFAULT_METRICS:
            rec = ObservabilityMetricV2(
                service_name=m['service_name'],
                error_rate_pct=m['error_rate_pct'],
                latency_p99_ms=m['latency_p99_ms'],
                predicted_incident_risk=m['predicted_incident_risk'],
                prediction_summary=m['prediction_summary'],
                metrics_json=json.dumps(m['metrics']),
            )
            self.db.add(rec)
        self.db.commit()
        return self.fetch_metrics()

    def fetch_metrics(self) -> list[dict[str, Any]]:
        records = self.db.query(ObservabilityMetricV2).all()
        return [
            {
                'id': r.id,
                'service_name': r.service_name,
                'error_rate_pct': r.error_rate_pct,
                'latency_p99_ms': r.latency_p99_ms,
                'predicted_incident_risk': r.predicted_incident_risk,
                'prediction_summary': r.prediction_summary,
                'metrics': json.loads(r.metrics_json),
                'created_at': r.created_at.isoformat(),
            }
            for r in records
        ]
