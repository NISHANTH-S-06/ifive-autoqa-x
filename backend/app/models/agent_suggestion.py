from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class AgentSuggestion(Base):
  __tablename__ = 'agent_suggestions'

  id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
  agent_name: Mapped[str] = mapped_column(String(80), nullable=False)
  suggestion_type: Mapped[str] = mapped_column(String(80), nullable=False)
  summary: Mapped[str] = mapped_column(Text, nullable=False)
  status: Mapped[str] = mapped_column(String(40), nullable=False, default='pending_human_review')
  created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

