from datetime import datetime
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.operator import Operator
from app.models.operator_session import OperatorSession


class OperatorRepository:
  def __init__(self, db: Session): self.db = db
  def get(self, operator_id: int): return self.db.get(Operator, operator_id)
  def by_username(self, username: str): return self.db.scalar(select(Operator).where(Operator.username == username))
  def list(self): return list(self.db.scalars(select(Operator).order_by(Operator.username)))
  def active_admin_count(self): return self.db.scalar(select(func.count(Operator.id)).where(Operator.role == 'ADMIN', Operator.is_active.is_(True))) or 0
  def session_by_hash(self, token_hash: str): return self.db.scalar(select(OperatorSession).where(OperatorSession.token_hash == token_hash))
