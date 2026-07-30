from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth import AuthContext, get_auth_context
from app.database import get_db
from app.ai.pattern_recognition import PatternRecognitionEngine

router = APIRouter(prefix='/pattern-recognition', tags=['pattern-recognition'], dependencies=[Depends(get_auth_context)])


@router.get('/analyze', summary='Get Pattern Detection Analysis & Pattern Score')
def analyze_patterns(
    project_id: int = Query(1),
    context: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db)
):
    engine = PatternRecognitionEngine(db)
    return engine.analyze_patterns(project_id)
