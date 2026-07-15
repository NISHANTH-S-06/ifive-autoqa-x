from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.project import Project
from app.schemas.project import ProjectCreate


class ProjectRepository:
  def __init__(self, db: Session):
    self.db = db

  def list_active(self, project_ids: tuple[int, ...] | None = None) -> list[Project]:
    statement = select(Project).where(Project.is_active.is_(True))
    if project_ids is not None:
      statement = statement.where(Project.id.in_(project_ids))
    return list(self.db.scalars(statement.order_by(Project.id)))

  def get(self, project_id: int) -> Project | None:
    return self.db.get(Project, project_id)

  def get_by_name(self, name: str) -> Project | None:
    return self.db.scalar(select(Project).where(func.lower(Project.name) == name.lower()))

  def count(self, active_only: bool = False, project_ids: tuple[int, ...] | None = None) -> int:
    statement = select(func.count(Project.id))
    if active_only:
      statement = statement.where(Project.is_active.is_(True))
    if project_ids is not None:
      statement = statement.where(Project.id.in_(project_ids))
    return self.db.scalar(statement) or 0

  def create(self, project: ProjectCreate) -> Project:
    record = Project(**project.model_dump())
    self.db.add(record)
    self.db.flush()
    return record
