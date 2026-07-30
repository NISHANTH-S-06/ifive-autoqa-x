"""Phase 14 – Enterprise Report Factory V2 API router."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth import get_auth_context, AuthContext
from app.database import get_db
from app.services.report_factory_v2 import ReportFactoryV2

router = APIRouter(prefix='/report-factory', tags=['Phase14-ReportFactory'])


class GenerateReportRequest(BaseModel):
    report_title: str
    report_persona: str
    export_format: str = 'PDF'


@router.post('/generate', status_code=201)
def generate_report(body: GenerateReportRequest, db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return ReportFactoryV2(db).generate_report(body.report_title, body.report_persona, body.export_format)


@router.get('/reports')
def list_reports(persona: str | None = None, db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return ReportFactoryV2(db).list_reports(persona=persona)
