from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class PasswordHistory(Base):
  __tablename__ = 'password_history'
  id: Mapped[int] = mapped_column(Integer, primary_key=True)
  operator_id: Mapped[int] = mapped_column(ForeignKey('operators.id'), nullable=False, index=True)
  password_hash: Mapped[str] = mapped_column(String(500), nullable=False)
  password_version: Mapped[int] = mapped_column(Integer, nullable=False)
  changed_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
  changed_by_operator_id: Mapped[int | None] = mapped_column(ForeignKey('operators.id'), nullable=True)
  change_reason: Mapped[str] = mapped_column(String(40), nullable=False)
