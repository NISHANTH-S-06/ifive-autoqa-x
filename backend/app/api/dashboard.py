from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.project_repository import ProjectRepository
from app.repositories.run_repository import RunRepository
from app.schemas.dashboard import DashboardSummary
from app.auth import AuthContext, get_auth_context
from app.services.project_access import ProjectAccessService

router = APIRouter(prefix='/dashboard', tags=['dashboard'], dependencies=[Depends(get_auth_context)])


@router.get('/summary', response_model=DashboardSummary)
def dashboard_summary(context: AuthContext = Depends(get_auth_context), db: Session = Depends(get_db)):
  projects = ProjectRepository(db)
  runs = RunRepository(db)
  project_ids = ProjectAccessService(db, context.operator.id).project_ids()
  return {
    'total_projects': projects.count(project_ids=project_ids),
    'active_projects': projects.count(active_only=True, project_ids=project_ids),
    **runs.summary_counts(project_ids=project_ids),
    'recent_runs': runs.list(limit=10, allowed_project_ids=project_ids),
  }
