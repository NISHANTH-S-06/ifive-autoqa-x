"""Phase 14 – Enterprise Autonomous AI QA Operating System (AI QA OS) models."""
from datetime import datetime
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


# ─── Module 1: AI Enterprise Command Brain ───────────────────────────────────

class EnterpriseBrainRun(Base):
    """Enterprise Brain orchestration runs, goal decomposition, and decision trees."""
    __tablename__ = 'enterprise_brain_runs'
    __table_args__ = (
        Index('ix_brain_runs_status', 'run_status'),
        Index('ix_brain_runs_project', 'project_id'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    project_id: Mapped[int | None] = mapped_column(ForeignKey('projects.id'), nullable=True)
    goal_description: Mapped[str] = mapped_column(Text, nullable=False)
    run_status: Mapped[str] = mapped_column(String(30), nullable=False, default='QUEUED')
    # QUEUED | RUNNING | COMPLETED | FAILED | PAUSED
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    decision_tree_json: Mapped[str] = mapped_column(Text, nullable=False, default='{}')
    dag_tasks_json: Mapped[str] = mapped_column(Text, nullable=False, default='[]')
    execution_plan_json: Mapped[str] = mapped_column(Text, nullable=False, default='{}')
    resource_allocation_json: Mapped[str] = mapped_column(Text, nullable=False, default='{}')
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


# ─── Module 2: Autonomous Workflow Composer ──────────────────────────────────

class WorkflowTemplate(Base):
    """Visual QA workflow templates."""
    __tablename__ = 'workflow_templates'
    __table_args__ = (
        Index('ix_workflow_templates_category', 'category'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    template_name: Mapped[str] = mapped_column(String(150), nullable=False)
    category: Mapped[str] = mapped_column(String(60), nullable=False, default='QA_PIPELINE')
    # QA_PIPELINE | REGRESSION | RELEASE_CHECK | INCIDENT_RESPONSE | ONBOARDING
    description: Mapped[str] = mapped_column(Text, nullable=False, default='')
    graph_definition_json: Mapped[str] = mapped_column(Text, nullable=False, default='{}')
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_by: Mapped[int | None] = mapped_column(ForeignKey('operators.id'), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


class WorkflowExecution(Base):
    """Running instance of a visual workflow."""
    __tablename__ = 'workflow_executions'
    __table_args__ = (
        Index('ix_workflow_executions_status', 'execution_status'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    template_id: Mapped[int | None] = mapped_column(ForeignKey('workflow_templates.id'), nullable=True)
    execution_name: Mapped[str] = mapped_column(String(150), nullable=False)
    execution_status: Mapped[str] = mapped_column(String(30), nullable=False, default='PENDING')
    # PENDING | RUNNING | COMPLETED | FAILED | CANCELLED
    current_step_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    state_json: Mapped[str] = mapped_column(Text, nullable=False, default='{}')
    execution_log_json: Mapped[str] = mapped_column(Text, nullable=False, default='[]')
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


# ─── Module 3: Enterprise AI Agents Marketplace ──────────────────────────────

class AgentPackage(Base):
    """Custom AI agent package registry."""
    __tablename__ = 'agent_packages'
    __table_args__ = (
        Index('ix_agent_packages_category', 'agent_category'),
        Index('ix_agent_packages_status', 'install_status'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    agent_name: Mapped[str] = mapped_column(String(150), nullable=False)
    agent_key: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    agent_category: Mapped[str] = mapped_column(String(60), nullable=False)
    # SECURITY | ACCESSIBILITY | FINANCE | PERFORMANCE | SAP | CRM | COMPLIANCE | BROWSER | DATABASE | API
    version: Mapped[str] = mapped_column(String(30), nullable=False, default='1.0.0')
    description: Mapped[str] = mapped_column(Text, nullable=False)
    install_status: Mapped[str] = mapped_column(String(30), nullable=False, default='AVAILABLE')
    # AVAILABLE | INSTALLED | UPDATING | ERROR
    health_status: Mapped[str] = mapped_column(String(30), nullable=False, default='HEALTHY')
    permissions_json: Mapped[str] = mapped_column(Text, nullable=False, default='[]')
    config_json: Mapped[str] = mapped_column(Text, nullable=False, default='{}')
    installed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


# ─── Module 4: AI Business Process Understanding ─────────────────────────────

class BusinessProcess(Base):
    """Industry-specific domain business flow graphs."""
    __tablename__ = 'business_processes'
    __table_args__ = (
        Index('ix_business_processes_domain', 'domain_type'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int | None] = mapped_column(ForeignKey('projects.id'), nullable=True)
    process_name: Mapped[str] = mapped_column(String(150), nullable=False)
    domain_type: Mapped[str] = mapped_column(String(60), nullable=False)
    # HRMS | PAYROLL | RECRUITMENT | CRM | SALES | INVENTORY | MANUFACTURING | FINANCE | PROCUREMENT | HEALTHCARE | INSURANCE | BANKING | EDUCATION | ERP
    risk_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    is_critical_path: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    flow_graph_json: Mapped[str] = mapped_column(Text, nullable=False, default='{}')
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


class BusinessRule(Base):
    """Critical transaction validation rules."""
    __tablename__ = 'business_rules'
    __table_args__ = (
        Index('ix_business_rules_process', 'process_id'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    process_id: Mapped[int] = mapped_column(ForeignKey('business_processes.id'), nullable=False)
    rule_name: Mapped[str] = mapped_column(String(150), nullable=False)
    rule_condition: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(String(30), nullable=False, default='HIGH')
    # CRITICAL | HIGH | MEDIUM | LOW
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


# ─── Module 5: Autonomous Release Simulation ─────────────────────────────────

class ReleaseSimulation(Base):
    """Pre-release simulation records."""
    __tablename__ = 'release_simulations'
    __table_args__ = (
        Index('ix_release_simulations_version', 'release_version'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    release_version: Mapped[str] = mapped_column(String(60), nullable=False)
    simulated_by: Mapped[int | None] = mapped_column(ForeignKey('operators.id'), nullable=True)
    rollback_probability_pct: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    predicted_failures_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    perf_degradation_pct: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    financial_risk_usd: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    customer_impact_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    breakdown_json: Mapped[str] = mapped_column(Text, nullable=False, default='{}')
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


# ─── Module 7: Autonomous Incident Commander ─────────────────────────────────

class Incident(Base):
    """Autonomous incident records."""
    __tablename__ = 'incidents'
    __table_args__ = (
        Index('ix_incidents_status', 'incident_status'),
        Index('ix_incidents_severity', 'severity'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    incident_number: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    severity: Mapped[str] = mapped_column(String(30), nullable=False, default='SEV-2')
    # SEV-1 | SEV-2 | SEV-3 | SEV-4
    incident_status: Mapped[str] = mapped_column(String(30), nullable=False, default='OPEN')
    # OPEN | INVESTIGATING | IDENTIFIED | MONITORING | RESOLVED
    assigned_team: Mapped[str] = mapped_column(String(100), nullable=False, default='SRE / QA')
    root_cause_summary: Mapped[str] = mapped_column(Text, nullable=False, default='')
    predicted_eta_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=60)
    recommendations_json: Mapped[str] = mapped_column(Text, nullable=False, default='[]')
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class IncidentTimeline(Base):
    """Incident evidence and timeline events."""
    __tablename__ = 'incident_timelines'
    __table_args__ = (
        Index('ix_incident_timelines_incident', 'incident_id'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    incident_id: Mapped[int] = mapped_column(ForeignKey('incidents.id'), nullable=False)
    event_type: Mapped[str] = mapped_column(String(60), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    evidence_json: Mapped[str] = mapped_column(Text, nullable=False, default='{}')
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


# ─── Module 8: Enterprise Knowledge Universe ────────────────────────────────

class KnowledgeUniverseNode(Base):
    """18-tier graph node."""
    __tablename__ = 'knowledge_universe_nodes'
    __table_args__ = (
        Index('ix_ku_nodes_type', 'node_type'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    node_key: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    label: Mapped[str] = mapped_column(String(200), nullable=False)
    node_type: Mapped[str] = mapped_column(String(60), nullable=False)
    # COMPANY | PRODUCT | MODULE | PAGE | COMPONENT | API | DATABASE | INFRASTRUCTURE | CLOUD | USER | ROLE | RULE | TEST | EXECUTION | EVIDENCE | BASELINE | INCIDENT | RELEASE
    attributes_json: Mapped[str] = mapped_column(Text, nullable=False, default='{}')
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


class KnowledgeUniverseEdge(Base):
    """18-tier graph connection."""
    __tablename__ = 'knowledge_universe_edges'
    __table_args__ = (
        Index('ix_ku_edges_source', 'source_node_id'),
        Index('ix_ku_edges_target', 'target_node_id'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_node_id: Mapped[int] = mapped_column(ForeignKey('knowledge_universe_nodes.id'), nullable=False)
    target_node_id: Mapped[int] = mapped_column(ForeignKey('knowledge_universe_nodes.id'), nullable=False)
    relationship_type: Mapped[str] = mapped_column(String(60), nullable=False)
    # CONTAINS | DEPENDS_ON | EXECUTES | CALLS | VALIDATES | BLOCKS | IMPACTS
    weight: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


# ─── Module 9: AI Executive Advisor ───────────────────────────────────────────

class ExecutiveInsight(Base):
    """Executive advisor interaction and insights repository."""
    __tablename__ = 'executive_insights'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    query_text: Mapped[str] = mapped_column(Text, nullable=False)
    resolved_intent: Mapped[str] = mapped_column(String(100), nullable=False)
    advice_summary: Mapped[str] = mapped_column(Text, nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.95)
    details_json: Mapped[str] = mapped_column(Text, nullable=False, default='{}')
    asked_by: Mapped[int | None] = mapped_column(ForeignKey('operators.id'), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


# ─── Module 10: Autonomous Optimization Engine V2 ───────────────────────────

class OptimizationHistory(Base):
    """V2 autonomous optimization logs."""
    __tablename__ = 'optimization_histories'
    __table_args__ = (
        Index('ix_opt_hist_target', 'target_subsystem'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    target_subsystem: Mapped[str] = mapped_column(String(60), nullable=False)
    # BROWSER_POOL | WORKER_QUEUE | PARALLELISM | LOCATORS | TIMEOUTS | HEALING | AI_MODELS | COST
    before_state_json: Mapped[str] = mapped_column(Text, nullable=False, default='{}')
    after_state_json: Mapped[str] = mapped_column(Text, nullable=False, default='{}')
    gain_pct: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    reasoning: Mapped[str] = mapped_column(Text, nullable=False, default='')
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


# ─── Module 11: Enterprise Governance Center ─────────────────────────────────

class GovernancePolicy(Base):
    """Enterprise policies and quality gates."""
    __tablename__ = 'governance_policies'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    policy_name: Mapped[str] = mapped_column(String(150), nullable=False)
    policy_type: Mapped[str] = mapped_column(String(60), nullable=False)
    # RETENTION | DATA_CLASSIFICATION | RELEASE_GATE | SECURITY_POLICY | AUDIT_POLICY
    rules_json: Mapped[str] = mapped_column(Text, nullable=False, default='{}')
    is_enforced: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


# ─── Module 12: AI Forecast Center ───────────────────────────────────────────

class ForecastMetric(Base):
    """Predictive forecasting metrics store."""
    __tablename__ = 'forecast_metrics'
    __table_args__ = (
        Index('ix_forecast_metrics_type', 'metric_type'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    metric_type: Mapped[str] = mapped_column(String(60), nullable=False)
    # BUG_DENSITY | TECH_DEBT | VELOCITY | AUTOMATION_GROWTH | EXECUTION_COST | CLOUD_USAGE | FLAKY_TESTS
    horizon_days: Mapped[int] = mapped_column(Integer, nullable=False, default=30)
    forecasted_value: Mapped[float] = mapped_column(Float, nullable=False)
    confidence_interval_low: Mapped[float] = mapped_column(Float, nullable=False)
    confidence_interval_high: Mapped[float] = mapped_column(Float, nullable=False)
    trend_json: Mapped[str] = mapped_column(Text, nullable=False, default='{}')
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


# ─── Module 13: Enterprise Report Factory V2 ─────────────────────────────────

class EnterpriseReport(Base):
    """Generated enterprise multi-persona reports."""
    __tablename__ = 'enterprise_reports'
    __table_args__ = (
        Index('ix_enterprise_reports_persona', 'report_persona'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    report_title: Mapped[str] = mapped_column(String(200), nullable=False)
    report_persona: Mapped[str] = mapped_column(String(60), nullable=False)
    # EXECUTIVE | TECHNICAL | DEVELOPER | QA | COMPLIANCE | AUDIT | BOARD
    export_format: Mapped[str] = mapped_column(String(20), nullable=False, default='PDF')
    # PDF | EXCEL | POWERPOINT | WORD | HTML | JSON | MARKDOWN
    content_json: Mapped[str] = mapped_column(Text, nullable=False, default='{}')
    download_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    generated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
