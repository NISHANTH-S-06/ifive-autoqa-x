import secrets
from datetime import datetime, timedelta

from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response
import hmac
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import COOKIE_NAME, AuthContext, get_auth_context, require_csrf
from app.config import settings
from app.database import get_db
from app.models.operator_session import OperatorSession
from app.repositories.operator_repository import OperatorRepository
from app.schemas.auth import LoginRequest, LoginResponse, OperatorRead, OperatorSessionRead, PasswordChangeRequest, SessionRevokeRequest
from app.services.audit_service import append_event
from app.services.operator_security import add_password_history, password_expiry_from, recent_password_reused, revoke_operator_sessions, safe_session_payload
from app.services.password_service import hash_password, hash_secret, normalize_username, validate_password, verify_password

router = APIRouter(prefix='/auth', tags=['authentication'])
MAX_ATTEMPTS = 5
LOCK_MINUTES = 15


@router.post('/login', response_model=LoginResponse)
def login(payload: LoginRequest, response: Response, request: Request, db: Session = Depends(get_db)):
  try: username = normalize_username(payload.username)
  except ValueError: username = payload.username.strip().lower()
  operator = OperatorRepository(db).by_username(username)
  now = datetime.utcnow()
  ip = request.client.host if request.client else None
  if operator and operator.locked_until and operator.locked_until > now:
    append_event(db, 'LOGIN_LOCKED', 'DENIED', operator.id, resource_type='OPERATOR', resource_id=str(operator.id), ip_address=ip)
    db.commit(); raise HTTPException(status_code=401, detail='Invalid username or password.')
  valid = operator is not None and operator.is_active and verify_password(payload.password, operator.password_hash)
  if not valid:
    if operator:
      operator.failed_login_count += 1
      if operator.failed_login_count >= MAX_ATTEMPTS: operator.locked_until = now + timedelta(minutes=LOCK_MINUTES)
    append_event(db, 'LOGIN_FAILED', 'DENIED', operator.id if operator else None, resource_type='OPERATOR', resource_id=str(operator.id) if operator else None, metadata={'username': username}, ip_address=ip)
    db.commit(); raise HTTPException(status_code=401, detail='Invalid username or password.')
  token, csrf = secrets.token_urlsafe(48), secrets.token_urlsafe(32)
  if operator.password_expires_at and operator.password_expires_at <= now and not operator.must_change_password:
    operator.must_change_password = True
    operator.force_password_change_reason = 'PASSWORD_EXPIRED'
    append_event(db, 'PASSWORD_EXPIRED', operator_id=operator.id, resource_type='OPERATOR', resource_id=str(operator.id), ip_address=ip)
  session = OperatorSession(operator_id=operator.id, token_hash=hash_secret(token), csrf_hash=hash_secret(csrf), expires_at=now + timedelta(hours=settings.session_hours), last_seen_at=now, last_activity_at=now, password_version_at_login=operator.password_version, user_agent=request.headers.get('user-agent'), ip_address=ip)
  operator.failed_login_count = 0; operator.locked_until = None; operator.last_login_at = now
  db.add(session); append_event(db, 'LOGIN_SUCCESS', operator_id=operator.id, resource_type='SESSION', ip_address=ip); db.commit()
  response.set_cookie(COOKIE_NAME, token, httponly=True, samesite='lax', secure=settings.cookie_secure, max_age=settings.session_hours * 3600, path='/')
  response.set_cookie('autoqa_csrf', csrf, httponly=False, samesite='lax', secure=settings.cookie_secure, max_age=settings.session_hours * 3600, path='/')
  return LoginResponse(operator=OperatorRead.model_validate(operator), csrf_token=csrf)


@router.post('/logout')
def logout(response: Response, context: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)):
  context.session.revoked_at = datetime.utcnow(); append_event(db, 'LOGOUT', operator_id=context.operator.id, resource_type='SESSION', resource_id=str(context.session.id)); db.commit()
  response.delete_cookie(COOKIE_NAME, path='/'); response.delete_cookie('autoqa_csrf', path='/'); return {'status': 'logged_out'}


@router.get('/me', response_model=OperatorRead)
def me(context: AuthContext = Depends(get_auth_context)): return context.operator


@router.get('/csrf')
def csrf_value(csrf: str | None = Cookie(default=None, alias='autoqa_csrf'), context: AuthContext = Depends(get_auth_context)):
  if not csrf or not hmac.compare_digest(hash_secret(csrf), context.session.csrf_hash):
    raise HTTPException(status_code=403, detail='CSRF validation failed.')
  return {'csrf_token': csrf}


