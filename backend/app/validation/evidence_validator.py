import hashlib
from typing import Any, Dict, List, Optional

from app.validation.base import BaseValidator, ValidationResultDTO, ValidationSeverity, ValidationStatus, ValidatorType


def compute_manifest_hash(manifest_data: Dict[str, Any]) -> str:
    canonical = json.dumps(manifest_data, sort_keys=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


import json


class EvidenceValidator(BaseValidator):
    def validate_completeness(
        self,
        artifacts_metadata: List[Dict[str, Any]],
        mandatory_types: Optional[List[str]] = None
    ) -> tuple[ValidationResultDTO, Dict[str, Any]]:
        mandatory_types = mandatory_types or ["SCREENSHOT", "SUMMARY"]

        found_types = {art.get("artifact_type") for art in artifacts_metadata if art.get("artifact_type")}
        missing_mandatory = [t for t in mandatory_types if t not in found_types]

        manifest_items = []
        for art in artifacts_metadata:
            art_id = art.get("id")
            art_type = art.get("artifact_type")
            sha256 = art.get("sha256")
            size = art.get("size_bytes", 0)

            # Verification 1: Fake / 1x1 screenshot check
            if art_type == "SCREENSHOT" and size < 50:
                return (
                    ValidationResultDTO(
                        validator_type=ValidatorType.EVIDENCE,
                        status=ValidationStatus.FAIL,
                        severity=ValidationSeverity.CRITICAL,
                        message=f"Evidence verification failed: Screenshot artifact {art_id} is invalid or fake 1x1 image.",
                        reason_code="EVIDENCE_MISSING"
                    ),
                    {}
                )

            # Verification 2: SHA256 integrity check
            if not sha256 or len(sha256) != 64:
                return (
                    ValidationResultDTO(
                        validator_type=ValidatorType.EVIDENCE,
                        status=ValidationStatus.FAIL,
                        severity=ValidationSeverity.CRITICAL,
                        message=f"Evidence verification failed: Artifact {art_id} missing valid SHA-256 signature.",
                        reason_code="EVIDENCE_HASH_MISMATCH"
                    ),
                    {}
                )

            manifest_items.append({
                "id": art_id,
                "type": art_type,
                "filename": art.get("original_filename"),
                "sha256": sha256,
                "size_bytes": size
            })

        if missing_mandatory:
            return (
                ValidationResultDTO(
                    validator_type=ValidatorType.EVIDENCE,
                    status=ValidationStatus.FAIL,
                    severity=ValidationSeverity.CRITICAL,
                    message=f"Evidence completeness validation failed: Missing mandatory artifact types: {', '.join(missing_mandatory)}",
                    reason_code="EVIDENCE_MISSING"
                ),
                {}
            )

        manifest = {
            "artifact_count": len(manifest_items),
            "artifacts": manifest_items,
        }
        manifest_hash = compute_manifest_hash(manifest)
        manifest["manifest_hash"] = manifest_hash

        return (
            ValidationResultDTO(
                validator_type=ValidatorType.EVIDENCE,
                status=ValidationStatus.PASS,
                severity=ValidationSeverity.INFO,
                message=f"Evidence completeness verified ({len(manifest_items)} artifacts verified, manifest SHA-256: {manifest_hash[:12]}...).",
                actual_json=manifest
            ),
            manifest
        )
