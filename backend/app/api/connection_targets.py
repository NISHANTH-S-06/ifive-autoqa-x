from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth import AuthContext, get_auth_context, require_csrf
from app.database import get_db
from app.models.connection_target import ConnectionCheck, ConnectionTarget, ConnectionTargetVersion, TargetCredentialProfile
from app.schemas.connection_target import (
  ConnectionCheckCreate,
  ConnectionCheckRead,
  ConnectionTargetCreate,
  ConnectionTargetList,
  ConnectionTargetRead,
  ConnectionTargetUpdate,
  ConnectionTargetVersionRead,
  CredentialProfileCreate,
  CredentialProfileRead,
  CredentialProfileUpdate,
  LifecycleReason,
)
from app.schemas.test_management import Page
from app.services.audit_service import append_event
from app.services.connection_service import check_read, create_target_version, run_connection_check, target_read
from app.services.target_policy import (
  load_probe_paths,
  normalize_target_key,
  normalize_url,
  probe_paths_json,
  validate_environment,
  validate_tls_policy,
)
from app.services.project_access import ProjectAccessService, ProjectAction

router = APIRouter(tags=['connection-targets'], dependencies=[Depends(get_auth_context)])


def _can_author(context: AuthContext) -> bool:
  return context.operator.role in {'TESTER', 'ADMIN'}


def _can_review(context: AuthContext) -> bool:
  return context.operator.role in {'APPROVER', 'ADMIN'}


def _can_check(context: AuthContext) -> bool:
  return context.operator.role in {'APPROVER', 'ADMIN'}


def _get_target(db: Session, target_id: int, context: AuthContext | None = None, action: ProjectAction = ProjectAction.READ) -> ConnectionTarget:
  target = db.get(ConnectionTarget, target_id)
  if target is None:
    raise HTTPException(status_code=404, detail='Connection target not found.')
  if context is not None:
    ProjectAccessService(db, context.operator.id).require(target.project_id, action)
  return target


def _page(limit: int, offset: int, total: int) -> Page:
  return Page(limit=limit, offset=offset, total=total)


def _apply_target_payload(target: ConnectionTarget, payload: ConnectionTargetCreate | ConnectionTargetUpdate) -> bool:
  data = payload.model_dump(exclude_unset=True)
  origin_fields = {'environment_type', 'base_url', 'allowed_probe_paths', 'tls_required', 'tls_verify', 'connection_timeout_seconds'}
  origin_changed = False
  if 'environment_type' in data and data['environment_type'] is not None:
    env = validate_environment(data['environment_type'].value if hasattr(data['environment_type'], 'value') else data['environment_type'])
    if target.environment_type != env:
      target.environment_type = env; origin_changed = True
  if 'base_url' in data and data['base_url'] is not None:
    normalized = normalize_url(data['base_url'])
    validate_tls_policy(target.environment_type, normalized.scheme, data.get('tls_verify', target.tls_verify))
    if target.normalized_origin and target.normalized_origin != normalized.origin:
      origin_changed = True
    target.base_url = normalized.base_url
    target.normalized_scheme = normalized.scheme
    target.normalized_host = normalized.host
    target.normalized_port = normalized.port
    target.normalized_origin = normalized.origin
  if 'allowed_probe_paths' in data and data['allowed_probe_paths'] is not None:
    next_paths = probe_paths_json(data['allowed_probe_paths'])
    if target.allowed_probe_paths_json != next_paths:
      target.allowed_probe_paths_json = next_paths; origin_changed = True
  for field in ('tls_required', 'tls_verify', 'connection_timeout_seconds'):
    if field in data and data[field] is not None and getattr(target, field) != data[field]:
      setattr(target, field, data[field]); origin_changed = origin_changed or field in origin_fields
  validate_tls_policy(target.environment_type, target.normalized_scheme, target.tls_verify)
  for field in ('name', 'description', 'owner_operator_id'):
    if field in data:
      value = data[field]
      setattr(target, field, value.strip() if isinstance(value, str) else value)
  return origin_changed


