"""Self-Learning Feedback Loop for Version 2.0 (User Feedback & Correction Memory)."""
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class LearningFeedback(BaseModel):
    feedback_id: str = Field(default_factory=lambda: f"fb-{uuid.uuid4().hex[:6]}")
    user_id: str = Field("admin")
    rating: int = Field(5, description="User rating (1 to 5)")
    comments: Optional[str] = Field(None)
    suggested_correction: Optional[str] = Field(None)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CorrectionMemory:
    def __init__(self):
        self._corrections: List[Dict[str, Any]] = []

    def record(self, key: str, correction: str) -> None:
        self._corrections.append({"key": key, "correction": correction, "timestamp": datetime.now(timezone.utc).isoformat()})

    def list_corrections(self) -> List[Dict[str, Any]]:
        return list(self._corrections)


class FeedbackEngine:
    def __init__(self):
        self.correction_memory = CorrectionMemory()
        self._feedback_list: List[LearningFeedback] = []

    def submit_feedback(self, rating: int, comments: Optional[str] = None, correction: Optional[str] = None) -> LearningFeedback:
        fb = LearningFeedback(rating=rating, comments=comments, suggested_correction=correction)
        self._feedback_list.append(fb)
        if correction:
            self.correction_memory.record("user_suggestion", correction)
        return fb

    def get_feedback_stats(self) -> Dict[str, Any]:
        if not self._feedback_list:
            return {"avg_rating": 5.0, "total_feedback": 0}
        avg_rating = sum(f.rating for f in self._feedback_list) / len(self._feedback_list)
        return {
            "avg_rating": round(avg_rating, 2),
            "total_feedback": len(self._feedback_list),
            "corrections_count": len(self.correction_memory.list_corrections()),
        }
