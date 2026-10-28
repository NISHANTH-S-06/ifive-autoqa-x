"""Explainability and Decision Trace Engine for Version 2.0 (Why, How, Rationale)."""
import uuid
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class DecisionTrace(BaseModel):
    trace_id: str = Field(default_factory=lambda: f"tr-{uuid.uuid4().hex[:6]}")
    decision_id: str
    why: str = Field(..., description="Explainable justification of why this decision was made")
    how: str = Field(..., description="Step-by-step logic of how the decision was evaluated")
    confidence_score: float = Field(..., description="Calculated 0-100 confidence score")
    alternatives_considered: List[Dict[str, Any]] = Field(default_factory=list)
    rules_applied: List[str] = Field(default_factory=list)


class ReasoningTrace(BaseModel):
    trace_id: str = Field(default_factory=lambda: f"rtr-{uuid.uuid4().hex[:6]}")
    reasoning_type: str
    premises: List[str] = Field(default_factory=list)
    rule_chain: List[str] = Field(default_factory=list)
    conclusion: str


class ExecutionTrace(BaseModel):
    trace_id: str = Field(default_factory=lambda: f"etr-{uuid.uuid4().hex[:6]}")
    execution_id: str
    steps_executed: int
    status: str
    duration_ms: float


class ExplanationEngine:
    def explain_decision(
        self,
        decision_id: str,
        selected_option: Dict[str, Any],
        confidence_score: float,
        ranked_options: List[Dict[str, Any]],
        rules_applied: List[str],
    ) -> DecisionTrace:
        opt_name = selected_option.get("name", selected_option.get("id", "Selected Option"))
        why = (
            f"Option '{opt_name}' was selected because it satisfied {len(rules_applied)} policy rules "
            f"and achieved the highest weighted decision score of {confidence_score:.1f}%."
        )
        how = (
            f"1. Context parameters were evaluated against policy rules. "
            f"2. Each rule contributed its weighted impact to candidate options. "
            f"3. Options were ranked by score descending."
        )
        alternatives = [opt for opt in ranked_options if opt.get("id") != selected_option.get("id")]

        return DecisionTrace(
            decision_id=decision_id,
            why=why,
            how=how,
            confidence_score=confidence_score,
            alternatives_considered=alternatives,
            rules_applied=rules_applied,
        )

    def explain_reasoning(
        self,
        reasoning_type: str,
        premises: List[str],
        rule_chain: List[str],
        conclusion: str,
    ) -> ReasoningTrace:
        return ReasoningTrace(
            reasoning_type=reasoning_type,
            premises=premises,
            rule_chain=rule_chain,
            conclusion=conclusion,
        )
