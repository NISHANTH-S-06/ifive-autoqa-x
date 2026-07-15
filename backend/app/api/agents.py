from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import AuthContext, get_auth_context
from app.database import get_db
from app.models.agent_suggestion import AgentSuggestion
from app.services.project_access import ProjectAccessService
from pydantic import BaseModel, ConfigDict

router = APIRouter(prefix='/agents', tags=['agents'], dependencies=[Depends(get_auth_context)])


class AgentSuggestionRead(BaseModel):
  model_config = ConfigDict(from_attributes=True)

  id: int
  agent_name: str
  summary: str
  status: str


@router.get('/suggestions', response_model=list[AgentSuggestionRead])
def list_agent_suggestions(context: AuthContext = Depends(get_auth_context), db: Session = Depends(get_db)) -> list[AgentSuggestionRead]:
  project_ids = ProjectAccessService(db, context.operator.id).project_ids()
  return list(db.scalars(select(AgentSuggestion).where(AgentSuggestion.project_id.in_(project_ids)).order_by(AgentSuggestion.created_at.desc())))
