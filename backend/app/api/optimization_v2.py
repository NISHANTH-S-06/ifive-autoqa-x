"""Phase 14 – Autonomous Optimization Engine V2 & Release Simulation API router."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth import get_auth_context, AuthContext
from app.database import get_db
from app.services.optimization_engine_v2 import OptimizationEngineV2
from app.services.release_simulation import ReleaseSimulationService

router = APIRouter(prefix='/optimization-v2', tags=['Phase14-OptimizationV2'])


class RunSimulationRequest(BaseModel):
    release_version: str


@router.post('/tune', status_code=200)
def run_full_tuning(db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return OptimizationEngineV2(db).run_full_tuning()


@router.get('/history')
def get_history(limit: int = 20, db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return OptimizationEngineV2(db).get_history(limit=limit)


@router.post('/simulation/run', status_code=201)
def run_simulation(body: RunSimulationRequest, db: Session = Depends(get_db), ctx: AuthContext = Depends(get_auth_context)):
    return ReleaseSimulationService(db).run_simulation(body.release_version, simulated_by=ctx.operator.id)


@router.get('/simulation/history')
def list_simulations(release_version: str | None = None, db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return ReleaseSimulationService(db).list_simulations(release_version=release_version)
