from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


PROJECT_ROLES = ('OWNER', 'ADMIN', 'APPROVER', 'TESTER', 'VIEWER')
PROJECT_MEMBERSHIP_STATUSES = ('ACTIVE', 'INACTIVE')


class ProjectMember(Base):
  __tablename__ = 'project_members'
  __table_args__ = (
    CheckConstraint("role IN ('OWNER','ADMIN','APPROVER','TESTER','VIEWER')", name='ck_project_members_role'),
    CheckConstraint("status IN ('ACTIVE','INACTIVE')", name='ck_project_members_status'),
    UniqueConstraint('project_id', 'operator_id', name='uq_project_members_project_operator'),
    Index('ix_project_members_project_status', 'project_id', 'status'),
    Index('ix_project_members_operator_status', 'operator_id', 'status'),
    Index('ix_project_members_project_role', 'project_id', 'role'),
  )

  id: Mapped[int] = mapped_column(Integer, primary_key=True)
  project_id: Mapped[int] = mapped_column(ForeignKey('projects.id'), nullable=False)
  operator_id: Mapped[int] = mapped_column(ForeignKey('operators.id'), nullable=False)
  role: Mapped[str] = mapped_column(String(20), nullable=False)
  status: Mapped[str] = mapped_column(String(20), nullable=False, default='ACTIVE', server_default='ACTIVE')
  created_by: Mapped[int | None] = mapped_column(ForeignKey('operators.id'), nullable=True)
  joined_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
  created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
  updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
  deactivated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

  project: Mapped['Project'] = relationship(back_populates='members')


class ProjectBackfillReport(Base):
  __tablename__ = 'project_backfill_reports'
  __table_args__ = (
    Index('ix_project_backfill_reports_source', 'source_table', 'source_id'),
    Index('ix_project_backfill_reports_project', 'project_id'),
    Index('ix_project_backfill_reports_ambiguous', 'ambiguous'),
  )

  id: Mapped[int] = mapped_column(Integer, primary_key=True)
  source_table: Mapped[str] = mapped_column(String(80), nullable=False)
  source_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
  project_id: Mapped[int] = mapped_column(ForeignKey('projects.id'), nullable=False)
  decision: Mapped[str] = mapped_column(String(40), nullable=False)
  provenance: Mapped[str] = mapped_column(Text, nullable=False)
  ambiguous: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default='0')
  created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
