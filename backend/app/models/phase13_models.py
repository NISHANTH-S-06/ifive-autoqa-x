"""Phase 13 – Enterprise Autonomous AI QA Cloud Platform models."""
from datetime import datetime
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


# ─── Module 1: Distributed Execution Orchestrator ────────────────────────────

class ExecutionWorkerNode(Base):
    """Distributed worker node registry."""
    __tablename__ = 'execution_worker_nodes'
    __table_args__ = (
        Index('ix_exec_worker_nodes_status', 'worker_status'),
        Index('ix_exec_worker_nodes_region', 'region'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    worker_name: Mapped[str] = mapped_column(String(120), nullable=False)
    worker_status: Mapped[str] = mapped_column(String(30), nullable=False, default='IDLE')
    # IDLE | BUSY | UNHEALTHY | DRAINING | OFFLINE
    region: Mapped[str] = mapped_column(String(60), nullable=False, default='local')
    # local | us-east-1 | eu-west-1 | ap-south-1 | etc.
    capacity: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    active_jobs: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    browser_types_json: Mapped[str] = mapped_column(Text, nullable=False, default='["CHROMIUM"]')
    # Supported: CHROMIUM | FIREFOX | WEBKIT | EDGE | CHROME | MOBILE_CHROME | MOBILE_SAFARI
    jobs_completed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    jobs_failed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    avg_job_duration_ms: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    total_cost_usd: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    last_heartbeat: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    registered_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class ExecutionQueueItem(Base):
    """Distributed execution priority queue."""
    __tablename__ = 'execution_queue_items'
    __table_args__ = (
        Index('ix_exec_queue_status', 'queue_status'),
        Index('ix_exec_queue_priority', 'priority'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    project_id: Mapped[int | None] = mapped_column(ForeignKey('projects.id'), nullable=True, index=True)
    queue_status: Mapped[str] = mapped_column(String(30), nullable=False, default='QUEUED')
    # QUEUED | ASSIGNED | RUNNING | COMPLETED | FAILED | RETRYING | CANCELLED
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    # 1 = highest, 10 = lowest
    browser_type: Mapped[str] = mapped_column(String(40), nullable=False, default='CHROMIUM')
    worker_id: Mapped[int | None] = mapped_column(ForeignKey('execution_worker_nodes.id'), nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_retries: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    estimated_duration_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=60000)
    actual_duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cost_usd: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    payload_json: Mapped[str] = mapped_column(Text, nullable=False, default='{}')
    result_json: Mapped[str] = mapped_column(Text, nullable=False, default='{}')
    queued_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


# ─── Module 2: Cloud Browser Farm ────────────────────────────────────────────

class BrowserFarmSession(Base):
    """Browser pool session tracking."""
    __tablename__ = 'browser_farm_sessions'
    __table_args__ = (
        Index('ix_browser_farm_sessions_status', 'session_status'),
        Index('ix_browser_farm_sessions_browser', 'browser_type'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    browser_type: Mapped[str] = mapped_column(String(40), nullable=False)
    # CHROMIUM | FIREFOX | WEBKIT | EDGE | CHROME | MOBILE_CHROME | MOBILE_SAFARI
    session_status: Mapped[str] = mapped_column(String(30), nullable=False, default='AVAILABLE')
    # AVAILABLE | RESERVED | ACTIVE | CLEANUP | UNHEALTHY | TERMINATED
    reserved_by_job_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    health_score: Mapped[float] = mapped_column(Float, nullable=False, default=100.0)
    recording_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    metrics_json: Mapped[str] = mapped_column(Text, nullable=False, default='{}')
    # cpu_pct, memory_mb, network_requests, page_load_ms
    region: Mapped[str] = mapped_column(String(60), nullable=False, default='local')
    reserved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    released_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


# ─── Module 3: Real-Time Execution Stream ────────────────────────────────────

class ExecutionStreamEvent(Base):
    """Execution real-time event log."""
    __tablename__ = 'execution_stream_events'
    __table_args__ = (
        Index('ix_exec_stream_events_job', 'job_id'),
        Index('ix_exec_stream_events_type', 'event_type'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_id: Mapped[str] = mapped_column(String(100), nullable=False)
    event_type: Mapped[str] = mapped_column(String(60), nullable=False)
    # STATUS | STEP | SCREENSHOT | LOG | NETWORK | CONSOLE | PERFORMANCE | AI_DECISION | VISUAL_COMPARE | BUG_CREATED
    event_payload_json: Mapped[str] = mapped_column(Text, nullable=False, default='{}')
    sequence_num: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


# ─── Module 4: Observability Platform ────────────────────────────────────────

class ObservabilityMetric(Base):
    """Observability metrics store."""
    __tablename__ = 'observability_metrics'
    __table_args__ = (
        Index('ix_obs_metrics_name', 'metric_name'),
        Index('ix_obs_metrics_source', 'metric_source'),
        Index('ix_obs_metrics_created', 'created_at'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int | None] = mapped_column(ForeignKey('projects.id'), nullable=True, index=True)
    metric_name: Mapped[str] = mapped_column(String(120), nullable=False)
    # browser_timing | api_timing | execution_timing | locator_heal | failure_rate | dashboard_load
    metric_value: Mapped[float] = mapped_column(Float, nullable=False)
    metric_unit: Mapped[str] = mapped_column(String(30), nullable=False, default='ms')
    metric_source: Mapped[str] = mapped_column(String(60), nullable=False, default='SYSTEM')
    # SYSTEM | BROWSER | API | EXECUTION | AI
    labels_json: Mapped[str] = mapped_column(Text, nullable=False, default='{}')
    trace_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


# ─── Module 5: Enterprise Analytics ──────────────────────────────────────────

class EnterpriseAnalyticsSnapshot(Base):
    """Periodic analytics snapshot for dashboards and trends."""
    __tablename__ = 'enterprise_analytics_snapshots'
    __table_args__ = (
        Index('ix_ent_analytics_type', 'snapshot_type'),
        Index('ix_ent_analytics_created', 'created_at'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int | None] = mapped_column(ForeignKey('projects.id'), nullable=True, index=True)
    snapshot_type: Mapped[str] = mapped_column(String(60), nullable=False)
    # QUALITY_TREND | RELEASE_TREND | DEVELOPER_QUALITY | MODULE_QUALITY | FAILURE_HEATMAP | FLAKY_TESTS | COVERAGE | BROWSER_STATS | COST
    quality_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    pass_rate: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    coverage_pct: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    flaky_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    cost_usd: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    data_json: Mapped[str] = mapped_column(Text, nullable=False, default='{}')
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


# ─── Module 6: Release Governance ────────────────────────────────────────────

class ReleaseGovernanceStage(Base):
    """Release approval workflow stage definition."""
    __tablename__ = 'release_governance_stages'
    __table_args__ = (
        Index('ix_rel_gov_stages_status', 'stage_status'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int | None] = mapped_column(ForeignKey('projects.id'), nullable=True, index=True)
    release_version: Mapped[str] = mapped_column(String(60), nullable=False)
    stage_order: Mapped[int] = mapped_column(Integer, nullable=False)
    stage_name: Mapped[str] = mapped_column(String(80), nullable=False)
    # QA_LEAD | QA_MANAGER | ENGINEERING_MANAGER | PRODUCT_OWNER | RELEASE_MANAGER | CTO
    required_role: Mapped[str] = mapped_column(String(60), nullable=False)
    stage_status: Mapped[str] = mapped_column(String(30), nullable=False, default='PENDING')
    # PENDING | APPROVED | REJECTED | SKIPPED
    is_blocking: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    notes: Mapped[str] = mapped_column(Text, nullable=False, default='')
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class ReleaseGovernanceApproval(Base):
    """Electronic approval record with digital signature."""
    __tablename__ = 'release_governance_approvals'
    __table_args__ = (
        Index('ix_rel_gov_approvals_stage', 'stage_id'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    stage_id: Mapped[int] = mapped_column(ForeignKey('release_governance_stages.id'), nullable=False)
    approver_id: Mapped[int | None] = mapped_column(ForeignKey('operators.id'), nullable=True)
    approver_name: Mapped[str] = mapped_column(String(120), nullable=False)
    approver_role: Mapped[str] = mapped_column(String(60), nullable=False)
    decision: Mapped[str] = mapped_column(String(20), nullable=False)
    # APPROVED | REJECTED | CONDITIONAL
    digital_signature: Mapped[str] = mapped_column(String(256), nullable=False)
    ip_address: Mapped[str] = mapped_column(String(60), nullable=False, default='127.0.0.1')
    comments: Mapped[str] = mapped_column(Text, nullable=False, default='')
    signed_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


# ─── Module 7: Compliance Center ─────────────────────────────────────────────

class ComplianceReport(Base):
    """Compliance audit report per standard."""
    __tablename__ = 'compliance_reports'
    __table_args__ = (
        Index('ix_compliance_reports_standard', 'compliance_standard'),
        Index('ix_compliance_reports_status', 'report_status'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    compliance_standard: Mapped[str] = mapped_column(String(30), nullable=False)
    # ISO_27001 | SOC2 | GDPR | HIPAA | PCI_DSS
    report_scope: Mapped[str] = mapped_column(String(120), nullable=False, default='PLATFORM')
    report_status: Mapped[str] = mapped_column(String(30), nullable=False, default='DRAFT')
    # DRAFT | GENERATING | COMPLETED | FAILED
    compliance_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    findings_json: Mapped[str] = mapped_column(Text, nullable=False, default='[]')
    recommendations_json: Mapped[str] = mapped_column(Text, nullable=False, default='[]')
    generated_by: Mapped[int | None] = mapped_column(ForeignKey('operators.id'), nullable=True)
    generated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


# ─── Module 8: Enterprise API Hub ────────────────────────────────────────────

class APIHubKey(Base):
    """API key registry for the public API hub."""
    __tablename__ = 'api_hub_keys'
    __table_args__ = (
        Index('ix_api_hub_keys_status', 'key_status'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    key_name: Mapped[str] = mapped_column(String(120), nullable=False)
    key_prefix: Mapped[str] = mapped_column(String(20), nullable=False)
    key_hash: Mapped[str] = mapped_column(String(256), nullable=False)
    key_status: Mapped[str] = mapped_column(String(20), nullable=False, default='ACTIVE')
    # ACTIVE | REVOKED | EXPIRED
    sdk_type: Mapped[str] = mapped_column(String(30), nullable=False, default='REST')
    # REST | PYTHON | JAVA | NODE | CSHARP | GO
    rate_limit_rpm: Mapped[int] = mapped_column(Integer, nullable=False, default=1000)
    permissions_json: Mapped[str] = mapped_column(Text, nullable=False, default='["READ"]')
    created_by: Mapped[int | None] = mapped_column(ForeignKey('operators.id'), nullable=True)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


class APIHubWebhook(Base):
    """Webhook endpoint registry."""
    __tablename__ = 'api_hub_webhooks'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    webhook_name: Mapped[str] = mapped_column(String(120), nullable=False)
    target_url: Mapped[str] = mapped_column(String(500), nullable=False)
    event_types_json: Mapped[str] = mapped_column(Text, nullable=False, default='["ALL"]')
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    secret_hash: Mapped[str] = mapped_column(String(256), nullable=False, default='')
    delivery_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    failure_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


# ─── Module 9: Marketplace Ecosystem ─────────────────────────────────────────

class MarketplacePlugin(Base):
    """Extended marketplace plugin registry."""
    __tablename__ = 'marketplace_plugins'
    __table_args__ = (
        Index('ix_marketplace_plugins_category', 'plugin_category'),
        Index('ix_marketplace_plugins_status', 'install_status'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    plugin_name: Mapped[str] = mapped_column(String(150), nullable=False)
    plugin_version: Mapped[str] = mapped_column(String(30), nullable=False)
    plugin_category: Mapped[str] = mapped_column(String(60), nullable=False)
    # PLUGIN | AI_AGENT | REPORT | THEME | CONNECTOR | VALIDATOR | EXECUTOR | EXTENSION
    author: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    install_status: Mapped[str] = mapped_column(String(20), nullable=False, default='AVAILABLE')
    # AVAILABLE | INSTALLED | DISABLED | DEPRECATED
    install_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    rating: Mapped[float] = mapped_column(Float, nullable=False, default=4.5)
    manifest_json: Mapped[str] = mapped_column(Text, nullable=False, default='{}')
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


# ─── Module 10: Enterprise DevOps ────────────────────────────────────────────

class DevOpsPipeline(Base):
    """DevOps CI/CD pipeline integration configuration."""
    __tablename__ = 'devops_pipelines'
    __table_args__ = (
        Index('ix_devops_pipelines_tool', 'ci_tool'),
        Index('ix_devops_pipelines_status', 'pipeline_status'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int | None] = mapped_column(ForeignKey('projects.id'), nullable=True, index=True)
    pipeline_name: Mapped[str] = mapped_column(String(150), nullable=False)
    ci_tool: Mapped[str] = mapped_column(String(40), nullable=False)
    # GITHUB | GITLAB | AZURE_DEVOPS | BITBUCKET | JENKINS | CIRCLECI | TEAMCITY | ARGOCD | KUBERNETES | DOCKER | TERRAFORM
    repo_url: Mapped[str] = mapped_column(String(500), nullable=False, default='')
    branch: Mapped[str] = mapped_column(String(100), nullable=False, default='main')
    pipeline_status: Mapped[str] = mapped_column(String(30), nullable=False, default='IDLE')
    # IDLE | RUNNING | SUCCESS | FAILED | QUEUED
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    config_json: Mapped[str] = mapped_column(Text, nullable=False, default='{}')
    last_triggered_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_run_duration_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


# ─── Module 11: Multi-Region Cloud ───────────────────────────────────────────

class CloudRegionConfig(Base):
    """Multi-region cloud deployment configuration."""
    __tablename__ = 'cloud_region_configs'
    __table_args__ = (
        Index('ix_cloud_region_provider', 'cloud_provider'),
        Index('ix_cloud_region_status', 'region_status'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cloud_provider: Mapped[str] = mapped_column(String(30), nullable=False)
    # AWS | AZURE | GCP | ON_PREMISE
    region_name: Mapped[str] = mapped_column(String(60), nullable=False)
    region_display: Mapped[str] = mapped_column(String(100), nullable=False)
    region_status: Mapped[str] = mapped_column(String(30), nullable=False, default='ACTIVE')
    # ACTIVE | FAILOVER | DEGRADED | OFFLINE
    failover_priority: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    is_primary: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_disaster_recovery: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    replication_lag_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_backup_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    config_json: Mapped[str] = mapped_column(Text, nullable=False, default='{}')
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


# ─── Module 12: Enterprise Security Center ───────────────────────────────────

class SecurityVaultEntry(Base):
    """Secrets vault entry."""
    __tablename__ = 'security_vault_entries'
    __table_args__ = (
        Index('ix_sec_vault_status', 'entry_status'),
        Index('ix_sec_vault_key', 'key_name'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    key_name: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    secret_type: Mapped[str] = mapped_column(String(40), nullable=False)
    # API_KEY | DB_PASSWORD | OAUTH_SECRET | CERTIFICATE | SSH_KEY | ENV_VAR
    encrypted_value: Mapped[str] = mapped_column(Text, nullable=False)
    entry_status: Mapped[str] = mapped_column(String(20), nullable=False, default='ACTIVE')
    # ACTIVE | ROTATED | EXPIRED | REVOKED
    rotation_schedule_days: Mapped[int] = mapped_column(Integer, nullable=False, default=90)
    last_rotated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    next_rotation_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_by: Mapped[int | None] = mapped_column(ForeignKey('operators.id'), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


# ─── Module 13: AI Execution Optimizer ───────────────────────────────────────

class AIOptimizerLog(Base):
    """AI autonomous optimization decision log."""
    __tablename__ = 'ai_optimizer_logs'
    __table_args__ = (
        Index('ix_ai_optimizer_target', 'optimization_target'),
        Index('ix_ai_optimizer_status', 'optimization_status'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int | None] = mapped_column(ForeignKey('projects.id'), nullable=True, index=True)
    optimization_target: Mapped[str] = mapped_column(String(60), nullable=False)
    # WORKER_COUNT | TIMEOUT | RETRY_STRATEGY | LOCATOR_STRATEGY | PARALLEL_FACTOR | EXECUTION_PLAN | BROWSER_ALLOCATION | INFRA_USAGE
    old_value_json: Mapped[str] = mapped_column(Text, nullable=False, default='{}')
    new_value_json: Mapped[str] = mapped_column(Text, nullable=False, default='{}')
    reasoning: Mapped[str] = mapped_column(Text, nullable=False, default='')
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.90)
    optimization_status: Mapped[str] = mapped_column(String(30), nullable=False, default='APPLIED')
    # APPLIED | PENDING | REVERTED | SKIPPED
    impact_delta: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


# ─── Module 14: Executive Command Center ─────────────────────────────────────

class ExecutiveCommandSnapshot(Base):
    """Global executive command center KPI snapshot."""
    __tablename__ = 'executive_command_snapshots'
    __table_args__ = (
        Index('ix_exec_cmd_created', 'created_at'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    snapshot_label: Mapped[str] = mapped_column(String(100), nullable=False)
    total_companies: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_projects: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_executions_today: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    active_workers: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    browser_farm_utilization_pct: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    ai_health_score: Mapped[float] = mapped_column(Float, nullable=False, default=100.0)
    release_readiness_score: Mapped[float] = mapped_column(Float, nullable=False, default=85.0)
    compliance_score: Mapped[float] = mapped_column(Float, nullable=False, default=95.0)
    security_score: Mapped[float] = mapped_column(Float, nullable=False, default=98.0)
    overall_quality_score: Mapped[float] = mapped_column(Float, nullable=False, default=90.0)
    kpi_data_json: Mapped[str] = mapped_column(Text, nullable=False, default='{}')
    alerts_json: Mapped[str] = mapped_column(Text, nullable=False, default='[]')
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
