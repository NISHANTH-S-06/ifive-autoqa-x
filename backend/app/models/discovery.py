from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Index, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class DiscoveryResult(Base):
    __tablename__ = 'discovery_results'
    __table_args__ = (
        Index('ix_discovery_results_target', 'target_id'),
        Index('ix_discovery_results_status', 'status'),
        Index('ix_discovery_results_created_at', 'created_at'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey('projects.id'), nullable=False, index=True)
    company_id: Mapped[int | None] = mapped_column(ForeignKey('companies.id'), nullable=True)
    product_id: Mapped[int | None] = mapped_column(ForeignKey('company_products.id'), nullable=True)
    module_id: Mapped[int | None] = mapped_column(ForeignKey('company_modules.id'), nullable=True)
    target_id: Mapped[int | None] = mapped_column(ForeignKey('connection_targets.id'), nullable=True)
    target_url: Mapped[str] = mapped_column(String(1000), nullable=False)

    # Discovered Data Structures (JSON strings)
    ui_map_json: Mapped[str] = mapped_column(Text, nullable=False, default='{}')
    module_tree_json: Mapped[str] = mapped_column(Text, nullable=False, default='{}')
    flow_graph_json: Mapped[str] = mapped_column(Text, nullable=False, default='{}')
    recommendations_json: Mapped[str] = mapped_column(Text, nullable=False, default='[]')
    risk_assessment_json: Mapped[str] = mapped_column(Text, nullable=False, default='{}')

    confidence_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.95)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default='PENDING_APPROVAL')
    # Statuses: PENDING_APPROVAL | APPROVED | REJECTED | EXECUTED

    created_by: Mapped[int] = mapped_column(ForeignKey('operators.id'), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    reviewed_by: Mapped[int | None] = mapped_column(ForeignKey('operators.id'), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
