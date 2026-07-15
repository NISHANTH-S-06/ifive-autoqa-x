from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class OperatorSession(Base):
  __tablename__ = 'operator_sessions'
  id: Mapped[int] = mapped_column(Integer, primary_key=True)
  operator_id: Mapped[int] = mapped_column(ForeignKey('operators.id'), nullable=False, index=True)
  token_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
  csrf_hash: Mapped[str] = mapped_column(String(64), nullable=False)
  created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
  expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
  last_seen_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
  session_name: Mapped[str | None] = mapped_column(String(160), nullable=True)
  revoked_by_operator_id: Mapped[int | None] = mapped_column(ForeignKey('operators.id'), nullable=True)
  revoke_reason: Mapped[str | None] = mapped_column(String(200), nullable=True)
  last_activity_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
  password_version_at_login: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
  revoked_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
  user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)
  ip_address: Mapped[str | None] = mapped_column(String(80), nullable=True)
  operator: Mapped['Operator'] = relationship(back_populates='sessions', foreign_keys=[operator_id])
