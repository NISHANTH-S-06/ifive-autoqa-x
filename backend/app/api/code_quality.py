"""Phase 16 API Router: AI Code Quality Governor."""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.code_quality_governor import CodeQualityGovernorService

code_quality_router = APIRouter(prefix="/api/code-quality", tags=["Code Quality"])

class CodeScanRequest(BaseModel):
    file_path: str
    language: str
    code_snippet: str

@code_quality_router.post("/seed")
def seed_code_quality(db: Session = Depends(get_db)):
    return CodeQualityGovernorService(db).seed_violations()

@code_quality_router.get("/violations")
def list_code_violations(
    language: Optional[str] = Query(None), category: Optional[str] = Query(None), db: Session = Depends(get_db)
):
    service = CodeQualityGovernorService(db)
    service.seed_violations()
    return service.fetch_violations(language=language, category=category)

@code_quality_router.post("/scan")
def scan_code(body: CodeScanRequest, db: Session = Depends(get_db)):
    return CodeQualityGovernorService(db).scan_code_file(
        file_path=body.file_path, language=body.language, code_snippet=body.code_snippet
    )
