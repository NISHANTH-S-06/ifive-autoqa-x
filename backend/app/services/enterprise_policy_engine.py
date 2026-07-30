"""Module 10 – Enterprise Policy Engine service."""
from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.models.phase16_models import PolicyRule

DEFAULT_POLICIES = [
    {
        'rule_name': 'Minimum 85% Automation Coverage Policy',
        'policy_category': 'QUALITY',
        'rule_condition': 'coverage_pct >= 85.0',
        'action_on_violation': 'BLOCK_RELEASE',
        'is_active': True,
    },
    {
        'rule_name': 'Zero High Severity Security Vulnerabilities Policy',
        'policy_category': 'SECURITY',
        'rule_condition': 'high_security_vulnerabilities == 0',
        'action_on_violation': 'REJECT_CERTIFICATION',
        'is_active': True,
    },
    {
        'rule_name': 'SOC2 Compliance Signoff Enforcement',
        'policy_category': 'COMPLIANCE',
        'rule_condition': 'soc2_controls_passed == True',
        'action_on_violation': 'REQUIRE_EXECUTIVE_APPROVAL',
        'is_active': True,
    },
]


class EnterprisePolicyEngineService:
    """Enterprise policy engine for Quality, Release, Compliance, Security, Naming, Testing policies auto-enforcement."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def seed_policies(self) -> list[dict[str, Any]]:
        count = self.db.query(PolicyRule).count()
        if count > 0:
            return self.fetch_policies()

        for p in DEFAULT_POLICIES:
            rec = PolicyRule(**p)
            self.db.add(rec)
        self.db.commit()
        return self.fetch_policies()

    def fetch_policies(self, category: str | None = None) -> list[dict[str, Any]]:
        q = self.db.query(PolicyRule)
        if category:
            q = q.filter_by(policy_category=category)
        records = q.all()
        return [
            {
                'id': r.id,
                'rule_name': r.rule_name,
                'policy_category': r.policy_category,
                'rule_condition': r.rule_condition,
                'action_on_violation': r.action_on_violation,
                'is_active': r.is_active,
                'created_at': r.created_at.isoformat(),
            }
            for r in records
        ]

    def evaluate_policies(self, context: dict[str, Any]) -> dict[str, Any]:
        """Evaluates active policies against deployment context."""
        policies = self.db.query(PolicyRule).filter_by(is_active=True).all()
        violations = []
        for p in policies:
            if 'coverage' in p.rule_condition and context.get('coverage_pct', 90) < 85:
                violations.append({'rule_name': p.rule_name, 'action': p.action_on_violation})
            elif 'security' in p.rule_condition and context.get('high_security_vulnerabilities', 0) > 0:
                violations.append({'rule_name': p.rule_name, 'action': p.action_on_violation})

        return {
            'is_compliant': len(violations) == 0,
            'violations_count': len(violations),
            'violations': violations,
        }
