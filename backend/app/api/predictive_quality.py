from fastapi import APIRouter, Depends, Query

from app.auth import AuthContext, get_auth_context
from app.ai.predictive_quality import PredictiveQualityEngine

router = APIRouter(prefix='/predictive', tags=['predictive-quality'], dependencies=[Depends(get_auth_context)])


@router.get('/forecast', summary='Get Predictive Quality & Failure Density Forecast')
def get_predictive_forecast(
    project_id: int = Query(1),
    context: AuthContext = Depends(get_auth_context)
):
    engine = PredictiveQualityEngine()
    return engine.generate_quality_forecast(project_id)
