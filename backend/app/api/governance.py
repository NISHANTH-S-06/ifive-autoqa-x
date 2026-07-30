"""Phase 14 – Enterprise Governance Center API router."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth import get_auth_context, AuthContext
from app.database import get_db
from app.services.governance_center import GovernanceCenterService

router = APIRouter(prefix='/governance-v2', tags=['Phase14-GovernanceV2'])


class CreatePolicyRequest(BaseModel):
    policy_name: str
    policy_type: str
    rules: dict[str, Any] = {}
    is_enforced: bool = True


@router.post('/policies/seed')
def seed_policies(db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return GovernanceCenterService(db).seed_policies()


@router.get('/policies')
def list_policies(policy_type: str | None = None, db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return GovernanceCenterService(db).list_policies(policy_type=policy_type)


@router.post('/policies', status_code=201)
def create_policy(body: CreatePolicyRequest, db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return GovernanceCenterService(db).create_policy(
        policy_name=body.policy_name,
        policy_type=body.policy_type,
        rules=body.rules,
        is_enforced=body.is_enforced,
    )


@router.post('/policies/{policy_id}/toggle')
def toggle_policy(policy_id: int, db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return GovernanceCenterService(db).toggle_policy(policy_id)
