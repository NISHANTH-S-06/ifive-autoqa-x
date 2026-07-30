"""Module 4 – Observability Platform service."""
from __future__ import annotations

import json
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.phase13_models import ObservabilityMetric


class ObservabilityPlatformService:
    """Collects, stores, and aggregates platform observability metrics."""

    def __init__(self, db: Session) -> None:
        self.db = db

    # ── Ingestion ─────────────────────────────────────────────────────────────

    def ingest_metric(
        self,
        metric_name: str,
        value: float,
        unit: str = 'ms',
        source: str = 'SYSTEM',
        labels: dict[str, Any] | None = None,
        project_id: int | None = None,
        trace_id: str | None = None,
    ) -> ObservabilityMetric:
        metric = ObservabilityMetric(
            project_id=project_id,
            metric_name=metric_name,
            metric_value=value,
            metric_unit=unit,
            metric_source=source,
            labels_json=json.dumps(labels or {}),
            trace_id=trace_id,
        )
        self.db.add(metric)
        self.db.commit()
        self.db.refresh(metric)
        return metric

    def ingest_batch(self, metrics: list[dict[str, Any]]) -> dict[str, Any]:
        ingested = 0
        for m in metrics:
            self.ingest_metric(
                metric_name=m.get('metric_name', 'unknown'),
                value=float(m.get('value', 0)),
                unit=m.get('unit', 'ms'),
                source=m.get('source', 'SYSTEM'),
                labels=m.get('labels'),
                project_id=m.get('project_id'),
                trace_id=m.get('trace_id'),
            )
            ingested += 1
        return {'ingested': ingested}

    # ── Querying ──────────────────────────────────────────────────────────────

    def query_metrics(
        self,
        metric_name: str | None = None,
        source: str | None = None,
        project_id: int | None = None,
        since_hours: int = 24,
        limit: int = 200,
    ) -> list[dict[str, Any]]:
        cutoff = datetime.utcnow() - timedelta(hours=since_hours)
        q = self.db.query(ObservabilityMetric).filter(ObservabilityMetric.created_at >= cutoff)
        if metric_name:
            q = q.filter_by(metric_name=metric_name)
        if source:
            q = q.filter_by(metric_source=source)
        if project_id:
            q = q.filter_by(project_id=project_id)
        rows = q.order_by(ObservabilityMetric.created_at.desc()).limit(limit).all()
        return [
            {
                'id': r.id,
                'metric_name': r.metric_name,
                'metric_value': r.metric_value,
                'metric_unit': r.metric_unit,
                'metric_source': r.metric_source,
                'labels': json.loads(r.labels_json),
                'trace_id': r.trace_id,
                'created_at': r.created_at.isoformat(),
            }
            for r in rows
        ]

    # ── Dashboard ─────────────────────────────────────────────────────────────

    def get_dashboard(self) -> dict[str, Any]:
        """Aggregate observability dashboard."""
        cutoff = datetime.utcnow() - timedelta(hours=24)
        all_metrics = self.db.query(ObservabilityMetric).filter(ObservabilityMetric.created_at >= cutoff).all()

        def avg_for(name: str) -> float:
            vals = [m.metric_value for m in all_metrics if m.metric_name == name]
            return round(sum(vals) / max(len(vals), 1), 2)

        metric_names = list({m.metric_name for m in all_metrics})
        summary: dict[str, float] = {name: avg_for(name) for name in metric_names}

        by_source: dict[str, int] = {}
        for m in all_metrics:
            by_source[m.metric_source] = by_source.get(m.metric_source, 0) + 1

        return {
            'period_hours': 24,
            'total_metrics_ingested': len(all_metrics),
            'metric_averages': summary,
            'by_source': by_source,
            'health_status': 'HEALTHY' if len(all_metrics) < 100000 else 'HIGH_VOLUME',
        }

    # ── Tracing ───────────────────────────────────────────────────────────────

    def get_traces(self, trace_id: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
        q = self.db.query(ObservabilityMetric).filter(ObservabilityMetric.trace_id.isnot(None))
        if trace_id:
            q = q.filter_by(trace_id=trace_id)
        rows = q.order_by(ObservabilityMetric.created_at.desc()).limit(limit).all()
        # Group by trace_id
        traces: dict[str, list[dict[str, Any]]] = {}
        for r in rows:
            tid = r.trace_id or 'unknown'
            if tid not in traces:
                traces[tid] = []
            traces[tid].append({
                'metric_name': r.metric_name,
                'metric_value': r.metric_value,
                'metric_unit': r.metric_unit,
                'created_at': r.created_at.isoformat(),
            })
        return [{'trace_id': k, 'spans': v} for k, v in traces.items()]

    def get_failure_metrics(self) -> dict[str, Any]:
        all_metrics = self.db.query(ObservabilityMetric).filter(
            ObservabilityMetric.metric_name.like('%failure%')
        ).all()
        total = len(all_metrics)
        avg_val = sum(m.metric_value for m in all_metrics) / max(total, 1)
        return {
            'total_failure_events': total,
            'avg_failure_value': round(avg_val, 2),
            'failure_rate_pct': round(min(avg_val, 100), 1),
        }
