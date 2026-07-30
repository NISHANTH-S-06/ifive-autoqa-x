from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth import AuthContext, get_auth_context
from app.database import get_db
from app.ai.digital_twin import DigitalTwinService

router = APIRouter(prefix='/digital-twin', tags=['digital-twin'], dependencies=[Depends(get_auth_context)])


@router.get('/mirror', summary='Get Digital Twin Application Mirror')
def get_digital_twin_mirror(
    company_id: int = Query(1),
    context: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db)
):
    service = DigitalTwinService(db)
    return service.get_digital_twin_mirror(company_id)