@router.get('/connection-targets', response_model=ConnectionTargetList)
def list_targets(search: str | None = None, lifecycle_state: str | None = None, environment_type: str | None = None, enabled: bool | None = None, include_archived: bool = False, limit: int = Query(50, ge=1, le=200), offset: int = Query(0, ge=0), context: AuthContext = Depends(get_auth_context), db: Session = Depends(get_db)):
  project_ids = ProjectAccessService(db, context.operator.id).project_ids()
  statement = select(ConnectionTarget).where(ConnectionTarget.project_id.in_(project_ids))
  count_statement = select(func.count(ConnectionTarget.id)).where(ConnectionTarget.project_id.in_(project_ids))
  filters = []
  if not include_archived:
    filters.append(ConnectionTarget.lifecycle_state != 'ARCHIVED')
  if search:
    term = f'%{search.strip().lower()}%'
    filters.append(func.lower(ConnectionTarget.name).like(term) | func.lower(ConnectionTarget.target_key).like(term) | func.lower(ConnectionTarget.normalized_origin).like(term))
  if lifecycle_state:
    filters.append(ConnectionTarget.lifecycle_state == lifecycle_state.upper())
  if environment_type:
    filters.append(ConnectionTarget.environment_type == environment_type.upper())
  if enabled is not None:
    filters.append(ConnectionTarget.enabled == enabled)
  for item in filters:
    statement = statement.where(item)
    count_statement = count_statement.where(item)
  total = db.scalar(count_statement) or 0
  items = [target_read(item) for item in db.scalars(statement.order_by(ConnectionTarget.updated_at.desc(), ConnectionTarget.id.desc()).offset(offset).limit(limit))]
  return ConnectionTargetList(items=items, page=_page(limit, offset, total))


@router.post('/connection-targets', response_model=ConnectionTargetRead, status_code=201)
def create_target(payload: ConnectionTargetCreate, context: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)):
  if not _can_author(context):
    raise HTTPException(status_code=403, detail='You do not have permission to perform this action.')
  project_id = ProjectAccessService(db, context.operator.id).resolve(payload.project_id, ProjectAction.TEST)
  env = validate_environment(payload.environment_type.value)
  normalized = normalize_url(payload.base_url)
  validate_tls_policy(env, normalized.scheme, payload.tls_verify)
  target = ConnectionTarget(
    project_id=project_id,
    target_key=normalize_target_key(payload.target_key),
    name=payload.name.strip(),
    description=payload.description,
    environment_type=env,
    base_url=normalized.base_url,
    normalized_scheme=normalized.scheme,
    normalized_host=normalized.host,
    normalized_port=normalized.port,
    normalized_origin=normalized.origin,
    allowed_probe_paths_json=probe_paths_json(payload.allowed_probe_paths),
    tls_required=payload.tls_required,
    tls_verify=payload.tls_verify,
    connection_timeout_seconds=payload.connection_timeout_seconds,
    owner_operator_id=payload.owner_operator_id,
    created_by=context.operator.id,
  )
  db.add(target)
  try:
    db.flush()
    create_target_version(db, target, context.operator.id, 'Initial draft', 'DRAFT')
  except IntegrityError:
    db.rollback()
    raise HTTPException(status_code=409, detail='Target key already exists.') from None
  append_event(db, 'connection_target_created', operator_id=context.operator.id, resource_type='CONNECTION_TARGET', resource_id=str(target.id), metadata={'target_key': target.target_key, 'environment': target.environment_type})
  db.commit(); db.refresh(target); return target_read(target)


@router.get('/connection-targets/{target_id}', response_model=ConnectionTargetRead)
def get_target(target_id: int, context: AuthContext = Depends(get_auth_context), db: Session = Depends(get_db)):
  return target_read(_get_target(db, target_id, context))


