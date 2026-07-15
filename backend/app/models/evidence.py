from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Evidence(Base):
  __tablename__ = 'evidence'

  id: Mapped[int] = mapped_column(Integer, primary_key=True)
  test_run_id: Mapped[int] = mapped_column(ForeignKey('test_runs.id'), nullable=False, index=True)
  test_result_id: Mapped[int | None] = mapped_column(ForeignKey('test_results.id'), nullable=True)
  evidence_type: Mapped[str] = mapped_column(String(30), nullable=False)
  relative_path: Mapped[str] = mapped_column(String(500), nullable=False)
  file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
  created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

  test_run: Mapped['TestRun'] = relationship(back_populates='evidence')
  test_result: Mapped['TestResult | None'] = relationship(back_populates='evidence')
