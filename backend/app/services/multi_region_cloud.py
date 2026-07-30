"""Module 11 – Multi-Region Cloud service (AWS, Azure, GCP)."""
from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.models.phase13_models import CloudRegionConfig

SEED_REGIONS = [
    {'cloud_provider': 'AWS', 'region_name': 'us-east-1', 'region_display': 'US East (N. Virginia)', 'is_primary': True, 'failover_priority': 1},
    {'cloud_provider': 'AWS', 'region_name': 'eu-west-1', 'region_display': 'EU West (Ireland)', 'is_primary': False, 'failover_priority': 2},
    {'cloud_provider': 'AWS', 'region_name': 'ap-south-1', 'region_display': 'Asia Pacific (Mumbai)', 'is_primary': False, 'failover_priority': 3},
    {'cloud_provider': 'AZURE', 'region_name': 'eastus', 'region_display': 'Azure East US', 'is_primary': False, 'failover_priority': 4},
    {'cloud_provider': 'AZURE', 'region_name': 'westeurope', 'region_display': 'Azure West Europe', 'is_primary': False, 'failover_priority': 5},
    {'cloud_provider': 'GCP', 'region_name': 'us-central1', 'region_display': 'GCP US Central (Iowa)', 'is_primary': False, 'failover_priority': 6},
    {'cloud_provider': 'GCP', 'region_name': 'europe-west1', 'region_display': 'GCP Europe West (Belgium)', 'is_primary': False, 'failover_priority': 7, 'is_disaster_recovery': True},
    {'cloud_provider': 'ON_PREMISE', 'region_name': 'local', 'region_display': 'On-Premise / Local', 'is_primary': False, 'failover_priority': 8},
]


class MultiRegionCloudService:
    """Manages multi-cloud region configurations, failover, and backup."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def seed_regions(self) -> list[dict[str, Any]]:
        existing = self.db.query(CloudRegionConfig).count()
        if existing > 0:
            return self.list_regions()
        for r in SEED_REGIONS:
            region = CloudRegionConfig(
                cloud_provider=r['cloud_provider'],
                region_name=r['region_name'],
                region_display=r['region_display'],
                is_primary=r.get('is_primary', False),
                is_disaster_recovery=r.get('is_disaster_recovery', False),
                failover_priority=r.get('failover_priority', 9),
                region_status='ACTIVE',
                replication_lag_ms=r.get('replication_lag_ms', 0),
                last_backup_at=datetime.utcnow(),
            )
            self.db.add(region)
        self.db.commit()
        return self.list_regions()

    def list_regions(self) -> list[dict[str, Any]]:
        regions = self.db.query(CloudRegionConfig).order_by(CloudRegionConfig.failover_priority).all()
        return [self._region_dict(r) for r in regions]

    def get_region(self, region_id: int) -> dict[str, Any] | None:
        r = self.db.query(CloudRegionConfig).filter_by(id=region_id).first()
        return self._region_dict(r) if r else None

    def add_region(
        self,
        cloud_provider: str,
        region_name: str,
        region_display: str,
        failover_priority: int = 9,
        config: dict[str, Any] | None = None,
    ) -> CloudRegionConfig:
        region = CloudRegionConfig(
            cloud_provider=cloud_provider,
            region_name=region_name,
            region_display=region_display,
            failover_priority=failover_priority,
            config_json=json.dumps(config or {}),
        )
        self.db.add(region)
        self.db.commit()
        self.db.refresh(region)
        return region

    def get_cloud_health(self) -> dict[str, Any]:
        regions = self.db.query(CloudRegionConfig).all()
        active = sum(1 for r in regions if r.region_status == 'ACTIVE')
        degraded = sum(1 for r in regions if r.region_status == 'DEGRADED')
        offline = sum(1 for r in regions if r.region_status == 'OFFLINE')
        by_provider: dict[str, dict[str, int]] = {}
        for r in regions:
            p = r.cloud_provider
            if p not in by_provider:
                by_provider[p] = {'total': 0, 'active': 0}
            by_provider[p]['total'] += 1
            if r.region_status == 'ACTIVE':
                by_provider[p]['active'] += 1
        return {
            'total_regions': len(regions),
            'active': active,
            'degraded': degraded,
            'offline': offline,
            'health_pct': round(active / max(len(regions), 1) * 100, 1),
            'by_provider': by_provider,
        }

    def trigger_failover(self, from_region_id: int, to_region_id: int) -> dict[str, Any]:
        from_region = self.db.query(CloudRegionConfig).filter_by(id=from_region_id).first()
        to_region = self.db.query(CloudRegionConfig).filter_by(id=to_region_id).first()
        if not from_region or not to_region:
            return {'error': 'Region not found'}
        from_region.region_status = 'OFFLINE'
        to_region.region_status = 'ACTIVE'
        to_region.is_primary = True
        self.db.commit()
        return {
            'failover_from': from_region.region_name,
            'failover_to': to_region.region_name,
            'status': 'FAILOVER_COMPLETE',
        }

    def get_backup_status(self) -> list[dict[str, Any]]:
        regions = self.db.query(CloudRegionConfig).filter(
            CloudRegionConfig.last_backup_at.isnot(None)
        ).all()
        return [
            {
                'region_name': r.region_name,
                'cloud_provider': r.cloud_provider,
                'last_backup_at': r.last_backup_at.isoformat() if r.last_backup_at else None,
                'replication_lag_ms': r.replication_lag_ms,
            }
            for r in regions
        ]

    def _region_dict(self, r: CloudRegionConfig) -> dict[str, Any]:
        return {
            'id': r.id,
            'cloud_provider': r.cloud_provider,
            'region_name': r.region_name,
            'region_display': r.region_display,
            'region_status': r.region_status,
            'failover_priority': r.failover_priority,
            'is_primary': r.is_primary,
            'is_disaster_recovery': r.is_disaster_recovery,
            'replication_lag_ms': r.replication_lag_ms,
            'last_backup_at': r.last_backup_at.isoformat() if r.last_backup_at else None,
        }
