"""Module 5 – Enterprise Analytics Engine service."""
from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.models.phase13_models import EnterpriseAnalyticsSnapshot


SNAPSHOT_TYPES = [
    'QUALITY_TREND', 'RELEASE_TREND', 'DEVELOPER_QUALITY',
    'MODULE_QUALITY', 'FAILURE_HEATMAP', 'FLAKY_TESTS',
    'COVERAGE', 'BROWSER_STATS', 'COST',
]

# Realistic simulated data profiles per snapshot type
_PROFILES: dict[str, dict[str, Any]] = {
    'QUALITY_TREND': {'quality_score': 91.4, 'pass_rate': 96.2, 'coverage_pct': 84.5},
    'RELEASE_TREND': {'quality_score': 88.7, 'pass_rate': 94.1, 'coverage_pct': 80.0},
    'DEVELOPER_QUALITY': {'quality_score': 87.3, 'pass_rate': 92.5, 'coverage_pct': 78.0},
    'MODULE_QUALITY': {'quality_score': 90.0, 'pass_rate': 95.0, 'coverage_pct': 82.0},
    'FAILURE_HEATMAP': {'quality_score': 72.0, 'pass_rate': 80.0, 'coverage_pct': 70.0},
    'FLAKY_TESTS': {'quality_score': 85.0, 'pass_rate': 90.0, 'flaky_count': 7},
    'COVERAGE': {'quality_score': 93.0, 'pass_rate': 97.0, 'coverage_pct': 91.0},
    'BROWSER_STATS': {'quality_score': 90.0, 'pass_rate': 95.5, 'coverage_pct': 85.0},
    'COST': {'quality_score': 95.0, 'cost_usd': 142.50},
}


class EnterpriseAnalyticsEngine:
    """Generates and retrieves enterprise analytics snapshots."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def generate_snapshot(self, snapshot_type: str, project_id: int | None = None) -> EnterpriseAnalyticsSnapshot:
        profile = _PROFILES.get(snapshot_type, {})
        snap = EnterpriseAnalyticsSnapshot(
            project_id=project_id,
            snapshot_type=snapshot_type,
            quality_score=profile.get('quality_score', 90.0),
            pass_rate=profile.get('pass_rate', 95.0),
            coverage_pct=profile.get('coverage_pct', 80.0),
            flaky_count=profile.get('flaky_count', 0),
            cost_usd=profile.get('cost_usd', 0.0),
            data_json=json.dumps(self._build_detail(snapshot_type)),
        )
        self.db.add(snap)
        self.db.commit()
        self.db.refresh(snap)
        return snap

    def _build_detail(self, snapshot_type: str) -> dict[str, Any]:
        if snapshot_type == 'QUALITY_TREND':
            return {
                'weeks': ['W1', 'W2', 'W3', 'W4'],
                'scores': [88.0, 89.5, 91.0, 91.4],
                'trend': 'IMPROVING',
            }
        if snapshot_type == 'RELEASE_TREND':
            return {
                'releases': ['v1.0', 'v1.1', 'v1.2', 'v2.0'],
                'pass_rates': [91.0, 92.5, 94.1, 94.1],
                'trend': 'STABLE',
            }
        if snapshot_type == 'DEVELOPER_QUALITY':
            return {
                'developers': [
                    {'name': 'Dev A', 'defects_introduced': 3, 'quality_score': 92.0},
                    {'name': 'Dev B', 'defects_introduced': 7, 'quality_score': 82.0},
                    {'name': 'Dev C', 'defects_introduced': 1, 'quality_score': 97.0},
                ]
            }
        if snapshot_type == 'FAILURE_HEATMAP':
            return {
                'modules': ['Login', 'Dashboard', 'Reports', 'API', 'Settings'],
                'failure_counts': [12, 5, 3, 8, 2],
            }
        if snapshot_type == 'FLAKY_TESTS':
            return {
                'tests': [
                    {'test_name': 'Login E2E', 'flakiness_pct': 15.0},
                    {'test_name': 'Checkout Flow', 'flakiness_pct': 10.0},
                    {'test_name': 'Report Export', 'flakiness_pct': 8.0},
                ]
            }
        if snapshot_type == 'BROWSER_STATS':
            return {
                'browsers': {
                    'CHROMIUM': {'runs': 450, 'pass_rate': 96.5},
                    'FIREFOX': {'runs': 320, 'pass_rate': 94.1},
                    'WEBKIT': {'runs': 180, 'pass_rate': 92.8},
                    'EDGE': {'runs': 90, 'pass_rate': 95.0},
                }
            }
        if snapshot_type == 'COST':
            return {
                'breakdown': {
                    'CHROMIUM': 68.50,
                    'FIREFOX': 42.30,
                    'WEBKIT': 21.70,
                    'other': 10.00,
                },
                'currency': 'USD',
            }
        return {}

    def get_quality_trends(self, project_id: int | None = None) -> list[dict[str, Any]]:
        return self._get_snapshots('QUALITY_TREND', project_id)

    def get_release_trends(self, project_id: int | None = None) -> list[dict[str, Any]]:
        return self._get_snapshots('RELEASE_TREND', project_id)

    def get_developer_quality(self, project_id: int | None = None) -> list[dict[str, Any]]:
        return self._get_snapshots('DEVELOPER_QUALITY', project_id)

    def get_failure_heatmap(self, project_id: int | None = None) -> list[dict[str, Any]]:
        return self._get_snapshots('FAILURE_HEATMAP', project_id)

    def get_flaky_tests(self, project_id: int | None = None) -> list[dict[str, Any]]:
        return self._get_snapshots('FLAKY_TESTS', project_id)

    def get_browser_stats(self) -> list[dict[str, Any]]:
        return self._get_snapshots('BROWSER_STATS', None)

    def get_cost_analytics(self, project_id: int | None = None) -> list[dict[str, Any]]:
        return self._get_snapshots('COST', project_id)

    def _get_snapshots(self, snapshot_type: str, project_id: int | None) -> list[dict[str, Any]]:
        q = self.db.query(EnterpriseAnalyticsSnapshot).filter_by(snapshot_type=snapshot_type)
        if project_id:
            q = q.filter_by(project_id=project_id)
        rows = q.order_by(EnterpriseAnalyticsSnapshot.created_at.desc()).limit(20).all()
        if not rows:
            # Auto-generate on first request
            snap = self.generate_snapshot(snapshot_type, project_id)
            rows = [snap]
        return [
            {
                'id': r.id,
                'snapshot_type': r.snapshot_type,
                'quality_score': r.quality_score,
                'pass_rate': r.pass_rate,
                'coverage_pct': r.coverage_pct,
                'flaky_count': r.flaky_count,
                'cost_usd': r.cost_usd,
                'data': json.loads(r.data_json),
                'created_at': r.created_at.isoformat(),
            }
            for r in rows
        ]

    def get_all_kpis(self) -> dict[str, Any]:
        """Aggregate KPIs across all snapshot types."""
        kpis: dict[str, Any] = {}
        for stype in SNAPSHOT_TYPES:
            snaps = self._get_snapshots(stype, None)
            if snaps:
                kpis[stype] = snaps[0]
        return kpis
