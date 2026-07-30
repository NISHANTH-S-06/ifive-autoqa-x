from fastapi import APIRouter, Depends, Query

from app.auth import AuthContext, get_auth_context
from app.services.autonomous_monitoring_v2 import AutonomousMonitoringV2Service

router = APIRouter(prefix='/monitoring-v2', tags=['autonomous-monitoring-v2'], dependencies=[Depends(get_auth_context)])


@router.get('/run-pass', summary='Execute Autonomous Monitoring 2.0 Check Pass')
def run_monitoring_v2_pass(
    target_url: str = Query('https://app.example.com'),
    context: AuthContext = Depends(get_auth_context)
):
    service = AutonomousMonitoringV2Service()
    return service.run_monitoring_pass(target_url)
