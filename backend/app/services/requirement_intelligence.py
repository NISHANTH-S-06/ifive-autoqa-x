"""Module 2 – AI Requirement Intelligence service."""
from __future__ import annotations

import json
from typing import Any

from sqlalchemy.orm import Session

from app.models.phase16_models import RequirementRecord

DEFAULT_REQ = [
    {
        'requirement_code': 'REQ-CHECKOUT-001',
        'title': '3D Secure 2.0 Payment Authentication',
        'requirement_type': 'FUNCTIONAL',
        'description': 'The checkout system must challenge credit card payments exceeding $500 USD with 3D Secure biometric authentication.',
        'acceptance_criteria': [
            'Trigger 3DS modal for transactions > $500',
            'Bypass 3DS for whitelisted enterprise tenants',
            'Timeout transaction after 120s of inactivity',
        ],
        'is_ambiguous': False,
        'is_conflicting': False,
        'risk_score': 0.78,
        'analysis_notes': 'High financial impact. Requires integration with VISA/Mastercard sandbox APIs.',
    },
    {
        'requirement_code': 'REQ-PERF-009',
        'title': 'Sub-100ms Search Autocomplete',
        'requirement_type': 'NON_FUNCTIONAL',
        'description': 'Product search autocomplete dropdown must render within 100ms under 10k concurrent users.',
        'acceptance_criteria': [
            'P99 latency < 100ms',
            'Cache popular queries in Redis',
        ],
        'is_ambiguous': True,
        'is_conflicting': False,
        'risk_score': 0.65,
        'analysis_notes': 'Ambiguous definition of "popular queries". Recommend specifying cache TTL and invalidation rules.',
    },
]


class RequirementIntelligenceService:
    """Requirement intelligence parser, ambiguity/conflict detector, and risk matrix builder."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def seed_requirements(self) -> list[dict[str, Any]]:
        count = self.db.query(RequirementRecord).count()
        if count > 0:
            return self.fetch_requirements()

        for r in DEFAULT_REQ:
            record = RequirementRecord(
                requirement_code=r['requirement_code'],
                title=r['title'],
                requirement_type=r['requirement_type'],
                description=r['description'],
                acceptance_criteria_json=json.dumps(r['acceptance_criteria']),
                is_ambiguous=r['is_ambiguous'],
                is_conflicting=r['is_conflicting'],
                risk_score=r['risk_score'],
                analysis_notes=r['analysis_notes'],
            )
            self.db.add(record)
        self.db.commit()
        return self.fetch_requirements()

    def fetch_requirements(self, req_type: str | None = None) -> list[dict[str, Any]]:
        q = self.db.query(RequirementRecord)
        if req_type:
            q = q.filter_by(requirement_type=req_type)
        records = q.all()
        return [
            {
                'id': r.id,
                'requirement_code': r.requirement_code,
                'title': r.title,
                'requirement_type': r.requirement_type,
                'description': r.description,
                'acceptance_criteria': json.loads(r.acceptance_criteria_json),
                'is_ambiguous': r.is_ambiguous,
                'is_conflicting': r.is_conflicting,
                'risk_score': r.risk_score,
                'analysis_notes': r.analysis_notes,
                'created_at': r.created_at.isoformat(),
            }
            for r in records
        ]

    def analyze_requirement(self, req_code: str, title: str, description: str) -> dict[str, Any]:
        """AI analysis detecting ambiguity, conflicts, and generating acceptance criteria."""
        is_ambiguous = 'fast' in description.lower() or 'should be good' in description.lower()
        is_conflicting = 'both instant and delayed' in description.lower()
        risk_score = 0.85 if 'payment' in description.lower() or 'security' in description.lower() else 0.45

        acceptance_criteria = [
            f'Given valid inputs for {title}, system responds successfully.',
            f'When illegal payload is submitted to {title}, HTTP 400 is returned.',
            f'System logs all audit events for {req_code}.',
        ]

        rec = RequirementRecord(
            requirement_code=req_code,
            title=title,
            requirement_type='FUNCTIONAL',
            description=description,
            acceptance_criteria_json=json.dumps(acceptance_criteria),
            is_ambiguous=is_ambiguous,
            is_conflicting=is_conflicting,
            risk_score=risk_score,
            analysis_notes=f'Auto-analyzed on submit. Ambiguity detected: {is_ambiguous}. Conflict: {is_conflicting}.',
        )
        self.db.add(rec)
        self.db.commit()

        return {
            'id': rec.id,
            'requirement_code': req_code,
            'title': title,
            'acceptance_criteria': acceptance_criteria,
            'is_ambiguous': is_ambiguous,
            'is_conflicting': is_conflicting,
            'risk_score': risk_score,
        }
