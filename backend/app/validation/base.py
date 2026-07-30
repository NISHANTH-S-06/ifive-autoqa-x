from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class ValidatorType(str, Enum):
    API = "API"
    DB = "DB"
    ACCESSIBILITY = "ACCESSIBILITY"
    PERFORMANCE = "PERFORMANCE"
    CONSOLE_NETWORK = "CONSOLE_NETWORK"
    EVIDENCE = "EVIDENCE"


class ValidationStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    WARNING = "WARNING"
    BLOCKED = "BLOCKED"
    INFO = "INFO"


class ValidationSeverity(str, Enum):
    CRITICAL = "CRITICAL"
    SERIOUS = "SERIOUS"
    MODERATE = "MODERATE"
    MINOR = "MINOR"
    INFO = "INFO"


@dataclass
class ValidationResultDTO:
    validator_type: ValidatorType
    status: ValidationStatus
    severity: ValidationSeverity = ValidationSeverity.INFO
    message: str = ""
    definition_id: Optional[int] = None
    expected_json: Optional[Dict[str, Any]] = None
    actual_json: Optional[Dict[str, Any]] = None
    duration_ms: int = 0
    artifact_ids: List[int] = field(default_factory=list)
    reason_code: Optional[str] = None


class BaseValidator:
    def validate(self, *args, **kwargs) -> List[ValidationResultDTO]:
        raise NotImplementedError("Subclasses must implement validate()")
