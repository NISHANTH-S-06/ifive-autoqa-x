from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.project_repository import ProjectRepository
from app.repositories.run_repository import RunRepository
from app.schemas.dashboard import DashboardSummary
from app.auth import get_auth_context

router = APIRouter(prefix='/dashboard', tags=['dashboard'], dependencies=[Depends(get_auth_context)])


@router.get('/summary', response_model=DashboardSummary)
def dashboard_summary(db: Session = Depends(get_db)):
  projects = ProjectRepository(db)
  runs = RunRepository(db)
  return {
    'total_projects': projects.count(),
    'active_projects': projects.count(active_only=True),
    **runs.summary_counts(),
    'recent_runs': runs.list(limit=10),
  }
