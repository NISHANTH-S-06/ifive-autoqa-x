from datetime import datetime
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class AIDigitalQAEngineRecord(Base):
    __tablename__ = 'ai_digital_qa_records'
    __table_args__ = (
        Index('ix_ai_digital_qa_records_type', 'action_type'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int | None] = mapped_column(ForeignKey('projects.id'), nullable=True, index=True)
    action_type: Mapped[str] = mapped_column(String(60), nullable=False)
    # Types: REASONING | EXPLORATION | STRATEGY | EXEC_CONTROL | RCA | IMPACT
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    payload_json: Mapped[str] = mapped_column(Text, nullable=False, default='{}')
    reasoning_tree_json: Mapped[str] = mapped_column(Text, nullable=False, default='{}')
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.96)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


class DigitalTwinEntity(Base):
    __tablename__ = 'digital_twin_entities'
    __table_args__ = (
        Index('ix_digital_twin_entities_type', 'entity_type'),
        Index('ix_digital_twin_entities_key', 'entity_key'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int | None] = mapped_column(ForeignKey('companies.id'), nullable=True, index=True)
    product_id: Mapped[int | None] = mapped_column(ForeignKey('company_products.id'), nullable=True, index=True)
    entity_type: Mapped[str] = mapped_column(String(60), nullable=False)
    # Entity Types: PAGE | COMPONENT | FLOW | MODULE | API | DATABASE_ENTITY | BUSINESS_RULE | USER_JOURNEY
    entity_key: Mapped[str] = mapped_column(String(160), nullable=False)
    label: Mapped[str] = mapped_column(String(200), nullable=False)
    metadata_json: Mapped[str] = mapped_column(Text, nullable=False, default='{}')
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class ContinuousMonitorAlert(Base):
    __tablename__ = 'continuous_monitor_alerts'
    __table_args__ = (
        Index('ix_continuous_monitor_alerts_type', 'alert_type'),
        Index('ix_continuous_monitor_alerts_severity', 'severity'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int | None] = mapped_column(ForeignKey('companies.id'), nullable=True, index=True)
    target_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    alert_type: Mapped[str] = mapped_column(String(80), nullable=False)
    # Alert Types: UI_DRIFT | BROKEN_LINK | PERF_DEGRADATION | API_FAILURE | CERT_EXPIRY | SECURITY_HEADER_CHANGE | A11Y_VIOLATION
    severity: Mapped[str] = mapped_column(String(30), nullable=False, default='MEDIUM')
    details_json: Mapped[str] = mapped_column(Text, nullable=False, default='{}')
    is_resolved: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


class PredictiveQualityMetric(Base):
    __tablename__ = 'predictive_quality_metrics'
    __table_args__ = (
        Index('ix_predictive_quality_metrics_type', 'metric_type'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int | None] = mapped_column(ForeignKey('projects.id'), nullable=True, index=True)
    metric_type: Mapped[str] = mapped_column(String(80), nullable=False)
    # Metric Types: FAILURE_PROBABILITY | UNSTABLE_MODULE | FLAKY_TEST | DEV_QUALITY_TREND | BUG_DENSITY
    target_entity: Mapped[str] = mapped_column(String(160), nullable=False)
    predicted_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.95)
    details_json: Mapped[str] = mapped_column(Text, nullable=False, default='{}')
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


class SelfOptimizationLog(Base):
    __tablename__ = 'self_optimization_logs'
    __table_args__ = (
        Index('ix_self_optimization_logs_type', 'optimization_type'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    optimization_type: Mapped[str] = mapped_column(String(80), nullable=False)
    # Types: EXECUTION_SPEED | BROWSER_ALLOCATION | LOCATOR_QUALITY | RETRY_STRATEGY | TEST_PRIORITIZATION
    improvement_summary: Mapped[str] = mapped_column(String(250), nullable=False)
    metrics_before_json: Mapped[str] = mapped_column(Text, nullable=False, default='{}')
    metrics_after_json: Mapped[str] = mapped_column(Text, nullable=False, default='{}')
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
