import json
import re
import time
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse
import httpx

from app.models.advanced_validation import ApiValidationDefinition
from app.validation.base import BaseValidator, ValidationResultDTO, ValidationSeverity, ValidationStatus, ValidatorType

APPROVED_LOCAL_ORIGINS = {
    "http://127.0.0.1:8000", "http://127.0.0.1:8001", "http://127.0.0.1:8002",
    "http://127.0.0.1:5173", "http://127.0.0.1:5174", "http://127.0.0.1:5175",
    "http://localhost:8000", "http://localhost:8001", "http://localhost:8002",
    "http://localhost:5173", "http://localhost:5174", "http://localhost:5175",
}

ALLOWED_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE"}
SECRET_REGEX = re.compile(r"(?i)(password|token|secret|cookie|authorization|auth|csrf)")


def redact_secrets(data: Any) -> Any:
    if isinstance(data, dict):
        cleaned = {}
        for k, v in data.items():
            if SECRET_REGEX.search(k):
                cleaned[k] = "[REDACTED]"
            else:
                cleaned[k] = redact_secrets(v)
        return cleaned
    elif isinstance(data, list):
        return [redact_secrets(item) for item in data]
    return data


def extract_json_path(data: Any, path_expression: str) -> Any:
    # Basic JsonPath solver for dot-separated keys, e.g. "data.id" or "items.0.name"
    keys = path_expression.strip().lstrip("$.").split(".")
    curr = data
    for k in keys:
        if not k:
            continue
        if isinstance(curr, dict) and k in curr:
            curr = curr[k]
        elif isinstance(curr, list) and k.isdigit() and int(k) < len(curr):
            curr = curr[int(k)]
        else:
            return None
    return curr


