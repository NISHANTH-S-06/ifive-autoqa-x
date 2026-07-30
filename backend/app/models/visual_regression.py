from datetime import datetime
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class VisualBaseline(Base):
    __tablename__ = 'visual_baselines'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey('test_projects.id'), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    module: Mapped[str] = mapped_column(String(60), nullable=False, default='GENERAL', index=True)
    browser: Mapped[str] = mapped_column(String(30), nullable=False, default='chromium', index=True)
    viewport_width: Mapped[int] = mapped_column(Integer, nullable=False, default=1280)
    viewport_height: Mapped[int] = mapped_column(Integer, nullable=False, default=720)
    capture_type: Mapped[str] = mapped_column(String(30), nullable=False, default='VIEWPORT')
    element_selector: Mapped[str | None] = mapped_column(String(255), nullable=True)
    route_path: Mapped[str] = mapped_column(String(255), nullable=False, default='/')
    image_path: Mapped[str] = mapped_column(String(255), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    ignore_rules_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_by: Mapped[int] = mapped_column(ForeignKey('operators.id'), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    history_records: Mapped[list['VisualBaselineHistory']] = relationship(back_populates='baseline', cascade='all, delete-orphan')
    comparisons: Mapped[list['VisualComparisonRun']] = relationship(back_populates='baseline')


class VisualBaselineHistory(Base):
    __tablename__ = 'visual_baseline_history'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    baseline_id: Mapped[int] = mapped_column(ForeignKey('visual_baselines.id'), nullable=False, index=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    image_path: Mapped[str] = mapped_column(String(255), nullable=False)
    ignore_rules_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    change_summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_by: Mapped[int] = mapped_column(ForeignKey('operators.id'), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    baseline: Mapped[VisualBaseline] = relationship(back_populates='history_records')


class VisualComparisonRun(Base):
    __tablename__ = 'visual_comparison_runs'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey('test_projects.id'), nullable=False, index=True)
    run_id: Mapped[int | None] = mapped_column(ForeignKey('automated_runs.id'), nullable=True, index=True)
    baseline_id: Mapped[int] = mapped_column(ForeignKey('visual_baselines.id'), nullable=False, index=True)
    baseline_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default='PASSED')
    browser: Mapped[str] = mapped_column(String(30), nullable=False, default='chromium', index=True)
    viewport_width: Mapped[int] = mapped_column(Integer, nullable=False, default=1280)
    viewport_height: Mapped[int] = mapped_column(Integer, nullable=False, default=720)
    module: Mapped[str] = mapped_column(String(60), nullable=False, default='GENERAL', index=True)
    capture_type: Mapped[str] = mapped_column(String(30), nullable=False, default='VIEWPORT')

    diff_percentage: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    total_pixels_changed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    layout_shifts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    missing_elements_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    color_changes_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    font_changes_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    icon_changes_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    alignment_issues_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    spacing_changes_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    responsive_changes_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    ai_classification: Mapped[str] = mapped_column(String(30), nullable=False, default='COSMETIC', index=True)
    ai_confidence_score: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    ai_severity: Mapped[str] = mapped_column(String(30), nullable=False, default='COSMETIC')
    ai_root_cause: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_recommendation: Mapped[str | None] = mapped_column(Text, nullable=True)

    current_image_path: Mapped[str] = mapped_column(String(255), nullable=False)
    diff_image_path: Mapped[str | None] = mapped_column(String(255), nullable=True)
    overlay_image_path: Mapped[str | None] = mapped_column(String(255), nullable=True)
    heatmap_image_path: Mapped[str | None] = mapped_column(String(255), nullable=True)
    bounding_box_image_path: Mapped[str | None] = mapped_column(String(255), nullable=True)
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_by: Mapped[int] = mapped_column(ForeignKey('operators.id'), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    baseline: Mapped[VisualBaseline] = relationship(back_populates='comparisons')
