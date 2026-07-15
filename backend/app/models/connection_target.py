from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ConnectionTarget(Base):
  __tablename__ = 'connection_targets'
  __table_args__ = (
    UniqueConstraint('target_key', name='uq_connection_targets_key'),
    Index('ix_connection_targets_lifecycle', 'lifecycle_state'),
    Index('ix_connection_targets_environment', 'environment_type'),
    Index('ix_connection_targets_enabled', 'enabled'),
    Index('ix_connection_targets_host', 'normalized_host'),
    Index('ix_connection_targets_owner', 'owner_operator_id'),
  )

  id: Mapped[int] = mapped_column(Integer, primary_key=True)
  project_id: Mapped[int] = mapped_column(ForeignKey('projects.id'), nullable=False, index=True)
  target_key: Mapped[str] = mapped_column(String(60), nullable=False, index=True)
  name: Mapped[str] = mapped_column(String(180), nullable=False)
  description: Mapped[str | None] = mapped_column(Text, nullable=True)
  environment_type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
  base_url: Mapped[str] = mapped_column(String(1000), nullable=False)
  normalized_scheme: Mapped[str] = mapped_column(String(10), nullable=False)
  normalized_host: Mapped[str] = mapped_column(String(255), nullable=False)
  normalized_port: Mapped[int] = mapped_column(Integer, nullable=False)
  normalized_origin: Mapped[str] = mapped_column(String(500), nullable=False)
  allowed_probe_paths_json: Mapped[str] = mapped_column(Text, nullable=False)
  tls_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
  tls_verify: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
  connection_timeout_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
  lifecycle_state: Mapped[str] = mapped_column(String(20), nullable=False, default='DRAFT')
  enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
  owner_operator_id: Mapped[int | None] = mapped_column(ForeignKey('operators.id'), nullable=True)
  created_by: Mapped[int] = mapped_column(ForeignKey('operators.id'), nullable=False, index=True)
  reviewed_by: Mapped[int | None] = mapped_column(ForeignKey('operators.id'), nullable=True)
  approved_by: Mapped[int | None] = mapped_column(ForeignKey('operators.id'), nullable=True)
  created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
  updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)
  submitted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
  approved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
  rejected_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
  disabled_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
  archived_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
  rejection_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
  last_check_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
  last_check_status: Mapped[str | None] = mapped_column(String(30), nullable=True)
  execution_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
  execution_submitted_by: Mapped[int | None] = mapped_column(ForeignKey('operators.id'), nullable=True)
  execution_submitted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
  execution_approved_by: Mapped[int | None] = mapped_column(ForeignKey('operators.id'), nullable=True)
  execution_approved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
  version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

  versions: Mapped[list['ConnectionTargetVersion']] = relationship(back_populates='target', order_by='ConnectionTargetVersion.version_number')
  checks: Mapped[list['ConnectionCheck']] = relationship(back_populates='target')
  credential_profiles: Mapped[list['TargetCredentialProfile']] = relationship(back_populates='target')


class ConnectionTargetVersion(Base):
  __tablename__ = 'connection_target_versions'
  __table_args__ = (
    UniqueConstraint('target_id', 'version_number', name='uq_connection_target_versions_target_version'),
    Index('ix_connection_target_versions_target_version', 'target_id', 'version_number'),
  )

  id: Mapped[int] = mapped_column(Integer, primary_key=True)
  project_id: Mapped[int] = mapped_column(ForeignKey('projects.id'), nullable=False, index=True)
  target_id: Mapped[int] = mapped_column(ForeignKey('connection_targets.id'), nullable=False, index=True)
  version_number: Mapped[int] = mapped_column(Integer, nullable=False)
  snapshot_json: Mapped[str] = mapped_column(Text, nullable=False)
  change_summary: Mapped[str | None] = mapped_column(String(500), nullable=True)
  created_by: Mapped[int] = mapped_column(ForeignKey('operators.id'), nullable=False)
  created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
  source_state: Mapped[str] = mapped_column(String(20), nullable=False)

  target: Mapped[ConnectionTarget] = relationship(back_populates='versions')


class ConnectionCheck(Base):
  __tablename__ = 'connection_checks'
  __table_args__ = (
    UniqueConstraint('check_key', name='uq_connection_checks_key'),
    Index('ix_connection_checks_target_id', 'target_id'),
    Index('ix_connection_checks_created_at', 'created_at'),
    Index('ix_connection_checks_status', 'status'),
  )

  id: Mapped[int] = mapped_column(Integer, primary_key=True)
  project_id: Mapped[int] = mapped_column(ForeignKey('projects.id'), nullable=False, index=True)
  check_key: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
  target_id: Mapped[int] = mapped_column(ForeignKey('connection_targets.id'), nullable=False)
  target_version: Mapped[int] = mapped_column(Integer, nullable=False)
  probe_path: Mapped[str] = mapped_column(String(500), nullable=False)
  method: Mapped[str] = mapped_column(String(10), nullable=False)
  requested_origin: Mapped[str] = mapped_column(String(500), nullable=False)
  resolved_addresses_json: Mapped[str] = mapped_column(Text, nullable=False)
  started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
  completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
  duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
  status: Mapped[str] = mapped_column(String(30), nullable=False, default='PENDING')
  http_status: Mapped[int | None] = mapped_column(Integer, nullable=True)
  final_origin: Mapped[str | None] = mapped_column(String(500), nullable=True)
  redirect_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
  tls_protocol: Mapped[str | None] = mapped_column(String(80), nullable=True)
  tls_certificate_summary_json: Mapped[str | None] = mapped_column(Text, nullable=True)
  response_headers_json: Mapped[str] = mapped_column(Text, nullable=False, default='{}')
  response_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
  error_category: Mapped[str | None] = mapped_column(String(80), nullable=True)
  safe_error_message: Mapped[str | None] = mapped_column(String(500), nullable=True)
  initiated_by: Mapped[int] = mapped_column(ForeignKey('operators.id'), nullable=False)
  created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

  target: Mapped[ConnectionTarget] = relationship(back_populates='checks')


class TargetCredentialProfile(Base):
  __tablename__ = 'target_credential_profiles'
  __table_args__ = (
    UniqueConstraint('target_id', 'profile_name', name='uq_target_credential_profiles_target_name'),
    Index('ix_target_credential_profiles_target_id', 'target_id'),
  )

  id: Mapped[int] = mapped_column(Integer, primary_key=True)
  project_id: Mapped[int] = mapped_column(ForeignKey('projects.id'), nullable=False, index=True)
  target_id: Mapped[int] = mapped_column(ForeignKey('connection_targets.id'), nullable=False)
  profile_name: Mapped[str] = mapped_column(String(120), nullable=False)
  username_hint: Mapped[str | None] = mapped_column(String(160), nullable=True)
  secret_source: Mapped[str] = mapped_column(String(40), nullable=False, default='NONE')
  enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
  created_by: Mapped[int] = mapped_column(ForeignKey('operators.id'), nullable=False)
  created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
  updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
  last_used_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

  target: Mapped[ConnectionTarget] = relationship(back_populates='credential_profiles')
