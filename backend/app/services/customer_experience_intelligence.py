"""Module 8 – Customer Experience Intelligence service."""
from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.models.phase16_models import CustomerFeedbackItem

DEFAULT_ITEMS = [
    {
        'source_type': 'SUPPORT_TICKET',
        'headline': 'TICKET-9921: Payment timeout on checkout button double click',
        'sentiment_score': 0.22,
        'nps_score': 4,
        'correlated_bug_key': 'BUG-1092',
        'assigned_developer': 'alex.dev@autoqa.com',
        'release_version': 'v4.9.2',
        'root_cause': 'Debounce missing on pay button click handler causing duplicate token submission.',
    },
    {
        'source_type': 'APP_REVIEW',
        'headline': 'AppStore Review: Fast checkout experience!',
        'sentiment_score': 0.95,
        'nps_score': 10,
        'correlated_bug_key': None,
        'assigned_developer': None,
        'release_version': 'v5.0.0',
        'root_cause': None,
    },
]


class CustomerExperienceIntelligenceService:
    """Customer experience intelligence correlator: Feedback → Bug → Dev → Release → Root Cause."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def seed_feedback(self) -> list[dict[str, Any]]:
        count = self.db.query(CustomerFeedbackItem).count()
        if count > 0:
            return self.fetch_feedback()

        for item in DEFAULT_ITEMS:
            rec = CustomerFeedbackItem(**item)
            self.db.add(rec)
        self.db.commit()
        return self.fetch_feedback()

    def fetch_feedback(self) -> list[dict[str, Any]]:
        records = self.db.query(CustomerFeedbackItem).all()
        return [
            {
                'id': r.id,
                'source_type': r.source_type,
                'headline': r.headline,
                'sentiment_score': r.sentiment_score,
                'nps_score': r.nps_score,
                'correlated_bug_key': r.correlated_bug_key,
                'assigned_developer': r.assigned_developer,
                'release_version': r.release_version,
                'root_cause': r.root_cause,
                'created_at': r.created_at.isoformat(),
            }
            for r in records
        ]
