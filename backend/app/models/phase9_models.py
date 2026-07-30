from datetime import datetime
from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class AIMemoryRecord(Base):
    __tablename__ = 'ai_memory_records'
    __table_args__ = (
        Index('ix_ai_memory_records_type', 'memory_type'),
        Index('ix_ai_memory_records_entity', 'entity_key'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int | None] = mapped_column(ForeignKey('projects.id'), nullable=True, index=True)
    memory_type: Mapped[str] = mapped_column(String(60), nullable=False)
    # Types: RUN | FAILURE | FIX | PLAN | VISUAL | BUG | RELEASE | LOCATOR
    entity_key: Mapped[str] = mapped_column(String(160), nullable=False)
    memory_data_json: Mapped[str] = mapped_column(Text, nullable=False, default='{}')
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.95)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class AILocatorHistory(Base):
    __tablename__ = 'ai_locator_histories'
    __table_args__ = (
        Index('ix_ai_locator_histories_target', 'target_url'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int | None] = mapped_column(ForeignKey('projects.id'), nullable=True, index=True)
    target_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    element_name: Mapped[str] = mapped_column(String(160), nullable=False)
    selector: Mapped[str] = mapped_column(String(500), nullable=False)
    alternative_selectors_json: Mapped[str] = mapped_column(Text, nullable=False, default='[]')
    success_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    failure_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_healed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default='ACTIVE')
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class KnowledgeGraphNode(Base):
    __tablename__ = 'knowledge_graph_nodes'
    __table_args__ = (
        Index('ix_knowledge_graph_nodes_type', 'node_type'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    node_type: Mapped[str] = mapped_column(String(60), nullable=False)
    # COMPANY | PROJECT | PRODUCT | MODULE | PAGE | COMPONENT | LOCATOR | API | DATABASE | TEST_CASE | EXECUTION | EVIDENCE | BUG | RELEASE
    entity_id: Mapped[str] = mapped_column(String(100), nullable=False)
    label: Mapped[str] = mapped_column(String(200), nullable=False)
    properties_json: Mapped[str] = mapped_column(Text, nullable=False, default='{}')
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


class KnowledgeGraphEdge(Base):
    __tablename__ = 'knowledge_graph_edges'
    __table_args__ = (
        Index('ix_knowledge_graph_edges_source', 'source_node_id'),
        Index('ix_knowledge_graph_edges_target', 'target_node_id'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_node_id: Mapped[int] = mapped_column(ForeignKey('knowledge_graph_nodes.id'), nullable=False)
    target_node_id: Mapped[int] = mapped_column(ForeignKey('knowledge_graph_nodes.id'), nullable=False)
    relationship_type: Mapped[str] = mapped_column(String(80), nullable=False)
    properties_json: Mapped[str] = mapped_column(Text, nullable=False, default='{}')
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


class ReleaseReadinessEvaluation(Base):
    __tablename__ = 'release_readiness_evaluations'
    __table_args__ = (
        Index('ix_release_readiness_evaluations_status', 'readiness_status'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey('projects.id'), nullable=False, index=True)
    release_version: Mapped[str] = mapped_column(String(60), nullable=False)
    release_score: Mapped[float] = mapped_column(Float, nullable=False, default=85.0)
    readiness_status: Mapped[str] = mapped_column(String(30), nullable=False, default='READY')
    # Statuses: READY | NOT_READY | BLOCKED
    automation_coverage: Mapped[float] = mapped_column(Float, nullable=False, default=95.0)
    pass_rate: Mapped[float] = mapped_column(Float, nullable=False, default=98.0)
    open_critical_bugs: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    risk_score: Mapped[float] = mapped_column(Float, nullable=False, default=10.0)
    breakdown_json: Mapped[str] = mapped_column(Text, nullable=False, default='{}')
    created_by: Mapped[int] = mapped_column(ForeignKey('operators.id'), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


class NotificationLog(Base):
    __tablename__ = 'notification_logs'
    __table_args__ = (
        Index('ix_notification_logs_status', 'status'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    channel: Mapped[str] = mapped_column(String(40), nullable=False)
    # Channels: DASHBOARD | EMAIL | SLACK | TEAMS | WEBHOOK
    notification_type: Mapped[str] = mapped_column(String(80), nullable=False)
    recipient: Mapped[str] = mapped_column(String(200), nullable=False)
    title: Mapped[str] = mapped_column(String(250), nullable=False)
    body_text: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default='SENT')
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
