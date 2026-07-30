"""Module 1 – Software Knowledge Lake V2 service."""
from __future__ import annotations

import json
from typing import Any

from sqlalchemy.orm import Session

from app.models.phase16_models import KnowledgeLakeV2Document

DEFAULT_DOCS = [
    {
        'source_type': 'REQUIREMENT',
        'title': 'REQ-2026-881: Multi-Currency Checkout Ledger',
        'content_text': 'System must support instant FX conversion and audit logging for multi-currency order payments.',
        'tags': ['REQUIREMENT', 'FINANCE', 'CHECKOUT'],
    },
    {
        'source_type': 'OPENAPI',
        'title': 'OpenAPI Specification v3.0 - Billing Microservice',
        'content_text': 'POST /api/v2/payments/charge - Parameters: amount, currency, token, customer_id.',
        'tags': ['OPENAPI', 'SWAGGER', 'PAYMENTS'],
    },
    {
        'source_type': 'CICD_LOG',
        'title': 'GitHub Actions Build Log #4891',
        'content_text': 'Step: Run Playwright Regression Tests. 142 passed, 0 failed. Execution time 45.2s.',
        'tags': ['CICD', 'BUILD', 'PLAYWRIGHT'],
    },
]


class KnowledgeLakeV2Service:
    """Multi-source knowledge lake with vector embeddings, hybrid search & relationship graph generation."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def seed_lake(self) -> list[dict[str, Any]]:
        existing = self.db.query(KnowledgeLakeV2Document).count()
        if existing > 0:
            return self.search_lake()

        for d in DEFAULT_DOCS:
            embedding = [0.12, 0.45, 0.88, 0.91]  # Simulated 4D embedding
            doc = KnowledgeLakeV2Document(
                source_type=d['source_type'],
                title=d['title'],
                content_text=d['content_text'],
                vector_embedding_json=json.dumps(embedding),
                hybrid_search_tags_json=json.dumps(d['tags']),
                metadata_json=json.dumps({'indexed_by': 'SQIP-V2-VectorEngine'}),
            )
            self.db.add(doc)
        self.db.commit()
        return self.search_lake()

    def search_lake(self, query: str = '', source_type: str | None = None) -> list[dict[str, Any]]:
        q = self.db.query(KnowledgeLakeV2Document)
        if source_type:
            q = q.filter_by(source_type=source_type)
        if query:
            q = q.filter(KnowledgeLakeV2Document.title.contains(query) | KnowledgeLakeV2Document.content_text.contains(query))
        docs = q.order_by(KnowledgeLakeV2Document.created_at.desc()).all()
        return [
            {
                'id': doc.id,
                'source_type': doc.source_type,
                'title': doc.title,
                'content_text': doc.content_text,
                'hybrid_search_tags': json.loads(doc.hybrid_search_tags_json),
                'vector_embedding': json.loads(doc.vector_embedding_json),
                'metadata': json.loads(doc.metadata_json),
                'created_at': doc.created_at.isoformat(),
            }
            for doc in docs
        ]
