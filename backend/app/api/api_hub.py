"""Phase 13 – Enterprise API Hub router."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.auth import get_auth_context, AuthContext
from app.database import get_db
from app.services.api_hub import APIHubService

router = APIRouter(prefix='/hub', tags=['Phase13-APIHub'])


class CreateKeyRequest(BaseModel):
    key_name: str
    sdk_type: str = 'REST'
    rate_limit_rpm: int = Field(default=1000, ge=1)
    permissions: list[str] = ['READ']
    expires_days: int | None = None


class RegisterWebhookRequest(BaseModel):
    webhook_name: str
    target_url: str
    event_types: list[str] = ['ALL']


class VerifyKeyRequest(BaseModel):
    raw_key: str


@router.get('/keys')
def list_keys(db: Session = Depends(get_db), ctx: AuthContext = Depends(get_auth_context)):
    return APIHubService(db).list_keys(created_by=ctx.operator.id)


@router.post('/keys', status_code=201)
def create_key(body: CreateKeyRequest, db: Session = Depends(get_db), ctx: AuthContext = Depends(get_auth_context)):
    return APIHubService(db).create_key(
        key_name=body.key_name,
        sdk_type=body.sdk_type,
        rate_limit_rpm=body.rate_limit_rpm,
        permissions=body.permissions,
        created_by=ctx.operator.id,
        expires_days=body.expires_days,
    )


@router.delete('/keys/{key_id}')
def revoke_key(key_id: int, db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return APIHubService(db).revoke_key(key_id)


@router.post('/keys/verify')
def verify_key(body: VerifyKeyRequest, db: Session = Depends(get_db)):
    return APIHubService(db).verify_key(body.raw_key)


@router.get('/webhooks')
def list_webhooks(db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return APIHubService(db).list_webhooks()


@router.post('/webhooks', status_code=201)
def register_webhook(body: RegisterWebhookRequest, db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return APIHubService(db).register_webhook(
        webhook_name=body.webhook_name,
        target_url=body.target_url,
        event_types=body.event_types,
    )


@router.delete('/webhooks/{webhook_id}')
def delete_webhook(webhook_id: int, db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return APIHubService(db).delete_webhook(webhook_id)


@router.get('/sdks')
def get_sdks(db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return APIHubService(db).get_sdk_info()
