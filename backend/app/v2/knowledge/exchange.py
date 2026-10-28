"""Knowledge Exchange for Version 2.1 Multi-Agent Knowledge Sharing."""
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class SharedKnowledgeArtifact(BaseModel):
    artifact_id: str = Field(default_factory=lambda: f"knw-{uuid.uuid4().hex[:6]}")
    source_agent_id: str
    category: str = Field(..., description="HISTORY, PATTERN, RECOMMENDATION, TRACE, SCORE, PROMPT")
    data: Dict[str, Any]
    confidence_score: float = Field(95.0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class KnowledgeExchange:
    def __init__(self):
        self._exchange_store: List[SharedKnowledgeArtifact] = []

    def share_knowledge(self, source_agent_id: str, category: str, data: Dict[str, Any], confidence_score: float = 95.0) -> SharedKnowledgeArtifact:
        art = SharedKnowledgeArtifact(
            source_agent_id=source_agent_id,
            category=category,
            data=data,
            confidence_score=confidence_score,
        )
        self._exchange_store.append(art)
        return art

    def query_knowledge(self, category: Optional[str] = None) -> List[SharedKnowledgeArtifact]:
        if not category:
            return list(self._exchange_store)
        cat_upper = category.upper()
        return [art for art in self._exchange_store if art.category.upper() == cat_upper]
