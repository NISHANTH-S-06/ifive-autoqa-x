import json
import logging
from typing import Dict, Any, List
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.phase10_models import DigitalTwinEntity

logger = logging.getLogger('autoqa.ai.digital_twin')

class DigitalTwinService:
    """
    Module 12: Enterprise Digital Twin
    Maintains a live digital twin mirror of connected enterprise applications.
    """

    def __init__(self, db: Session):
        self.db = db

    def sync_entity(self, company_id: int, product_id: int, entity_type: str, entity_key: str, label: str, metadata: Dict[str, Any]) -> DigitalTwinEntity:
        entity_type_upper = entity_type.upper()
        stmt = select(DigitalTwinEntity).where(
            DigitalTwinEntity.company_id == company_id,
            DigitalTwinEntity.entity_type == entity_type_upper,
            DigitalTwinEntity.entity_key == entity_key
        )
        existing = self.db.scalar(stmt)

        if existing:
            existing.label = label
            existing.metadata_json = json.dumps(metadata)
            self.db.commit()
            self.db.refresh(existing)
            return existing

        entity = DigitalTwinEntity(
            company_id=company_id,
            product_id=product_id,
            entity_type=entity_type_upper,
            entity_key=entity_key,
            label=label,
            metadata_json=json.dumps(metadata)
        )
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def get_digital_twin_mirror(self, company_id: int) -> Dict[str, Any]:
        stmt = select(DigitalTwinEntity).where(DigitalTwinEntity.company_id == company_id)
        entities = list(self.db.scalars(stmt).all())

        grouped = {}
        for e in entities:
            grouped.setdefault(e.entity_type, []).append({
                'id': e.id,
                'key': e.entity_key,
                'label': e.label,
                'metadata': json.loads(e.metadata_json or '{}')
            })

        return {
            'company_id': company_id,
            'total_twin_entities': len(entities),
            'mirror': grouped
        }
