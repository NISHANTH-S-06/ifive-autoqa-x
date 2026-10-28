"""Policy and Security Engine for Version 2.0 (Validation & Guardrails)."""
import uuid
from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class PolicyType(str, Enum):
    EXECUTION = "EXECUTION"
    SECURITY = "SECURITY"
    PLUGIN = "PLUGIN"
    WORKFLOW = "WORKFLOW"
    AGENT = "AGENT"


class PolicyRule(BaseModel):
    rule_id: str = Field(default_factory=lambda: f"pol-{uuid.uuid4().hex[:6]}")
    policy_type: PolicyType = PolicyType.SECURITY
    name: str
    condition_key: str
    prohibited_values: List[Any] = Field(default_factory=list)
    severity: str = Field("HIGH", description="LOW, MEDIUM, HIGH, CRITICAL")


class PolicyViolation(BaseModel):
    rule_id: str
    policy_type: PolicyType
    violated_key: str
    actual_value: Any
    severity: str
    message: str


class PolicyValidator:
    def validate_rules(self, rules: List[PolicyRule], context_params: Dict[str, Any]) -> List[PolicyViolation]:
        violations = []
        for r in rules:
            actual = context_params.get(r.condition_key)
            if actual in r.prohibited_values:
                violations.append(
                    PolicyViolation(
                        rule_id=r.rule_id,
                        policy_type=r.policy_type,
                        violated_key=r.condition_key,
                        actual_value=actual,
                        severity=r.severity,
                        message=f"Prohibited value '{actual}' detected for policy key '{r.condition_key}' ({r.name})",
                    )
                )
        return violations


class PolicyEngine:
    def __init__(self):
        self.validator = PolicyValidator()
        self._rules: List[PolicyRule] = [
            PolicyRule(
                policy_type=PolicyType.SECURITY,
                name="SSRF Metadata URL Block",
                condition_key="target_host",
                prohibited_values=["169.254.169.254", "metadata.google.internal"],
                severity="CRITICAL",
            ),
            PolicyRule(
                policy_type=PolicyType.SECURITY,
                name="Prohibit Production Target Modifying",
                condition_key="environment",
                prohibited_values=["PROD_UNAPPROVED"],
                severity="HIGH",
            ),
        ]

    def register_rule(self, rule: PolicyRule) -> None:
        self._rules.append(rule)

    def evaluate_context(self, context_params: Dict[str, Any]) -> Dict[str, Any]:
        violations = self.validator.validate_rules(self._rules, context_params)
        is_compliant = len(violations) == 0
        has_critical = any(v.severity == "CRITICAL" for v in violations)

        return {
            "is_compliant": is_compliant,
            "has_critical_violations": has_critical,
            "total_violations": len(violations),
            "violations": [v.model_dump() for v in violations],
        }
