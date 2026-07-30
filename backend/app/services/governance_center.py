"""Module 11 – Enterprise Governance Center service."""
from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.models.phase14_models import GovernancePolicy

DEFAULT_POLICIES = [
    {
        'policy_name': 'Zero Critical Defect Release Gate',
        'policy_type': 'RELEASE_GATE',
        'rules': {'block_on_critical_defects': True, 'min_pass_rate_pct': 90.0, 'require_security_scan': True},
    },
    {
        'policy_name': 'GDPR & PII Data Retention Policy',
        'policy_type': 'RETENTION',
        'rules': {'audit_log_retention_days': 365, 'evidence_retention_days': 90, 'auto_mask_pii': True},
    },
    {
        'policy_name': 'Enterprise Secret Vault Classification',
        'policy_type': 'DATA_CLASSIFICATION',
        'rules': {'require_aes256': True, 'enforce_90day_rotation': True, 'audit_key_access': True},
    },
    {
        'policy_name': 'ISO 27001 Security Gate',
        'policy_type': 'SECURITY_POLICY',
        'rules': {'mfa_required': True, 'sso_enforced': True, 'session_timeout_minutes': 30},
    },
]


class GovernanceCenterService:
    """Enterprise Governance Center – policy enforcement, retention, data classification, quality gates."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def seed_policies(self) -> list[dict[str, Any]]:
        existing = self.db.query(GovernancePolicy).count()
        if existing > 0:
            return self.list_policies()
        for p in DEFAULT_POLICIES:
            pol = GovernancePolicy(
                policy_name=p['policy_name'],
                policy_type=p['policy_type'],
                rules_json=json.dumps(p['rules']),
                is_enforced=True,
            )
            self.db.add(pol)
        self.db.commit()
        return self.list_policies()

    def list_policies(self, policy_type: str | None = None) -> list[dict[str, Any]]:
        q = self.db.query(GovernancePolicy)
        if policy_type:
            q = q.filter_by(policy_type=policy_type)
        policies = q.order_by(GovernancePolicy.policy_name).all()
        return [self._pol_dict(p) for p in policies]

    def create_policy(
        self,
        policy_name: str,
        policy_type: str,
        rules: dict[str, Any] | None = None,
        is_enforced: bool = True,
    ) -> dict[str, Any]:
        pol = GovernancePolicy(
            policy_name=policy_name,
            policy_type=policy_type,
            rules_json=json.dumps(rules or {}),
            is_enforced=is_enforced,
        )
        self.db.add(pol)
        self.db.commit()
        self.db.refresh(pol)
        return self._pol_dict(pol)

    def toggle_policy(self, policy_id: int) -> dict[str, Any]:
        pol = self.db.query(GovernancePolicy).filter_by(id=policy_id).first()
        if not pol:
            return {'error': 'Policy not found'}
        pol.is_enforced = not pol.is_enforced
        self.db.commit()
        return self._pol_dict(pol)

    def _pol_dict(self, p: GovernancePolicy) -> dict[str, Any]:
        return {
            'id': p.id,
            'policy_name': p.policy_name,
            'policy_type': p.policy_type,
            'rules': json.loads(p.rules_json),
            'is_enforced': p.is_enforced,
            'created_at': p.created_at.isoformat(),
        }
