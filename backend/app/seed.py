from sqlalchemy.orm import Session

from app.models.project import Project
from app.repositories.project_repository import ProjectRepository
from app.schemas.project import ProductCode, ProjectCreate


DEMO_PROJECTS = (
  ('iFive AutoQA Dashboard', ProductCode.AUTOQA),
  ('Demo ERP', ProductCode.ERP),
  ('iFive ERP', ProductCode.ERP),
  ('iFive HRMS', ProductCode.HRMS),
  ('iFive CRM', ProductCode.CRM),
  ('iFive IIoT', ProductCode.IIOT),
  ('iFive Application Integration', ProductCode.INTEGRATION),
  ('iFive Corporate Website', ProductCode.IIOT),
)


def seed_local_projects(db: Session) -> int:
  repository = ProjectRepository(db)
  if repository.count() != 0:
    return 0
  for name, product_code in DEMO_PROJECTS:
    db.add(Project(**ProjectCreate(
      name=name,
      product_code=product_code,
      description='Local demo project for Stage 3 validation.',
      environment='local',
    ).model_dump()))
  db.commit()
  return len(DEMO_PROJECTS)
