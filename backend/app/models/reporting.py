from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ReportExport(Base):
  __tablename__ = 'report_exports'
  __table_args__ = (
    UniqueConstraint('export_key', name='uq_report_exports_key'),
  )

  id: Mapped[int] = mapped_column(Integer, primary_key=True)
  project_id: Mapped[int] = mapped_column(ForeignKey('projects.id'), nullable=False, index=True)
  export_key: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
  report_type: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
  export_format: Mapped[str] = mapped_column(String(10), nullable=False)
  filters_json: Mapped[str] = mapped_column(Text, nullable=False, default='{}')
  original_filename: Mapped[str] = mapped_column(String(180), nullable=False)
  stored_filename: Mapped[str] = mapped_column(String(180), nullable=False, unique=True)
  relative_path: Mapped[str] = mapped_column(String(500), nullable=False)
  mime_type: Mapped[str] = mapped_column(String(120), nullable=False)
  size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
  sha256: Mapped[str] = mapped_column(String(64), nullable=False)
  row_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
  created_by: Mapped[int] = mapped_column(ForeignKey('operators.id'), nullable=False, index=True)
  created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
  expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
  deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class ReportDefinition(Base):
  __tablename__ = 'report_definitions'
  __table_args__ = (
    UniqueConstraint('owner_operator_id', 'name', name='uq_report_definitions_owner_name'),
  )

  id: Mapped[int] = mapped_column(Integer, primary_key=True)
  project_id: Mapped[int] = mapped_column(ForeignKey('projects.id'), nullable=False, index=True)
  name: Mapped[str] = mapped_column(String(160), nullable=False)
  report_type: Mapped[str] = mapped_column(String(40), nullable=False)
  filters_json: Mapped[str] = mapped_column(Text, nullable=False, default='{}')
  frequency: Mapped[str] = mapped_column(String(20), nullable=False)
  enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
  owner_operator_id: Mapped[int] = mapped_column(ForeignKey('operators.id'), nullable=False, index=True)
  last_run_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
  next_run_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
  last_error: Mapped[str | None] = mapped_column(String(500), nullable=True)
  created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
  updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
