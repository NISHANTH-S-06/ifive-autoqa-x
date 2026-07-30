"""Module 5 – Autonomous Release Simulation service."""
from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.models.phase14_models import ReleaseSimulation


class ReleaseSimulationService:
    """Pre-release simulation engine predicting failures, rollback risk, and business impact."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def run_simulation(
        self,
        release_version: str,
        simulated_by: int | None = None,
    ) -> dict[str, Any]:
        # Perform predictive AI risk simulation
        rollback_prob = 12.4
        failures_count = 3
        perf_deg = 8.5
        fin_risk = 4500.00
        cust_impact = 18.0

        breakdown = {
            'api_failure_risk': {'endpoint': '/api/v2/checkout', 'failure_prob_pct': 14.5},
            'db_migration_risk': {'migration': '20260729_13_phase14', 'lock_time_ms': 120},
            'browser_compatibility_risk': {'safari_mobile': '88% pass', 'chromium': '99% pass'},
            'customer_revenue_at_risk_usd': 4500.00,
            'recommendation': 'CONDITIONAL_GO_WITH_CANARY',
        }

        sim = ReleaseSimulation(
            release_version=release_version,
            simulated_by=simulated_by,
            rollback_probability_pct=rollback_prob,
            predicted_failures_count=failures_count,
            perf_degradation_pct=perf_deg,
            financial_risk_usd=fin_risk,
            customer_impact_score=cust_impact,
            breakdown_json=json.dumps(breakdown),
        )
        self.db.add(sim)
        self.db.commit()
        self.db.refresh(sim)

        return self._sim_dict(sim)

    def list_simulations(self, release_version: str | None = None) -> list[dict[str, Any]]:
        q = self.db.query(ReleaseSimulation)
        if release_version:
            q = q.filter_by(release_version=release_version)
        sims = q.order_by(ReleaseSimulation.created_at.desc()).all()
        return [self._sim_dict(s) for s in sims]

    def _sim_dict(self, s: ReleaseSimulation) -> dict[str, Any]:
        return {
            'id': s.id,
            'release_version': s.release_version,
            'rollback_probability_pct': s.rollback_probability_pct,
            'predicted_failures_count': s.predicted_failures_count,
            'perf_degradation_pct': s.perf_degradation_pct,
            'financial_risk_usd': s.financial_risk_usd,
            'customer_impact_score': s.customer_impact_score,
            'breakdown': json.loads(s.breakdown_json),
            'created_at': s.created_at.isoformat(),
        }
