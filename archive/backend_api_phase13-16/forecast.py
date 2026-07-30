"""Phase 14 – AI Forecast Center API router."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth import get_auth_context, AuthContext
from app.database import get_db
from app.services.forecast_center import ForecastCenterService

router = APIRouter(prefix='/forecast', tags=['Phase14-Forecast'])


@router.post('/generate', status_code=201)
def generate_forecasts(horizon_days: int = 30, db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return ForecastCenterService(db).generate_forecasts(horizon_days=horizon_days)


@router.get('/metrics')
def list_forecasts(db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return ForecastCenterService(db).list_forecasts()
