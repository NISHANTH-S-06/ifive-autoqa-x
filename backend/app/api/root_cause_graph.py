from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth import AuthContext, get_auth_context
from app.database import get_db
from app.ai.root_cause_graph import AIRootCauseGraphService

router = APIRouter(prefix='/root-cause-graph', tags=['root-cause-graph'], dependencies=[Depends(get_auth_context)])


@router.get('/chain', summary='Get AI Root Cause Dependency Chain')
def get_root_cause_chain(
    defect_id: str = Query('DEF-001'),
    context: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db)
):
    service = AIRootCauseGraphService(db)
    return service.build_root_cause_chain(defect_id)
