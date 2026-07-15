from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Defect(Base):
  __tablename__ = 'defects'
  __table_args__ = (
    UniqueConstraint('defect_key', name='uq_defects_key'),
    Index('ix_defects_status', 'status'),
    Index('ix_defects_project_status', 'project_id', 'status'),
    Index('ix_defects_assignee', 'assigned_to'),
  )

  id: Mapped[int] = mapped_column(Integer, primary_key=True)
  access_project_id: Mapped[int] = mapped_column(ForeignKey('projects.id'), nullable=False, index=True)
  defect_key: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
  title: Mapped[str] = mapped_column(String(220), nullable=False)
  description: Mapped[str | None] = mapped_column(Text, nullable=True)
  project_id: Mapped[int] = mapped_column(ForeignKey('test_projects.id'), nullable=False, index=True)
  module_id: Mapped[int | None] = mapped_column(ForeignKey('test_modules.id'), nullable=True)
  suite_id: Mapped[int | None] = mapped_column(ForeignKey('managed_test_suites.id'), nullable=True)
  test_case_id: Mapped[int | None] = mapped_column(ForeignKey('managed_test_cases.id'), nullable=True, index=True)
  test_case_version: Mapped[int | None] = mapped_column(Integer, nullable=True)
  manual_run_id: Mapped[int | None] = mapped_column(ForeignKey('manual_test_runs.id'), nullable=True, index=True)
  manual_run_case_id: Mapped[int | None] = mapped_column(ForeignKey('manual_test_run_cases.id'), nullable=True)
  manual_step_result_id: Mapped[int | None] = mapped_column(ForeignKey('manual_step_results.id'), nullable=True)
  automated_run_id: Mapped[int | None] = mapped_column(ForeignKey('automated_runs.id'), nullable=True, index=True)
  automated_run_case_id: Mapped[int | None] = mapped_column(ForeignKey('automated_run_cases.id'), nullable=True)
  automated_step_result_id: Mapped[int | None] = mapped_column(ForeignKey('automated_step_results.id'), nullable=True)
  severity: Mapped[str] = mapped_column(String(20), nullable=False, default='MEDIUM')
  priority: Mapped[str] = mapped_column(String(20), nullable=False, default='MEDIUM')
  status: Mapped[str] = mapped_column(String(30), nullable=False, default='NEW')
  assigned_to: Mapped[int | None] = mapped_column(ForeignKey('operators.id'), nullable=True)
  reporter_id: Mapped[int] = mapped_column(ForeignKey('operators.id'), nullable=False)
  environment: Mapped[str | None] = mapped_column(String(80), nullable=True)
  target_id: Mapped[int | None] = mapped_column(ForeignKey('connection_targets.id'), nullable=True)
  target_version: Mapped[int | None] = mapped_column(Integer, nullable=True)
  failure_category: Mapped[str | None] = mapped_column(String(80), nullable=True)
  expected_result: Mapped[str | None] = mapped_column(Text, nullable=True)
  actual_result: Mapped[str | None] = mapped_column(Text, nullable=True)
  reproduction_steps: Mapped[str | None] = mapped_column(Text, nullable=True)
  resolution: Mapped[str | None] = mapped_column(Text, nullable=True)
  duplicate_of_defect_id: Mapped[int | None] = mapped_column(ForeignKey('defects.id'), nullable=True)
  created_by: Mapped[int] = mapped_column(ForeignKey('operators.id'), nullable=False)
  created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
  updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
  closed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
  archived_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

  comments: Mapped[list['DefectComment']] = relationship(back_populates='defect', cascade='all, delete-orphan')
  history: Mapped[list['DefectHistory']] = relationship(back_populates='defect', cascade='all, delete-orphan')
  evidence_links: Mapped[list['DefectEvidenceLink']] = relationship(back_populates='defect', cascade='all, delete-orphan')
  retests: Mapped[list['DefectRetest']] = relationship(back_populates='defect', cascade='all, delete-orphan')


