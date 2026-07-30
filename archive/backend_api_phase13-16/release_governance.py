"""Phase 13 – Release Governance API router."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth import get_auth_context, AuthContext
from app.database import get_db
from app.services.release_governance import ReleaseGovernanceService

router = APIRouter(prefix='/governance', tags=['Phase13-Governance'])


class CreateWorkflowRequest(BaseModel):
    project_id: int | None = None
    release_version: str


class ApproveRequest(BaseModel):
    approver_name: str
    approver_role: str
    decision: str  # APPROVED | REJECTED | CONDITIONAL
    comments: str = ''
    ip_address: str = '127.0.0.1'


class RollbackRequest(BaseModel):
    project_id: int | None = None
    release_version: str
    requested_by: str
    reason: str


@router.get('/stages')
def list_stages(project_id: int | None = None, release_version: str | None = None, db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return ReleaseGovernanceService(db).list_stages(project_id=project_id, release_version=release_version)


@router.post('/stages', status_code=201)
def create_workflow(body: CreateWorkflowRequest, db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return ReleaseGovernanceService(db).create_workflow(body.project_id, body.release_version)


@router.post('/stages/{stage_id}/approve')
def submit_approval(
    stage_id: int,
    body: ApproveRequest,
    db: Session = Depends(get_db),
    ctx: AuthContext = Depends(get_auth_context),
):
    return ReleaseGovernanceService(db).submit_approval(
        stage_id=stage_id,
        approver_name=body.approver_name,
        approver_role=body.approver_role,
        decision=body.decision,
        comments=body.comments,
        approver_id=ctx.operator.id,
        ip_address=body.ip_address,
    )


@router.get('/audit-trail')
def audit_trail(release_version: str | None = None, db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return ReleaseGovernanceService(db).get_audit_trail(release_version=release_version)


@router.post('/rollback', status_code=201)
def create_rollback(body: RollbackRequest, db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return ReleaseGovernanceService(db).create_rollback_approval(
        body.project_id, body.release_version, body.requested_by, body.reason
    )


@router.get('/status/{release_version}')
def workflow_status(release_version: str, db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return ReleaseGovernanceService(db).get_workflow_status(release_version)
