from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import AuthContext, get_auth_context, require_csrf
from app.services.audit_service import append_event
from app.repositories.project_repository import ProjectRepository
from app.models.project_membership import ProjectMember
from app.schemas.project import ProjectCreate, ProjectMemberCreate, ProjectMemberRead, ProjectMemberUpdate, ProjectRead
from app.services.project_access import ProjectAccessService, ProjectAction
from app.security import SafetyViolation, validate_environment

router = APIRouter(prefix='/projects', tags=['projects'], dependencies=[Depends(get_auth_context)])


@router.get('', response_model=list[ProjectRead])
def list_projects(context: AuthContext = Depends(get_auth_context), db: Session = Depends(get_db)):
  access = ProjectAccessService(db, context.operator.id)
  return ProjectRepository(db).list_active(access.project_ids())


@router.get('/{project_id}', response_model=ProjectRead)
def get_project(project_id: int, context: AuthContext = Depends(get_auth_context), db: Session = Depends(get_db)):
  ProjectAccessService(db, context.operator.id).require(project_id)
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
    membership = db.scalar(select(ProjectMember).where(ProjectMember.project_id == record.id, ProjectMember.operator_id == context.operator.id))
    if membership is None:
      db.add(ProjectMember(
        project_id=record.id, operator_id=context.operator.id, role='OWNER', status='ACTIVE',
        created_by=context.operator.id, joined_at=datetime.utcnow(), created_at=datetime.utcnow(), updated_at=datetime.utcnow(),
      ))
    else:
      membership.role = 'OWNER'; membership.status = 'ACTIVE'; membership.updated_at = datetime.utcnow()
    append_event(db, 'PROJECT_CREATED', operator_id=context.operator.id, resource_type='PROJECT', resource_id=str(record.id), metadata={'name': record.name, 'product_code': record.product_code}); db.commit()
    return record
  except IntegrityError:
    db.rollback()
    raise HTTPException(status_code=409, detail='A project with this name already exists.') from None


@router.get('/{project_id}/members', response_model=list[ProjectMemberRead])
def list_project_members(project_id: int, context: AuthContext = Depends(get_auth_context), db: Session = Depends(get_db)):
  ProjectAccessService(db, context.operator.id).require(project_id, ProjectAction.MANAGE)
  return list(db.scalars(select(ProjectMember).where(ProjectMember.project_id == project_id).order_by(ProjectMember.id)))


@router.post('/{project_id}/members', response_model=ProjectMemberRead, status_code=201)
def add_project_member(project_id: int, payload: ProjectMemberCreate, context: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)):
  ProjectAccessService(db, context.operator.id).require(project_id, ProjectAction.MANAGE)
  if db.scalar(select(ProjectMember).where(ProjectMember.project_id == project_id, ProjectMember.operator_id == payload.operator_id)):
    raise HTTPException(status_code=409, detail='Operator already has a project membership.')
  now = datetime.utcnow()
  member = ProjectMember(
    project_id=project_id, operator_id=payload.operator_id, role=payload.role, status='ACTIVE',
    created_by=context.operator.id, joined_at=now, created_at=now, updated_at=now,
  )
  db.add(member); db.flush()
  append_event(db, 'PROJECT_MEMBERSHIP_CREATED', operator_id=context.operator.id, resource_type='PROJECT_MEMBER', resource_id=str(member.id), metadata={'project_id': project_id, 'member_operator_id': payload.operator_id, 'role': payload.role})
  db.commit(); db.refresh(member); return member


@router.patch('/{project_id}/members/{member_id}', response_model=ProjectMemberRead)
def update_project_member(project_id: int, member_id: int, payload: ProjectMemberUpdate, context: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)):
  ProjectAccessService(db, context.operator.id).require(project_id, ProjectAction.MANAGE)
  member = db.get(ProjectMember, member_id)
  if member is None or member.project_id != project_id:
    raise HTTPException(status_code=404, detail='Project member not found.')
  if payload.role is not None:
    member.role = payload.role
  if payload.status is not None:
    member.status = payload.status
    member.deactivated_at = datetime.utcnow() if payload.status == 'INACTIVE' else None
  member.updated_at = datetime.utcnow()
  append_event(db, 'PROJECT_MEMBERSHIP_UPDATED', operator_id=context.operator.id, resource_type='PROJECT_MEMBER', resource_id=str(member.id), metadata={'project_id': project_id, 'role': member.role, 'status': member.status})
  db.commit(); db.refresh(member); return member
