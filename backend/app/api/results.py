from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.result_repository import ResultRepository
from app.schemas.result import TestResultRead
from app.auth import get_auth_context

router = APIRouter(prefix='/results', tags=['results'], dependencies=[Depends(get_auth_context)])


@router.get('', response_model=list[TestResultRead])
def list_results(run_id: int = Query(..., ge=1), db: Session = Depends(get_db)):
  return ResultRepository(db).list_by_run(run_id)
