from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any

from app.auth import AuthContext, get_auth_context
from app.database import get_db
from app.ai.copilot import AICopilotEngine

router = APIRouter(prefix='/copilot', tags=['ai-copilot'], dependencies=[Depends(get_auth_context)])


class CopilotQueryRequest(BaseModel):
    query: str
    context_data: Optional[Dict[str, Any]] = None


@router.post('/query', summary='Query AI Copilot')
def query_copilot(
    payload: CopilotQueryRequest,
    context: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db)
):
    if not payload.query or not payload.query.strip():
        raise HTTPException(status_code=422, detail='Query string is required.')

    engine = AICopilotEngine()
    return engine.answer_query(payload.query, payload.context_data, db)
