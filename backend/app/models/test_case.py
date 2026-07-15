from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class TestCase(Base):
  __tablename__ = 'test_cases'

  id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
  suite_id: Mapped[int] = mapped_column(ForeignKey('test_suites.id'), nullable=False)
  name: Mapped[str] = mapped_column(String(200), nullable=False)
  file_path: Mapped[str] = mapped_column(String(500), nullable=False)
  status: Mapped[str] = mapped_column(String(40), nullable=False, default='draft')

