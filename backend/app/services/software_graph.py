"""Module 1 – Enterprise Software Intelligence Graph service."""
from __future__ import annotations

import json
from typing import Any

from sqlalchemy.orm import Session

from app.models.phase15_models import SoftwareGraphEdge, SoftwareGraphNode

SOFTWARE_GRAPH_TIERS = [
    'COMPANY', 'PRODUCT', 'MODULE', 'FEATURE', 'EPIC', 'STORY',
    'TASK', 'SOURCE_FILE', 'API', 'DATABASE', 'INFRASTRUCTURE',
    'DEPLOYMENT', 'TEST', 'EXECUTION', 'BUG', 'INCIDENT',
    'RELEASE', 'FEEDBACK',
]

SEED_NODES = [
    {'node_key': 'sg-comp-1', 'label': 'AutoQA Enterprise Global', 'node_type': 'COMPANY'},
    {'node_key': 'sg-prod-1', 'label': 'Core QA OS Platform', 'node_type': 'PRODUCT'},
    {'node_key': 'sg-mod-1', 'label': 'Quality Intelligence Module', 'node_type': 'MODULE'},
    {'node_key': 'sg-feat-1', 'label': 'AI Code Reviewer Engine', 'node_type': 'FEATURE'},
    {'node_key': 'sg-src-1', 'label': 'backend/app/services/ai_code_reviewer.py', 'node_type': 'SOURCE_FILE'},
    {'node_key': 'sg-api-1', 'label': 'POST /api/code-review/analyze', 'node_type': 'API'},
    {'node_key': 'sg-db-1', 'label': 'code_review_records Table', 'node_type': 'DATABASE'},
    {'node_key': 'sg-test-1', 'label': 'test_ai_code_reviewer_flow', 'node_type': 'TEST'},
    {'node_key': 'sg-rel-1', 'label': 'Release SQIP v5.0.0', 'node_type': 'RELEASE'},
]

SEED_EDGES = [
    ('sg-comp-1', 'sg-prod-1', 'CONTAINS'),
    ('sg-prod-1', 'sg-mod-1', 'CONTAINS'),
    ('sg-mod-1', 'sg-feat-1', 'CONTAINS'),
    ('sg-feat-1', 'sg-src-1', 'IMPLEMENTS'),
    ('sg-src-1', 'sg-api-1', 'CALLS'),
    ('sg-api-1', 'sg-db-1', 'DEPENDS_ON'),
    ('sg-test-1', 'sg-api-1', 'COVERS'),
    ('sg-test-1', 'sg-rel-1', 'BLOCKS'),
]


class SoftwareGraphService:
    """18-tier Software Intelligence Graph database builder, change propagator & visualizer."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def seed_graph(self) -> dict[str, Any]:
        existing = self.db.query(SoftwareGraphNode).count()
        if existing > 0:
            return self.get_graph()

        key_map: dict[str, int] = {}
        for sn in SEED_NODES:
            node = SoftwareGraphNode(
                node_key=sn['node_key'],
                label=sn['label'],
                node_type=sn['node_type'],
            )
            self.db.add(node)
            self.db.flush()
            key_map[sn['node_key']] = node.id

        for src, tgt, rel in SEED_EDGES:
            if src in key_map and tgt in key_map:
                edge = SoftwareGraphEdge(
                    source_node_id=key_map[src],
                    target_node_id=key_map[tgt],
                    relationship_type=rel,
                )
                self.db.add(edge)

        self.db.commit()
        return self.get_graph()

    def get_graph(self, node_type: str | None = None) -> dict[str, Any]:
        qn = self.db.query(SoftwareGraphNode)
        if node_type:
            qn = qn.filter_by(node_type=node_type)
        nodes = qn.all()
        node_ids = {n.id for n in nodes}

        edges = self.db.query(SoftwareGraphEdge).all()
        if node_type:
            edges = [e for e in edges if e.source_node_id in node_ids and e.target_node_id in node_ids]

        return {
            'tiers': SOFTWARE_GRAPH_TIERS,
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
                    'impact_weight': e.impact_weight,
                }
                for e in edges
            ],
        }

    def analyze_impact(self, node_key: str) -> dict[str, Any]:
        target = self.db.query(SoftwareGraphNode).filter_by(node_key=node_key).first()
        if not target:
            return {'error': 'Node not found'}

        # Find direct dependencies & dependent tests/releases
        downstream_edges = self.db.query(SoftwareGraphEdge).filter_by(source_node_id=target.id).all()
        target_ids = [e.target_node_id for e in downstream_edges]
        impacted_nodes = self.db.query(SoftwareGraphNode).filter(SoftwareGraphNode.id.in_(target_ids)).all() if target_ids else []

        return {
            'target_node': target.label,
            'node_type': target.node_type,
            'direct_impact_count': len(impacted_nodes),
            'impacted_nodes': [{'id': n.id, 'label': n.label, 'node_type': n.node_type} for n in impacted_nodes],
            'propagation_risk': 'HIGH' if len(impacted_nodes) > 2 else 'LOW',
        }
