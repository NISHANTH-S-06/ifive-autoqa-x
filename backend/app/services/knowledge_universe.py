"""Module 8 – Enterprise Knowledge Universe service."""
from __future__ import annotations

import json
from typing import Any

from sqlalchemy.orm import Session

from app.models.phase14_models import KnowledgeUniverseEdge, KnowledgeUniverseNode

ENTITY_TIERS = [
    'COMPANY', 'PRODUCT', 'MODULE', 'PAGE', 'COMPONENT',
    'API', 'DATABASE', 'INFRASTRUCTURE', 'CLOUD', 'USER',
    'ROLE', 'RULE', 'TEST', 'EXECUTION', 'EVIDENCE',
    'BASELINE', 'INCIDENT', 'RELEASE',
]

SEED_NODES = [
    {'node_key': 'comp-1', 'label': 'Acme Enterprise Global', 'node_type': 'COMPANY'},
    {'node_key': 'prod-1', 'label': 'AutoQA Platform Core', 'node_type': 'PRODUCT'},
    {'node_key': 'mod-1', 'label': 'Execution Orchestrator', 'node_type': 'MODULE'},
    {'node_key': 'page-1', 'label': 'Live Execution Center', 'node_type': 'PAGE'},
    {'node_key': 'api-1', 'label': 'POST /api/execution/queue/submit', 'node_type': 'API'},
    {'node_key': 'db-1', 'label': 'SQLite / PostgreSQL Master DB', 'node_type': 'DATABASE'},
    {'node_key': 'infra-1', 'label': 'Browser Farm Worker Swarm', 'node_type': 'INFRASTRUCTURE'},
    {'node_key': 'rule-1', 'label': 'Max Worker Queue Depth <= 50', 'node_type': 'RULE'},
    {'node_key': 'test-1', 'label': 'Parallel Distributed Run Test', 'node_type': 'TEST'},
    {'node_key': 'release-1', 'label': 'AutoQA v2.0.0 Release', 'node_type': 'RELEASE'},
]

SEED_EDGES = [
    ('comp-1', 'prod-1', 'CONTAINS'),
    ('prod-1', 'mod-1', 'CONTAINS'),
    ('mod-1', 'page-1', 'CONTAINS'),
    ('page-1', 'api-1', 'CALLS'),
    ('api-1', 'db-1', 'DEPENDS_ON'),
    ('mod-1', 'infra-1', 'EXECUTES'),
    ('rule-1', 'test-1', 'VALIDATES'),
    ('test-1', 'release-1', 'BLOCKS'),
]


class KnowledgeUniverseService:
    """18-tier interactive knowledge universe graph database builder & visualizer."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def seed_universe(self) -> dict[str, Any]:
        existing = self.db.query(KnowledgeUniverseNode).count()
        if existing > 0:
            return self.get_graph()

        key_to_id: dict[str, int] = {}
        for sn in SEED_NODES:
            node = KnowledgeUniverseNode(
                node_key=sn['node_key'],
                label=sn['label'],
                node_type=sn['node_type'],
            )
            self.db.add(node)
            self.db.flush()
            key_to_id[sn['node_key']] = node.id

        for src, tgt, rel in SEED_EDGES:
            if src in key_to_id and tgt in key_to_id:
                edge = KnowledgeUniverseEdge(
                    source_node_id=key_to_id[src],
                    target_node_id=key_to_id[tgt],
                    relationship_type=rel,
                )
                self.db.add(edge)

        self.db.commit()
        return self.get_graph()

    def get_graph(self, node_type: str | None = None) -> dict[str, Any]:
        qn = self.db.query(KnowledgeUniverseNode)
        if node_type:
            qn = qn.filter_by(node_type=node_type)
        nodes = qn.all()

        node_ids = {n.id for n in nodes}
        edges = self.db.query(KnowledgeUniverseEdge).all()
        # Filter edges where both source and target exist in node list if filtered
        if node_type:
            edges = [e for e in edges if e.source_node_id in node_ids and e.target_node_id in node_ids]

        return {
            'entity_tiers': ENTITY_TIERS,
            'nodes': [
                {
                    'id': n.id,
                    'node_key': n.node_key,
                    'label': n.label,
                    'node_type': n.node_type,
                    'attributes': json.loads(n.attributes_json),
                }
                for n in nodes
            ],
            'edges': [
                {
                    'id': e.id,
                    'source': e.source_node_id,
                    'target': e.target_node_id,
                    'relationship_type': e.relationship_type,
                    'weight': e.weight,
                }
                for e in edges
            ],
        }

    def add_node(self, label: str, node_type: str, node_key: str | None = None) -> KnowledgeUniverseNode:
        key = node_key or f'{node_type.lower()}-{self.db.query(KnowledgeUniverseNode).count() + 1}'
        node = KnowledgeUniverseNode(
            node_key=key,
            label=label,
            node_type=node_type,
        )
        self.db.add(node)
        self.db.commit()
        self.db.refresh(node)
        return node
