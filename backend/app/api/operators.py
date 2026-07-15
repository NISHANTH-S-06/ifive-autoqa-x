from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import AuthContext, require_csrf, require_roles
from app.database import get_db
from app.models.operator import Operator
from app.models.operator_session import OperatorSession
from app.repositories.operator_repository import OperatorRepository
from app.schemas.auth import AdminPasswordResetRequest, OperatorCreate, OperatorRead, OperatorRoleUpdate, OperatorSessionRead, OperatorStatusUpdate, SessionRevokeRequest
from app.services.audit_service import append_event
from app.services.operator_security import add_password_history, password_expiry_from, recent_password_reused, revoke_operator_sessions, safe_session_payload
from app.services.password_service import hash_password, normalize_username, validate_password

router = APIRouter(prefix='/operators', tags=['operators'])


def admin_csrf(context: AuthContext = Depends(require_csrf)):
  if context.operator.role != 'ADMIN': raise HTTPException(status_code=403, detail='You do not have permission to perform this action.')
  return context


@router.get('', response_model=list[OperatorRead])
def list_operators(context: AuthContext = Depends(require_roles('ADMIN')), db: Session = Depends(get_db)): return OperatorRepository(db).list()


@router.post('', response_model=OperatorRead, status_code=201)
def create_operator(payload: OperatorCreate, context: AuthContext = Depends(admin_csrf), db: Session = Depends(get_db)):
  try: username = normalize_username(payload.username); validate_password(payload.temporary_password, username, payload.display_name)
  except ValueError as exc: raise HTTPException(status_code=400, detail=str(exc)) from None
  repository = OperatorRepository(db)
  if repository.by_username(username): raise HTTPException(status_code=409, detail='An operator with this username already exists.')
  now = datetime.utcnow()
  operator = Operator(username=username, display_name=payload.display_name.strip(), password_hash=hash_password(payload.temporary_password), role=payload.role.value, must_change_password=True, password_version=1, force_password_change_reason='BOOTSTRAP', credentials_updated_at=now, password_expires_at=password_expiry_from(now))
  db.add(operator); db.flush(); add_password_history(db, operator, context.operator.id, 'BOOTSTRAP', now); append_event(db, 'OPERATOR_CREATED', operator_id=context.operator.id, resource_type='OPERATOR', resource_id=str(operator.id), metadata={'username': username, 'role': operator.role}); db.commit(); db.refresh(operator); return operator


@router.patch('/{operator_id}/status', response_model=OperatorRead)
def update_status(operator_id: int, payload: OperatorStatusUpdate, context: AuthContext = Depends(admin_csrf), db: Session = Depends(get_db)):
  operator = OperatorRepository(db).get(operator_id)
  if not operator: raise HTTPException(status_code=404, detail='Operator not found.')
  if operator.id == context.operator.id and not payload.is_active: raise HTTPException(status_code=400, detail='You cannot deactivate your own account.')
  operator.is_active = payload.is_active; action = 'OPERATOR_ACTIVATED' if payload.is_active else 'OPERATOR_DEACTIVATED'; append_event(db, action, operator_id=context.operator.id, resource_type='OPERATOR', resource_id=str(operator.id)); db.commit(); db.refresh(operator); return operator


@router.patch('/{operator_id}/role', response_model=OperatorRead)
def update_role(operator_id: int, payload: OperatorRoleUpdate, context: AuthContext = Depends(admin_csrf), db: Session = Depends(get_db)):
  repository = OperatorRepository(db); operator = repository.get(operator_id)
  if not operator: raise HTTPException(status_code=404, detail='Operator not found.')
  if operator.role == 'ADMIN' and payload.role.value != 'ADMIN' and operator.is_active and repository.active_admin_count() <= 1: raise HTTPException(status_code=400, detail='The final active ADMIN role cannot be removed.')
  old = operator.role; operator.role = payload.role.value; append_event(db, 'OPERATOR_ROLE_CHANGED', operator_id=context.operator.id, resource_type='OPERATOR', resource_id=str(operator.id), metadata={'old_role': old, 'new_role': operator.role}); db.commit(); db.refresh(operator); return operator


