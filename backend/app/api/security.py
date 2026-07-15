from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.auth import AuthContext, require_roles
from app.database import get_db
from app.models.audit_event import AuditEvent
from app.models.operator import Operator
from app.models.operator_session import OperatorSession
from app.schemas.auth import OperatorRole, OperatorSecurityRead, SecuritySummaryRead
from app.services.audit_service import append_event, verify_chain
from app.services.operator_security import session_active

router = APIRouter(prefix='/security', tags=['security'])


@router.get('/summary', response_model=SecuritySummaryRead)
def security_summary(context: AuthContext = Depends(require_roles('ADMIN')), db: Session = Depends(get_db)):
  now = datetime.utcnow()
  day_ago = now - timedelta(days=1)
  month_ago = now - timedelta(days=30)
  operators = list(db.scalars(select(Operator)))
  sessions = list(db.scalars(select(OperatorSession)))
  actions_24h = lambda action: db.scalar(select(func.count(AuditEvent.id)).where(AuditEvent.action == action, AuditEvent.occurred_at >= day_ago)) or 0
  actions_30d = lambda action: db.scalar(select(func.count(AuditEvent.id)).where(AuditEvent.action == action, AuditEvent.occurred_at >= month_ago)) or 0
  operators_by_role = {role.value: 0 for role in OperatorRole}
  for operator in operators:
    operators_by_role[operator.role] = operators_by_role.get(operator.role, 0) + 1
  valid, _, _ = verify_chain(db)
  append_event(db, 'SECURITY_SUMMARY_VIEWED', operator_id=context.operator.id, resource_type='SECURITY_REPORT')
  db.commit()
  return {
    'total_operators': len(operators),
    'active_operators': sum(1 for operator in operators if operator.is_active),
    'inactive_operators': sum(1 for operator in operators if not operator.is_active),
    'operators_by_role': operators_by_role,
    'locked_operators': sum(1 for operator in operators if operator.locked_until and operator.locked_until > now),
    'must_change_password_count': sum(1 for operator in operators if operator.must_change_password),
    'expired_password_count': sum(1 for operator in operators if operator.password_expires_at and operator.password_expires_at <= now),
    'active_sessions': sum(1 for session in sessions if session_active(session, session.operator, now)),
    'revoked_sessions_last_24h': sum(1 for session in sessions if session.revoked_at and session.revoked_at >= day_ago),
    'failed_logins_last_24h': actions_24h('LOGIN_FAILED'),
    'successful_logins_last_24h': actions_24h('LOGIN_SUCCESS'),
    'password_changes_last_30d': actions_30d('PASSWORD_CHANGED') + actions_30d('PASSWORD_FIRST_LOGIN_CHANGED'),
    'password_resets_last_30d': actions_30d('OPERATOR_PASSWORD_RESET'),
    'audit_chain_valid': valid,
    'last_audit_verification_at': now,
  }


@router.get('/operators', response_model=list[OperatorSecurityRead])
def security_operators(role: OperatorRole | None = None, is_active: bool | None = None, must_change_password: bool | None = None, is_locked: bool | None = None, limit: int = Query(50, ge=1, le=200), offset: int = Query(0, ge=0), context: AuthContext = Depends(require_roles('ADMIN')), db: Session = Depends(get_db)):
  now = datetime.utcnow()
  statement = select(Operator).order_by(Operator.username).limit(limit).offset(offset)
  if role is not None:
    statement = statement.where(Operator.role == role.value)
  if is_active is not None:
    statement = statement.where(Operator.is_active.is_(is_active))
  if must_change_password is not None:
    statement = statement.where(Operator.must_change_password.is_(must_change_password))
  operators = list(db.scalars(statement))
  rows = []
  for operator in operators:
    locked = bool(operator.locked_until and operator.locked_until > now)
    if is_locked is not None and locked != is_locked:
      continue
    active_session_count = sum(1 for session in operator.sessions if session_active(session, operator, now))
    rows.append({
      'id': operator.id,
      'username': operator.username,
      'display_name': operator.display_name,
      'role': operator.role,
      'is_active': operator.is_active,
      'must_change_password': operator.must_change_password,
      'password_changed_at': operator.password_changed_at,
      'password_expires_at': operator.password_expires_at,
      'last_login_at': operator.last_login_at,
      'failed_login_count': operator.failed_login_count,
      'is_locked': locked,
      'active_session_count': active_session_count,
    })
  append_event(db, 'SECURITY_OPERATOR_REPORT_VIEWED', operator_id=context.operator.id, resource_type='SECURITY_REPORT')
  db.commit()
  return rows
