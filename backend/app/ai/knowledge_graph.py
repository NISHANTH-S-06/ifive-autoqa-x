import json
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.phase9_models import KnowledgeGraphNode, KnowledgeGraphEdge

logger = logging.getLogger('autoqa.ai.knowledge_graph')

NODE_TYPES = [
    'COMPANY', 'PROJECT', 'PRODUCT', 'MODULE', 'PAGE',
    'COMPONENT', 'LOCATOR', 'API', 'DATABASE', 'TEST_CASE',
    'EXECUTION', 'EVIDENCE', 'BUG', 'RELEASE'
]

class KnowledgeGraphService:
    """
    Enterprise Knowledge Graph Service:
    Manages topological nodes and directed relationship edges spanning 
    Companies down to Locators, APIs, Executions, Bugs, and Releases.
    """

    def __init__(self, db: Session):
        self.db = db

    def add_node(self, node_type: str, entity_id: str, label: str, properties: Optional[Dict[str, Any]] = None) -> KnowledgeGraphNode:
        node_type_upper = node_type.upper()
        stmt = select(KnowledgeGraphNode).where(
            KnowledgeGraphNode.node_type == node_type_upper,
            KnowledgeGraphNode.entity_id == str(entity_id)
        )
        existing = self.db.scalar(stmt)
        if existing:
            existing.label = label
            existing.properties_json = json.dumps(properties or {})
            self.db.commit()
            self.db.refresh(existing)
            return existing

        node = KnowledgeGraphNode(
            node_type=node_type_upper,
            entity_id=str(entity_id),
            label=label,
            properties_json=json.dumps(properties or {})
        )
        self.db.add(node)
        self.db.commit()
        self.db.refresh(node)
        return node

    def add_edge(self, source_node_id: int, target_node_id: int, relationship_type: str, properties: Optional[Dict[str, Any]] = None) -> KnowledgeGraphEdge:
        edge = KnowledgeGraphEdge(
            source_node_id=source_node_id,
            target_node_id=target_node_id,
            relationship_type=relationship_type.upper(),
            properties_json=json.dumps(properties or {})
        )
        self.db.add(edge)
        self.db.commit()
        self.db.refresh(edge)
        return edge

    def get_topology_graph(self) -> Dict[str, Any]:
        nodes = list(self.db.scalars(select(KnowledgeGraphNode)).all())
        edges = list(self.db.scalars(select(KnowledgeGraphEdge)).all())

        return {
            'total_nodes': len(nodes),
            'total_edges': len(edges),
            'nodes': [
                {
                    'id': n.id,
                    'type': n.node_type,
                    'entity_id': n.entity_id,
                    'label': n.label,
                    'properties': json.loads(n.properties_json or '{}')
                }
                for n in nodes
            ],
            'edges': [
                {
                    'id': e.id,
                    'source': e.source_node_id,
                    'target': e.target_node_id,
                    'relationship': e.relationship_type
                }
                for e in edges
            ]
        }
