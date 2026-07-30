from typing import Any, Dict, Optional

from app.models.advanced_validation import PerformanceValidationDefinition
from app.validation.base import BaseValidator, ValidationResultDTO, ValidationSeverity, ValidationStatus, ValidatorType


class PerformanceValidator(BaseValidator):
    def validate_metric(
        self,
        definition: PerformanceValidationDefinition,
        captured_metrics: Dict[str, Any]
    ) -> ValidationResultDTO:
        if not definition.enabled:
            return ValidationResultDTO(
                validator_type=ValidatorType.PERFORMANCE,
                status=ValidationStatus.INFO,
                severity=ValidationSeverity.INFO,
                message=f"Performance check for route '{definition.route}' metric '{definition.metric}' is disabled.",
                definition_id=definition.id,
            )

        metric_key = definition.metric.lower()
        if metric_key not in captured_metrics or captured_metrics[metric_key] is None:
            return ValidationResultDTO(
                validator_type=ValidatorType.PERFORMANCE,
                status=ValidationStatus.BLOCKED,
                severity=ValidationSeverity.MODERATE,
                message=f"Performance metric '{definition.metric}' unavailable for route '{definition.route}' (cannot false PASS).",
                definition_id=definition.id,
                reason_code="TARGET_UNAVAILABLE"
            )

        val = float(captured_metrics[metric_key])

        if val > definition.failure_threshold:
            return ValidationResultDTO(
                validator_type=ValidatorType.PERFORMANCE,
                status=ValidationStatus.FAIL,
                severity=ValidationSeverity.CRITICAL,
                message=f"Performance metric '{definition.metric}' on '{definition.route}' exceeded failure threshold: {val} > {definition.failure_threshold}",
                definition_id=definition.id,
                expected_json={"warning_threshold": definition.warning_threshold, "failure_threshold": definition.failure_threshold},
                actual_json={"metric": definition.metric, "value": val, "route": definition.route},
                reason_code="PERFORMANCE_THRESHOLD_EXCEEDED"
            )
        elif val > definition.warning_threshold:
            return ValidationResultDTO(
                validator_type=ValidatorType.PERFORMANCE,
                status=ValidationStatus.WARNING,
                severity=ValidationSeverity.MODERATE,
                message=f"Performance metric '{definition.metric}' on '{definition.route}' exceeded warning threshold: {val} > {definition.warning_threshold}",
                definition_id=definition.id,
                expected_json={"warning_threshold": definition.warning_threshold, "failure_threshold": definition.failure_threshold},
                actual_json={"metric": definition.metric, "value": val, "route": definition.route}
            )
        else:
            return ValidationResultDTO(
                validator_type=ValidatorType.PERFORMANCE,
                status=ValidationStatus.PASS,
                severity=ValidationSeverity.INFO,
                message=f"Performance metric '{definition.metric}' on '{definition.route}' passed ({val} <= {definition.warning_threshold}).",
                definition_id=definition.id,
                actual_json={"metric": definition.metric, "value": val, "route": definition.route}
            )