class ApiValidator(BaseValidator):
    def validate_definition(
        self,
        definition: ApiValidationDefinition,
        base_origin: str = "http://127.0.0.1:8002",
        context: Optional[Dict[str, Any]] = None
    ) -> ValidationResultDTO:
        if not definition.enabled:
            return ValidationResultDTO(
                validator_type=ValidatorType.API,
                status=ValidationStatus.INFO,
                severity=ValidationSeverity.INFO,
                message=f"API validation '{definition.name}' is disabled.",
                definition_id=definition.id,
            )

        context = context or {}
        method = definition.method.upper()
        if method not in ALLOWED_METHODS:
            return ValidationResultDTO(
                validator_type=ValidatorType.API,
                status=ValidationStatus.FAIL,
                severity=ValidationSeverity.CRITICAL,
                message=f"HTTP method '{method}' is not allowed.",
                definition_id=definition.id,
                reason_code="API_METHOD_NOT_ALLOWED"
            )

        path = definition.path
        # Substitute template vars from context e.g. /api/employees/{id}
        for k, v in context.items():
            path = path.replace(f"{{{k}}}", str(v))

        # Check full URL
        if path.startswith("http://") or path.startswith("https://"):
            full_url = path
        else:
            full_url = f"{base_origin.rstrip('/')}/{path.lstrip('/')}"

        parsed = urlparse(full_url)
        origin = f"{parsed.scheme}://{parsed.netloc}"
        if origin not in APPROVED_LOCAL_ORIGINS:
            return ValidationResultDTO(
                validator_type=ValidatorType.API,
                status=ValidationStatus.BLOCKED,
                severity=ValidationSeverity.CRITICAL,
                message=f"External or unapproved API origin rejected: '{origin}'",
                definition_id=definition.id,
                reason_code="TARGET_UNAVAILABLE"
            )

        headers = {}
        if definition.request_headers_template:
            try:
                hdr_str = definition.request_headers_template
                for k, v in context.items():
                    hdr_str = hdr_str.replace(f"{{{k}}}", str(v))
                headers = json.loads(hdr_str)
            except Exception:
                headers = {}

        body = None
        if definition.request_body_template:
            try:
                body_str = definition.request_body_template
                for k, v in context.items():
                    body_str = body_str.replace(f"{{{k}}}", str(v))
                body = json.loads(body_str)
            except Exception:
                body = None

        timeout_sec = (definition.timeout_ms or 5000) / 1000.0
        start_time = time.time()
        try:
            with httpx.Client(timeout=timeout_sec, follow_redirects=False) as client:
                if method == "GET":
                    resp = client.get(full_url, headers=headers)
                elif method == "POST":
                    resp = client.post(full_url, headers=headers, json=body)
                elif method == "PUT":
                    resp = client.put(full_url, headers=headers, json=body)
                elif method == "PATCH":
                    resp = client.patch(full_url, headers=headers, json=body)
                elif method == "DELETE":
                    resp = client.delete(full_url, headers=headers)
                else:
                    raise ValueError(f"Unsupported method {method}")
        except httpx.TimeoutException:
            duration_ms = int((time.time() - start_time) * 1000)
            return ValidationResultDTO(
                validator_type=ValidatorType.API,
                status=ValidationStatus.FAIL,
                severity=ValidationSeverity.SERIOUS,
                message=f"API request timed out after {definition.timeout_ms or 5000}ms",
                definition_id=definition.id,
                duration_ms=duration_ms,
                reason_code="API_STATUS_MISMATCH"
            )
        except Exception as exc:
            duration_ms = int((time.time() - start_time) * 1000)
            return ValidationResultDTO(
                validator_type=ValidatorType.API,
                status=ValidationStatus.BLOCKED,
                severity=ValidationSeverity.CRITICAL,
                message=f"API connection failed: {str(exc)}",
                definition_id=definition.id,
                duration_ms=duration_ms,
                reason_code="TARGET_UNAVAILABLE"
            )

        duration_ms = int((time.time() - start_time) * 1000)

        # Check response status
        if resp.status_code != definition.expected_status:
            return ValidationResultDTO(
                validator_type=ValidatorType.API,
                status=ValidationStatus.FAIL,
                severity=ValidationSeverity.CRITICAL,
                message=f"Status code mismatch: expected {definition.expected_status}, got {resp.status_code}",
                definition_id=definition.id,
                expected_json={"status_code": definition.expected_status},
                actual_json={"status_code": resp.status_code, "body": redact_secrets(resp.text[:500])},
                duration_ms=duration_ms,
                reason_code="API_STATUS_MISMATCH"
            )

        # Parse JSON
        resp_json = {}
        try:
            resp_json = resp.json()
        except Exception:
            resp_json = {"raw": resp.text[:500]}

        safe_actual = redact_secrets(resp_json)

        # Assert JSON paths if specified
        if definition.expected_json_paths:
            try:
                paths_dict = json.loads(definition.expected_json_paths)
                for path_expr, expected_val in paths_dict.items():
                    extracted = extract_json_path(resp_json, path_expr)
                    if extracted != expected_val and str(extracted) != str(expected_val):
                        return ValidationResultDTO(
                            validator_type=ValidatorType.API,
                            status=ValidationStatus.FAIL,
                            severity=ValidationSeverity.SERIOUS,
                            message=f"JSON path assertion failed for '{path_expr}': expected '{expected_val}', got '{extracted}'",
                            definition_id=definition.id,
                            expected_json={path_expr: expected_val},
                            actual_json={path_expr: extracted, "response": safe_actual},
                            duration_ms=duration_ms,
                            reason_code="API_SCHEMA_MISMATCH"
                        )
            except json.JSONDecodeError:
                pass

        # Store context variables if present (e.g. employee id)
        if isinstance(resp_json, dict):
            if "id" in resp_json:
                context["id"] = resp_json["id"]
                context["created_id"] = resp_json["id"]
            if "email" in resp_json:
                context["email"] = resp_json["email"]

        return ValidationResultDTO(
            validator_type=ValidatorType.API,
            status=ValidationStatus.PASS,
            severity=ValidationSeverity.INFO,
            message=f"API validation '{definition.name}' passed ({resp.status_code} OK in {duration_ms}ms).",
            definition_id=definition.id,
            actual_json=safe_actual,
            duration_ms=duration_ms
        )
