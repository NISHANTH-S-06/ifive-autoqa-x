"""Module 6 – Release Governance service with 6-stage approval workflow."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.models.phase13_models import ReleaseGovernanceApproval, ReleaseGovernanceStage

GOVERNANCE_STAGES = [
    {'order': 1, 'name': 'QA_LEAD', 'role': 'TESTER'},
    {'order': 2, 'name': 'QA_MANAGER', 'role': 'PROJECT_MANAGER'},
    {'order': 3, 'name': 'ENGINEERING_MANAGER', 'role': 'APPROVER'},
    {'order': 4, 'name': 'PRODUCT_OWNER', 'role': 'APPROVER'},
    {'order': 5, 'name': 'RELEASE_MANAGER', 'role': 'ADMIN'},
    {'order': 6, 'name': 'CTO', 'role': 'ADMIN'},
]


class ReleaseGovernanceService:
    """Manages multi-stage release approval workflow."""

    def __init__(self, db: Session) -> None:
        self.db = db

    # ── Workflow creation ─────────────────────────────────────────────────────

    def create_workflow(self, project_id: int | None, release_version: str) -> list[dict[str, Any]]:
        """Create all 6 governance stages for a release."""
        stages = []
        for s in GOVERNANCE_STAGES:
            stage = ReleaseGovernanceStage(
                project_id=project_id,
                release_version=release_version,
                stage_order=s['order'],
                stage_name=s['name'],
                required_role=s['role'],
                stage_status='PENDING',
                is_blocking=True,
            )
            self.db.add(stage)
            stages.append(stage)
        self.db.commit()
        for stage in stages:
            self.db.refresh(stage)
        return [self._stage_dict(s) for s in stages]

    def list_stages(self, project_id: int | None = None, release_version: str | None = None) -> list[dict[str, Any]]:
        q = self.db.query(ReleaseGovernanceStage)
        if project_id:
            q = q.filter_by(project_id=project_id)
        if release_version:
            q = q.filter_by(release_version=release_version)
        stages = q.order_by(ReleaseGovernanceStage.stage_order).all()
        return [self._stage_dict(s) for s in stages]

    # ── Approval submission ───────────────────────────────────────────────────

    def submit_approval(
        self,
        stage_id: int,
        approver_name: str,
        approver_role: str,
        decision: str,
        comments: str = '',
        approver_id: int | None = None,
        ip_address: str = '127.0.0.1',
    ) -> dict[str, Any]:
        stage = self.db.query(ReleaseGovernanceStage).filter_by(id=stage_id).first()
        if not stage:
            return {'error': 'Stage not found'}
        if stage.stage_status not in ('PENDING',):
            return {'error': f'Stage already {stage.stage_status}'}

        # Digital signature = SHA256(stage_id + approver_name + decision + timestamp)
        sig_data = f'{stage_id}:{approver_name}:{decision}:{datetime.utcnow().isoformat()}'
        digital_signature = hashlib.sha256(sig_data.encode()).hexdigest()

        approval = ReleaseGovernanceApproval(
            stage_id=stage_id,
            approver_id=approver_id,
            approver_name=approver_name,
            approver_role=approver_role,
            decision=decision,
            digital_signature=digital_signature,
            ip_address=ip_address,
            comments=comments,
        )
        self.db.add(approval)

        # Update stage status
        stage.stage_status = 'APPROVED' if decision == 'APPROVED' else 'REJECTED'
        stage.notes = comments
        self.db.commit()
        return {
            'stage_id': stage_id,
            'decision': decision,
            'digital_signature': digital_signature,
            'stage_status': stage.stage_status,
        }

    # ── Audit trail ───────────────────────────────────────────────────────────

    def get_audit_trail(self, release_version: str | None = None) -> list[dict[str, Any]]:
        q = self.db.query(ReleaseGovernanceApproval)
        if release_version:
            # Join to filter by release version
            stage_ids = [
                s.id for s in
                self.db.query(ReleaseGovernanceStage)
                .filter_by(release_version=release_version)
                .all()
            ]
            if stage_ids:
                q = q.filter(ReleaseGovernanceApproval.stage_id.in_(stage_ids))
        approvals = q.order_by(ReleaseGovernanceApproval.signed_at.desc()).all()
        return [
            {
                'id': a.id,
                'stage_id': a.stage_id,
                'approver_name': a.approver_name,
                'approver_role': a.approver_role,
                'decision': a.decision,
                'digital_signature': a.digital_signature[:16] + '...',
                'ip_address': a.ip_address,
                'comments': a.comments,
                'signed_at': a.signed_at.isoformat(),
            }
            for a in approvals
        ]

    # ── Rollback ──────────────────────────────────────────────────────────────

    def create_rollback_approval(
        self,
        project_id: int | None,
        release_version: str,
        requested_by: str,
        reason: str,
    ) -> dict[str, Any]:
        stage = ReleaseGovernanceStage(
            project_id=project_id,
            release_version=f'{release_version}-ROLLBACK',
            stage_order=1,
            stage_name='ROLLBACK_APPROVAL',
            required_role='ADMIN',
            stage_status='PENDING',
            is_blocking=True,
            notes=f'Rollback requested by {requested_by}: {reason}',
        )
        self.db.add(stage)
        self.db.commit()
        self.db.refresh(stage)
        return {
            'rollback_stage_id': stage.id,
            'release_version': f'{release_version}-ROLLBACK',
            'status': 'PENDING_APPROVAL',
        }

    def get_workflow_status(self, release_version: str) -> dict[str, Any]:
        stages = self.db.query(ReleaseGovernanceStage).filter_by(release_version=release_version).all()
        approved = sum(1 for s in stages if s.stage_status == 'APPROVED')
        rejected = sum(1 for s in stages if s.stage_status == 'REJECTED')
        pending = sum(1 for s in stages if s.stage_status == 'PENDING')
        overall = 'APPROVED' if approved == len(stages) else ('REJECTED' if rejected > 0 else 'IN_PROGRESS')
        return {
            'release_version': release_version,
            'total_stages': len(stages),
            'approved': approved,
            'rejected': rejected,
            'pending': pending,
            'overall_status': overall,
        }

    def _stage_dict(self, s: ReleaseGovernanceStage) -> dict[str, Any]:
        return {
            'id': s.id,
            'release_version': s.release_version,
            'stage_order': s.stage_order,
            'stage_name': s.stage_name,
            'required_role': s.required_role,
            'stage_status': s.stage_status,
            'is_blocking': s.is_blocking,
            'notes': s.notes,
        }
