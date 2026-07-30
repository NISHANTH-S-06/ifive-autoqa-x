import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.phase9_models import AIMemoryRecord, AILocatorHistory

logger = logging.getLogger('autoqa.ai.memory')

class AIMemoryService:
    """
    Enterprise AI Memory Service:
    Provides long-term recall and persistence for runs, failures, fixes, 
    visual diffs, bug fingerprints, and locator healing history.
    """

    def __init__(self, db: Session):
        self.db = db

    def store_memory(
        self,
        memory_type: str,
        entity_key: str,
        memory_data: Dict[str, Any],
        project_id: Optional[int] = None,
        confidence_score: float = 0.95
    ) -> AIMemoryRecord:
        record = AIMemoryRecord(
            project_id=project_id,
            memory_type=memory_type.upper(),
            entity_key=entity_key,
            memory_data_json=json.dumps(memory_data),
            confidence_score=confidence_score
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def recall_memory(self, memory_type: str, entity_key: str) -> List[Dict[str, Any]]:
        stmt = select(AIMemoryRecord).where(
            AIMemoryRecord.memory_type == memory_type.upper(),
            AIMemoryRecord.entity_key == entity_key
        ).order_by(AIMemoryRecord.created_at.desc())
        
        records = self.db.scalars(stmt).all()
        return [json.loads(r.memory_data_json) for r in records]

    def record_locator_result(
        self,
        target_url: str,
        element_name: str,
        selector: str,
        success: bool,
        alternative_selectors: Optional[List[str]] = None,
        project_id: Optional[int] = None
    ) -> AILocatorHistory:
        stmt = select(AILocatorHistory).where(
            AILocatorHistory.target_url == target_url,
            AILocatorHistory.element_name == element_name
        )
        history = self.db.scalar(stmt)

        if history is None:
            history = AILocatorHistory(
                project_id=project_id,
                target_url=target_url,
                element_name=element_name,
                selector=selector,
                alternative_selectors_json=json.dumps(alternative_selectors or []),
                success_count=1 if success else 0,
                failure_count=0 if success else 1
            )
            self.db.add(history)
        else:
            if success:
                history.success_count += 1
            else:
                history.failure_count += 1
                history.last_healed_at = datetime.utcnow()
            history.selector = selector
            if alternative_selectors:
                history.alternative_selectors_json = json.dumps(alternative_selectors)

        self.db.commit()
        self.db.refresh(history)
        return history

    def get_best_locator(self, target_url: str, element_name: str) -> Optional[str]:
        stmt = select(AILocatorHistory).where(
            AILocatorHistory.target_url == target_url,
            AILocatorHistory.element_name == element_name,
            AILocatorHistory.status == 'ACTIVE'
        )
        history = self.db.scalar(stmt)
        if history:
            return history.selector
        return None
