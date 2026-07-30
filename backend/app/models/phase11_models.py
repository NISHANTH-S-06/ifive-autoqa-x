from datetime import datetime
from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class AIExperienceRecord(Base):
    __tablename__ = 'ai_experience_records'
    __table_args__ = (
        Index('ix_ai_experience_records_type', 'experience_type'),
        Index('ix_ai_experience_records_key', 'entity_key'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int | None] = mapped_column(ForeignKey('projects.id'), nullable=True, index=True)
    experience_type: Mapped[str] = mapped_column(String(60), nullable=False)
    # Types: EXECUTION | FAILURE_TRACE | LOCATOR_HEALING | PERFORMANCE_TREND | FLAKY_TEST | DEV_QUALITY | RELEASE_HISTORY
    entity_key: Mapped[str] = mapped_column(String(160), nullable=False)
    experience_data_json: Mapped[str] = mapped_column(Text, nullable=False, default='{}')
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.98)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


class PatternDetectionRecord(Base):
    __tablename__ = 'pattern_detection_records'
    __table_args__ = (
        Index('ix_pattern_detection_records_type', 'pattern_type'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int | None] = mapped_column(ForeignKey('projects.id'), nullable=True, index=True)
    pattern_type: Mapped[str] = mapped_column(String(80), nullable=False)
    # Types: REPEATED_FAILURE | DEV_MISTAKE | MODULE_INSTABILITY | API_FAILURE | UI_DRIFT | DB_INCONSISTENCY
    pattern_key: Mapped[str] = mapped_column(String(160), nullable=False)
    pattern_score: Mapped[float] = mapped_column(Float, nullable=False, default=85.0)
    details_json: Mapped[str] = mapped_column(Text, nullable=False, default='{}')
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


class TestEvolutionRecord(Base):
    __tablename__ = 'test_evolution_records'
    __table_args__ = (
        Index('ix_test_evolution_records_type', 'action_type'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int | None] = mapped_column(ForeignKey('projects.id'), nullable=True, index=True)
    action_type: Mapped[str] = mapped_column(String(60), nullable=False)
    # Types: IMPROVED | REMOVED_DUPLICATE | MERGED | CREATED_MISSING | EDGE_CASE_GEN | REGRESSION_GEN
    test_name: Mapped[str] = mapped_column(String(200), nullable=False)
    details_json: Mapped[str] = mapped_column(Text, nullable=False, default='{}')
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


class RootCauseGraphNode(Base):
    __tablename__ = 'root_cause_graph_nodes'
    __table_args__ = (
        Index('ix_root_cause_graph_nodes_type', 'entity_type'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int | None] = mapped_column(ForeignKey('projects.id'), nullable=True, index=True)
    entity_type: Mapped[str] = mapped_column(String(60), nullable=False)
    # Types: BUG | COMPONENT | API | DATABASE | SERVICE | TASK | RELEASE | CUSTOMER_IMPACT
    entity_key: Mapped[str] = mapped_column(String(160), nullable=False)
    label: Mapped[str] = mapped_column(String(200), nullable=False)
    metadata_json: Mapped[str] = mapped_column(Text, nullable=False, default='{}')
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


class RootCauseGraphEdge(Base):
    __tablename__ = 'root_cause_graph_edges'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_node_id: Mapped[int] = mapped_column(ForeignKey('root_cause_graph_nodes.id'), nullable=False)
    target_node_id: Mapped[int] = mapped_column(ForeignKey('root_cause_graph_nodes.id'), nullable=False)
    relationship_type: Mapped[str] = mapped_column(String(80), nullable=False)
    properties_json: Mapped[str] = mapped_column(Text, nullable=False, default='{}')
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
