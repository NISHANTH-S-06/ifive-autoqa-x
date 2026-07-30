from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.auth import AuthContext, get_auth_context
from app.database import get_db
from app.models.agent_suggestion import AgentSuggestion
from app.services.project_access import ProjectAccessService
from app.ai.agents.agent_registry import AgentRegistry
from app.ai.agents.orchestrator import AgentOrchestrator

router = APIRouter(prefix='/agents', tags=['agents'], dependencies=[Depends(get_auth_context)])


class AgentSuggestionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    agent_name: str
    summary: str
    status: str

class PipelineRunRequest(BaseModel):
    pipeline_name: str = 'FULL_AUTONOMOUS_QA'
    payload: Dict[str, Any] = {}


@router.get('/suggestions', response_model=list[AgentSuggestionRead])
def list_agent_suggestions(context: AuthContext = Depends(get_auth_context), db: Session = Depends(get_db)) -> list[AgentSuggestionRead]:
    project_ids = ProjectAccessService(db, context.operator.id).project_ids()
    return list(db.scalars(select(AgentSuggestion).where(AgentSuggestion.project_id.in_(project_ids)).order_by(AgentSuggestion.created_at.desc())))


@router.get('/list', summary='List 13 Specialized AI Agents')
def list_specialized_agents():
    registry = AgentRegistry()
    return registry.list_agents()


@router.post('/pipeline/run', summary='Execute Multi-Agent Pipeline')
def run_agent_pipeline(payload: PipelineRunRequest):
    orchestrator = AgentOrchestrator()
    return orchestrator.run_pipeline(payload.pipeline_name, payload.payload)