@router.patch('/connection-targets/{target_id}', response_model=ConnectionTargetRead)
def update_target(target_id: int, payload: ConnectionTargetUpdate, context: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)):
  target = _get_target(db, target_id, context, ProjectAction.TEST)
  if target.lifecycle_state not in {'DRAFT', 'REJECTED', 'APPROVED', 'DISABLED'}:
    raise HTTPException(status_code=409, detail='Target cannot be edited in its current state.')
  if context.operator.role != 'ADMIN' and target.created_by != context.operator.id:
    raise HTTPException(status_code=403, detail='Only the creator or ADMIN can edit this target.')
  if payload.version is not None and payload.version != target.version:
    raise HTTPException(status_code=409, detail='Target version conflict.')
  origin_changed = _apply_target_payload(target, payload)
  if origin_changed and target.lifecycle_state in {'APPROVED', 'DISABLED'}:
    target.lifecycle_state = 'DRAFT'
    target.enabled = False
    target.approved_by = None
    target.approved_at = None
    target.reviewed_by = None
    target.submitted_at = None
    target.execution_enabled = False
    target.execution_submitted_by = None
    target.execution_submitted_at = None
    target.execution_approved_by = None
    target.execution_approved_at = None
  target.updated_at = datetime.utcnow()
  create_target_version(db, target, context.operator.id, 'Target updated', target.lifecycle_state)
  append_event(db, 'connection_target_updated', operator_id=context.operator.id, resource_type='CONNECTION_TARGET', resource_id=str(target.id), metadata={'target_key': target.target_key, 'requires_review': origin_changed})
  db.commit(); return target_read(_get_target(db, target_id))


@router.post('/connection-targets/{target_id}/submit', response_model=ConnectionTargetRead)
def submit_target(target_id: int, context: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)):
  target = _get_target(db, target_id, context, ProjectAction.TEST)
  if target.lifecycle_state not in {'DRAFT', 'REJECTED', 'DISABLED'}:
    raise HTTPException(status_code=409, detail='Only draft, rejected, or disabled targets can be submitted.')
  if context.operator.role != 'ADMIN' and target.created_by != context.operator.id:
    raise HTTPException(status_code=403, detail='Only the creator or ADMIN can submit this target.')
  target.lifecycle_state = 'IN_REVIEW'; target.enabled = False; target.submitted_at = datetime.utcnow(); target.rejection_reason = None; target.updated_at = datetime.utcnow()
  create_target_version(db, target, context.operator.id, 'Submitted for review', 'IN_REVIEW')
  append_event(db, 'connection_target_submitted', operator_id=context.operator.id, resource_type='CONNECTION_TARGET', resource_id=str(target.id), metadata={'target_key': target.target_key})
  db.commit(); return target_read(_get_target(db, target_id))


@router.post('/connection-targets/{target_id}/approve', response_model=ConnectionTargetRead)
def approve_target(target_id: int, context: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)):
  if not _can_review(context):
    raise HTTPException(status_code=403, detail='You do not have permission to perform this action.')
  target = _get_target(db, target_id, context, ProjectAction.APPROVE)
  if target.lifecycle_state != 'IN_REVIEW':
    raise HTTPException(status_code=409, detail='Only targets in review can be approved.')
  if target.created_by == context.operator.id:
    append_event(db, 'connection_target_approval_denied', 'DENIED', context.operator.id, resource_type='CONNECTION_TARGET', resource_id=str(target.id), metadata={'reason': 'creator_separation'})
    db.commit()
    raise HTTPException(status_code=400, detail='Target creators cannot approve their own target.')
  validate_environment(target.environment_type)
  target.lifecycle_state = 'APPROVED'; target.enabled = True; target.approved_by = context.operator.id; target.reviewed_by = context.operator.id; target.approved_at = datetime.utcnow(); target.updated_at = datetime.utcnow()
  create_target_version(db, target, context.operator.id, 'Approved', 'APPROVED')
  append_event(db, 'connection_target_approved', operator_id=context.operator.id, resource_type='CONNECTION_TARGET', resource_id=str(target.id), metadata={'target_key': target.target_key, 'version': target.version})
  db.commit(); return target_read(_get_target(db, target_id))


