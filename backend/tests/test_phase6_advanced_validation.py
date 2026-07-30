import json
import pytest
from fastapi import HTTPException

from app.models.advanced_validation import (
    AccessibilityValidationDefinition,
    AdvancedValidationProfile,
    ApiValidationDefinition,
    DatabaseValidationDefinition,
    PerformanceValidationDefinition,
)
from app.models.operator import Operator
from app.models.project import Project
from app.models.test_plan import TestPlan, TestPlanVersion
from app.reporting.advanced_report_service import AdvancedReportService
from app.scheduling.local_schedule_service import LocalScheduleService
from app.validation.accessibility_validator import AccessibilityValidator
from app.validation.api_validator import ApiValidator
from app.validation.base import ValidationSeverity, ValidationStatus, ValidatorType
from app.validation.db_validator import DatabaseValidator, is_sql_read_only
from app.validation.evidence_validator import EvidenceValidator
from app.validation.performance_validator import PerformanceValidator
from app.validation.result_aggregator import ResultAggregator


def test_api_validator_approved_origin_and_external_rejection():
    validator = ApiValidator()

    # Approved origin
    defn_ok = ApiValidationDefinition(
        id=1, name="Test Local", method="GET", path="http://127.0.0.1:8000/api/health", expected_status=200, enabled=True
    )
    # External origin
    defn_ext = ApiValidationDefinition(
        id=2, name="Test External", method="GET", path="http://example.com/api/test", expected_status=200, enabled=True
    )

    res_ext = validator.validate_definition(defn_ext)
    assert res_ext.status == ValidationStatus.BLOCKED
    assert res_ext.reason_code == "TARGET_UNAVAILABLE"
    assert "External or unapproved API origin" in res_ext.message


def test_api_validator_method_not_allowed():
    validator = ApiValidator()
    defn_bad_method = ApiValidationDefinition(
        id=3, name="Bad Method", method="INVALID_METHOD", path="http://127.0.0.1:8000/api/health", expected_status=200, enabled=True
    )
    res = validator.validate_definition(defn_bad_method)
    assert res.status == ValidationStatus.FAIL
    assert res.reason_code == "API_METHOD_NOT_ALLOWED"


def test_db_validator_sql_read_only_parser():
    # Allowed
    ok, _ = is_sql_read_only("SELECT * FROM employees WHERE id = 1")
    assert ok is True

    ok, _ = is_sql_read_only("WITH dept_summary AS (SELECT id FROM departments) SELECT * FROM dept_summary")
    assert ok is True

    # Mutating SQL - Rejected
    for query in [
        "INSERT INTO employees (name) VALUES ('Test')",
        "UPDATE employees SET name = 'Hacked' WHERE id = 1",
        "DELETE FROM employees",
        "DROP TABLE employees",
        "ALTER TABLE employees ADD COLUMN test TEXT",
        "CREATE TABLE test (id INT)",
        "REPLACE INTO employees (id, name) VALUES (1, 'X')",
        "TRUNCATE TABLE employees",
        "ATTACH DATABASE 'other.db' AS aux",
        "PRAGMA user_version = 10",
        "SELECT * FROM employees; DELETE FROM employees;",
        "SELECT * FROM employees -- comment bypass",
        "SELECT * FROM employees /* comment */",
    ]:
        safe, reason = is_sql_read_only(query)
        assert safe is False, f"Query should be rejected: {query} -> {reason}"


