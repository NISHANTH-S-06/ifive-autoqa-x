from datetime import datetime
from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class TestPlan(Base):
    __tablename__ = 'test_plans'
    __table_args__ = (
        UniqueConstraint('project_id', 'external_task_import_id', name='uq_test_plans_project_import'),
        Index('ix_test_plans_status', 'status'),
        Index('ix_test_plans_created_by', 'created_by'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey('test_projects.id'), nullable=False, index=True)
    external_task_import_id: Mapped[int] = mapped_column(ForeignKey('external_task_imports.id'), nullable=False, index=True)
    source_task_id: Mapped[str] = mapped_column(String(60), nullable=False)
    source_revision: Mapped[int] = mapped_column(Integer, nullable=False)
    analysis_id: Mapped[str | None] = mapped_column(String(60), nullable=True)
    plan_code: Mapped[str] = mapped_column(String(60), nullable=False, unique=True, index=True)
    title: Mapped[str] = mapped_column(String(220), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default='DRAFT')
    current_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    approved_version_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    
    created_by: Mapped[int] = mapped_column(ForeignKey('operators.id'), nullable=False)
    submitted_by: Mapped[int | None] = mapped_column(ForeignKey('operators.id'), nullable=True)
    approved_by: Mapped[int | None] = mapped_column(ForeignKey('operators.id'), nullable=True)
    rejected_by: Mapped[int | None] = mapped_column(ForeignKey('operators.id'), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    rejected_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    execution_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    optional_regression_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    versions: Mapped[list['TestPlanVersion']] = relationship(back_populates='test_plan', order_by='TestPlanVersion.version_number', cascade='all, delete-orphan')


class TestPlanVersion(Base):
    __tablename__ = 'test_plan_versions'
    __table_args__ = (
        UniqueConstraint('test_plan_id', 'version_number', name='uq_test_plan_versions_plan_version'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    test_plan_id: Mapped[int] = mapped_column(ForeignKey('test_plans.id'), nullable=False, index=True)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    source_revision: Mapped[int] = mapped_column(Integer, nullable=False)
    provider: Mapped[str | None] = mapped_column(String(60), nullable=True)
    model: Mapped[str | None] = mapped_column(String(60), nullable=True)
    prompt_version: Mapped[str | None] = mapped_column(String(60), nullable=True)
    schema_version: Mapped[str | None] = mapped_column(String(60), nullable=True)
    input_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    output_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    plan_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    created_by: Mapped[int] = mapped_column(ForeignKey('operators.id'), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    immutable_snapshot_json: Mapped[str] = mapped_column(Text, nullable=False)

    test_plan: Mapped[TestPlan] = relationship(back_populates='versions')
    scenarios: Mapped[list['TestScenario']] = relationship(back_populates='version', order_by='TestScenario.order_index', cascade='all, delete-orphan')


class TestScenario(Base):
    __tablename__ = 'test_scenarios'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    test_plan_version_id: Mapped[int] = mapped_column(ForeignKey('test_plan_versions.id'), nullable=False, index=True)
    scenario_type: Mapped[str] = mapped_column(String(40), nullable=False) # PRIMARY, NEGATIVE, REGRESSION, BOUNDARY
    title: Mapped[str] = mapped_column(String(220), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    priority: Mapped[str] = mapped_column(String(20), nullable=False, default='P1')
    risk: Mapped[str] = mapped_column(String(20), nullable=False, default='MEDIUM')
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    mandatory: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    version: Mapped[TestPlanVersion] = relationship(back_populates='scenarios')
    steps: Mapped[list['TestStep']] = relationship(back_populates='scenario', order_by='TestStep.step_order', cascade='all, delete-orphan')


class TestStep(Base):
    __tablename__ = 'test_steps'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    scenario_id: Mapped[int] = mapped_column(ForeignKey('test_scenarios.id'), nullable=False, index=True)
    step_order: Mapped[int] = mapped_column(Integer, nullable=False)
    action: Mapped[str] = mapped_column(String(60), nullable=False)
    locator_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    input_value_reference: Mapped[str | None] = mapped_column(String(120), nullable=True)
    expected_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    timeout_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=10000)
    continue_on_failure: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    scenario: Mapped[TestScenario] = relationship(back_populates='steps')