@router.post('/connection-targets/{target_id}/reject', response_model=ConnectionTargetRead)
def reject_target(target_id: int, payload: LifecycleReason, context: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)):
  if not _can_review(context):
    raise HTTPException(status_code=403, detail='You do not have permission to perform this action.')
  if not payload.reason or not payload.reason.strip():
    raise HTTPException(status_code=422, detail='Rejection reason is required.')
  target = _get_target(db, target_id, context, ProjectAction.APPROVE)
  if target.lifecycle_state != 'IN_REVIEW':
    raise HTTPException(status_code=409, detail='Only targets in review can be rejected.')
  if target.created_by == context.operator.id:
    raise HTTPException(status_code=400, detail='Target creators cannot review their own target.')
  target.lifecycle_state = 'REJECTED'; target.enabled = False; target.reviewed_by = context.operator.id; target.rejected_at = datetime.utcnow(); target.rejection_reason = payload.reason.strip(); target.updated_at = datetime.utcnow()
  create_target_version(db, target, context.operator.id, payload.reason.strip(), 'REJECTED')
  append_event(db, 'connection_target_rejected', operator_id=context.operator.id, resource_type='CONNECTION_TARGET', resource_id=str(target.id), metadata={'target_key': target.target_key})
  db.commit(); return target_read(_get_target(db, target_id))


@router.post('/connection-targets/{target_id}/revision', response_model=ConnectionTargetRead)
def revise_target(target_id: int, payload: LifecycleReason, context: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)):
  target = _get_target(db, target_id, context, ProjectAction.TEST)
  if target.lifecycle_state != 'REJECTED':
    raise HTTPException(status_code=409, detail='Only rejected targets can return to draft revision.')
  if context.operator.role != 'ADMIN' and target.created_by != context.operator.id:
    raise HTTPException(status_code=403, detail='Only the creator or ADMIN can revise this target.')
  target.lifecycle_state = 'DRAFT'; target.enabled = False; target.reviewed_by = None; target.rejection_reason = None; target.updated_at = datetime.utcnow()
  create_target_version(db, target, context.operator.id, payload.reason or 'Draft revision created', 'DRAFT')
  append_event(db, 'connection_target_revision_created', operator_id=context.operator.id, resource_type='CONNECTION_TARGET', resource_id=str(target.id), metadata={'target_key': target.target_key})
  db.commit(); return target_read(_get_target(db, target_id))


@router.post('/connection-targets/{target_id}/disable', response_model=ConnectionTargetRead)
def disable_target(target_id: int, context: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)):
  if context.operator.role != 'ADMIN':
    raise HTTPException(status_code=403, detail='You do not have permission to perform this action.')
  target = _get_target(db, target_id, context, ProjectAction.MANAGE)
  if target.lifecycle_state != 'APPROVED':
    raise HTTPException(status_code=409, detail='Only approved targets can be disabled.')
  target.lifecycle_state = 'DISABLED'; target.enabled = False; target.execution_enabled = False; target.disabled_at = datetime.utcnow(); target.updated_at = datetime.utcnow()
  create_target_version(db, target, context.operator.id, 'Disabled', 'DISABLED')
  append_event(db, 'connection_target_disabled', operator_id=context.operator.id, resource_type='CONNECTION_TARGET', resource_id=str(target.id), metadata={'target_key': target.target_key})
  db.commit(); return target_read(_get_target(db, target_id))


@router.post('/connection-targets/{target_id}/archive', response_model=ConnectionTargetRead)
def archive_target(target_id: int, context: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)):
  if context.operator.role != 'ADMIN':
    raise HTTPException(status_code=403, detail='You do not have permission to perform this action.')
  target = _get_target(db, target_id, context, ProjectAction.MANAGE)
  if target.lifecycle_state == 'ARCHIVED':
    raise HTTPException(status_code=409, detail='Target is already archived.')
  target.lifecycle_state = 'ARCHIVED'; target.enabled = False; target.execution_enabled = False; target.archived_at = datetime.utcnow(); target.updated_at = datetime.utcnow()
  create_target_version(db, target, context.operator.id, 'Archived', 'ARCHIVED')
  append_event(db, 'connection_target_archived', operator_id=context.operator.id, resource_type='CONNECTION_TARGET', resource_id=str(target.id), metadata={'target_key': target.target_key})
  db.commit(); return target_read(_get_target(db, target_id))


