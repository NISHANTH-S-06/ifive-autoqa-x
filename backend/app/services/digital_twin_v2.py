"""Module 9 – Autonomous Quality Digital Twin V2 service."""
from __future__ import annotations

import json
from typing import Any

from sqlalchemy.orm import Session

from app.models.phase16_models import DigitalTwinV2Node

DEFAULT_TWIN = [
    {'twin_key': 'TWIN-SERVICE-PAYMENT', 'entity_name': 'Payments Core Microservice', 'entity_type': 'SERVICE', 'health_status': 'HEALTHY', 'state': {'instances': 4, 'cpu_pct': 32}},
    {'twin_key': 'TWIN-INFRA-AWS-EAST', 'entity_name': 'AWS us-east-1 EKS Cluster', 'entity_type': 'INFRASTRUCTURE', 'health_status': 'HEALTHY', 'state': {'node_count': 12, 'network_io_mbps': 450}},
    {'twin_key': 'TWIN-API-CHARGE', 'entity_name': 'POST /api/v2/payments/charge', 'entity_type': 'API', 'health_status': 'HEALTHY', 'state': {'p95_ms': 18.2, 'error_pct': 0.01}},
    {'twin_key': 'TWIN-RELEASE-V5', 'entity_name': 'Enterprise Release v5.0.0', 'entity_type': 'RELEASE', 'health_status': 'HEALTHY', 'state': {'quality_score': 96.5, 'certified': True}},
]


class DigitalTwinV2Service:
    """Live software digital twin representing Services, Infra, API, Users, DB, Deployments, Releases, Quality, and Risk."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def sync_digital_twin(self) -> list[dict[str, Any]]:
        count = self.db.query(DigitalTwinV2Node).count()
        if count == 0:
            for t in DEFAULT_TWIN:
                rec = DigitalTwinV2Node(
                    twin_key=t['twin_key'],
                    entity_name=t['entity_name'],
                    entity_type=t['entity_type'],
                    health_status=t['health_status'],
                    live_state_json=json.dumps(t['state']),
                )
                self.db.add(rec)
            self.db.commit()

        nodes = self.db.query(DigitalTwinV2Node).all()
        return [
            {
                'id': n.id,
                'twin_key': n.twin_key,
                'entity_name': n.entity_name,
                'entity_type': n.entity_type,
                'health_status': n.health_status,
                'live_state': json.loads(n.live_state_json),
                'last_synced_at': n.last_synced_at.isoformat(),
            }
            for n in nodes
        ]
