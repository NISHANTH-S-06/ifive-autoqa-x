import json
from datetime import datetime
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import AuthContext, get_auth_context, require_csrf
from app.database import get_db
from app.models.advanced_validation import (
    AccessibilityValidationDefinition,
    AdvancedValidationProfile,
    AdvancedValidationResult,
    AdvancedValidationRun,
    ApiValidationDefinition,
    DatabaseValidationDefinition,
    PerformanceValidationDefinition,
)
from app.models.automated_execution import AutomatedRun, ExecutionArtifact
from app.models.test_plan import TestPlan, TestPlanVersion
from app.reporting.advanced_report_service import AdvancedReportService
from app.validation.accessibility_validator import AccessibilityValidator
from app.validation.api_validator import ApiValidator
from app.validation.base import ValidationResultDTO, ValidationSeverity, ValidationStatus, ValidatorType
from app.validation.db_validator import DatabaseValidator
from app.validation.evidence_validator import EvidenceValidator
from app.validation.performance_validator import PerformanceValidator
from app.validation.result_aggregator import ResultAggregator

router = APIRouter(tags=['advanced-validation'])


class CreateProfileRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: Optional[str] = None
    enabled: bool = True
    api_validation_enabled: bool = True
    db_validation_enabled: bool = True
    accessibility_enabled: bool = False
    performance_enabled: bool = False
    console_network_enabled: bool = True
    evidence_completeness_enabled: bool = True


class ApiDefinitionRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    method: str = Field(default="GET")
    path: str = Field(min_length=1, max_length=255)
    request_headers_template: Optional[str] = None
    request_body_template: Optional[str] = None
    expected_status: int = 200
    expected_schema_json: Optional[str] = None
    expected_json_paths: Optional[str] = None
    timeout_ms: int = 5000
    auth_profile_reference: Optional[str] = None
    enabled: bool = True


class DbDefinitionRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    connection_profile_reference: str = Field(min_length=1, max_length=100)
    query_template: str = Field(min_length=1)
    expected_result_json: Optional[str] = None
    timeout_ms: int = 5000
    max_rows: int = 100
    enabled: bool = True


class AccessibilityDefinitionRequest(BaseModel):
    route: str = Field(min_length=1, max_length=255)
    standard: str = Field(default="WCAG21AA")
    severity_threshold: str = Field(default="critical")
    include_rules: Optional[str] = None
    exclude_rules: Optional[str] = None
    enabled: bool = True


class PerformanceDefinitionRequest(BaseModel):
    route: str = Field(min_length=1, max_length=255)
    metric: str = Field(min_length=1, max_length=50)
    warning_threshold: float
    failure_threshold: float
    sample_count: int = 1
    enabled: bool = True


class TriggerRunRequest(BaseModel):
    test_plan_id: int
    validation_profile_id: int
    automated_run_id: Optional[int] = None
    captured_metrics: Optional[Dict[str, Any]] = None
    accessibility_scans: Optional[Dict[str, Any]] = None
    console_errors: Optional[List[str]] = None
    network_errors: Optional[List[Dict[str, Any]]] = None


@router.post('/projects/{project_id}/advanced-profiles', status_code=201)
def create_profile(
    project_id: int,
    payload: CreateProfileRequest,
    context: AuthContext = Depends(require_csrf),
    db: Session = Depends(get_db)
):
    profile = AdvancedValidationProfile(
        project_id=project_id,
        name=payload.name,
        description=payload.description,
        enabled=payload.enabled,
        api_validation_enabled=payload.api_validation_enabled,
        db_validation_enabled=payload.db_validation_enabled,
        accessibility_enabled=payload.accessibility_enabled,
        performance_enabled=payload.performance_enabled,
        console_network_enabled=payload.console_network_enabled,
        evidence_completeness_enabled=payload.evidence_completeness_enabled,
        created_by=context.operator.id
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


@router.get('/projects/{project_id}/advanced-profiles')
def list_profiles(
    project_id: int,
    context: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db)
):
    return db.scalars(select(AdvancedValidationProfile).where(AdvancedValidationProfile.project_id == project_id)).all()


@router.get('/projects/{project_id}/advanced-profiles/{profile_id}')
def get_profile_detail(
    project_id: int,
    profile_id: int,
    context: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db)
):
    prof = db.get(AdvancedValidationProfile, profile_id)
    if not prof or prof.project_id != project_id:
        raise HTTPException(status_code=404, detail="Profile not found.")
    return {
        "profile": prof,
        "api_definitions": prof.api_definitions,
        "db_definitions": prof.db_definitions,
        "accessibility_definitions": prof.accessibility_definitions,
        "performance_definitions": prof.performance_definitions
    }


