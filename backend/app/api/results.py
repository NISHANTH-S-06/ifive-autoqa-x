from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.result_repository import ResultRepository
from app.schemas.result import TestResultRead
from app.auth import AuthContext, get_auth_context
from app.models.test_run import TestRun
from app.services.project_access import ProjectAccessService

router = APIRouter(prefix='/results', tags=['results'], dependencies=[Depends(get_auth_context)])


@router.get('', response_model=list[TestResultRead])
def list_results(run_id: int = Query(..., ge=1), context: AuthContext = Depends(get_auth_context), db: Session = Depends(get_db)):
  run = db.get(TestRun, run_id)
  if run is None:
    return []
  ProjectAccessService(db, context.operator.id).require(run.project_id)
  return ResultRepository(db).list_by_run(run_id)
