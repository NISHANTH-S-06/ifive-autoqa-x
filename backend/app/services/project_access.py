from __future__ import annotations

from enum import StrEnum

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.project_membership import ProjectMember
from app.services.audit_service import append_event


class ProjectAction(StrEnum):
  READ = 'READ'
  TEST = 'TEST'
  APPROVE = 'APPROVE'
  MANAGE = 'MANAGE'


ACTION_ROLES = {
  ProjectAction.READ: {'OWNER', 'ADMIN', 'APPROVER', 'TESTER', 'VIEWER'},
  ProjectAction.TEST: {'OWNER', 'ADMIN', 'TESTER'},
  ProjectAction.APPROVE: {'OWNER', 'ADMIN', 'APPROVER'},
  ProjectAction.MANAGE: {'OWNER', 'ADMIN'},
}


class ProjectAccessService:
  """Single fail-closed policy for project-scoped API and service operations."""

  def __init__(self, db: Session, operator_id: int):
    self.db = db
    self.operator_id = operator_id

  def membership(self, project_id: int) -> ProjectMember | None:
    return self.db.scalar(select(ProjectMember).where(
      ProjectMember.project_id == project_id,
      ProjectMember.operator_id == self.operator_id,
      ProjectMember.status == 'ACTIVE',
    ))

  def project_ids(self, action: ProjectAction = ProjectAction.READ) -> tuple[int, ...]:
    return tuple(self.db.scalars(select(ProjectMember.project_id).where(
      ProjectMember.operator_id == self.operator_id,
      ProjectMember.status == 'ACTIVE',
      ProjectMember.role.in_(ACTION_ROLES[action]),
    )))

  def require(self, project_id: int, action: ProjectAction = ProjectAction.READ) -> ProjectMember:
    membership = self.membership(project_id)
    if membership is None:
      self._deny(project_id, action, hidden=True)
    if membership.role not in ACTION_ROLES[action]:
      self._deny(project_id, action, hidden=False)
    return membership

  def resolve(self, project_id: int | None, action: ProjectAction) -> int:
    """Resolve an omitted scope only when the choice is unambiguous."""
    if project_id is not None:
      self.require(project_id, action)
      return project_id
    candidates = self.project_ids(action)
    if len(candidates) != 1:
      raise HTTPException(status_code=422, detail='project_id is required when more than one project is available.')
    return candidates[0]

  def assert_same_project(self, expected_project_id: int, actual_project_id: int, resource: str) -> None:
    if expected_project_id != actual_project_id:
      append_event(
        self.db, 'PROJECT_RELATIONSHIP_DENIED', 'DENIED', self.operator_id,
        resource_type=resource, resource_id=str(actual_project_id),
        metadata={'expected_project_id': expected_project_id},
      )
      self.db.commit()
      raise HTTPException(status_code=400, detail='Cross-project parent/child relationship is not allowed.')

  def _deny(self, project_id: int, action: ProjectAction, *, hidden: bool) -> None:
    self.db.rollback()
    append_event(
      self.db, 'PROJECT_ACCESS_DENIED', 'DENIED', self.operator_id,
      resource_type='PROJECT', resource_id=str(project_id),
      metadata={'action': action.value, 'hidden_non_member': hidden},
    )
    self.db.commit()
    if hidden:
      raise HTTPException(status_code=404, detail='Resource not found.')
    raise HTTPException(status_code=403, detail='Project role does not permit this action.')