@router.post('/projects/{project_id}/advanced-profiles/{profile_id}/api-definitions', status_code=201)
def add_api_definition(
    project_id: int,
    profile_id: int,
    payload: ApiDefinitionRequest,
    context: AuthContext = Depends(require_csrf),
    db: Session = Depends(get_db)
):
    prof = db.get(AdvancedValidationProfile, profile_id)
    if not prof or prof.project_id != project_id:
        raise HTTPException(status_code=404, detail="Profile not found.")

    item = ApiValidationDefinition(
        validation_profile_id=prof.id,
        name=payload.name,
        method=payload.method,
        path=payload.path,
        request_headers_template=payload.request_headers_template,
        request_body_template=payload.request_body_template,
        expected_status=payload.expected_status,
        expected_schema_json=payload.expected_schema_json,
        expected_json_paths=payload.expected_json_paths,
        timeout_ms=payload.timeout_ms,
        auth_profile_reference=payload.auth_profile_reference,
        enabled=payload.enabled
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.post('/projects/{project_id}/advanced-profiles/{profile_id}/db-definitions', status_code=201)
def add_db_definition(
    project_id: int,
    profile_id: int,
    payload: DbDefinitionRequest,
    context: AuthContext = Depends(require_csrf),
    db: Session = Depends(get_db)
):
    prof = db.get(AdvancedValidationProfile, profile_id)
    if not prof or prof.project_id != project_id:
        raise HTTPException(status_code=404, detail="Profile not found.")

    item = DatabaseValidationDefinition(
        validation_profile_id=prof.id,
        name=payload.name,
        connection_profile_reference=payload.connection_profile_reference,
        query_template=payload.query_template,
        expected_result_json=payload.expected_result_json,
        timeout_ms=payload.timeout_ms,
        max_rows=payload.max_rows,
        enabled=payload.enabled
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.post('/projects/{project_id}/advanced-profiles/{profile_id}/accessibility-definitions', status_code=201)
def add_accessibility_definition(
    project_id: int,
    profile_id: int,
    payload: AccessibilityDefinitionRequest,
    context: AuthContext = Depends(require_csrf),
    db: Session = Depends(get_db)
):
    prof = db.get(AdvancedValidationProfile, profile_id)
    if not prof or prof.project_id != project_id:
        raise HTTPException(status_code=404, detail="Profile not found.")

    item = AccessibilityValidationDefinition(
        validation_profile_id=prof.id,
        route=payload.route,
        standard=payload.standard,
        severity_threshold=payload.severity_threshold,
        include_rules=payload.include_rules,
        exclude_rules=payload.exclude_rules,
        enabled=payload.enabled
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.post('/projects/{project_id}/advanced-profiles/{profile_id}/performance-definitions', status_code=201)
def add_performance_definition(
    project_id: int,
    profile_id: int,
    payload: PerformanceDefinitionRequest,
    context: AuthContext = Depends(require_csrf),
    db: Session = Depends(get_db)
):
    prof = db.get(AdvancedValidationProfile, profile_id)
    if not prof or prof.project_id != project_id:
        raise HTTPException(status_code=404, detail="Profile not found.")

    item = PerformanceValidationDefinition(
        validation_profile_id=prof.id,
        route=payload.route,
        metric=payload.metric,
        warning_threshold=payload.warning_threshold,
        failure_threshold=payload.failure_threshold,
        sample_count=payload.sample_count,
        enabled=payload.enabled
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.post('/projects/{project_id}/advanced-runs/trigger', status_code=201)
def trigger_advanced_run(
    project_id: int,
    payload: TriggerRunRequest,
    context: AuthContext = Depends(require_csrf),
    db: Session = Depends(get_db)
):
    plan = db.get(TestPlan, payload.test_plan_id)
    if not plan or plan.project_id != project_id:
        raise HTTPException(status_code=404, detail="Test plan not found.")
    if plan.status != "APPROVED" or not plan.approved_version_number:
        raise HTTPException(status_code=409, detail="Only approved test plans can be executed.")

    version = db.scalar(select(TestPlanVersion).where(TestPlanVersion.test_plan_id == plan.id, TestPlanVersion.version_number == plan.approved_version_number))
    if not version:
        raise HTTPException(status_code=409, detail="Approved test plan version missing.")

    profile = db.get(AdvancedValidationProfile, payload.validation_profile_id)
    if not profile or profile.project_id != project_id:
        raise HTTPException(status_code=404, detail="Validation profile not found.")

    run = AdvancedValidationRun(
        project_id=project_id,
        automated_run_id=payload.automated_run_id,
        test_plan_id=plan.id,
        test_plan_version_id=version.id,
        validation_profile_id=profile.id,
        status="RUNNING",
        started_at=datetime.utcnow()
    )
    db.add(run)
    db.flush()

    validation_dtos: List[ValidationResultDTO] = []
    correlation_context = {"run_id": run.id}

    # 1. API Validation
    if profile.api_validation_enabled:
        api_val = ApiValidator()
        for api_def in profile.api_definitions:
            dto = api_val.validate_definition(api_def, context=correlation_context)
            validation_dtos.append(dto)

    # 2. Read-Only DB Validation
    if profile.db_validation_enabled:
        db_val = DatabaseValidator()
        for db_def in profile.db_definitions:
            dto = db_val.validate_definition(db_def, context=correlation_context)
            validation_dtos.append(dto)

    # 3. Accessibility Validation
    if profile.accessibility_enabled:
        acc_val = AccessibilityValidator()
        scans = payload.accessibility_scans or {}
        for acc_def in profile.accessibility_definitions:
            scan_data = scans.get(acc_def.route, {"violations": []})
            dtos = acc_val.validate_scan(acc_def, scan_data)
            validation_dtos.extend(dtos)

    # 4. Performance Validation
    if profile.performance_enabled:
        perf_val = PerformanceValidator()
        metrics = payload.captured_metrics or {}
        for perf_def in profile.performance_definitions:
            dto = perf_val.validate_metric(perf_def, metrics)
            validation_dtos.append(dto)

    # 5. Console & Network Analysis
    if profile.console_network_enabled:
        if payload.console_errors:
            for err in payload.console_errors:
                validation_dtos.append(ValidationResultDTO(
                    validator_type=ValidatorType.CONSOLE_NETWORK,
                    status=ValidationStatus.FAIL,
                    severity=ValidationSeverity.CRITICAL,
                    message=f"Console error detected: {err}",
                    reason_code="CONSOLE_UNCAUGHT_EXCEPTION"
                ))

        if payload.network_errors:
            for nerr in payload.network_errors:
                status_code = nerr.get("status", 500)
                url = nerr.get("url", "")
                if status_code >= 500:
                    validation_dtos.append(ValidationResultDTO(
                        validator_type=ValidatorType.CONSOLE_NETWORK,
                        status=ValidationStatus.FAIL,
                        severity=ValidationSeverity.CRITICAL,
                        message=f"Network HTTP {status_code} server error on {url}",
                        reason_code="NETWORK_5XX"
                    ))
                elif status_code >= 400 and not nerr.get("expected_negative"):
                    validation_dtos.append(ValidationResultDTO(
                        validator_type=ValidatorType.CONSOLE_NETWORK,
                        status=ValidationStatus.WARNING,
                        severity=ValidationSeverity.MODERATE,
                        message=f"Unexpected network HTTP {status_code} on {url}",
                        reason_code="API_STATUS_MISMATCH"
                    ))

    # 6. Evidence Completeness
    if profile.evidence_completeness_enabled:
        ev_val = EvidenceValidator()
        artifacts = []
        if payload.automated_run_id:
            arts = db.scalars(select(ExecutionArtifact).where(ExecutionArtifact.run_id == payload.automated_run_id)).all()
            artifacts = [
                {"id": a.id, "artifact_type": a.artifact_type, "original_filename": a.original_filename, "sha256": a.sha256, "size_bytes": a.size_bytes}
                for a in arts
            ]
        ev_dto, _ = ev_val.validate_completeness(artifacts)
        validation_dtos.append(ev_dto)

    # 7. Unified Result Aggregation & Defect Grouping
    aggregator = ResultAggregator()
    overall_status, reason_codes, result_hash = aggregator.aggregate(validation_dtos)
    defects = aggregator.group_defects(project_id, plan.source_task_id, version.version_number, validation_dtos)

    run.status = overall_status
    run.completed_at = datetime.utcnow()
    run.summary_json = json.dumps({
        "reason_codes": reason_codes,
        "results_count": len(validation_dtos),
        "defects_count": len(defects),
        "defects": defects
    })
    run.result_hash = result_hash

    # Save detailed results to DB
    for dto in validation_dtos:
        db_res = AdvancedValidationResult(
            advanced_validation_run_id=run.id,
            validator_type=dto.validator_type.value,
            definition_id=dto.definition_id,
            status=dto.status.value,
            severity=dto.severity.value,
            expected_json=json.dumps(dto.expected_json) if dto.expected_json else None,
            actual_json=json.dumps(dto.actual_json) if dto.actual_json else None,
            message=dto.message,
            duration_ms=dto.duration_ms,
            artifact_ids=json.dumps(dto.artifact_ids) if dto.artifact_ids else None
        )
        db.add(db_res)

    db.commit()
    db.refresh(run)
    return run


@router.get('/advanced-runs/{run_id}')
def get_advanced_run(
    run_id: int,
    context: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db)
):
    run = db.get(AdvancedValidationRun, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Advanced run not found.")
    return run


@router.get('/advanced-runs/{run_id}/results')
def get_advanced_run_results(
    run_id: int,
    context: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db)
):
    return db.scalars(select(AdvancedValidationResult).where(AdvancedValidationResult.advanced_validation_run_id == run_id)).all()


@router.get('/advanced-runs/{run_id}/evidence-manifest')
def get_evidence_manifest(
    run_id: int,
    context: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db)
):
    run = db.get(AdvancedValidationRun, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Advanced run not found.")

    artifacts = []
    if run.automated_run_id:
        arts = db.scalars(select(ExecutionArtifact).where(ExecutionArtifact.run_id == run.automated_run_id)).all()
        artifacts = [
            {"id": a.id, "artifact_type": a.artifact_type, "original_filename": a.original_filename, "sha256": a.sha256, "size_bytes": a.size_bytes}
            for a in arts
        ]

    ev_val = EvidenceValidator()
    _, manifest = ev_val.validate_completeness(artifacts)
    return manifest


@router.get('/advanced-runs/{run_id}/report/html')
def get_html_report(
    run_id: int,
    context: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db)
):
    run = db.get(AdvancedValidationRun, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Advanced run not found.")

    results_db = db.scalars(select(AdvancedValidationResult).where(AdvancedValidationResult.advanced_validation_run_id == run_id)).all()
    results_list = [
        {
            "validator_type": r.validator_type,
            "status": r.status,
            "severity": r.severity,
            "message": r.message,
            "duration_ms": r.duration_ms
        }
        for r in results_db
    ]

    summary = json.loads(run.summary_json or "{}")
    defects = summary.get("defects", [])

    run_dict = {
        "id": run.id,
        "project_id": run.project_id,
        "automated_run_id": run.automated_run_id,
        "test_plan_version_id": run.test_plan_version_id,
        "status": run.status,
        "started_at": run.started_at.isoformat(),
        "completed_at": run.completed_at.isoformat() if run.completed_at else None,
        "result_hash": run.result_hash
    }

    report_svc = AdvancedReportService()
    html_content = report_svc.generate_html_report(run_dict, results_list, defects)
    return Response(content=html_content, media_type="text/html")


@router.get('/advanced-runs/{run_id}/report/pdf')
def get_pdf_report(
    run_id: int,
    context: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db)
):
    run = db.get(AdvancedValidationRun, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Advanced run not found.")

    results_db = db.scalars(select(AdvancedValidationResult).where(AdvancedValidationResult.advanced_validation_run_id == run_id)).all()
    results_list = [
        {
            "validator_type": r.validator_type,
            "status": r.status,
            "severity": r.severity,
            "message": r.message,
            "duration_ms": r.duration_ms
        }
        for r in results_db
    ]

    summary = json.loads(run.summary_json or "{}")
    defects = summary.get("defects", [])

    run_dict = {
        "id": run.id,
        "project_id": run.project_id,
        "automated_run_id": run.automated_run_id,
        "test_plan_version_id": run.test_plan_version_id,
        "status": run.status,
        "started_at": run.started_at.isoformat(),
        "completed_at": run.completed_at.isoformat() if run.completed_at else None,
        "result_hash": run.result_hash
    }

    report_svc = AdvancedReportService()
    pdf_bytes = report_svc.generate_pdf_report(run_dict, results_list, defects)
    return Response(content=pdf_bytes, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=advanced_run_{run.id}_report.pdf"})
