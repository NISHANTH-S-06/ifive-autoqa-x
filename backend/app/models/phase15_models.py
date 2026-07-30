"""Phase 15 – Autonomous Enterprise Software Quality Intelligence Platform (SQIP) models."""
from datetime import datetime
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


# ─── Module 1: Enterprise Software Intelligence Graph ────────────────────────

class SoftwareGraphNode(Base):
    """18-tier software intelligence graph node."""
    __tablename__ = 'software_graph_nodes'
    __table_args__ = (
        Index('ix_sg_nodes_type', 'node_type'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    node_key: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    label: Mapped[str] = mapped_column(String(200), nullable=False)
    node_type: Mapped[str] = mapped_column(String(60), nullable=False)
    # COMPANY | PRODUCT | MODULE | FEATURE | EPIC | STORY | TASK | SOURCE_FILE | API | DATABASE | INFRASTRUCTURE | DEPLOYMENT | TEST | EXECUTION | BUG | INCIDENT | RELEASE | FEEDBACK
    attributes_json: Mapped[str] = mapped_column(Text, nullable=False, default='{}')
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


class SoftwareGraphEdge(Base):
    """18-tier software intelligence graph edge."""
    __tablename__ = 'software_graph_edges'
    __table_args__ = (
        Index('ix_sg_edges_source', 'source_node_id'),
        Index('ix_sg_edges_target', 'target_node_id'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_node_id: Mapped[int] = mapped_column(ForeignKey('software_graph_nodes.id'), nullable=False)
    target_node_id: Mapped[int] = mapped_column(ForeignKey('software_graph_nodes.id'), nullable=False)
    relationship_type: Mapped[str] = mapped_column(String(60), nullable=False)
    # CONTAINS | IMPLEMENTS | IMPACTS | CALLS | DEPENDS_ON | COVERS | BLOCKS | REVEALS
    impact_weight: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


# ─── Module 2: AI Change Impact Intelligence ─────────────────────────────────

class ChangeImpactRecord(Base):
    """Commit change impact analysis."""
    __tablename__ = 'change_impact_records'
    __table_args__ = (
        Index('ix_change_impact_commit', 'commit_hash'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    commit_hash: Mapped[str] = mapped_column(String(100), nullable=False)
    author: Mapped[str] = mapped_column(String(100), nullable=False)
    changed_files_json: Mapped[str] = mapped_column(Text, nullable=False, default='[]')
    impacted_modules_json: Mapped[str] = mapped_column(Text, nullable=False, default='[]')
    impacted_apis_json: Mapped[str] = mapped_column(Text, nullable=False, default='[]')
    affected_tests_json: Mapped[str] = mapped_column(Text, nullable=False, default='[]')
    risk_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    estimated_execution_cost_usd: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


# ─── Module 3: Enterprise AI Code Reviewer ───────────────────────────────────

class CodeReviewRecord(Base):
    """AI code review findings record."""
    __tablename__ = 'code_review_records'
    __table_args__ = (
        Index('ix_code_review_file', 'file_path'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    file_path: Mapped[str] = mapped_column(String(300), nullable=False)
    language: Mapped[str] = mapped_column(String(40), nullable=False)
    # PYTHON | TYPESCRIPT | REACT | SQL | PLAYWRIGHT | FASTAPI
    bugs_found_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    security_issues_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    code_smells_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    test_gaps_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    review_comments_json: Mapped[str] = mapped_column(Text, nullable=False, default='[]')
    reviewed_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


# ─── Module 4: AI Test Coverage Intelligence ────────────────────────────────

class CoverageMetric(Base):
    """8-dimension test coverage metric record."""
    __tablename__ = 'coverage_metrics'
    __table_args__ = (
        Index('ix_coverage_dimension', 'dimension_type'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    dimension_type: Mapped[str] = mapped_column(String(60), nullable=False)
    # FEATURE | MODULE | API | REQUIREMENT | RISK | REGRESSION | AUTOMATION | BUSINESS_RULE
    target_name: Mapped[str] = mapped_column(String(150), nullable=False)
    coverage_pct: Mapped[float] = mapped_column(Float, nullable=False)
    missing_items_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    details_json: Mapped[str] = mapped_column(Text, nullable=False, default='{}')
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


# ─── Module 5: Enterprise Release Intelligence ───────────────────────────────

class ReleaseIntelligence(Base):
    """Enterprise release intelligence calculation."""
    __tablename__ = 'release_intelligences'
    __table_args__ = (
        Index('ix_release_intel_version', 'release_version'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    release_version: Mapped[str] = mapped_column(String(60), nullable=False)
    composite_release_score: Mapped[float] = mapped_column(Float, nullable=False)
    deployment_risk_pct: Mapped[float] = mapped_column(Float, nullable=False)
    rollback_risk_pct: Mapped[float] = mapped_column(Float, nullable=False)
    business_risk_pct: Mapped[float] = mapped_column(Float, nullable=False)
    security_risk_pct: Mapped[float] = mapped_column(Float, nullable=False)
    performance_risk_pct: Mapped[float] = mapped_column(Float, nullable=False)
    customer_risk_pct: Mapped[float] = mapped_column(Float, nullable=False)
    recommendation: Mapped[str] = mapped_column(String(30), nullable=False, default='READY')
    # READY | HOLD | ROLLBACK
    breakdown_json: Mapped[str] = mapped_column(Text, nullable=False, default='{}')
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


# ─── Module 6: AI Defect Intelligence Hub ─────────────────────────────────────

class DefectCluster(Base):
    """Clustered defect group and AI pattern analysis."""
    __tablename__ = 'defect_clusters'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cluster_name: Mapped[str] = mapped_column(String(150), nullable=False)
    root_cause_pattern: Mapped[str] = mapped_column(Text, nullable=False)
    defect_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    assigned_owner: Mapped[str] = mapped_column(String(100), nullable=False, default='Unassigned')
    estimated_fix_hours: Mapped[float] = mapped_column(Float, nullable=False, default=4.0)
    priority: Mapped[str] = mapped_column(String(30), nullable=False, default='HIGH')
    customer_impact_rating: Mapped[str] = mapped_column(String(30), nullable=False, default='MODERATE')
    defects_json: Mapped[str] = mapped_column(Text, nullable=False, default='[]')
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


# ─── Module 7: Enterprise Engineering Analytics ─────────────────────────────

class EngineeringMetric(Base):
    """Engineering productivity and cycle time metrics."""
    __tablename__ = 'engineering_metrics'
    __table_args__ = (
        Index('ix_engineering_metric_type', 'metric_name'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    metric_name: Mapped[str] = mapped_column(String(100), nullable=False)
    # CYCLE_TIME_HOURS | LEAD_TIME_HOURS | MTTR_MINUTES | BUG_LEAKAGE_PCT | DEV_PRODUCTIVITY_SCORE | QA_PRODUCTIVITY_SCORE | AUTOMATION_GROWTH_PCT
    metric_value: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(30), nullable=False, default='hours')
    trend_json: Mapped[str] = mapped_column(Text, nullable=False, default='{}')
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


# ─── Module 11: Enterprise Knowledge Lake ────────────────────────────────────

class QualityKnowledge(Base):
    """Knowledge lake semantic AI document index."""
    __tablename__ = 'quality_knowledges'
    __table_args__ = (
        Index('ix_quality_knowledge_type', 'item_type'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    item_type: Mapped[str] = mapped_column(String(60), nullable=False)
    # LOG | REPORT | EVIDENCE | SCREENSHOT | VIDEO | TRACE | CONSOLE | NETWORK | ACCESSIBILITY | BASELINE
    title: Mapped[str] = mapped_column(String(250), nullable=False)
    content_text: Mapped[str] = mapped_column(Text, nullable=False)
    tags_json: Mapped[str] = mapped_column(Text, nullable=False, default='[]')
    media_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


# ─── Module 12: Executive Mission Control ─────────────────────────────────────

class MissionControlSnapshot(Base):
    """Executive mission control single-screen KPI snapshot."""
    __tablename__ = 'mission_control_snapshots'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    global_health_score: Mapped[float] = mapped_column(Float, nullable=False)
    overall_risk_score: Mapped[float] = mapped_column(Float, nullable=False)
    overall_quality_score: Mapped[float] = mapped_column(Float, nullable=False)
    overall_coverage_pct: Mapped[float] = mapped_column(Float, nullable=False)
    ai_confidence_pct: Mapped[float] = mapped_column(Float, nullable=False)
    active_incidents_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    active_workers_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    monthly_cost_usd: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    kpi_breakdown_json: Mapped[str] = mapped_column(Text, nullable=False, default='{}')
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
