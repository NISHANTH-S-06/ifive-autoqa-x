"""Phase 13 – Enterprise Security Center API router."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.auth import get_auth_context, AuthContext
from app.database import get_db
from app.services.enterprise_security_center import EnterpriseSecurityCenterService

router = APIRouter(prefix='/security-center', tags=['Phase13-Security'])


class AddSecretRequest(BaseModel):
    key_name: str
    secret_type: str
    value: str
    rotation_schedule_days: int = Field(default=90, ge=1, le=365)


class RotateSecretRequest(BaseModel):
    new_value: str


@router.get('/vault')
def list_secrets(db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return EnterpriseSecurityCenterService(db).list_secrets()


@router.post('/vault', status_code=201)
def add_secret(
    body: AddSecretRequest,
    db: Session = Depends(get_db),
    ctx: AuthContext = Depends(get_auth_context),
):
    return EnterpriseSecurityCenterService(db).add_secret(
        key_name=body.key_name,
        secret_type=body.secret_type,
        value=body.value,
        rotation_schedule_days=body.rotation_schedule_days,
        created_by=ctx.operator.id,
    )


@router.post('/vault/{entry_id}/rotate')
def rotate_secret(entry_id: int, body: RotateSecretRequest, db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return EnterpriseSecurityCenterService(db).rotate_secret(entry_id, body.new_value)


@router.delete('/vault/{entry_id}')
def delete_secret(entry_id: int, db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return EnterpriseSecurityCenterService(db).delete_secret(entry_id)


@router.get('/dashboard')
def security_dashboard(db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return EnterpriseSecurityCenterService(db).get_security_dashboard()


@router.get('/sso-config')
def sso_config(db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return EnterpriseSecurityCenterService(db).get_sso_config()
