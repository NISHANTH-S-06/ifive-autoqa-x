from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.auth import AuthContext, get_auth_context
from app.database import get_db
from app.services.release_war_room import ReleaseWarRoomService
from app.ai.root_cause_engine_v2 import RootCauseEngineV2

router = APIRouter(prefix='/war-room', tags=['release-war-room'], dependencies=[Depends(get_auth_context)])


@router.get('/metrics', summary='Enterprise Release War Room – Single Pane Executive View')
def get_war_room(context: AuthContext = Depends(get_auth_context), db: Session = Depends(get_db)):
    service = ReleaseWarRoomService(db)
    return service.get_war_room_metrics()


@router.post('/root-cause-v2', summary='AI Root Cause Engine V2 – 9-Layer Correlation')
def analyze_root_cause(
    defect_key: str = Query('DEF-001'),
    context_data: Dict[str, Any] = Body({}, embed=True),
    context: AuthContext = Depends(get_auth_context),
):
    engine = RootCauseEngineV2()
    return engine.analyze(defect_key, context_data)
