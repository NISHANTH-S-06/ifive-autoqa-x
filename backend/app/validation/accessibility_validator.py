import json
from typing import Any, Dict, List, Optional

from app.models.advanced_validation import AccessibilityValidationDefinition
from app.validation.base import BaseValidator, ValidationResultDTO, ValidationSeverity, ValidationStatus, ValidatorType


class AccessibilityValidator(BaseValidator):
    def validate_scan(
        self,
        definition: AccessibilityValidationDefinition,
        scan_results: Dict[str, Any]
    ) -> List[ValidationResultDTO]:
        if not definition.enabled:
            return [
                ValidationResultDTO(
                    validator_type=ValidatorType.ACCESSIBILITY,
                    status=ValidationStatus.INFO,
                    severity=ValidationSeverity.INFO,
                    message=f"Accessibility check for route '{definition.route}' is disabled.",
                    definition_id=definition.id,
                )
            ]

        exclude_rules = set()
        if definition.exclude_rules:
            try:
                exclude_rules = set(json.loads(definition.exclude_rules))
            except Exception:
                pass

        violations = scan_results.get("violations", [])
        dtos: List[ValidationResultDTO] = []

        for v in violations:
            rule_id = v.get("id")
            if rule_id in exclude_rules:
                continue

            impact = (v.get("impact") or "minor").lower()
            help_text = v.get("help", "Accessibility violation")
            nodes = v.get("nodes", [])

            if impact == "critical":
                status = ValidationStatus.FAIL
                severity = ValidationSeverity.CRITICAL
                reason_code = "ACCESSIBILITY_CRITICAL"
            elif impact == "serious":
                status = ValidationStatus.FAIL if definition.severity_threshold in ("critical", "serious") else ValidationStatus.WARNING
                severity = ValidationSeverity.SERIOUS
                reason_code = "ACCESSIBILITY_CRITICAL"
            elif impact == "moderate":
                status = ValidationStatus.WARNING
                severity = ValidationSeverity.MODERATE
                reason_code = None
            else:
                status = ValidationStatus.INFO
                severity = ValidationSeverity.MINOR
                reason_code = None

            message = f"Accessibility [{impact.upper()}] {rule_id}: {help_text} ({len(nodes)} elements on {definition.route})"

            dtos.append(
                ValidationResultDTO(
                    validator_type=ValidatorType.ACCESSIBILITY,
                    status=status,
                    severity=severity,
                    message=message,
                    definition_id=definition.id,
                    actual_json={
                        "rule_id": rule_id,
                        "impact": impact,
                        "help": help_text,
                        "nodes_count": len(nodes),
                        "nodes": nodes[:3],
                        "route": definition.route
                    },
                    reason_code=reason_code
                )
            )

        if not dtos:
            dtos.append(
                ValidationResultDTO(
                    validator_type=ValidatorType.ACCESSIBILITY,
                    status=ValidationStatus.PASS,
                    severity=ValidationSeverity.INFO,
                    message=f"Accessibility scan for route '{definition.route}' passed with zero violations ({definition.standard}).",
                    definition_id=definition.id,
                    actual_json={"violations_count": 0, "route": definition.route}
                )
            )

        return dtos
