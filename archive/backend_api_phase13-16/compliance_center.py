"""Phase 13 – Compliance Center API router."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth import get_auth_context, AuthContext
from app.database import get_db
from app.services.compliance_center import ComplianceCenterService

router = APIRouter(prefix='/compliance', tags=['Phase13-Compliance'])


class GenerateReportRequest(BaseModel):
    compliance_standard: str
    scope: str = 'PLATFORM'


@router.get('/standards')
def get_standards(db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return ComplianceCenterService(db).get_supported_standards()


@router.get('/reports')
def list_reports(db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return ComplianceCenterService(db).list_reports()


@router.post('/reports/generate', status_code=201)
def generate_report(
    body: GenerateReportRequest,
    db: Session = Depends(get_db),
    ctx: AuthContext = Depends(get_auth_context),
):
    report = ComplianceCenterService(db).generate_report(
        compliance_standard=body.compliance_standard,
        scope=body.scope,
        generated_by=ctx.operator.id,
    )
    return {
        'id': report.id,
        'compliance_standard': report.compliance_standard,
        'compliance_score': report.compliance_score,
        'report_status': report.report_status,
    }


@router.get('/dashboard')
def compliance_dashboard(db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return ComplianceCenterService(db).get_dashboard()
