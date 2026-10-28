"""Decision Engine for Version 2.0 (Deterministic Evaluation & Rule Ranking)."""
import uuid
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class DecisionRule(BaseModel):
    rule_id: str = Field(default_factory=lambda: f"rule-{uuid.uuid4().hex[:6]}")
    name: str
    weight: float = Field(1.0, description="Rule weight multiplier")
    condition_key: str = Field(..., description="Parameter key to evaluate")
    expected_value: Any = Field(..., description="Expected value for rule match")
    score_impact: float = Field(10.0, description="Score contribution if rule matches")


class DecisionPolicy(BaseModel):
    policy_id: str = Field(default_factory=lambda: f"pol-{uuid.uuid4().hex[:6]}")
    rules: List[DecisionRule] = Field(default_factory=list)
    min_confidence_threshold: float = Field(50.0)


class DecisionContext(BaseModel):
    context_id: str = Field(default_factory=lambda: f"ctx-{uuid.uuid4().hex[:6]}")
    options: List[Dict[str, Any]] = Field(default_factory=list, description="Candidate options to evaluate")
    parameters: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DecisionResult(BaseModel):
    decision_id: str = Field(default_factory=lambda: f"dec-{uuid.uuid4().hex[:6]}")
    selected_option: Optional[Dict[str, Any]] = Field(None)
    confidence_score: float = Field(0.0, description="Calculated 0-100 confidence score")
    rationale: str = Field("", description="Explainable decision rationale")
    ranked_options: List[Dict[str, Any]] = Field(default_factory=list)
    rules_applied: List[str] = Field(default_factory=list)


class DecisionNode(BaseModel):
    node_id: str
    condition_key: str
    branches: Dict[str, str]  # value -> next_node_id or option_id
    default_branch: Optional[str] = None


class DecisionTree:
    def __init__(self, root_node_id: str, nodes: Dict[str, DecisionNode]):
        self.root_node_id = root_node_id
        self.nodes = nodes

    def evaluate(self, parameters: Dict[str, Any]) -> Optional[str]:
        current_id = self.root_node_id
        while current_id in self.nodes:
            node = self.nodes[current_id]
            val = str(parameters.get(node.condition_key, ""))
            if val in node.branches:
                current_id = node.branches[val]
            elif node.default_branch:
                current_id = node.default_branch
            else:
                return None
        return current_id


class DecisionEngine:
    def __init__(self, policy: Optional[DecisionPolicy] = None):
        self.policy = policy or DecisionPolicy(
            rules=[
                DecisionRule(name="Passed Review Check", condition_key="review_verdict", expected_value="PASSED", score_impact=40.0),
                DecisionRule(name="Zero Failures Check", condition_key="failure_count", expected_value=0, score_impact=30.0),
                DecisionRule(name="Complete Steps Check", condition_key="is_complete", expected_value=True, score_impact=30.0),
            ]
        )

    def evaluate_options(self, context: DecisionContext) -> DecisionResult:
        if not context.options:
            return DecisionResult(rationale="No options provided for evaluation", confidence_score=0.0)

        scored_options = []
        rules_applied = []

        for opt in context.options:
            score = 0.0
            opt_params = {**context.parameters, **opt}
            
            for rule in self.policy.rules:
                actual_val = opt_params.get(rule.condition_key)
                if actual_val == rule.expected_value:
                    score += rule.score_impact * rule.weight
                    if rule.name not in rules_applied:
                        rules_applied.append(rule.name)

            capped_score = min(100.0, max(0.0, score))
            scored_opt = dict(opt)
            scored_opt["_decision_score"] = capped_score
            scored_options.append(scored_opt)

        # Rank decisions by score descending
        ranked = sorted(scored_options, key=lambda x: x["_decision_score"], reverse=True)
        best_option = ranked[0]
        best_score = best_option["_decision_score"]

        rationale = (
            f"Selected option '{best_option.get('name', best_option.get('id', 'Option 1'))}' "
            f"with confidence {best_score:.1f}% based on {len(rules_applied)} applied rules."
        )

        return DecisionResult(
            selected_option=best_option,
            confidence_score=best_score,
            rationale=rationale,
            ranked_options=ranked,
            rules_applied=rules_applied,
        )
