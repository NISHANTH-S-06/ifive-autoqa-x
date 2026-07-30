from datetime import datetime
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class AdvancedValidationProfile(Base):
    __tablename__ = 'advanced_validation_profiles'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey('test_projects.id'), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    api_validation_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    db_validation_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    accessibility_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)  # OFF by default
    performance_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)    # OFF by default
    console_network_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    evidence_completeness_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    created_by: Mapped[int] = mapped_column(ForeignKey('operators.id'), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    api_definitions: Mapped[list['ApiValidationDefinition']] = relationship(back_populates='profile', cascade='all, delete-orphan')
    db_definitions: Mapped[list['DatabaseValidationDefinition']] = relationship(back_populates='profile', cascade='all, delete-orphan')
    accessibility_definitions: Mapped[list['AccessibilityValidationDefinition']] = relationship(back_populates='profile', cascade='all, delete-orphan')
    performance_definitions: Mapped[list['PerformanceValidationDefinition']] = relationship(back_populates='profile', cascade='all, delete-orphan')


class ApiValidationDefinition(Base):
    __tablename__ = 'api_validation_definitions'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    validation_profile_id: Mapped[int] = mapped_column(ForeignKey('advanced_validation_profiles.id'), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    method: Mapped[str] = mapped_column(String(10), nullable=False, default='GET')  # GET, POST, PUT, PATCH, DELETE
    path: Mapped[str] = mapped_column(String(255), nullable=False)
    request_headers_template: Mapped[str | None] = mapped_column(Text, nullable=True)
    request_body_template: Mapped[str | None] = mapped_column(Text, nullable=True)
    expected_status: Mapped[int] = mapped_column(Integer, nullable=False, default=200)
    expected_schema_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    expected_json_paths: Mapped[str | None] = mapped_column(Text, nullable=True)
    timeout_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=5000)
    auth_profile_reference: Mapped[str | None] = mapped_column(String(100), nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    profile: Mapped[AdvancedValidationProfile] = relationship(back_populates='api_definitions')


class DatabaseValidationDefinition(Base):
    __tablename__ = 'database_validation_definitions'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    validation_profile_id: Mapped[int] = mapped_column(ForeignKey('advanced_validation_profiles.id'), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    connection_profile_reference: Mapped[str] = mapped_column(String(100), nullable=False)
    query_template: Mapped[str] = mapped_column(Text, nullable=False)
    expected_result_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    timeout_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=5000)
    max_rows: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    profile: Mapped[AdvancedValidationProfile] = relationship(back_populates='db_definitions')


class AccessibilityValidationDefinition(Base):
    __tablename__ = 'accessibility_validation_definitions'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    validation_profile_id: Mapped[int] = mapped_column(ForeignKey('advanced_validation_profiles.id'), nullable=False, index=True)
    route: Mapped[str] = mapped_column(String(255), nullable=False)
    standard: Mapped[str] = mapped_column(String(50), nullable=False, default='WCAG21AA')
    severity_threshold: Mapped[str] = mapped_column(String(20), nullable=False, default='critical')
    include_rules: Mapped[str | None] = mapped_column(Text, nullable=True)
    exclude_rules: Mapped[str | None] = mapped_column(Text, nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    profile: Mapped[AdvancedValidationProfile] = relationship(back_populates='accessibility_definitions')


class PerformanceValidationDefinition(Base):
    __tablename__ = 'performance_validation_definitions'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    validation_profile_id: Mapped[int] = mapped_column(ForeignKey('advanced_validation_profiles.id'), nullable=False, index=True)
    route: Mapped[str] = mapped_column(String(255), nullable=False)
    metric: Mapped[str] = mapped_column(String(50), nullable=False)
    warning_threshold: Mapped[float] = mapped_column(Float, nullable=False)
    failure_threshold: Mapped[float] = mapped_column(Float, nullable=False)
    sample_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    profile: Mapped[AdvancedValidationProfile] = relationship(back_populates='performance_definitions')


class AdvancedValidationRun(Base):
    __tablename__ = 'advanced_validation_runs'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey('test_projects.id'), nullable=False, index=True)
    automated_run_id: Mapped[int | None] = mapped_column(ForeignKey('automated_runs.id'), nullable=True, index=True)
    test_plan_id: Mapped[int] = mapped_column(ForeignKey('test_plans.id'), nullable=False, index=True)
    test_plan_version_id: Mapped[int] = mapped_column(ForeignKey('test_plan_versions.id'), nullable=False, index=True)
    validation_profile_id: Mapped[int] = mapped_column(ForeignKey('advanced_validation_profiles.id'), nullable=False, index=True)

    status: Mapped[str] = mapped_column(String(30), nullable=False, default='RUNNING')  # PASS, FAIL, BLOCKED, PASS_WITH_WARNINGS
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    summary_json: Mapped[str] = mapped_column(Text, nullable=False, default='{}')
    result_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)

    results: Mapped[list['AdvancedValidationResult']] = relationship(back_populates='run', cascade='all, delete-orphan')


class AdvancedValidationResult(Base):
    __tablename__ = 'advanced_validation_results'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    advanced_validation_run_id: Mapped[int] = mapped_column(ForeignKey('advanced_validation_runs.id'), nullable=False, index=True)
    validator_type: Mapped[str] = mapped_column(String(30), nullable=False)  # API, DB, ACCESSIBILITY, PERFORMANCE, CONSOLE_NETWORK, EVIDENCE
    definition_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False)  # PASS, FAIL, WARNING, BLOCKED, INFO
    severity: Mapped[str] = mapped_column(String(20), nullable=False, default='INFO')  # CRITICAL, SERIOUS, MODERATE, MINOR, INFO
    expected_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    actual_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    duration_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    artifact_ids: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array of artifact IDs
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    run: Mapped[AdvancedValidationRun] = relationship(back_populates='results')


class LocalSchedule(Base):
    __tablename__ = 'local_schedules'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey('test_projects.id'), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    cron_expression: Mapped[str] = mapped_column(String(60), nullable=False)
    timezone: Mapped[str] = mapped_column(String(60), nullable=False, default='UTC')

    approved_test_plan_id: Mapped[int] = mapped_column(ForeignKey('test_plans.id'), nullable=False, index=True)
    approved_version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    validation_profile_id: Mapped[int] = mapped_column(ForeignKey('advanced_validation_profiles.id'), nullable=False, index=True)
    browser: Mapped[str] = mapped_column(String(30), nullable=False, default='chromium')

    created_by: Mapped[int] = mapped_column(ForeignKey('operators.id'), nullable=False)
    approved_by: Mapped[int | None] = mapped_column(ForeignKey('operators.id'), nullable=True)

    last_run_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    next_run_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
