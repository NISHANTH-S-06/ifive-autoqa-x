import hmac
from dataclasses import dataclass
from datetime import datetime

from fastapi import Cookie, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.operator import Operator
from app.models.operator_session import OperatorSession
from app.repositories.operator_repository import OperatorRepository
from app.services.audit_service import append_event
from app.services.operator_security import record_password_version_mismatches, touch_session_activity
from app.services.password_service import hash_secret

COOKIE_NAME = 'autoqa_session'
PASSWORD_CHANGE_ALLOWED_PATHS = {
  '/api/auth/me',
  '/api/auth/csrf',
  '/api/auth/change-required-password',
  '/api/auth/logout',
  '/api/health',
  '/health',
}
PASSWORD_CHANGE_REQUIRED_MESSAGE = 'Password change is required before accessing this resource.'


@dataclass
class AuthContext:
  operator: Operator
  session: OperatorSession


def get_auth_context(request: Request, db: Session = Depends(get_db), token: str | None = Cookie(default=None, alias=COOKIE_NAME)) -> AuthContext:
  if not token:
    raise HTTPException(status_code=401, detail='Authentication required.')
  session = OperatorRepository(db).session_by_hash(hash_secret(token))
  now = datetime.utcnow()
  if session is None or session.revoked_at is not None:
    raise HTTPException(status_code=401, detail='Session is invalid or expired.')
  if session.expires_at <= now:
    append_event(db, 'SESSION_EXPIRED', 'DENIED', session.operator_id, resource_type='SESSION', resource_id=str(session.id), ip_address=request.client.host if request.client else None)
    db.commit()
    raise HTTPException(status_code=401, detail='Session is invalid or expired.')
  operator = session.operator
  if not operator.is_active:
    raise HTTPException(status_code=403, detail='Operator account is inactive.')
  if session.password_version_at_login != operator.password_version:
    record_password_version_mismatches(db, session, operator)
    db.commit()
    raise HTTPException(status_code=401, detail='Session is invalid or expired.')
  if operator.password_expires_at and operator.password_expires_at <= now and not operator.must_change_password:
    operator.must_change_password = True
    operator.force_password_change_reason = 'PASSWORD_EXPIRED'
    append_event(db, 'PASSWORD_EXPIRED', operator_id=operator.id, resource_type='OPERATOR', resource_id=str(operator.id))
  if operator.must_change_password and request.url.path not in PASSWORD_CHANGE_ALLOWED_PATHS:
    append_event(db, 'ACCESS_DENIED_PASSWORD_CHANGE_REQUIRED', 'DENIED', operator.id, resource_type='ENDPOINT', resource_id=request.url.path)
    db.commit()
    raise HTTPException(status_code=403, detail=PASSWORD_CHANGE_REQUIRED_MESSAGE)
  touch_session_activity(db, session, now)
  db.commit()
  return AuthContext(operator, session)


def require_roles(*roles: str):
  def dependency(request: Request, context: AuthContext = Depends(get_auth_context), db: Session = Depends(get_db)) -> AuthContext:
    if context.operator.role not in roles:
      append_event(db, 'ACCESS_DENIED', 'DENIED', context.operator.id, resource_type='ENDPOINT', resource_id=request.url.path, metadata={'required_roles': ','.join(roles)})
      db.commit()
      raise HTTPException(status_code=403, detail='You do not have permission to perform this action.')
    return context
  return dependency


def require_csrf(request: Request, csrf_token: str | None = Header(default=None, alias='X-CSRF-Token'), context: AuthContext = Depends(get_auth_context), db: Session = Depends(get_db)) -> AuthContext:
  if not csrf_token or not hmac.compare_digest(hash_secret(csrf_token), context.session.csrf_hash):
    append_event(db, 'CSRF_VALIDATION_FAILED', 'DENIED', context.operator.id, resource_type='ENDPOINT', resource_id=request.url.path)
    db.commit()
    raise HTTPException(status_code=403, detail='CSRF validation failed.')
  return context
