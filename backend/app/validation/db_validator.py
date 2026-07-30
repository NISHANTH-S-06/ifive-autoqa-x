import hashlib
import json
import re
import sqlite3
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.models.advanced_validation import DatabaseValidationDefinition
from app.validation.base import BaseValidator, ValidationResultDTO, ValidationSeverity, ValidationStatus, ValidatorType

PROJECT_ROOT = Path(__file__).resolve().parents[3]

# Connection profiles map profile references to relative file paths from project root
CONNECTION_PROFILE_MAP = {
    "autoqa": "backend/data/autoqa.db",
    "demo_product": "demo-product/backend/data/demo_product.db",
    "mock_task_portal": "mock-task-portal/backend/data/mock_task_portal.db",
}

FORBIDDEN_SQL_PATTERNS = re.compile(
    r"(?i)\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|REPLACE|TRUNCATE|ATTACH|DETACH|VACUUM|REINDEX|BEGIN|COMMIT|ROLLBACK)\b"
)
COMMENT_PATTERN = re.compile(r"(--|/\*)|\bPRAGMA\b", re.IGNORECASE)


def is_sql_read_only(query: str) -> tuple[bool, str]:
    stripped = query.strip()
    if not stripped:
        return False, "Empty query"

    # Multi-statement check
    statements = [s for s in stripped.split(";") if s.strip()]
    if len(statements) > 1:
        return False, "Multi-statement SQL queries are strictly prohibited."

    # Must start with SELECT or WITH
    upper_query = stripped.upper()
    if not (upper_query.startswith("SELECT") or upper_query.startswith("WITH")):
        return False, "Query must start with SELECT or WITH."

    if FORBIDDEN_SQL_PATTERNS.search(stripped):
        return False, "Query contains forbidden mutating SQL keyword."

    if COMMENT_PATTERN.search(stripped):
        return False, "Query contains forbidden SQL comments or PRAGMA commands."

    return True, "OK"


