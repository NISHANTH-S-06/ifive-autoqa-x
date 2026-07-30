from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth import AuthContext, get_auth_context
from app.database import get_db
from app.ai.knowledge_graph import KnowledgeGraphService

router = APIRouter(prefix='/knowledge-graph', tags=['knowledge-graph'], dependencies=[Depends(get_auth_context)])


@router.get('/topology', summary='Get Application Knowledge Graph Topology')
def get_topology_graph(
    context: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db)
):
    service = KnowledgeGraphService(db)
    return service.get_topology_graph()
