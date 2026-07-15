from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class TestRun(Base):
  __tablename__ = 'test_runs'

  id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
  run_code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
  project_id: Mapped[int] = mapped_column(ForeignKey('projects.id'), nullable=False, index=True)
  created_by_operator_id: Mapped[int | None] = mapped_column(ForeignKey('operators.id'), nullable=True)
  approved_by_operator_id: Mapped[int | None] = mapped_column(ForeignKey('operators.id'), nullable=True)
  executed_by_operator_id: Mapped[int | None] = mapped_column(ForeignKey('operators.id'), nullable=True)
  cancelled_by_operator_id: Mapped[int | None] = mapped_column(ForeignKey('operators.id'), nullable=True)
  suite_name: Mapped[str] = mapped_column(String(160), nullable=False)
  browser: Mapped[str] = mapped_column(String(40), nullable=False, default='chromium')
  environment: Mapped[str] = mapped_column(String(40), nullable=False, default='local')
  status: Mapped[str] = mapped_column(String(20), nullable=False, default='QUEUED', index=True)
  total_tests: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
  passed_tests: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
  failed_tests: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
  skipped_tests: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
  duration_seconds: Mapped[float] = mapped_column(Float, nullable=False, default=0)
  report_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
  approved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
  started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
  completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
  exit_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
  error_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
  result_json_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
  html_report_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
  stdout_log_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
  stderr_log_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
  created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

  project: Mapped['Project'] = relationship(back_populates='test_runs')
  results: Mapped[list['TestResult']] = relationship(back_populates='test_run', cascade='all, delete-orphan')
  evidence: Mapped[list['Evidence']] = relationship(back_populates='test_run', cascade='all, delete-orphan')