def test_db_validator_unavailable_and_missing_row(db, tmp_path):
    validator = DatabaseValidator()

    # Unavailable connection profile reference
    defn_unavail = DatabaseValidationDefinition(
        id=1, name="Missing DB", connection_profile_reference="non_existent_profile",
        query_template="SELECT * FROM test", enabled=True
    )
    res_unavail = validator.validate_definition(defn_unavail)
    assert res_unavail.status == ValidationStatus.BLOCKED
    assert res_unavail.reason_code == "DB_UNAVAILABLE"

    # Create temporary sqlite db to test missing row -> FAIL
    test_db_file = tmp_path / "test_sample.db"
    import sqlite3
    conn = sqlite3.connect(test_db_file)
    conn.execute("CREATE TABLE test_projects (id INT, name TEXT)")
    conn.commit()
    conn.close()

    defn_missing = DatabaseValidationDefinition(
        id=2, name="Missing Row", connection_profile_reference=str(test_db_file),
        query_template="SELECT * FROM test_projects WHERE name = 'NON_EXISTENT_PROJECT_XYZ_999'", enabled=True
    )
    res_missing = validator.validate_definition(defn_missing)
    assert res_missing.status == ValidationStatus.FAIL
    assert res_missing.reason_code == "DB_ROW_NOT_FOUND"


def test_accessibility_validator_severity_mapping():
    validator = AccessibilityValidator()
    defn = AccessibilityValidationDefinition(
        id=1, route="/hr/employees", standard="WCAG21AA", severity_threshold="critical", enabled=True
    )

    scan_data = {
        "violations": [
            {"id": "color-contrast", "impact": "critical", "help": "Elements must have sufficient color contrast", "nodes": [{"html": "<button>"}]},
            {"id": "label", "impact": "moderate", "help": "Form elements must have labels", "nodes": [{"html": "<input>"}]},
        ]
    }

    dtos = validator.validate_scan(defn, scan_data)
    assert len(dtos) == 2
    assert dtos[0].status == ValidationStatus.FAIL
    assert dtos[0].severity == ValidationSeverity.CRITICAL
    assert dtos[0].reason_code == "ACCESSIBILITY_CRITICAL"

    assert dtos[1].status == ValidationStatus.WARNING
    assert dtos[1].severity == ValidationSeverity.MODERATE


def test_performance_validator_thresholds():
    validator = PerformanceValidator()
    defn = PerformanceValidationDefinition(
        id=1, route="/dashboard", metric="navigation_duration", warning_threshold=1000.0, failure_threshold=2000.0, enabled=True
    )

    # Pass case
    dto_pass = validator.validate_metric(defn, {"navigation_duration": 500.0})
    assert dto_pass.status == ValidationStatus.PASS

    # Warning case
    dto_warn = validator.validate_metric(defn, {"navigation_duration": 1500.0})
    assert dto_warn.status == ValidationStatus.WARNING

    # Failure case
    dto_fail = validator.validate_metric(defn, {"navigation_duration": 2500.0})
    assert dto_fail.status == ValidationStatus.FAIL
    assert dto_fail.reason_code == "PERFORMANCE_THRESHOLD_EXCEEDED"

    # Metric unavailable case -> BLOCKED
    dto_unavail = validator.validate_metric(defn, {})
    assert dto_unavail.status == ValidationStatus.BLOCKED
    assert "cannot false PASS" in dto_unavail.message


def test_evidence_validator_fake_screenshot_and_missing_mandatory():
    validator = EvidenceValidator()

    # 1x1 / Fake screenshot rejected
    fake_screenshot_meta = [{"id": 1, "artifact_type": "SCREENSHOT", "original_filename": "screen.png", "sha256": "a" * 64, "size_bytes": 10}]
    dto_fake, _ = validator.validate_completeness(fake_screenshot_meta)
    assert dto_fake.status == ValidationStatus.FAIL
    assert dto_fake.reason_code == "EVIDENCE_MISSING"

    # Valid screenshot & summary metadata
    valid_meta = [
        {"id": 1, "artifact_type": "SCREENSHOT", "original_filename": "screen.png", "sha256": "a" * 64, "size_bytes": 5000},
        {"id": 2, "artifact_type": "SUMMARY", "original_filename": "summary.json", "sha256": "b" * 64, "size_bytes": 300}
    ]
    dto_valid, manifest = validator.validate_completeness(valid_meta)
    assert dto_valid.status == ValidationStatus.PASS
    assert "manifest_hash" in manifest


