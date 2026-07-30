from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth import AuthContext, get_auth_context
from app.database import get_db
from app.services.continuous_monitoring import ContinuousMonitoringService

router = APIRouter(prefix='/monitoring', tags=['continuous-monitoring'], dependencies=[Depends(get_auth_context)])


@router.get('/alerts', summary='Get Continuous Autonomous Monitoring Alerts')
def get_monitoring_alerts(
    company_id: int = Query(1),
    context: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db)
):
    service = ContinuousMonitoringService(db)
    return service.get_active_alerts(company_id)
