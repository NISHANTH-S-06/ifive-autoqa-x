from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any

from app.auth import AuthContext, get_auth_context
from app.services.multi_format_reports import MultiFormatReportEngine

router = APIRouter(prefix='/reports/multi', tags=['multi-reports'], dependencies=[Depends(get_auth_context)])


class MultiReportRequest(BaseModel):
    report_type: str = 'EXECUTIVE'
    export_format: str = 'HTML'
    project_data: Optional[Dict[str, Any]] = {}


@router.post('/generate', summary='Generate Multi-Format Enterprise Report')
def generate_multi_format_report(payload: MultiReportRequest):
    engine = MultiFormatReportEngine()
    return engine.generate_report(payload.report_type, payload.export_format, payload.project_data or {})
