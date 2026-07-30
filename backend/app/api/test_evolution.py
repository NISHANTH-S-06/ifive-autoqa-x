from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth import AuthContext, get_auth_context
from app.database import get_db
from app.ai.test_evolution import AutonomousTestEvolutionEngine

router = APIRouter(prefix='/test-evolution', tags=['test-evolution'], dependencies=[Depends(get_auth_context)])


@router.post('/evolve', summary='Trigger Autonomous Test Evolution & Deduplication')
def evolve_tests(
    project_id: int = Query(1),
    context: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db)
):
    engine = AutonomousTestEvolutionEngine(db)
    return engine.evolve_test_suite(project_id)