class DatabaseValidator(BaseValidator):
    def resolve_db_path(self, profile_ref: str) -> Optional[Path]:
        direct = Path(profile_ref)
        if direct.is_file():
            return direct.resolve()

        rel = CONNECTION_PROFILE_MAP.get(profile_ref.lower())
        if rel:
            path = (PROJECT_ROOT / rel).resolve()
            if path.is_file():
                return path
            alt_path = (PROJECT_ROOT / "backend" / rel).resolve()
            if alt_path.is_file():
                return alt_path
            try:
                from app.config import settings
                if "sqlite" in settings.database_url:
                    clean_url = settings.database_url.replace("sqlite:///", "").replace("sqlite://", "")
                    fpath = Path(clean_url).resolve()
                    if fpath.is_file():
                        return fpath
            except Exception:
                pass

        if profile_ref.endswith(".db") or "/" in profile_ref or "\\" in profile_ref:
            path = (PROJECT_ROOT / profile_ref).resolve()
            if path.is_file():
                return path
        return None

    def validate_definition(
        self,
        definition: DatabaseValidationDefinition,
        context: Optional[Dict[str, Any]] = None
    ) -> ValidationResultDTO:
        if not definition.enabled:
            return ValidationResultDTO(
                validator_type=ValidatorType.DB,
                status=ValidationStatus.INFO,
                severity=ValidationSeverity.INFO,
                message=f"DB validation '{definition.name}' is disabled.",
                definition_id=definition.id,
            )

        context = context or {}
        query = definition.query_template
        for k, v in context.items():
            query = query.replace(f"{{{k}}}", str(v))

        # 1. Enforce strict SQL parser + denylist
        is_safe, reason = is_sql_read_only(query)
        if not is_safe:
            return ValidationResultDTO(
                validator_type=ValidatorType.DB,
                status=ValidationStatus.FAIL,
                severity=ValidationSeverity.CRITICAL,
                message=f"SQL validation rejected: {reason}",
                definition_id=definition.id,
                reason_code="DB_READ_ONLY_VIOLATION"
            )

        # 2. Resolve connection profile
        db_path = self.resolve_db_path(definition.connection_profile_reference)
        if not db_path:
            return ValidationResultDTO(
                validator_type=ValidatorType.DB,
                status=ValidationStatus.BLOCKED,
                severity=ValidationSeverity.CRITICAL,
                message=f"Database connection profile '{definition.connection_profile_reference}' is unavailable.",
                definition_id=definition.id,
                reason_code="DB_UNAVAILABLE"
            )

        query_hash = hashlib.sha256(query.encode("utf-8")).hexdigest()
        start_time = time.time()

        timeout_sec = (definition.timeout_ms or 5000) / 1000.0
        max_rows = definition.max_rows or 100

        # 3. Execute query in read-only mode
        try:
            uri_path = f"{db_path.as_uri()}?mode=ro"
            conn = sqlite3.connect(uri_path, uri=True, timeout=timeout_sec)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query)

            rows = cursor.fetchmany(max_rows + 1)
            conn.close()
        except Exception as exc:
            duration_ms = int((time.time() - start_time) * 1000)
            return ValidationResultDTO(
                validator_type=ValidatorType.DB,
                status=ValidationStatus.BLOCKED,
                severity=ValidationSeverity.CRITICAL,
                message=f"DB query execution failed: {str(exc)}",
                definition_id=definition.id,
                duration_ms=duration_ms,
                reason_code="DB_UNAVAILABLE"
            )

        duration_ms = int((time.time() - start_time) * 1000)

        if len(rows) > max_rows:
            return ValidationResultDTO(
                validator_type=ValidatorType.DB,
                status=ValidationStatus.FAIL,
                severity=ValidationSeverity.SERIOUS,
                message=f"DB query returned row count exceeding max_rows limit ({max_rows}).",
                definition_id=definition.id,
                duration_ms=duration_ms,
                reason_code="DB_ROW_LIMIT_EXCEEDED"
            )

        row_dicts = [dict(row) for row in rows]
        actual_json = {
            "query_hash": query_hash,
            "row_count": len(row_dicts),
            "rows": row_dicts[:10]  # Redacted preview
        }

        # If zero rows returned and expected result is defined or row required
        if not row_dicts:
            return ValidationResultDTO(
                validator_type=ValidatorType.DB,
                status=ValidationStatus.FAIL,
                severity=ValidationSeverity.CRITICAL,
                message=f"DB validation '{definition.name}' failed: Expected record not found in database.",
                definition_id=definition.id,
                actual_json=actual_json,
                duration_ms=duration_ms,
                reason_code="DB_ROW_NOT_FOUND"
            )

        # Compare expected result if provided
        if definition.expected_result_json:
            try:
                expected_dict = json.loads(definition.expected_result_json)
                first_row = row_dicts[0]
                for exp_k, exp_v in expected_dict.items():
                    if exp_k in first_row:
                        actual_val = first_row[exp_k]
                        if str(actual_val) != str(exp_v):
                            return ValidationResultDTO(
                                validator_type=ValidatorType.DB,
                                status=ValidationStatus.FAIL,
                                severity=ValidationSeverity.CRITICAL,
                                message=f"DB column mismatch for '{exp_k}': expected '{exp_v}', got '{actual_val}'",
                                definition_id=definition.id,
                                expected_json=expected_dict,
                                actual_json=actual_json,
                                duration_ms=duration_ms,
                                reason_code="DB_ROW_NOT_FOUND"
                            )
            except json.JSONDecodeError:
                pass

        return ValidationResultDTO(
            validator_type=ValidatorType.DB,
            status=ValidationStatus.PASS,
            severity=ValidationSeverity.INFO,
            message=f"DB validation '{definition.name}' passed ({len(row_dicts)} rows verified in {duration_ms}ms).",
            definition_id=definition.id,
            actual_json=actual_json,
            duration_ms=duration_ms
        )
