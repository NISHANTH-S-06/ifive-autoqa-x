"""Phase 16 – Enterprise Autonomous Software Engineering Intelligence Platform (ASEIP) models."""
from datetime import datetime
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


# ─── Module 1: Software Knowledge Lake V2 ─────────────────────────────────────

class KnowledgeLakeV2Document(Base):
    """Multi-source ingestion document index with vector/hybrid search tags."""
    __tablename__ = 'knowledge_lake_v2_documents'
    __table_args__ = (
        Index('ix_kl_v2_source_type', 'source_type'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_type: Mapped[str] = mapped_column(String(60), nullable=False)
    # REQUIREMENT | STORY | ARCH_DOC | OPENAPI | DB_SCHEMA | COMMIT | PR | BUILD_LOG | CICD_LOG | QA_REPORT | SECURITY_REPORT | PROD_LOG | FEEDBACK
    title: Mapped[str] = mapped_column(String(250), nullable=False)
    content_text: Mapped[str] = mapped_column(Text, nullable=False)
    vector_embedding_json: Mapped[str] = mapped_column(Text, nullable=False, default='[]')
    hybrid_search_tags_json: Mapped[str] = mapped_column(Text, nullable=False, default='[]')
    metadata_json: Mapped[str] = mapped_column(Text, nullable=False, default='{}')
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


# ─── Module 2: AI Requirement Intelligence ───────────────────────────────────

class RequirementRecord(Base):
    """Requirement intelligence record with risk matrix & ambiguity flags."""
    __tablename__ = 'requirement_records'
    __table_args__ = (
        Index('ix_requirement_type', 'requirement_type'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    requirement_code: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    requirement_type: Mapped[str] = mapped_column(String(60), nullable=False)
    # BUSINESS | FUNCTIONAL | NON_FUNCTIONAL
    description: Mapped[str] = mapped_column(Text, nullable=False)
    acceptance_criteria_json: Mapped[str] = mapped_column(Text, nullable=False, default='[]')
    is_ambiguous: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_conflicting: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    risk_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    analysis_notes: Mapped[str] = mapped_column(Text, nullable=False, default='')
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


# ─── Module 3: Autonomous Requirement → Test Traceability ───────────────────

class TraceabilityMapping(Base):
    """End-to-end 10-tier requirement to release traceability mapping."""
    __tablename__ = 'traceability_mappings'
    __table_args__ = (
        Index('ix_traceability_req', 'requirement_code'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    requirement_code: Mapped[str] = mapped_column(String(100), nullable=False)
    user_story_key: Mapped[str] = mapped_column(String(100), nullable=False)
    design_doc_ref: Mapped[str] = mapped_column(String(200), nullable=False)
    api_endpoint: Mapped[str] = mapped_column(String(200), nullable=False)
    db_table: Mapped[str] = mapped_column(String(100), nullable=False)
    ui_page: Mapped[str] = mapped_column(String(150), nullable=False)
    test_scenario: Mapped[str] = mapped_column(String(200), nullable=False)
    evidence_url: Mapped[str] = mapped_column(String(300), nullable=False)
    defect_key: Mapped[str | None] = mapped_column(String(100), nullable=True)
    release_version: Mapped[str] = mapped_column(String(60), nullable=False)
    is_coverage_complete: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


# ─── Module 4: Architecture Intelligence ─────────────────────────────────────

class ArchitectureNode(Base):
    """Architecture intelligence graph node."""
    __tablename__ = 'architecture_nodes'
    __table_args__ = (
        Index('ix_arch_nodes_type', 'node_type'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    node_key: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    label: Mapped[str] = mapped_column(String(200), nullable=False)
    node_type: Mapped[str] = mapped_column(String(60), nullable=False)
    # MICROSERVICE | MONOLITH | EVENT_QUEUE | KAFKA | RABBITMQ | REDIS | DATABASE | EXTERNAL_API
    is_bottleneck: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    risk_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    attributes_json: Mapped[str] = mapped_column(Text, nullable=False, default='{}')
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


class ArchitectureEdge(Base):
    """Architecture dependency & call flow edge."""
    __tablename__ = 'architecture_edges'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_node_id: Mapped[int] = mapped_column(ForeignKey('architecture_nodes.id'), nullable=False)
    target_node_id: Mapped[int] = mapped_column(ForeignKey('architecture_nodes.id'), nullable=False)
    call_protocol: Mapped[str] = mapped_column(String(40), nullable=False, default='HTTP_REST')
    latency_p95_ms: Mapped[float] = mapped_column(Float, nullable=False, default=12.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


# ─── Module 5: AI Code Quality Governor ─────────────────────────────────────

class CodeQualityViolation(Base):
    """Multi-language code quality governor finding."""
    __tablename__ = 'code_quality_violations'
    __table_args__ = (
        Index('ix_cq_lang', 'language'),
        Index('ix_cq_category', 'category'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    file_path: Mapped[str] = mapped_column(String(300), nullable=False)
    language: Mapped[str] = mapped_column(String(40), nullable=False)
    # PYTHON | TYPESCRIPT | REACT | NODE | JAVA | DOTNET | GO | SQL
    category: Mapped[str] = mapped_column(String(60), nullable=False)
    # DEAD_CODE | CODE_DUPLICATION | SECURITY | PERFORMANCE | ARCH_VIOLATION | TECH_DEBT
    line_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    recommendation: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(String(30), nullable=False, default='MEDIUM')
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


# ─── Module 6: Autonomous Release Certification ─────────────────────────────

class ReleaseCertification(Base):
    """Autonomous release certification decision record."""
    __tablename__ = 'release_certifications'
    __table_args__ = (
        Index('ix_release_cert_version', 'release_version'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    release_version: Mapped[str] = mapped_column(String(60), nullable=False)
    certification_status: Mapped[str] = mapped_column(String(40), nullable=False, default='CERTIFIED')
    # CERTIFIED | CONDITIONALLY_CERTIFIED | REJECTED
    overall_quality_score: Mapped[float] = mapped_column(Float, nullable=False)
    qa_score: Mapped[float] = mapped_column(Float, nullable=False)
    security_score: Mapped[float] = mapped_column(Float, nullable=False)
    performance_score: Mapped[float] = mapped_column(Float, nullable=False)
    accessibility_score: Mapped[float] = mapped_column(Float, nullable=False)
    compliance_score: Mapped[float] = mapped_column(Float, nullable=False)
    business_rules_score: Mapped[float] = mapped_column(Float, nullable=False)
    report_summary: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


# ─── Module 7: Production Observability AI ───────────────────────────────────

class ObservabilityMetricV2(Base):
    """Production APM observability metrics and predictions."""
    __tablename__ = 'observability_metrics_v2'
    __table_args__ = (
        Index('ix_obs_v2_service', 'service_name'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    service_name: Mapped[str] = mapped_column(String(100), nullable=False)
    error_rate_pct: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    latency_p99_ms: Mapped[float] = mapped_column(Float, nullable=False, default=45.0)
    predicted_incident_risk: Mapped[float] = mapped_column(Float, nullable=False, default=0.05)
    prediction_summary: Mapped[str] = mapped_column(Text, nullable=False, default='Service health optimal.')
    metrics_json: Mapped[str] = mapped_column(Text, nullable=False, default='{}')
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


# ─── Module 8: Customer Experience Intelligence ──────────────────────────────

class CustomerFeedbackItem(Base):
    """Customer experience item correlated to Bug → Dev → Release → Root Cause."""
    __tablename__ = 'customer_feedback_items'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_type: Mapped[str] = mapped_column(String(60), nullable=False)
    # SUPPORT_TICKET | FEEDBACK | APP_REVIEW | NPS | CRASH_REPORT
    headline: Mapped[str] = mapped_column(String(200), nullable=False)
    sentiment_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.8)
    nps_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    correlated_bug_key: Mapped[str | None] = mapped_column(String(100), nullable=True)
    assigned_developer: Mapped[str | None] = mapped_column(String(100), nullable=True)
    release_version: Mapped[str | None] = mapped_column(String(60), nullable=True)
    root_cause: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


# ─── Module 9: Autonomous Quality Digital Twin V2 ────────────────────────────

class DigitalTwinV2Node(Base):
    """Live software digital twin node representation."""
    __tablename__ = 'digital_twin_v2_nodes'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    twin_key: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    entity_name: Mapped[str] = mapped_column(String(200), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(60), nullable=False)
    # SERVICE | INFRASTRUCTURE | API | USER | DATABASE | BUSINESS_RULE | DEPLOYMENT | RELEASE | QUALITY | RISK
    health_status: Mapped[str] = mapped_column(String(30), nullable=False, default='HEALTHY')
    live_state_json: Mapped[str] = mapped_column(Text, nullable=False, default='{}')
    last_synced_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


# ─── Module 10: Enterprise Policy Engine ─────────────────────────────────────

class PolicyRule(Base):
    """Enterprise policy engine rule for auto-enforcement."""
    __tablename__ = 'policy_rules'
    __table_args__ = (
        Index('ix_policy_cat', 'policy_category'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    rule_name: Mapped[str] = mapped_column(String(150), nullable=False)
    policy_category: Mapped[str] = mapped_column(String(60), nullable=False)
    # QUALITY | RELEASE | COMPLIANCE | SECURITY | NAMING | TESTING | APPROVAL
    rule_condition: Mapped[str] = mapped_column(Text, nullable=False)
    action_on_violation: Mapped[str] = mapped_column(String(60), nullable=False, default='BLOCK_RELEASE')
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


# ─── Module 11: AI Executive Decision Engine ─────────────────────────────────

class ExecutiveDecisionRecord(Base):
    """AI executive recommendation record with reasoning."""
    __tablename__ = 'executive_decision_records'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    decision_type: Mapped[str] = mapped_column(String(60), nullable=False)
    # DELAY_RELEASE | INCREASE_TESTING | ROLLBACK | DEPLOY_GRADUALLY | INCREASE_MONITORING | ADD_RESOURCES
    recommendation_summary: Mapped[str] = mapped_column(Text, nullable=False)
    reasoning_explanation: Mapped[str] = mapped_column(Text, nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.92)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


# ─── Module 12: Autonomous SDLC Orchestrator ─────────────────────────────────

class SDLCStageExecution(Base):
    """Autonomous SDLC stage execution coordinator record."""
    __tablename__ = 'sdlc_stage_executions'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    stage_name: Mapped[str] = mapped_column(String(60), nullable=False)
    # PLANNING | DEVELOPMENT | TESTING | RELEASE | PRODUCTION | MONITORING | LEARNING
    status: Mapped[str] = mapped_column(String(30), nullable=False, default='COMPLETED')
    scheduled_actions_json: Mapped[str] = mapped_column(Text, nullable=False, default='[]')
    execution_notes: Mapped[str] = mapped_column(Text, nullable=False, default='')
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
