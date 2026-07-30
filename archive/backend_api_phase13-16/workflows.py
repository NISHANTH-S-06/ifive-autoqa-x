"""Phase 14 – Autonomous Workflow Composer API router."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth import get_auth_context, AuthContext
from app.database import get_db
from app.services.workflow_composer import WorkflowComposerService

router = APIRouter(prefix='/workflows', tags=['Phase14-Workflows'])


class CreateTemplateRequest(BaseModel):
    template_name: str
    category: str = 'QA_PIPELINE'
    description: str = ''
    graph_definition: dict[str, Any] = {}


class ExecuteWorkflowRequest(BaseModel):
    template_id: int
    execution_name: str


@router.post('/templates/seed')
def seed_templates(db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return WorkflowComposerService(db).seed_templates()


@router.get('/templates')
def list_templates(db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return WorkflowComposerService(db).list_templates()


@router.post('/templates', status_code=201)
def create_template(body: CreateTemplateRequest, db: Session = Depends(get_db), ctx: AuthContext = Depends(get_auth_context)):
    t = WorkflowComposerService(db).create_template(
        template_name=body.template_name,
        category=body.category,
        description=body.description,
        graph_definition=body.graph_definition,
        created_by=ctx.operator.id,
    )
    return {'id': t.id, 'template_name': t.template_name, 'category': t.category}


@router.post('/execute', status_code=201)
def execute_workflow(body: ExecuteWorkflowRequest, db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return WorkflowComposerService(db).execute_workflow(body.template_id, body.execution_name)


@router.get('/executions')
def list_executions(limit: int = 20, db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return WorkflowComposerService(db).list_executions(limit=limit)
