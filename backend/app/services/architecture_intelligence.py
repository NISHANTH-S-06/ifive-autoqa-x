"""Module 4 – Architecture Intelligence service."""
from __future__ import annotations

import json
from typing import Any

from sqlalchemy.orm import Session

from app.models.phase16_models import ArchitectureEdge, ArchitectureNode

DEFAULT_NODES = [
    {'node_key': 'MS-CHECKOUT', 'label': 'Checkout Service', 'node_type': 'MICROSERVICE', 'is_bottleneck': False, 'risk_score': 0.35},
    {'node_key': 'MS-PAYMENTS', 'label': 'Payments Core Service', 'node_type': 'MICROSERVICE', 'is_bottleneck': True, 'risk_score': 0.82},
    {'node_key': 'QUEUE-KAFKA', 'label': 'Payment Events Stream', 'node_type': 'KAFKA', 'is_bottleneck': False, 'risk_score': 0.20},
    {'node_key': 'REDIS-CACHE', 'label': 'Global Session Cache', 'node_type': 'REDIS', 'is_bottleneck': False, 'risk_score': 0.15},
    {'node_key': 'DB-PRIMARY', 'label': 'Primary PostgreSQL Cluster', 'node_type': 'DATABASE', 'is_bottleneck': True, 'risk_score': 0.75},
]


class ArchitectureIntelligenceService:
    """Microservices, event-driven (Kafka/Redis), DB architecture graph builder & bottleneck analyzer."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def seed_architecture(self) -> dict[str, Any]:
        count = self.db.query(ArchitectureNode).count()
        if count > 0:
            return self.fetch_architecture_graph()

        nodes_map = {}
        for n in DEFAULT_NODES:
            node = ArchitectureNode(
                node_key=n['node_key'],
                label=n['label'],
                node_type=n['node_type'],
                is_bottleneck=n['is_bottleneck'],
                risk_score=n['risk_score'],
                attributes_json=json.dumps({'replica_count': 3, 'cpu_utilization_pct': 42.5}),
            )
            self.db.add(node)
            self.db.flush()
            nodes_map[n['node_key']] = node.id

        # Edges
        edge1 = ArchitectureEdge(source_node_id=nodes_map['MS-CHECKOUT'], target_node_id=nodes_map['MS-PAYMENTS'], call_protocol='gRPC', latency_p95_ms=8.5)
        edge2 = ArchitectureEdge(source_node_id=nodes_map['MS-PAYMENTS'], target_node_id=nodes_map['QUEUE-KAFKA'], call_protocol='KAFKA_PRODUCE', latency_p95_ms=4.2)
        edge3 = ArchitectureEdge(source_node_id=nodes_map['MS-PAYMENTS'], target_node_id=nodes_map['DB-PRIMARY'], call_protocol='SQL_JDBC', latency_p95_ms=22.4)
        self.db.add_all([edge1, edge2, edge3])
        self.db.commit()

        return self.fetch_architecture_graph()

    def fetch_architecture_graph(self) -> dict[str, Any]:
        nodes = self.db.query(ArchitectureNode).all()
        edges = self.db.query(ArchitectureEdge).all()

        nodes_data = [
            {
                'id': n.id,
                'node_key': n.node_key,
                'label': n.label,
                'node_type': n.node_type,
                'is_bottleneck': n.is_bottleneck,
                'risk_score': n.risk_score,
                'attributes': json.loads(n.attributes_json),
            }
            for n in nodes
        ]

        edges_data = [
            {
                'id': e.id,
                'source_node_id': e.source_node_id,
                'target_node_id': e.target_node_id,
                'call_protocol': e.call_protocol,
                'latency_p95_ms': e.latency_p95_ms,
            }
            for e in edges
        ]

        critical_path = [n['node_key'] for n in nodes_data if n['risk_score'] > 0.7]
        bottlenecks = [n['node_key'] for n in nodes_data if n['is_bottleneck']]

        return {
            'nodes': nodes_data,
            'edges': edges_data,
            'critical_path': critical_path,
            'bottlenecks': bottlenecks,
            'architecture_risk_score': round(sum(n['risk_score'] for n in nodes_data) / max(1, len(nodes_data)), 2),
        }
