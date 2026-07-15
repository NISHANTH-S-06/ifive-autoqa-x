from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class AuditEvent(Base):
  __tablename__ = 'audit_events'
  id: Mapped[int] = mapped_column(Integer, primary_key=True)
  occurred_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
  actor_type: Mapped[str] = mapped_column(String(20), nullable=False)
  operator_id: Mapped[int | None] = mapped_column(ForeignKey('operators.id'), nullable=True)
  action: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
  resource_type: Mapped[str | None] = mapped_column(String(80), nullable=True)
  resource_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
  outcome: Mapped[str] = mapped_column(String(20), nullable=False)
  request_id: Mapped[str] = mapped_column(String(64), nullable=False)
  ip_address: Mapped[str | None] = mapped_column(String(80), nullable=True)
  user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)
  metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)
  previous_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
  event_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
