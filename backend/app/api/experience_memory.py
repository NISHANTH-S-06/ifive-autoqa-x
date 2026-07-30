from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth import AuthContext, get_auth_context
from app.database import get_db
from app.ai.experience_memory import AIExperienceMemoryService

router = APIRouter(prefix='/experience-memory', tags=['experience-memory'], dependencies=[Depends(get_auth_context)])


@router.get('/recall', summary='Recall AI Experience Memory Records')
def recall_memory_records(
    experience_type: str = Query('EXECUTION'),
    project_id: int = Query(1),
    context: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db)
):
    service = AIExperienceMemoryService(db)
    return service.recall_experiences(experience_type, project_id)


@router.get('/global-patterns', summary='Get Tenant-Isolated Global QA Patterns')
def get_global_patterns(
    context: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db)
):
    service = AIExperienceMemoryService(db)
    return service.get_global_qa_patterns()
