import hashlib
import json
import re
from datetime import datetime
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.audit_event import AuditEvent

SECRET_KEYS = re.compile(r'(?i)(password|token|cookie|csrf|authorization|secret)')


def safe_metadata(metadata: dict | None) -> dict:
  if not metadata: return {}
  return {str(key): ('[REDACTED]' if SECRET_KEYS.search(str(key)) else value) for key, value in metadata.items() if isinstance(value, (str, int, float, bool, type(None)))}


def canonical_event(event: dict) -> str:
  return json.dumps(event, sort_keys=True, separators=(',', ':'), ensure_ascii=True)


def event_payload(previous_hash, occurred_at, actor_type, operator_id, action, resource_type, resource_id, outcome, metadata_json):
  return {'previous_hash': previous_hash, 'occurred_at': occurred_at.isoformat(), 'actor_type': actor_type, 'operator_id': operator_id, 'action': action, 'resource_type': resource_type, 'resource_id': resource_id, 'outcome': outcome, 'metadata_json': metadata_json}


def append_event(db: Session, action: str, outcome: str = 'SUCCESS', operator_id: int | None = None, actor_type: str = 'OPERATOR', resource_type: str | None = None, resource_id: str | None = None, metadata: dict | None = None, request_id: str | None = None, ip_address: str | None = None, user_agent: str | None = None) -> AuditEvent:
  previous = db.scalar(select(AuditEvent).order_by(AuditEvent.id.desc()).limit(1))
  occurred_at = datetime.utcnow()
  metadata_json = canonical_event(safe_metadata(metadata)) if metadata else None
  previous_hash = previous.event_hash if previous else None
  digest = hashlib.sha256(canonical_event(event_payload(previous_hash, occurred_at, actor_type, operator_id, action, resource_type, resource_id, outcome, metadata_json)).encode()).hexdigest()
  event = AuditEvent(occurred_at=occurred_at, actor_type=actor_type, operator_id=operator_id, action=action, resource_type=resource_type, resource_id=resource_id, outcome=outcome, request_id=request_id or uuid4().hex, ip_address=ip_address, user_agent=user_agent, metadata_json=metadata_json, previous_hash=previous_hash, event_hash=digest)
  db.add(event); db.flush()
  return event


def verify_chain(db: Session) -> tuple[bool, int, int | None]:
  events = list(db.scalars(select(AuditEvent).order_by(AuditEvent.id)))
  previous_hash = None
  for event in events:
    expected = hashlib.sha256(canonical_event(event_payload(previous_hash, event.occurred_at, event.actor_type, event.operator_id, event.action, event.resource_type, event.resource_id, event.outcome, event.metadata_json)).encode()).hexdigest()
    if event.previous_hash != previous_hash or not __import__('hmac').compare_digest(expected, event.event_hash):
      return False, len(events), event.id
    previous_hash = event.event_hash
  return True, len(events), None
