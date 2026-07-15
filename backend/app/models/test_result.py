from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class TestResult(Base):
  __tablename__ = 'test_results'

  id: Mapped[int] = mapped_column(Integer, primary_key=True)
  test_run_id: Mapped[int] = mapped_column(ForeignKey('test_runs.id'), nullable=False, index=True)
  test_name: Mapped[str] = mapped_column(String(500), nullable=False)
  test_file: Mapped[str] = mapped_column(String(500), nullable=False)
  status: Mapped[str] = mapped_column(String(20), nullable=False)
  duration_seconds: Mapped[float] = mapped_column(Float, nullable=False, default=0)
  error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
  created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

  test_run: Mapped['TestRun'] = relationship(back_populates='results')
  evidence: Mapped[list['Evidence']] = relationship(back_populates='test_result')
