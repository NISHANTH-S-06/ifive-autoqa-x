from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Operator(Base):
  __tablename__ = 'operators'
  id: Mapped[int] = mapped_column(Integer, primary_key=True)
  username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False, index=True)
  display_name: Mapped[str] = mapped_column(String(160), nullable=False)
  password_hash: Mapped[str] = mapped_column(String(500), nullable=False)
  role: Mapped[str] = mapped_column(String(20), nullable=False)
  is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
  must_change_password: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
  failed_login_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
  locked_until: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
  last_login_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
  password_changed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
  password_expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
  password_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
  force_password_change_reason: Mapped[str | None] = mapped_column(String(80), nullable=True)
  credentials_updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
  created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
  updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
  sessions: Mapped[list['OperatorSession']] = relationship(back_populates='operator', foreign_keys='OperatorSession.operator_id')