@router.post('/connection-targets/{target_id}/execution-submit', response_model=ConnectionTargetRead)
def submit_target_execution(target_id: int, context: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)):
  target = _get_target(db, target_id, context, ProjectAction.TEST)
  if not _can_author(context):
    raise HTTPException(status_code=403, detail='You do not have permission to perform this action.')
  if target.lifecycle_state != 'APPROVED' or not target.enabled:
    raise HTTPException(status_code=409, detail='Only approved enabled targets can be submitted for execution approval.')
  if target.environment_type == 'PRODUCTION':
    raise HTTPException(status_code=403, detail='Production execution is blocked.')
  if context.operator.role != 'ADMIN' and target.created_by != context.operator.id:
    raise HTTPException(status_code=403, detail='Only the creator or ADMIN can request execution approval.')
  target.execution_enabled = False
  target.execution_submitted_by = context.operator.id
  target.execution_submitted_at = datetime.utcnow()
  target.execution_approved_by = None
  target.execution_approved_at = None
  target.updated_at = datetime.utcnow()
  append_event(db, 'connection_target_execution_submitted', operator_id=context.operator.id, resource_type='CONNECTION_TARGET', resource_id=str(target.id), metadata={'target_key': target.target_key})
  db.commit(); return target_read(_get_target(db, target_id))


@router.post('/connection-targets/{target_id}/execution-approve', response_model=ConnectionTargetRead)
def approve_target_execution(target_id: int, context: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)):
  if not _can_review(context):
    raise HTTPException(status_code=403, detail='You do not have permission to perform this action.')
  target = _get_target(db, target_id, context, ProjectAction.APPROVE)
  if target.lifecycle_state != 'APPROVED' or not target.enabled:
    raise HTTPException(status_code=409, detail='Only approved enabled targets can receive execution approval.')
  if target.environment_type == 'PRODUCTION':
    raise HTTPException(status_code=403, detail='Production execution is blocked.')
  if target.execution_submitted_by is None:
    raise HTTPException(status_code=409, detail='Execution approval must be requested first.')
  if target.created_by == context.operator.id or target.execution_submitted_by == context.operator.id:
    append_event(db, 'connection_target_execution_approval_denied', 'DENIED', context.operator.id, resource_type='CONNECTION_TARGET', resource_id=str(target.id), metadata={'reason': 'creator_separation'})
    db.commit()
    raise HTTPException(status_code=400, detail='Target creators cannot approve execution for their own target.')
  target.execution_enabled = True
  target.execution_approved_by = context.operator.id
  target.execution_approved_at = datetime.utcnow()
  target.updated_at = datetime.utcnow()
  append_event(db, 'connection_target_execution_approved', operator_id=context.operator.id, resource_type='CONNECTION_TARGET', resource_id=str(target.id), metadata={'target_key': target.target_key, 'target_version': target.version})
  db.commit(); return target_read(_get_target(db, target_id))


@router.post('/connection-targets/{target_id}/execution-disable', response_model=ConnectionTargetRead)
def disable_target_execution(target_id: int, context: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)):
  if context.operator.role != 'ADMIN':
    raise HTTPException(status_code=403, detail='You do not have permission to perform this action.')
  target = _get_target(db, target_id, context, ProjectAction.MANAGE)
  target.execution_enabled = False
  target.execution_approved_by = None
  target.execution_approved_at = None
  target.updated_at = datetime.utcnow()
  append_event(db, 'connection_target_execution_disabled', operator_id=context.operator.id, resource_type='CONNECTION_TARGET', resource_id=str(target.id), metadata={'target_key': target.target_key})
  db.commit(); return target_read(_get_target(db, target_id))


@router.get('/connection-targets/{target_id}/versions', response_model=list[ConnectionTargetVersionRead])
def list_target_versions(target_id: int, context: AuthContext = Depends(get_auth_context), db: Session = Depends(get_db)):
  _get_target(db, target_id, context)
  return list(db.scalars(select(ConnectionTargetVersion).where(ConnectionTargetVersion.target_id == target_id).order_by(ConnectionTargetVersion.version_number)))


@router.get('/connection-targets/{target_id}/checks', response_model=list[ConnectionCheckRead])
def list_target_checks(target_id: int, context: AuthContext = Depends(get_auth_context), db: Session = Depends(get_db)):
  _get_target(db, target_id, context)
  append_event(db, 'connection_history_viewed', operator_id=context.operator.id, resource_type='CONNECTION_TARGET', resource_id=str(target_id)); db.commit()
  return [check_read(item) for item in db.scalars(select(ConnectionCheck).where(ConnectionCheck.target_id == target_id).order_by(ConnectionCheck.created_at.desc()).limit(100))]


