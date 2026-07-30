from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth import AuthContext, get_auth_context
from app.database import get_db
from app.services.autonomous_test_lab import AutonomousTestLabService
from app.ai.test_generation_v3 import TestGenerationV3Engine

router = APIRouter(prefix='/test-lab', tags=['autonomous-test-lab'], dependencies=[Depends(get_auth_context)])


@router.post('/provision', summary='Provision Autonomous Browser Farm Workers')
def provision_workers(context: AuthContext = Depends(get_auth_context), db: Session = Depends(get_db)):
    service = AutonomousTestLabService(db)
    return service.provision_workers()


@router.get('/farm-status', summary='Get Browser Farm Worker Status')
def get_farm_status(context: AuthContext = Depends(get_auth_context), db: Session = Depends(get_db)):
    service = AutonomousTestLabService(db)
    return service.get_farm_status()


@router.post('/self-heal', summary='Self-Heal Unhealthy Browser Workers')
def self_heal(context: AuthContext = Depends(get_auth_context), db: Session = Depends(get_db)):
    service = AutonomousTestLabService(db)
    return service.self_heal_workers()


@router.get('/generate-suite', summary='Generate Full 23-Strategy Autonomous Test Suite')
def generate_test_suite(
    project_id: int = Query(1),
    target_url: str = Query('https://app.example.com'),
    context: AuthContext = Depends(get_auth_context),
):
    engine = TestGenerationV3Engine()
    return engine.generate_full_suite(project_id, target_url)


@router.get('/generate-strategy', summary='Generate Tests for a Specific Strategy')
def generate_strategy(
    project_id: int = Query(1),
    strategy: str = Query('SMOKE'),
    context: AuthContext = Depends(get_auth_context),
):
    engine = TestGenerationV3Engine()
    return engine.generate_strategy(project_id, strategy)
