"""Phase 13 – Enterprise DevOps API router."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth import get_auth_context, AuthContext
from app.database import get_db
from app.services.enterprise_devops import EnterpriseDevOpsService

router = APIRouter(prefix='/devops', tags=['Phase13-DevOps'])


class CreatePipelineRequest(BaseModel):
    pipeline_name: str
    ci_tool: str
    repo_url: str = ''
    branch: str = 'main'
    project_id: int | None = None
    config: dict[str, Any] = {}


class CompletePipelineRequest(BaseModel):
    success: bool = True
    duration_ms: int = 0


@router.get('/tools')
def supported_tools(db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return EnterpriseDevOpsService(db).get_supported_tools()


@router.get('/pipelines')
def list_pipelines(project_id: int | None = None, db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return EnterpriseDevOpsService(db).list_pipelines(project_id=project_id)


@router.post('/pipelines', status_code=201)
def create_pipeline(body: CreatePipelineRequest, db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    p = EnterpriseDevOpsService(db).create_pipeline(
        pipeline_name=body.pipeline_name,
        ci_tool=body.ci_tool,
        repo_url=body.repo_url,
        branch=body.branch,
        project_id=body.project_id,
        config=body.config,
    )
    return {'id': p.id, 'pipeline_name': p.pipeline_name, 'ci_tool': p.ci_tool, 'pipeline_status': p.pipeline_status}


@router.get('/pipelines/{pipeline_id}/status')
def pipeline_status(pipeline_id: int, db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return EnterpriseDevOpsService(db).get_pipeline_status(pipeline_id)


@router.post('/pipelines/{pipeline_id}/trigger')
def trigger_pipeline(pipeline_id: int, db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return EnterpriseDevOpsService(db).trigger_pipeline(pipeline_id)


@router.post('/pipelines/{pipeline_id}/complete')
def complete_pipeline(pipeline_id: int, body: CompletePipelineRequest, db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return EnterpriseDevOpsService(db).complete_pipeline(pipeline_id, body.success, body.duration_ms)


@router.delete('/pipelines/{pipeline_id}')
def delete_pipeline(pipeline_id: int, db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return EnterpriseDevOpsService(db).delete_pipeline(pipeline_id)
