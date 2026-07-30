"""Phase 15 – Enterprise AI Code Reviewer API router."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth import get_auth_context, AuthContext
from app.database import get_db
from app.services.ai_code_reviewer import AICodeReviewerService

router = APIRouter(prefix='/code-review', tags=['Phase15-CodeReview'])


class ReviewCodeRequest(BaseModel):
    file_path: str
    language: str
    code_snippet: str = ''


@router.post('/analyze', status_code=201)
def review_code(body: ReviewCodeRequest, db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return AICodeReviewerService(db).review_code(body.file_path, body.language, body.code_snippet)


@router.get('/history')
def list_reviews(limit: int = 20, db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return AICodeReviewerService(db).list_reviews(limit=limit)