class DefectComment(Base):
  __tablename__ = 'defect_comments'
  __table_args__ = (Index('ix_defect_comments_defect_created', 'defect_id', 'created_at'),)

  id: Mapped[int] = mapped_column(Integer, primary_key=True)
  project_id: Mapped[int] = mapped_column(ForeignKey('projects.id'), nullable=False, index=True)
  defect_id: Mapped[int] = mapped_column(ForeignKey('defects.id'), nullable=False, index=True)
  body: Mapped[str] = mapped_column(Text, nullable=False)
  created_by: Mapped[int] = mapped_column(ForeignKey('operators.id'), nullable=False)
  created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

  defect: Mapped[Defect] = relationship(back_populates='comments')


class DefectHistory(Base):
  __tablename__ = 'defect_history'
  __table_args__ = (Index('ix_defect_history_defect_created', 'defect_id', 'created_at'),)

  id: Mapped[int] = mapped_column(Integer, primary_key=True)
  project_id: Mapped[int] = mapped_column(ForeignKey('projects.id'), nullable=False, index=True)
  defect_id: Mapped[int] = mapped_column(ForeignKey('defects.id'), nullable=False, index=True)
  event_type: Mapped[str] = mapped_column(String(60), nullable=False)
  old_value: Mapped[str | None] = mapped_column(String(500), nullable=True)
  new_value: Mapped[str | None] = mapped_column(String(500), nullable=True)
  safe_message: Mapped[str | None] = mapped_column(String(500), nullable=True)
  created_by: Mapped[int] = mapped_column(ForeignKey('operators.id'), nullable=False)
  created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

  defect: Mapped[Defect] = relationship(back_populates='history')


class DefectEvidenceLink(Base):
  __tablename__ = 'defect_evidence_links'
  __table_args__ = (
    UniqueConstraint('defect_id', 'manual_evidence_id', name='uq_defect_manual_evidence'),
    UniqueConstraint('defect_id', 'execution_artifact_id', name='uq_defect_execution_artifact'),
  )

  id: Mapped[int] = mapped_column(Integer, primary_key=True)
  project_id: Mapped[int] = mapped_column(ForeignKey('projects.id'), nullable=False, index=True)
  defect_id: Mapped[int] = mapped_column(ForeignKey('defects.id'), nullable=False, index=True)
  manual_evidence_id: Mapped[int | None] = mapped_column(ForeignKey('manual_evidence.id'), nullable=True)
  execution_artifact_id: Mapped[int | None] = mapped_column(ForeignKey('execution_artifacts.id'), nullable=True)
  link_type: Mapped[str] = mapped_column(String(30), nullable=False, default='SOURCE')
  created_by: Mapped[int] = mapped_column(ForeignKey('operators.id'), nullable=False)
  created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

  defect: Mapped[Defect] = relationship(back_populates='evidence_links')


class DefectRetest(Base):
  __tablename__ = 'defect_retests'
  __table_args__ = (Index('ix_defect_retests_defect_created', 'defect_id', 'created_at'),)

  id: Mapped[int] = mapped_column(Integer, primary_key=True)
  project_id: Mapped[int] = mapped_column(ForeignKey('projects.id'), nullable=False, index=True)
  defect_id: Mapped[int] = mapped_column(ForeignKey('defects.id'), nullable=False, index=True)
  manual_run_id: Mapped[int | None] = mapped_column(ForeignKey('manual_test_runs.id'), nullable=True)
  automated_run_id: Mapped[int | None] = mapped_column(ForeignKey('automated_runs.id'), nullable=True)
  test_case_id: Mapped[int | None] = mapped_column(ForeignKey('managed_test_cases.id'), nullable=True)
  test_case_version: Mapped[int | None] = mapped_column(Integer, nullable=True)
  target_id: Mapped[int | None] = mapped_column(ForeignKey('connection_targets.id'), nullable=True)
  target_version: Mapped[int | None] = mapped_column(Integer, nullable=True)
  result_status: Mapped[str] = mapped_column(String(30), nullable=False, default='PLANNED')
  safe_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
  created_by: Mapped[int] = mapped_column(ForeignKey('operators.id'), nullable=False)
  created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

  defect: Mapped[Defect] = relationship(back_populates='retests')
