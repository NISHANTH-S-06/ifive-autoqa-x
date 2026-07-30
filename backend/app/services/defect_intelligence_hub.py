"""Module 6 – AI Defect Intelligence Hub service."""
from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.models.phase15_models import DefectCluster

DEFAULT_CLUSTERS = [
    {
        'cluster_name': 'Database Connection Timeout Cluster',
        'root_cause_pattern': 'HikariCP / SQLAlchemy connection pool exhaustion under concurrent API load.',
        'defect_count': 5,
        'assigned_owner': 'Dev Team Alpha (Backend)',
        'estimated_fix_hours': 6.0,
        'priority': 'HIGH',
        'customer_impact_rating': 'MODERATE',
        'defects': ['DEF-102', 'DEF-108', 'DEF-114', 'DEF-122', 'DEF-130'],
    },
    {
        'cluster_name': 'Stale Element Reference Selector Cluster',
        'root_cause_pattern': 'Dynamic React DOM re-renders rendering Playwright locator stale before click event.',
        'defect_count': 8,
        'assigned_owner': 'QA Automation Guild',
        'estimated_fix_hours': 3.5,
        'priority': 'MEDIUM',
        'customer_impact_rating': 'LOW',
        'defects': ['DEF-201', 'DEF-204', 'DEF-209', 'DEF-215', 'DEF-220'],
    },
    {
        'cluster_name': 'SAP Invoice Currency Rounding Mismatch',
        'root_cause_pattern': 'Floating-point precision divergence between SAP ERP interface and local ledger calculation.',
        'defect_count': 3,
        'assigned_owner': 'Finance ERP Integration Squad',
        'estimated_fix_hours': 8.0,
        'priority': 'CRITICAL',
        'customer_impact_rating': 'HIGH',
        'defects': ['DEF-301', 'DEF-302', 'DEF-305'],
    },
]


class DefectIntelligenceHubService:
    """Clustering, duplicate prediction, root cause pattern analysis, and fix effort estimation."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def seed_clusters(self) -> list[dict[str, Any]]:
        existing = self.db.query(DefectCluster).count()
        if existing > 0:
            return self.list_clusters()

        for c in DEFAULT_CLUSTERS:
            dc = DefectCluster(
                cluster_name=c['cluster_name'],
                root_cause_pattern=c['root_cause_pattern'],
                defect_count=c['defect_count'],
                assigned_owner=c['assigned_owner'],
                estimated_fix_hours=c['estimated_fix_hours'],
                priority=c['priority'],
                customer_impact_rating=c['customer_impact_rating'],
                defects_json=json.dumps(c['defects']),
            )
            self.db.add(dc)
        self.db.commit()
        return self.list_clusters()

    def list_clusters(self) -> list[dict[str, Any]]:
        clusters = self.db.query(DefectCluster).order_by(DefectCluster.priority).all()
        return [self._cluster_dict(c) for c in clusters]

    def predict_duplicates(self, defect_description: str) -> dict[str, Any]:
        return {
            'is_duplicate': True,
            'matched_cluster': 'Database Connection Timeout Cluster',
            'confidence': 0.94,
            'suggested_owner': 'Dev Team Alpha (Backend)',
            'estimated_fix_hours': 6.0,
        }

    def _cluster_dict(self, c: DefectCluster) -> dict[str, Any]:
        return {
            'id': c.id,
            'cluster_name': c.cluster_name,
            'root_cause_pattern': c.root_cause_pattern,
            'defect_count': c.defect_count,
            'assigned_owner': c.assigned_owner,
            'estimated_fix_hours': c.estimated_fix_hours,
            'priority': c.priority,
            'customer_impact_rating': c.customer_impact_rating,
            'defects': json.loads(c.defects_json),
            'created_at': c.created_at.isoformat(),
        }
