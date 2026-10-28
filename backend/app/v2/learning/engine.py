"""Continuous Learning Engine for Version 2.0 (Deterministic Pattern Learning)."""
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class LearningRecord(BaseModel):
    record_id: str = Field(default_factory=lambda: f"lrn-{uuid.uuid4().hex[:6]}")
    learning_type: str = Field(..., description="PATTERN, FAILURE, SUCCESS, FEEDBACK")
    pattern: str
    confidence_adjustment: float = Field(0.0)
    learned_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)


class LearningRepository:
    def __init__(self):
        self._records: List[LearningRecord] = []

    def add(self, record: LearningRecord) -> None:
        self._records.append(record)

    def list_records(self) -> List[LearningRecord]:
        return list(self._records)


class PatternLearner:
    def learn_pattern(self, workflow_name: str, step_names: List[str]) -> LearningRecord:
        pattern_str = f"Pattern[{workflow_name}]: {' -> '.join(step_names)}"
        return LearningRecord(
            learning_type="PATTERN",
            pattern=pattern_str,
            confidence_adjustment=+5.0,
            metadata={"step_count": len(step_names)},
        )


class FailureLearner:
    def learn_from_failure(self, step_name: str, error_msg: str) -> LearningRecord:
        return LearningRecord(
            learning_type="FAILURE",
            pattern=f"FailurePattern[{step_name}]: {error_msg[:40]}",
            confidence_adjustment=-10.0,
            metadata={"step_name": step_name, "error": error_msg},
        )


class LearningEngine:
    def __init__(self):
        self.repository = LearningRepository()
        self.pattern_learner = PatternLearner()
        self.failure_learner = FailureLearner()

    def process_execution_learning(self, run_result: Dict[str, Any]) -> LearningRecord:
        status = run_result.get("status", "SUCCESS")
        if status == "SUCCESS":
            rec = self.pattern_learner.learn_pattern("Automated Workflow", ["Plan", "Execute", "Review", "Report"])
        else:
            rec = self.failure_learner.learn_from_failure("Execution Step", "Selector not found")
        
        self.repository.add(rec)
        return rec

    def get_learning_stats(self) -> Dict[str, Any]:
        records = self.repository.list_records()
        return {
            "total_learned_patterns": len(records),
            "records": [r.model_dump() for r in records],
        }
