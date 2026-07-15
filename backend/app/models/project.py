from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Project(Base):
  __tablename__ = 'projects'

  id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
  name: Mapped[str] = mapped_column(String(160), nullable=False, unique=True)
  product_code: Mapped[str] = mapped_column(String(20), nullable=False)
  description: Mapped[str | None] = mapped_column(String(500), nullable=True)
  base_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
  environment: Mapped[str] = mapped_column(String(40), nullable=False, default='local')
  is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
  created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
  updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

  test_runs: Mapped[list['TestRun']] = relationship(back_populates='project')
  members: Mapped[list['ProjectMember']] = relationship(back_populates='project')
