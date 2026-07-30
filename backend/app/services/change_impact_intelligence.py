"""Module 2 – AI Change Impact Intelligence service."""
from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.models.phase15_models import ChangeImpactRecord


class ChangeImpactService:
    """Detects changed files in commit, finds impacted APIs/rules, and generates regression suites."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def analyze_commit(
        self,
        commit_hash: str,
        author: str,
        changed_files: list[str],
    ) -> dict[str, Any]:
        impacted_modules = list({f.split('/')[2] if len(f.split('/')) > 2 else 'root' for f in changed_files})
        impacted_apis = [f'/api/{m}' for m in impacted_modules]
        affected_tests = [f'test_{m}_regression' for m in impacted_modules]

        risk_score = round(min(len(changed_files) * 18.5, 95.0), 1)
        est_cost = round(len(affected_tests) * 0.45, 2)

        rec = ChangeImpactRecord(
            commit_hash=commit_hash,
            author=author,
            changed_files_json=json.dumps(changed_files),
            impacted_modules_json=json.dumps(impacted_modules),
            impacted_apis_json=json.dumps(impacted_apis),
            affected_tests_json=json.dumps(affected_tests),
            risk_score=risk_score,
            estimated_execution_cost_usd=est_cost,
        )
        self.db.add(rec)
        self.db.commit()
        self.db.refresh(rec)

        return self._record_dict(rec)

    def list_records(self, limit: int = 20) -> list[dict[str, Any]]:
        records = self.db.query(ChangeImpactRecord).order_by(ChangeImpactRecord.created_at.desc()).limit(limit).all()
        return [self._record_dict(r) for r in records]

    def _record_dict(self, r: ChangeImpactRecord) -> dict[str, Any]:
        return {
            'id': r.id,
            'commit_hash': r.commit_hash,
            'author': r.author,
            'changed_files': json.loads(r.changed_files_json),
            'impacted_modules': json.loads(r.impacted_modules_json),
            'impacted_apis': json.loads(r.impacted_apis_json),
            'affected_tests': json.loads(r.affected_tests_json),
            'risk_score': r.risk_score,
            'estimated_execution_cost_usd': r.estimated_execution_cost_usd,
            'created_at': r.created_at.isoformat(),
        }
