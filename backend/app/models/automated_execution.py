from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class AutomatedRun(Base):
  __tablename__ = 'automated_runs'
  __table_args__ = (
    UniqueConstraint('run_key', name='uq_automated_runs_key'),
    Index('ix_automated_runs_status', 'status'),
    Index('ix_automated_runs_target', 'target_id'),
  )

  id: Mapped[int] = mapped_column(Integer, primary_key=True)
  project_id: Mapped[int] = mapped_column(ForeignKey('projects.id'), nullable=False, index=True)
  run_key: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
  name: Mapped[str] = mapped_column(String(180), nullable=False)
  description: Mapped[str | None] = mapped_column(Text, nullable=True)
  target_id: Mapped[int] = mapped_column(ForeignKey('connection_targets.id'), nullable=False, index=True)
  target_version: Mapped[int] = mapped_column(Integer, nullable=False)
  target_origin: Mapped[str] = mapped_column(String(500), nullable=False)
  status: Mapped[str] = mapped_column(String(30), nullable=False, default='DRAFT')
  risk_level: Mapped[str] = mapped_column(String(30), nullable=False, default='READ_ONLY')
  preflight_status: Mapped[str] = mapped_column(String(30), nullable=False, default='PENDING')
  dns_pinning_status: Mapped[str] = mapped_column(String(30), nullable=False, default='PENDING')
  runtime_secret_status: Mapped[str] = mapped_column(String(80), nullable=False, default='NOT_REQUIRED')
  created_by: Mapped[int] = mapped_column(ForeignKey('operators.id'), nullable=False, index=True)
  submitted_by: Mapped[int | None] = mapped_column(ForeignKey('operators.id'), nullable=True)
  approved_by: Mapped[int | None] = mapped_column(ForeignKey('operators.id'), nullable=True)
  queued_by: Mapped[int | None] = mapped_column(ForeignKey('operators.id'), nullable=True)
  cancelled_by: Mapped[int | None] = mapped_column(ForeignKey('operators.id'), nullable=True)
  worker_key: Mapped[str | None] = mapped_column(String(120), nullable=True)
  timeout_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=60)
  max_retries: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
  attempt_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
  total_steps: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
  completed_steps: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
  failed_steps: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
  failure_classification: Mapped[str | None] = mapped_column(String(80), nullable=True)
  safe_error_message: Mapped[str | None] = mapped_column(String(500), nullable=True)
  submitted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
  approved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
  queued_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
  started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
  completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
  cancelled_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
  lease_expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
  created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
  updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

  cases: Mapped[list['AutomatedRunCase']] = relationship(back_populates='run', cascade='all, delete-orphan')
  jobs: Mapped[list['ExecutionJob']] = relationship(back_populates='run', cascade='all, delete-orphan')
  artifacts: Mapped[list['ExecutionArtifact']] = relationship(back_populates='run')


class AutomatedRunCase(Base):
  __tablename__ = 'automated_run_cases'
  __table_args__ = (
    UniqueConstraint('run_id', 'test_case_id', 'test_case_version', name='uq_automated_run_cases_case_version'),
    Index('ix_automated_run_cases_status', 'status'),
  )

  id: Mapped[int] = mapped_column(Integer, primary_key=True)
  project_id: Mapped[int] = mapped_column(ForeignKey('projects.id'), nullable=False, index=True)
  run_id: Mapped[int] = mapped_column(ForeignKey('automated_runs.id'), nullable=False, index=True)
  test_case_id: Mapped[int | None] = mapped_column(ForeignKey('managed_test_cases.id'), nullable=True)
  test_case_version: Mapped[int | None] = mapped_column(Integer, nullable=True)
  test_plan_id: Mapped[int | None] = mapped_column(ForeignKey('test_plans.id'), nullable=True)
  test_plan_version: Mapped[int | None] = mapped_column(Integer, nullable=True)
  test_plan_version_id: Mapped[int | None] = mapped_column(ForeignKey('test_plan_versions.id'), nullable=True)
  plan_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
  source_revision: Mapped[int | None] = mapped_column(Integer, nullable=True)
  case_snapshot_json: Mapped[str] = mapped_column(Text, nullable=False)
  sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
  status: Mapped[str] = mapped_column(String(30), nullable=False, default='NOT_RUN')
  failure_classification: Mapped[str | None] = mapped_column(String(80), nullable=True)
  safe_error_message: Mapped[str | None] = mapped_column(String(500), nullable=True)
  started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
  completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

  run: Mapped[AutomatedRun] = relationship(back_populates='cases')
  step_results: Mapped[list['AutomatedStepResult']] = relationship(back_populates='run_case', cascade='all, delete-orphan')


class AutomatedStepResult(Base):
  __tablename__ = 'automated_step_results'
  __table_args__ = (
    UniqueConstraint('run_case_id', 'step_number', name='uq_automated_step_results_case_step'),
    Index('ix_automated_step_results_status', 'status'),
  )

  id: Mapped[int] = mapped_column(Integer, primary_key=True)
  project_id: Mapped[int] = mapped_column(ForeignKey('projects.id'), nullable=False, index=True)
  run_case_id: Mapped[int] = mapped_column(ForeignKey('automated_run_cases.id'), nullable=False, index=True)
  step_number: Mapped[int] = mapped_column(Integer, nullable=False)
  action_type: Mapped[str] = mapped_column(String(40), nullable=False)
  selector: Mapped[str | None] = mapped_column(String(500), nullable=True)
  value_redacted: Mapped[str | None] = mapped_column(String(500), nullable=True)
  expected_redacted: Mapped[str | None] = mapped_column(String(500), nullable=True)
  status: Mapped[str] = mapped_column(String(30), nullable=False, default='NOT_RUN')
  failure_classification: Mapped[str | None] = mapped_column(String(80), nullable=True)
  safe_error_message: Mapped[str | None] = mapped_column(String(500), nullable=True)
  started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
  completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
  duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

  run_case: Mapped[AutomatedRunCase] = relationship(back_populates='step_results')
  artifacts: Mapped[list['ExecutionArtifact']] = relationship(back_populates='step_result')


