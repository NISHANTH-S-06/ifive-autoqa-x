from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import AuthContext, get_auth_context, require_csrf
from app.services.audit_service import append_event
from app.repositories.project_repository import ProjectRepository
from app.schemas.project import ProjectCreate, ProjectRead
from app.security import SafetyViolation, validate_environment

router = APIRouter(prefix='/projects', tags=['projects'], dependencies=[Depends(get_auth_context)])


@router.get('', response_model=list[ProjectRead])
def list_projects(db: Session = Depends(get_db)):
  return ProjectRepository(db).list_active()


@router.get('/{project_id}', response_model=ProjectRead)
def get_project(project_id: int, db: Session = Depends(get_db)):
  project = ProjectRepository(db).get(project_id)
  if project is None:
    raise HTTPException(status_code=404, detail='Project not found.')
  return project


@router.post('', response_model=ProjectRead, status_code=201)
def create_project(project: ProjectCreate, context: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)):
  if context.operator.role not in ('TESTER', 'ADMIN'):
    raise HTTPException(status_code=403, detail='You do not have permission to perform this action.')
  try:
    validate_environment(project.environment)
  except SafetyViolation as exc:
    raise HTTPException(status_code=400, detail=str(exc)) from None
  repository = ProjectRepository(db)
  if repository.get_by_name(project.name):
    raise HTTPException(status_code=409, detail='A project with this name already exists.')
  try:
    record = repository.create(project)
    append_event(db, 'PROJECT_CREATED', operator_id=context.operator.id, resource_type='PROJECT', resource_id=str(record.id), metadata={'name': record.name, 'product_code': record.product_code}); db.commit()
    return record
  except IntegrityError:
    db.rollback()
    raise HTTPException(status_code=409, detail='A project with this name already exists.') from None
