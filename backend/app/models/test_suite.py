from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class TestSuite(Base):
  __tablename__ = 'test_suites'

  id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
  project_id: Mapped[int] = mapped_column(ForeignKey('projects.id'), nullable=False)
  name: Mapped[str] = mapped_column(String(160), nullable=False)
  product: Mapped[str] = mapped_column(String(80), nullable=False)
  module: Mapped[str] = mapped_column(String(120), nullable=False)