@router.post('/connection-targets/{target_id}/checks', response_model=ConnectionCheckRead, status_code=201)
def create_target_check(target_id: int, payload: ConnectionCheckCreate, context: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)):
  if not _can_check(context):
    raise HTTPException(status_code=403, detail='You do not have permission to perform this action.')
  target = _get_target(db, target_id, context, ProjectAction.APPROVE)
  append_event(db, 'connection_check_started', operator_id=context.operator.id, resource_type='CONNECTION_TARGET', resource_id=str(target.id), metadata={'method': payload.method.value, 'probe_path': payload.probe_path})
  check = run_connection_check(db, target, payload.method.value, payload.probe_path, context.operator.id)
  append_event(db, 'connection_check_completed' if check.status == 'REACHABLE' else 'connection_check_failed', 'SUCCESS' if check.status == 'REACHABLE' else 'FAILED', context.operator.id, resource_type='CONNECTION_CHECK', resource_id=str(check.id), metadata={'status': check.status, 'http_status': check.http_status, 'target_version': check.target_version})
  db.commit(); db.refresh(check); return check_read(check)


@router.get('/connection-checks/{check_id}', response_model=ConnectionCheckRead)
def get_connection_check(check_id: int, context: AuthContext = Depends(get_auth_context), db: Session = Depends(get_db)):
  check = db.get(ConnectionCheck, check_id)
  if check is None:
    raise HTTPException(status_code=404, detail='Connection check not found.')
  ProjectAccessService(db, context.operator.id).require(check.project_id)
  return check_read(check)


@router.get('/connection-targets/{target_id}/credential-profiles', response_model=list[CredentialProfileRead])
def list_credential_profiles(target_id: int, context: AuthContext = Depends(get_auth_context), db: Session = Depends(get_db)):
  _get_target(db, target_id, context)
  return list(db.scalars(select(TargetCredentialProfile).where(TargetCredentialProfile.target_id == target_id).order_by(TargetCredentialProfile.profile_name)))


@router.post('/connection-targets/{target_id}/credential-profiles', response_model=CredentialProfileRead, status_code=201)
def create_credential_profile(target_id: int, payload: CredentialProfileCreate, context: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)):
  if context.operator.role not in {'TESTER', 'ADMIN'}:
    raise HTTPException(status_code=403, detail='You do not have permission to perform this action.')
  target = _get_target(db, target_id, context, ProjectAction.TEST)
  item = TargetCredentialProfile(project_id=target.project_id, target_id=target_id, profile_name=payload.profile_name.strip(), username_hint=payload.username_hint, secret_source=payload.secret_source.value, enabled=payload.enabled, created_by=context.operator.id)
  db.add(item)
  try: db.flush()
  except IntegrityError:
    db.rollback(); raise HTTPException(status_code=409, detail='Credential profile already exists for this target.') from None
  append_event(db, 'credential_profile_created', operator_id=context.operator.id, resource_type='CONNECTION_TARGET', resource_id=str(target_id), metadata={'profile_name': item.profile_name, 'secret_source': item.secret_source})
  db.commit(); db.refresh(item); return item


@router.patch('/credential-profiles/{profile_id}', response_model=CredentialProfileRead)
def update_credential_profile(profile_id: int, payload: CredentialProfileUpdate, context: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)):
  if context.operator.role not in {'TESTER', 'ADMIN'}:
    raise HTTPException(status_code=403, detail='You do not have permission to perform this action.')
  item = db.get(TargetCredentialProfile, profile_id)
  if item is None:
    raise HTTPException(status_code=404, detail='Credential profile not found.')
  ProjectAccessService(db, context.operator.id).require(item.project_id, ProjectAction.TEST)
  for key, value in payload.model_dump(exclude_unset=True).items():
    if hasattr(value, 'value'):
      value = value.value
    setattr(item, key, value.strip() if isinstance(value, str) else value)
  append_event(db, 'credential_profile_updated', operator_id=context.operator.id, resource_type='CREDENTIAL_PROFILE', resource_id=str(item.id), metadata={'secret_source': item.secret_source})
  db.commit(); db.refresh(item); return item
