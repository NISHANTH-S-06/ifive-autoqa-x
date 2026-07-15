from fastapi import APIRouter, Depends
from app.auth import get_auth_context
from pydantic import BaseModel

router = APIRouter(prefix='/agents', tags=['agents'], dependencies=[Depends(get_auth_context)])


class AgentSuggestionRead(BaseModel):
  id: str
  agent_name: str
  summary: str
  status: str


@router.get('/suggestions', response_model=list[AgentSuggestionRead])
def list_agent_suggestions() -> list[AgentSuggestionRead]:
  return [
    AgentSuggestionRead(
      id='suggestion_001',
      agent_name='Healer Agent',
      summary='Update selector after approved UI label change.',
      status='pending_human_review',
    )
  ]