def _change_password(db: Session, context: AuthContext, payload: PasswordChangeRequest, reason: str, preserve_current_session: bool = True):
  operator = context.operator
  if not verify_password(payload.current_password, operator.password_hash):
    append_event(db, 'PASSWORD_CHANGE_FAILED', 'DENIED', operator.id, resource_type='OPERATOR', resource_id=str(operator.id), metadata={'reason': 'current_password'})
    db.commit()
    raise HTTPException(status_code=400, detail='Current password is incorrect.')
  if payload.new_password != payload.confirm_password:
    append_event(db, 'PASSWORD_CHANGE_FAILED', 'DENIED', operator.id, resource_type='OPERATOR', resource_id=str(operator.id), metadata={'reason': 'confirmation_mismatch'})
    db.commit()
    raise HTTPException(status_code=400, detail='New password and confirmation password do not match.')
  try:
    validate_password(payload.new_password, operator.username, operator.display_name)
  except ValueError as exc:
    append_event(db, 'PASSWORD_CHANGE_FAILED', 'DENIED', operator.id, resource_type='OPERATOR', resource_id=str(operator.id), metadata={'reason': 'policy'})
    db.commit()
    raise HTTPException(status_code=400, detail=str(exc)) from None
  if recent_password_reused(db, operator, payload.new_password):
    append_event(db, 'PASSWORD_REUSE_BLOCKED', 'DENIED', operator.id, resource_type='OPERATOR', resource_id=str(operator.id))
    db.commit()
    raise HTTPException(status_code=400, detail='This password was used recently. Choose a different password.')
  now = datetime.utcnow()
  operator.password_version += 1
  operator.password_hash = hash_password(payload.new_password)
  operator.must_change_password = False
  operator.force_password_change_reason = None
  operator.password_changed_at = now
  operator.password_expires_at = password_expiry_from(now)
  operator.credentials_updated_at = now
  operator.failed_login_count = 0
  operator.locked_until = None
  add_password_history(db, operator, operator.id, reason, now)
  revoked = revoke_operator_sessions(db, operator.id, operator.id, 'PASSWORD_CHANGED', except_session_id=context.session.id if preserve_current_session else None)
  if preserve_current_session:
    context.session.password_version_at_login = operator.password_version
    context.session.last_activity_at = now
  append_event(db, 'SESSION_INVALIDATED_BY_PASSWORD_CHANGE', operator_id=operator.id, resource_type='SESSION', metadata={'revoked_count': revoked})
  append_event(db, 'PASSWORD_FIRST_LOGIN_CHANGED' if reason == 'FIRST_LOGIN_CHANGE' else 'PASSWORD_CHANGED', operator_id=operator.id, resource_type='OPERATOR', resource_id=str(operator.id))
  db.commit()
  return {'status': 'password_changed'}


@router.post('/change-required-password')
def change_required_password(payload: PasswordChangeRequest, context: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)):
  if not context.operator.must_change_password:
    raise HTTPException(status_code=400, detail='Password change is not currently required.')
  return _change_password(db, context, payload, 'FIRST_LOGIN_CHANGE')


@router.post('/change-password')
def change_password(payload: PasswordChangeRequest, context: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)):
  if context.operator.must_change_password:
    raise HTTPException(status_code=403, detail='Password change is required before accessing this resource.')
  return _change_password(db, context, payload, 'SELF_SERVICE_CHANGE')


@router.get('/sessions', response_model=list[OperatorSessionRead])
def list_sessions(context: AuthContext = Depends(get_auth_context), db: Session = Depends(get_db)):
  sessions = list(db.scalars(select(OperatorSession).where(OperatorSession.operator_id == context.operator.id).order_by(OperatorSession.created_at.desc(), OperatorSession.id.desc())))
  return [safe_session_payload(session, context.operator, context.session.id) for session in sessions]


@router.post('/sessions/revoke-others')
def revoke_other_sessions(context: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)):
  count = revoke_operator_sessions(db, context.operator.id, context.operator.id, 'OWNER_REVOKE_OTHERS', except_session_id=context.session.id)
  append_event(db, 'OTHER_SESSIONS_REVOKED', operator_id=context.operator.id, resource_type='SESSION', metadata={'revoked_count': count})
  db.commit()
  return {'revoked_count': count}


@router.post('/sessions/{session_id}/revoke')
def revoke_session(session_id: int, response: Response, payload: SessionRevokeRequest | None = None, context: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)):
  session = db.get(OperatorSession, session_id)
  if session is None or session.operator_id != context.operator.id:
    raise HTTPException(status_code=404, detail='Session not found.')
  now = datetime.utcnow()
  session.revoked_at = now
  session.revoked_by_operator_id = context.operator.id
  session.revoke_reason = (payload.reason if payload and payload.reason else 'OWNER_REVOKE')[:200]
  append_event(db, 'SESSION_REVOKED_BY_OWNER', operator_id=context.operator.id, resource_type='SESSION', resource_id=str(session.id))
  db.commit()
  if session.id == context.session.id:
    response.delete_cookie(COOKIE_NAME, path='/')
    response.delete_cookie('autoqa_csrf', path='/')
    return {'status': 'logged_out'}
  return {'status': 'revoked'}
