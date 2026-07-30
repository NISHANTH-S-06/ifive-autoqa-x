from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class CompanyTask(Base):
  """
  Enterprise task lifecycle model — Phase 2 expanded.

  Status Pipeline:
    NEW → ASSIGNED → IN_PROGRESS → DEVELOPER_COMPLETED
        → TESTING_L2 → TEST_APPROVED → AUTOQA_RUNNING
        → PASSED → DELIVERY_COMPLETED
        → FAILED → BACK_TO_DEVELOPER → (loop back to IN_PROGRESS)
        → CLOSED (terminal, manual)
  """
  __tablename__ = 'company_tasks'
  __table_args__ = (
    Index('ix_company_tasks_status', 'status'),
    Index('ix_company_tasks_project', 'project_id'),
    Index('ix_company_tasks_developer', 'assigned_developer_id'),
    Index('ix_company_tasks_tester', 'assigned_tester_id'),
    Index('ix_company_tasks_created_by', 'created_by'),
    Index('ix_company_tasks_updated_at', 'updated_at'),
  )







  id: Mapped[int] = mapped_column(Integer, primary_key=True)

  # ── Project reference ───────────────────────────────────────────────────
  project_id: Mapped[int | None] = mapped_column(ForeignKey('projects.id'), nullable=True, index=True)

  # ── Core task metadata ─────────────────────────────────────────────────
  title: Mapped[str] = mapped_column(String(250), nullable=False)
  module: Mapped[str | None] = mapped_column(String(100), nullable=True)    # e.g. "Sales"
  feature: Mapped[str | None] = mapped_column(String(150), nullable=True)   # e.g. "Create Sales Order"
  description: Mapped[str | None] = mapped_column(Text, nullable=True)      # Context for developer

  # ── AutoQA inputs (mandatory for AI testing) ───────────────────────────
  target_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
  expected_flow: Mapped[str | None] = mapped_column(Text, nullable=True)        # Arrow-separated flow
  acceptance_criteria: Mapped[str | None] = mapped_column(Text, nullable=True)  # What defines PASS
  expected_result: Mapped[str | None] = mapped_column(Text, nullable=True)      # Expected final state
  api_endpoint: Mapped[str | None] = mapped_column(String(500), nullable=True)  # Optional API to validate

  # ── Testing context ────────────────────────────────────────────────────
  browser: Mapped[str] = mapped_column(String(20), nullable=False, default='CHROMIUM')
  # BROWSER values: CHROMIUM | FIREFOX | WEBKIT
  environment: Mapped[str] = mapped_column(String(50), nullable=False, default='local')
  # ENVIRONMENT: local | staging | qa | production (production blocked by engine)
  reference_screenshot_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)

  # ── Priority and scheduling ────────────────────────────────────────────
  priority: Mapped[str] = mapped_column(String(20), nullable=False, default='MEDIUM')
  # PRIORITY: LOW | MEDIUM | HIGH | CRITICAL
  severity: Mapped[str] = mapped_column(String(20), nullable=False, default='MEDIUM')
  # SEVERITY: LOW | MEDIUM | HIGH | CRITICAL
  estimated_hours: Mapped[float | None] = mapped_column(Float, nullable=True)
  target_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

  # ── Status pipeline ────────────────────────────────────────────────────
  status: Mapped[str] = mapped_column(String(30), nullable=False, default='NEW')

  # ── People assignments ─────────────────────────────────────────────────
  assigned_developer_id: Mapped[int | None] = mapped_column(ForeignKey('operators.id'), nullable=True)
  assigned_tester_id: Mapped[int | None] = mapped_column(ForeignKey('operators.id'), nullable=True)
  created_by: Mapped[int] = mapped_column(ForeignKey('operators.id'), nullable=False)
  approved_by_tester_id: Mapped[int | None] = mapped_column(ForeignKey('operators.id'), nullable=True)

  # ── AutoQA execution linkage ───────────────────────────────────────────
  autoqa_run_id: Mapped[int | None] = mapped_column(ForeignKey('automated_runs.id'), nullable=True)
  autoqa_result: Mapped[str | None] = mapped_column(String(20), nullable=True)   # PASS | FAIL
  autoqa_notes: Mapped[str | None] = mapped_column(Text, nullable=True)          # AI summary / failure details
  retest_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)  # BACK_TO_DEVELOPER cycles

  # ── Core timestamps ────────────────────────────────────────────────────
  created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
  updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

  # ── Pipeline milestone timestamps ──────────────────────────────────────
  assigned_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
  in_progress_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
  developer_completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
  testing_l2_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
  test_approved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
  autoqa_started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
  autoqa_completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
  back_to_developer_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
  delivery_completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
  closed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

  # ── Relationships ──────────────────────────────────────────────────────
  assigned_developer = relationship('Operator', foreign_keys=[assigned_developer_id])
  assigned_tester = relationship('Operator', foreign_keys=[assigned_tester_id])
  creator = relationship('Operator', foreign_keys=[created_by])
  approver = relationship('Operator', foreign_keys=[approved_by_tester_id])
  autoqa_run = relationship('AutomatedRun', foreign_keys=[autoqa_run_id])
