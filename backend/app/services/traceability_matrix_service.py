"""Module 3 – Autonomous Requirement → Test Traceability Matrix service."""
from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.models.phase16_models import TraceabilityMapping

DEFAULT_TRACE = [
    {
        'requirement_code': 'REQ-CHECKOUT-001',
        'user_story_key': 'US-PAY-402',
        'design_doc_ref': 'ARCH-DOC#checkout-3ds2',
        'api_endpoint': 'POST /api/v2/payments/charge',
        'db_table': 'payment_transactions',
        'ui_page': '/checkout/pay',
        'test_scenario': 'test_3ds2_biometric_challenge_flow',
        'evidence_url': 's3://qa-evidence/runs/4891/screenshot_3ds.png',
        'defect_key': None,
        'release_version': 'v5.0.0',
        'is_coverage_complete': True,
    },
    {
        'requirement_code': 'REQ-PERF-009',
        'user_story_key': 'US-SEARCH-108',
        'design_doc_ref': 'ARCH-DOC#search-cache',
        'api_endpoint': 'GET /api/v1/search/autocomplete',
        'db_table': 'product_catalog',
        'ui_page': '/catalog',
        'test_scenario': 'test_autocomplete_latency_under_load',
        'evidence_url': 's3://qa-evidence/runs/4891/k6_report.html',
        'defect_key': 'BUG-1092',
        'release_version': 'v5.0.0',
        'is_coverage_complete': False,
    },
]


class TraceabilityMatrixService:
    """10-tier requirement to release traceability matrix generator and gap analyzer."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def seed_traceability(self) -> list[dict[str, Any]]:
        count = self.db.query(TraceabilityMapping).count()
        if count > 0:
            return self.fetch_matrix()

        for t in DEFAULT_TRACE:
            mapping = TraceabilityMapping(**t)
            self.db.add(mapping)
        self.db.commit()
        return self.fetch_matrix()

    def fetch_matrix(self, release_version: str | None = None) -> list[dict[str, Any]]:
        q = self.db.query(TraceabilityMapping)
        if release_version:
            q = q.filter_by(release_version=release_version)
        records = q.all()
        return [
            {
                'id': r.id,
                'requirement_code': r.requirement_code,
                'user_story_key': r.user_story_key,
                'design_doc_ref': r.design_doc_ref,
                'api_endpoint': r.api_endpoint,
                'db_table': r.db_table,
                'ui_page': r.ui_page,
                'test_scenario': r.test_scenario,
                'evidence_url': r.evidence_url,
                'defect_key': r.defect_key,
                'release_version': r.release_version,
                'is_coverage_complete': r.is_coverage_complete,
                'created_at': r.created_at.isoformat(),
            }
            for r in records
        ]

    def compute_gap_report(self) -> dict[str, Any]:
        """Calculates missing coverage gaps across requirements."""
        total = self.db.query(TraceabilityMapping).count()
        incomplete = self.db.query(TraceabilityMapping).filter_by(is_coverage_complete=False).all()
        return {
            'total_requirements_mapped': total,
            'incomplete_coverage_count': len(incomplete),
            'completeness_pct': round(((total - len(incomplete)) / max(1, total)) * 100, 2),
            'uncovered_requirements': [i.requirement_code for i in incomplete],
        }