class ExecutionJob(Base):
  __tablename__ = 'execution_jobs'
  __table_args__ = (
    UniqueConstraint('run_id', name='uq_execution_jobs_run'),
    Index('ix_execution_jobs_status', 'status'),
    Index('ix_execution_jobs_lease', 'lease_expires_at'),
  )

  id: Mapped[int] = mapped_column(Integer, primary_key=True)
  project_id: Mapped[int] = mapped_column(ForeignKey('projects.id'), nullable=False, index=True)
  run_id: Mapped[int] = mapped_column(ForeignKey('automated_runs.id'), nullable=False, index=True)
  status: Mapped[str] = mapped_column(String(30), nullable=False, default='QUEUED')
  priority: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
  lease_owner: Mapped[str | None] = mapped_column(String(120), nullable=True)
  lease_expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
  attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
  created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
  updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

  run: Mapped[AutomatedRun] = relationship(back_populates='jobs')


class ExecutionWorker(Base):
  __tablename__ = 'execution_workers'
  __table_args__ = (
    UniqueConstraint('worker_key', name='uq_execution_workers_key'),
    Index('ix_execution_workers_status', 'status'),
  )

  id: Mapped[int] = mapped_column(Integer, primary_key=True)
  worker_key: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
  status: Mapped[str] = mapped_column(String(30), nullable=False, default='IDLE')
  max_concurrency: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
  current_run_id: Mapped[int | None] = mapped_column(ForeignKey('automated_runs.id'), nullable=True)
  heartbeat_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
  created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
  updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class ExecutionAttempt(Base):
  __tablename__ = 'execution_attempts'
  __table_args__ = (
    UniqueConstraint('run_id', 'attempt_number', name='uq_execution_attempts_run_number'),
    Index('ix_execution_attempts_status', 'status'),
  )

  id: Mapped[int] = mapped_column(Integer, primary_key=True)
  project_id: Mapped[int] = mapped_column(ForeignKey('projects.id'), nullable=False, index=True)
  run_id: Mapped[int] = mapped_column(ForeignKey('automated_runs.id'), nullable=False, index=True)
  attempt_number: Mapped[int] = mapped_column(Integer, nullable=False)
  worker_key: Mapped[str] = mapped_column(String(120), nullable=False)
  status: Mapped[str] = mapped_column(String(30), nullable=False, default='RUNNING')
  started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
  completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
  failure_classification: Mapped[str | None] = mapped_column(String(80), nullable=True)
  safe_error_message: Mapped[str | None] = mapped_column(String(500), nullable=True)


class ExecutionEvent(Base):
  __tablename__ = 'execution_events'
  __table_args__ = (Index('ix_execution_events_run_created', 'run_id', 'created_at'),)

  id: Mapped[int] = mapped_column(Integer, primary_key=True)
  project_id: Mapped[int] = mapped_column(ForeignKey('projects.id'), nullable=False, index=True)
  run_id: Mapped[int] = mapped_column(ForeignKey('automated_runs.id'), nullable=False, index=True)
  event_type: Mapped[str] = mapped_column(String(80), nullable=False)
  status: Mapped[str] = mapped_column(String(30), nullable=False, default='INFO')
  safe_message: Mapped[str | None] = mapped_column(String(500), nullable=True)
  metadata_json: Mapped[str] = mapped_column(Text, nullable=False, default='{}')
  created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


class ExecutionArtifact(Base):
  __tablename__ = 'execution_artifacts'
  __table_args__ = (
    Index('ix_execution_artifacts_run', 'run_id'),
    Index('ix_execution_artifacts_case', 'run_case_id'),
  )

  id: Mapped[int] = mapped_column(Integer, primary_key=True)
  project_id: Mapped[int] = mapped_column(ForeignKey('projects.id'), nullable=False, index=True)
  run_id: Mapped[int] = mapped_column(ForeignKey('automated_runs.id'), nullable=False, index=True)
  run_case_id: Mapped[int | None] = mapped_column(ForeignKey('automated_run_cases.id'), nullable=True)
  step_result_id: Mapped[int | None] = mapped_column(ForeignKey('automated_step_results.id'), nullable=True)
  artifact_type: Mapped[str] = mapped_column(String(30), nullable=False)
  original_filename: Mapped[str] = mapped_column(String(160), nullable=False)
  stored_filename: Mapped[str] = mapped_column(String(160), nullable=False, unique=True)
  relative_path: Mapped[str] = mapped_column(String(500), nullable=False)
  mime_type: Mapped[str] = mapped_column(String(120), nullable=False)
  size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
  sha256: Mapped[str] = mapped_column(String(64), nullable=False)
  safe: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
  created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

  run: Mapped[AutomatedRun] = relationship(back_populates='artifacts')
  step_result: Mapped[AutomatedStepResult | None] = relationship(back_populates='artifacts')
