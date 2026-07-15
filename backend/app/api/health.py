from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.diagnostics import health_snapshot


router = APIRouter(tags=['health'])


@router.get('/health')
def health_check(db: Session = Depends(get_db)) -> dict:
  return health_snapshot(db)

