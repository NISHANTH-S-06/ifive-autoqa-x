import hashlib
from typing import Any, Dict, List, Tuple

from app.validation.base import ValidationResultDTO, ValidationStatus


def compute_result_hash(results: List[ValidationResultDTO], overall_status: str) -> str:
    serialized = []
    for r in sorted(results, key=lambda item: (item.validator_type, item.message)):
        serialized.append({
            "type": r.validator_type,
            "status": r.status,
            "severity": r.severity,
            "message": r.message,
            "reason_code": r.reason_code
        })
    payload = {"status": overall_status, "results": serialized}
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()


import json


class ResultAggregator:
    def aggregate(self, results: List[ValidationResultDTO]) -> Tuple[str, List[str], str]:
        """
        Returns (overall_status, reason_codes, result_hash).
        Precedence:
          1. BLOCKED
          2. FAIL
          3. PASS_WITH_WARNINGS
          4. PASS
        """
        statuses = {r.status for r in results}
        reason_codes = list({r.reason_code for r in results if r.reason_code})

        if ValidationStatus.BLOCKED in statuses:
            overall = "BLOCKED"
        elif ValidationStatus.FAIL in statuses:
            overall = "FAIL"
        elif ValidationStatus.WARNING in statuses:
            overall = "PASS_WITH_WARNINGS"
        else:
            overall = "PASS"

        result_hash = compute_result_hash(results, overall)
        return overall, reason_codes, result_hash

    def group_defects(
        self,
        project_id: int,
        source_task_id: str,
        plan_version: int,
        results: List[ValidationResultDTO]
    ) -> List[Dict[str, Any]]:
        """
        Generates defect fingerprints for failed validation results.
        BLOCKED results create NO product defects.
        """
        defects = []
        seen_fingerprints = set()

        for r in results:
            if r.status != ValidationStatus.FAIL:
                continue
            if r.reason_code == "TARGET_UNAVAILABLE" or r.reason_code == "DB_UNAVAILABLE":
                # Dependency / Environment BLOCKED creates no product defect
                continue

            normalized_msg = r.message.split(":")[0].strip()
            raw_fingerprint = f"{project_id}:{source_task_id}:{plan_version}:{r.validator_type}:{r.reason_code or 'UNKNOWN'}:{normalized_msg}"
            fp_hash = hashlib.sha256(raw_fingerprint.encode("utf-8")).hexdigest()

            if fp_hash in seen_fingerprints:
                continue
            seen_fingerprints.add(fp_hash)

            defects.append({
                "fingerprint": fp_hash,
                "project_id": project_id,
                "source_task_id": source_task_id,
                "plan_version": plan_version,
                "validator_type": r.validator_type,
                "reason_code": r.reason_code or "UNCLASSIFIED_FAILURE",
                "severity": r.severity,
                "title": f"[{r.validator_type}] {r.message[:120]}",
                "description": r.message,
                "expected": r.expected_json,
                "actual": r.actual_json,
            })

        return defects
