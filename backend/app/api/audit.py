from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import AuthContext, require_roles
from app.database import get_db
from app.models.audit_event import AuditEvent
from app.schemas.audit import AuditEventRead, AuditVerifyRead
from app.services.audit_service import append_event, verify_chain

router = APIRouter(prefix='/audit', tags=['audit'])


@router.get('/events', response_model=list[AuditEventRead])
def events(action: str | None = None, outcome: str | None = None, operator_id: int | None = None, resource_type: str | None = None, resource_id: str | None = None, date_from: datetime | None = None, date_to: datetime | None = None, limit: int = Query(50, ge=1, le=200), offset: int = Query(0, ge=0), context: AuthContext = Depends(require_roles('ADMIN')), db: Session = Depends(get_db)):
  statement = select(AuditEvent).order_by(AuditEvent.id.desc()).limit(limit).offset(offset)
  for condition in (AuditEvent.action == action if action else None, AuditEvent.outcome == outcome if outcome else None, AuditEvent.operator_id == operator_id if operator_id else None, AuditEvent.resource_type == resource_type if resource_type else None, AuditEvent.resource_id == resource_id if resource_id else None, AuditEvent.occurred_at >= date_from if date_from else None, AuditEvent.occurred_at <= date_to if date_to else None):
    if condition is not None: statement = statement.where(condition)
  return list(db.scalars(statement))


@router.get('/verify', response_model=AuditVerifyRead)
def verify(context: AuthContext = Depends(require_roles('ADMIN')), db: Session = Depends(get_db)):
  valid, total, invalid = verify_chain(db)
  append_event(db, 'AUDIT_CHAIN_VERIFIED' if valid else 'AUDIT_CHAIN_INVALID', 'SUCCESS' if valid else 'FAILED', context.operator.id, resource_type='AUDIT_LOG', metadata={'valid': valid, 'checked_events': total}); db.commit()
  return AuditVerifyRead(valid=valid, total_events=total, first_invalid_event_id=invalid, checked_at=datetime.utcnow())
