"""Phase 14 – Enterprise Knowledge Universe API router."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth import get_auth_context, AuthContext
from app.database import get_db
from app.services.knowledge_universe import KnowledgeUniverseService

router = APIRouter(prefix='/knowledge-universe', tags=['Phase14-KnowledgeUniverse'])


class AddNodeRequest(BaseModel):
    label: str
    node_type: str
    node_key: str | None = None


@router.post('/seed')
def seed_universe(db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return KnowledgeUniverseService(db).seed_universe()


@router.get('/graph')
def get_graph(node_type: str | None = None, db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return KnowledgeUniverseService(db).get_graph(node_type=node_type)


@router.post('/nodes', status_code=201)
def add_node(body: AddNodeRequest, db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    node = KnowledgeUniverseService(db).add_node(body.label, body.node_type, body.node_key)
    return {'id': node.id, 'node_key': node.node_key, 'label': node.label, 'node_type': node.node_type}