@router.post('/{operator_id}/reset-password')
def reset_password(operator_id: int, payload: AdminPasswordResetRequest, context: AuthContext = Depends(admin_csrf), db: Session = Depends(get_db)):
  operator = OperatorRepository(db).get(operator_id)
  if not operator:
    raise HTTPException(status_code=404, detail='Operator not found.')
  if operator.id == context.operator.id:
    raise HTTPException(status_code=400, detail='ADMIN cannot reset their own password through this endpoint.')
  reason = payload.reason.strip()
  if not reason:
    raise HTTPException(status_code=400, detail='Reset reason is required.')
  if payload.temporary_password != payload.confirm_temporary_password:
    raise HTTPException(status_code=400, detail='Temporary password and confirmation password do not match.')
  try:
    validate_password(payload.temporary_password, operator.username, operator.display_name)
  except ValueError as exc:
    raise HTTPException(status_code=400, detail=str(exc)) from None
  if recent_password_reused(db, operator, payload.temporary_password):
    append_event(db, 'PASSWORD_REUSE_BLOCKED', 'DENIED', context.operator.id, resource_type='OPERATOR', resource_id=str(operator.id))
    db.commit()
    raise HTTPException(status_code=400, detail='This password was used recently. Choose a different password.')
  now = datetime.utcnow()
  operator.password_version += 1
  operator.password_hash = hash_password(payload.temporary_password)
  operator.must_change_password = True
  operator.force_password_change_reason = 'ADMIN_RESET'
  operator.credentials_updated_at = now
  operator.password_expires_at = password_expiry_from(now)
  add_password_history(db, operator, context.operator.id, 'ADMIN_RESET', now)
  revoked = revoke_operator_sessions(db, operator.id, context.operator.id, reason)
  append_event(db, 'OPERATOR_PASSWORD_RESET', operator_id=context.operator.id, resource_type='OPERATOR', resource_id=str(operator.id), metadata={'reason': reason, 'revoked_sessions': revoked})
  db.commit()
  return {'message': 'Operator password reset. Password change is required at next login.'}


@router.get('/{operator_id}/sessions', response_model=list[OperatorSessionRead])
def list_operator_sessions(operator_id: int, context: AuthContext = Depends(require_roles('ADMIN')), db: Session = Depends(get_db)):
  operator = OperatorRepository(db).get(operator_id)
  if not operator:
    raise HTTPException(status_code=404, detail='Operator not found.')
  sessions = list(db.scalars(select(OperatorSession).where(OperatorSession.operator_id == operator.id).order_by(OperatorSession.created_at.desc(), OperatorSession.id.desc())))
  return [safe_session_payload(session, operator, context.session.id) for session in sessions]


@router.post('/{operator_id}/sessions/revoke-all')
def revoke_operator_sessions_endpoint(operator_id: int, payload: SessionRevokeRequest, context: AuthContext = Depends(admin_csrf), db: Session = Depends(get_db)):
  operator = OperatorRepository(db).get(operator_id)
  if not operator:
    raise HTTPException(status_code=404, detail='Operator not found.')
  reason = (payload.reason or '').strip()
  if not reason:
    raise HTTPException(status_code=400, detail='Revocation reason is required.')
  if operator.id == context.operator.id and not payload.confirm_self_revoke:
    raise HTTPException(status_code=400, detail='Explicit confirmation is required before revoking your own sessions.')
  revoked = revoke_operator_sessions(db, operator.id, context.operator.id, reason)
  append_event(db, 'OPERATOR_SESSIONS_REVOKED', operator_id=context.operator.id, resource_type='OPERATOR', resource_id=str(operator.id), metadata={'reason': reason, 'revoked_sessions': revoked})
  db.commit()
  return {'revoked_count': revoked}
