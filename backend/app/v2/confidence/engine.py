"""Confidence Scoring Engine for Version 2.0 (0-100 Score & Rationale)."""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class ConfidenceFactor(BaseModel):
    factor_name: str
    weight: float = Field(1.0)
    score_impact: float = Field(0.0)
    explanation: str = Field("")


class ConfidenceEvaluation(BaseModel):
    overall_score: float = Field(..., description="0-100 confidence score")
    confidence_level: str = Field("HIGH", description="HIGH, MEDIUM, LOW")
    explanation: str = Field(...)
    factors: List[ConfidenceFactor] = Field(default_factory=list)


class ConfidenceEngine:
    def compute_execution_confidence(self, step_results: List[Dict[str, Any]]) -> ConfidenceEvaluation:
        total_steps = len(step_results)
        if total_steps == 0:
            return ConfidenceEvaluation(
                overall_score=0.0,
                confidence_level="LOW",
                explanation="Zero execution steps evaluated; confidence is 0%",
            )

        passed_steps = sum(1 for s in step_results if s.get("status") == "PASSED")
        pass_ratio = passed_steps / total_steps
        score = pass_ratio * 100.0

        factors = [
            ConfidenceFactor(
                factor_name="Pass Ratio",
                weight=1.0,
                score_impact=score,
                explanation=f"{passed_steps} of {total_steps} execution steps passed ({pass_ratio*100:.1f}%)",
            )
        ]

        level = "HIGH" if score >= 80.0 else ("MEDIUM" if score >= 50.0 else "LOW")
        explanation = f"Execution confidence evaluated at {score:.1f}% ({passed_steps}/{total_steps} passed)."

        return ConfidenceEvaluation(
            overall_score=round(score, 1),
            confidence_level=level,
            explanation=explanation,
            factors=factors,
        )

    def compute_planning_confidence(self, subtasks: List[Dict[str, Any]]) -> ConfidenceEvaluation:
        total = len(subtasks)
        score = 95.0 if total >= 3 else 60.0
        level = "HIGH" if score >= 80.0 else "MEDIUM"
        return ConfidenceEvaluation(
            overall_score=score,
            confidence_level=level,
            explanation=f"Planning confidence evaluated at {score}% based on {total} structured subtasks.",
            factors=[ConfidenceFactor(factor_name="Task Structure", score_impact=score, explanation="Subtask count check")],
        )

    def compute_decision_confidence(self, decision_score: float) -> ConfidenceEvaluation:
        score = min(100.0, max(0.0, decision_score))
        level = "HIGH" if score >= 80.0 else ("MEDIUM" if score >= 50.0 else "LOW")
        return ConfidenceEvaluation(
            overall_score=round(score, 1),
            confidence_level=level,
            explanation=f"Decision confidence evaluated at {score:.1f}% based on rule weights.",
        )

    def compute_workflow_confidence(self, workflow_status: str, step_count: int) -> ConfidenceEvaluation:
        score = 100.0 if workflow_status == "SUCCESS" else 25.0
        level = "HIGH" if score >= 80.0 else "LOW"
        return ConfidenceEvaluation(
            overall_score=score,
            confidence_level=level,
            explanation=f"Workflow status is {workflow_status} across {step_count} steps.",
        )
