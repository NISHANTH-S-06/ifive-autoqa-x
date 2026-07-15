from datetime import datetime, timedelta

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.config import settings
from app.models.operator import Operator
from app.models.operator_session import OperatorSession
from app.models.password_history import PasswordHistory
from app.services.audit_service import append_event
from app.services.password_service import verify_password

HISTORY_REUSE_LIMIT = 5
SESSION_ACTIVITY_INTERVAL_SECONDS = 60


def password_expiry_from(now: datetime) -> datetime | None:
  if settings.password_max_age_days <= 0:
    return None
  return now + timedelta(days=settings.password_max_age_days)


def add_password_history(db: Session, operator: Operator, changed_by_operator_id: int | None, reason: str, changed_at: datetime) -> PasswordHistory:
  history = PasswordHistory(
    operator_id=operator.id,
    password_hash=operator.password_hash,
    password_version=operator.password_version,
    changed_at=changed_at,
    changed_by_operator_id=changed_by_operator_id,
    change_reason=reason,
  )
  db.add(history)
  db.flush()
  return history


def recent_password_reused(db: Session, operator: Operator, password: str, limit: int = HISTORY_REUSE_LIMIT) -> bool:
  hashes = [operator.password_hash]
  statement = (
    select(PasswordHistory)
    .where(PasswordHistory.operator_id == operator.id)
    .order_by(desc(PasswordHistory.changed_at), desc(PasswordHistory.id))
    .limit(limit)
  )
  hashes.extend(item.password_hash for item in db.scalars(statement))
  return any(verify_password(password, encoded) for encoded in hashes)


def revoke_operator_sessions(db: Session, operator_id: int, revoked_by_operator_id: int | None, reason: str, except_session_id: int | None = None) -> int:
  now = datetime.utcnow()
  sessions = list(db.scalars(select(OperatorSession).where(OperatorSession.operator_id == operator_id, OperatorSession.revoked_at.is_(None))))
  count = 0
  for session in sessions:
    if except_session_id is not None and session.id == except_session_id:
      continue
    session.revoked_at = now
    session.revoked_by_operator_id = revoked_by_operator_id
    session.revoke_reason = reason[:200]
    count += 1
  return count


def touch_session_activity(db: Session, session: OperatorSession, now: datetime) -> None:
  previous = session.last_activity_at or session.last_seen_at
  session.last_seen_at = now
  if previous is None or (now - previous).total_seconds() >= SESSION_ACTIVITY_INTERVAL_SECONDS:
    session.last_activity_at = now


def session_active(session: OperatorSession, operator: Operator, now: datetime | None = None) -> bool:
  now = now or datetime.utcnow()
  return (
    session.revoked_at is None
    and session.expires_at > now
    and operator.is_active
    and session.password_version_at_login == operator.password_version
  )


def summarize_user_agent(value: str | None) -> str | None:
  if not value:
    return None
  lowered = value.lower()
  browser = 'Browser'
  for name in ('edg', 'chrome', 'firefox', 'safari'):
    if name in lowered:
      browser = {'edg': 'Edge', 'chrome': 'Chrome', 'firefox': 'Firefox', 'safari': 'Safari'}[name]
      break
  platform = 'Unknown OS'
  for marker, label in (('windows', 'Windows'), ('mac os', 'macOS'), ('linux', 'Linux'), ('android', 'Android'), ('iphone', 'iOS')):
    if marker in lowered:
      platform = label
      break
  return f'{browser} on {platform}'


def mask_ip(value: str | None) -> str | None:
  if not value:
    return None
  if ':' in value:
    parts = value.split(':')
    return ':'.join(parts[:2] + ['****'])
  parts = value.split('.')
  if len(parts) == 4:
    return '.'.join(parts[:2] + ['x', 'x'])
  return 'masked'


def safe_session_payload(session: OperatorSession, operator: Operator, current_session_id: int) -> dict:
  return {
    'session_id': session.id,
    'session_name': session.session_name,
    'created_at': session.created_at,
    'last_seen_at': session.last_seen_at,
    'last_activity_at': session.last_activity_at,
    'expires_at': session.expires_at,
    'revoked_at': session.revoked_at,
    'user_agent': summarize_user_agent(session.user_agent),
    'ip_address': mask_ip(session.ip_address),
    'is_current': session.id == current_session_id,
    'is_active': session_active(session, operator),
  }


def record_password_version_mismatches(db: Session, session: OperatorSession, operator: Operator) -> None:
  append_event(
    db,
    'SESSION_PASSWORD_VERSION_MISMATCH',
    'DENIED',
    operator.id,
    resource_type='SESSION',
    resource_id=str(session.id),
    metadata={'session_credential_version': session.password_version_at_login, 'operator_credential_version': operator.password_version},
  )