def test_result_aggregator_precedence_and_defect_grouping():
    aggregator = ResultAggregator()

    from app.validation.base import ValidationResultDTO, ValidationStatus

    r_pass = ValidationResultDTO(validator_type=ValidatorType.API, status=ValidationStatus.PASS, message="OK")
    r_warn = ValidationResultDTO(validator_type=ValidatorType.PERFORMANCE, status=ValidationStatus.WARNING, message="Slow response")
    r_fail = ValidationResultDTO(validator_type=ValidatorType.API, status=ValidationStatus.FAIL, severity=ValidationSeverity.CRITICAL, message="Status mismatch: expected 200 got 500", reason_code="API_STATUS_MISMATCH")
    r_blocked = ValidationResultDTO(validator_type=ValidatorType.DB, status=ValidationStatus.BLOCKED, message="DB unavailable", reason_code="DB_UNAVAILABLE")

    # 1. BLOCKED > FAIL > WARNING > PASS
    status_pass, _, _ = aggregator.aggregate([r_pass])
    assert status_pass == "PASS"

    status_warn, _, _ = aggregator.aggregate([r_pass, r_warn])
    assert status_warn == "PASS_WITH_WARNINGS"

    status_fail, _, _ = aggregator.aggregate([r_pass, r_warn, r_fail])
    assert status_fail == "FAIL"

    status_blocked, _, _ = aggregator.aggregate([r_pass, r_warn, r_fail, r_blocked])
    assert status_blocked == "BLOCKED"

    # 2. Defect grouping: BLOCKED creates NO product defect
    defects = aggregator.group_defects(project_id=1, source_task_id="TASK-01", plan_version=1, results=[r_fail, r_blocked])
    assert len(defects) == 1
    assert defects[0]["reason_code"] == "API_STATUS_MISMATCH"


def test_local_schedule_service_rules(db):
    svc = LocalScheduleService()

    # Require operator & project in db
    proj = Project(name="Schedule Test Project", product_code="SCHED", environment="test", is_active=True)
    db.add(proj)
    op = Operator(username="schedule_admin", display_name="Sched Admin", password_hash="hash", role="ADMIN", is_active=True)
    db.add(op)
    db.commit()

    # Draft plan should be rejected
    draft_plan = TestPlan(
        project_id=proj.id, external_task_import_id=1, source_task_id="TASK-SCHED", source_revision=1,
        plan_code="PLAN-SCHED-DRAFT", title="Draft Plan", status="DRAFT", created_by=op.id
    )

    prof = AdvancedValidationProfile(project_id=proj.id, name="Sched Profile", created_by=op.id)
    db.add(draft_plan)
    db.add(prof)
    db.commit()

    with pytest.raises(HTTPException) as exc_info:
        svc.create_schedule(
            db=db, project_id=proj.id, name="Hourly Audit", cron_expression="0 0 * * *",
            approved_test_plan_id=draft_plan.id, validation_profile_id=prof.id, created_by=op.id
        )
    assert exc_info.value.status_code == 409
    assert "Schedules cannot use draft" in exc_info.value.detail


def test_advanced_report_service():
    report_svc = AdvancedReportService()
    run_dict = {"id": 100, "project_id": 1, "status": "PASS", "result_hash": "a" * 64, "started_at": "2026-07-24T16:00:00"}
    results = [{"validator_type": "API", "status": "PASS", "severity": "INFO", "message": "API check passed", "duration_ms": 45}]
    defects = []

    html = report_svc.generate_html_report(run_dict, results, defects)
    assert "iFive AutoQA X — Advanced QA Validation Report" in html
    assert "API check passed" in html

    pdf_bytes = report_svc.generate_pdf_report(run_dict, results, defects)
    assert pdf_bytes.startswith(b"%PDF-1.4")
    assert b"iFive AutoQA X - Advanced QA Validation Report" in pdf_bytes
