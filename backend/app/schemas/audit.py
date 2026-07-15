from datetime import datetime
from pydantic import BaseModel, ConfigDict


class AuditEventRead(BaseModel):
  model_config = ConfigDict(from_attributes=True)
  id: int
  occurred_at: datetime
  actor_type: str
  operator_id: int | None
  action: str
  resource_type: str | None
  resource_id: str | None
  outcome: str
  request_id: str
  metadata_json: str | None
  previous_hash: str | None
  event_hash: str


class AuditVerifyRead(BaseModel):
  valid: bool
  total_events: int
  first_invalid_event_id: int | None
  checked_at: datetime
