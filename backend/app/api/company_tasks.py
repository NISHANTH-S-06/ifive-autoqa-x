"""
Company Task API — Phase 2 Enterprise task lifecycle management.

New Status Pipeline:
  NEW → ASSIGNED → IN_PROGRESS → DEVELOPER_COMPLETED
      → TESTING_L2 → TEST_APPROVED → AUTOQA_RUNNING
      → PASSED → DELIVERY_COMPLETED
      → FAILED → BACK_TO_DEVELOPER (loop)
      → CLOSED (terminal)

Role-based access:
  PROJECT_MANAGER / ADMIN  — Create, update, assign, close, mark delivery complete
  DEVELOPER                — Update own tasks (IN_PROGRESS → DEVELOPER_COMPLETED)
  TESTER / APPROVER        — Move to TESTING_L2, approve & run AutoQA
  VIEWER                   — Read-only
"""
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import AuthContext, get_auth_context, require_csrf, require_roles
from app.database import get_db
from app.models.automated_execution import AutomatedRun, ExecutionArtifact
from app.models.company_task import CompanyTask
from app.models.operator import Operator
from app.schemas.company_task import (
  AutoQARunStatusRead,
  CompanyTaskCreate,
  CompanyTaskListRead,
  CompanyTaskRead,
  CompanyTaskUpdate,
  TaskAssignRequest,
  TaskAssignTesterRequest,
  TaskStatus,
  TaskStatusTransition,
  ApproveAutoQARequest,
)
from app.services.audit_service import append_event
from app.services.company_task_autoqa import trigger_autoqa_for_task, parse_expected_flow_to_steps

router = APIRouter(prefix='/company-tasks', tags=['company-tasks'])

# ---------------------------------------------------------------------------
# Status transition rules (role → allowed moves)
# ---------------------------------------------------------------------------

ALLOWED_TRANSITIONS: dict[str, dict[str, list[str]]] = {
  'NEW': {
    'PROJECT_MANAGER': ['ASSIGNED', 'CLOSED'],
    'ADMIN':           ['ASSIGNED', 'IN_PROGRESS', 'CLOSED'],
  },
  'ASSIGNED': {
    'DEVELOPER':       ['IN_PROGRESS'],
    'PROJECT_MANAGER': ['NEW', 'CLOSED'],
    'ADMIN':           ['NEW', 'IN_PROGRESS', 'CLOSED'],
  },
  'IN_PROGRESS': {
    'DEVELOPER':       ['DEVELOPER_COMPLETED'],
    'PROJECT_MANAGER': ['ASSIGNED', 'CLOSED'],
    'ADMIN':           ['ASSIGNED', 'DEVELOPER_COMPLETED', 'CLOSED'],
  },
  'DEVELOPER_COMPLETED': {
    'DEVELOPER':       ['IN_PROGRESS'],       # take back for changes
    'TESTER':          ['TESTING_L2'],        # tester picks up
    'APPROVER':        ['TESTING_L2'],
    'PROJECT_MANAGER': ['IN_PROGRESS', 'TESTING_L2'],
    'ADMIN':           ['IN_PROGRESS', 'TESTING_L2'],
  },
  'TESTING_L2': {
    'TESTER':          ['TEST_APPROVED', 'DEVELOPER_COMPLETED'],  # approve or send back
    'APPROVER':        ['TEST_APPROVED', 'DEVELOPER_COMPLETED'],
    'PROJECT_MANAGER': ['DEVELOPER_COMPLETED'],
    'ADMIN':           ['DEVELOPER_COMPLETED', 'TEST_APPROVED'],
  },
  'TEST_APPROVED': {
    # AutoQA is triggered — normally auto-transitions. Admin can revert.
    'ADMIN':           ['TESTING_L2'],
  },
  'AUTOQA_RUNNING': {
    # Only admin emergency revert
    'ADMIN':           ['TESTING_L2'],
  },
  'PASSED': {
    'PROJECT_MANAGER': ['DELIVERY_COMPLETED', 'CLOSED'],
    'ADMIN':           ['DELIVERY_COMPLETED', 'CLOSED'],
  },
  'FAILED': {
    'PROJECT_MANAGER': ['BACK_TO_DEVELOPER'],
    'ADMIN':           ['BACK_TO_DEVELOPER', 'TESTING_L2'],
  },
  'BACK_TO_DEVELOPER': {
    'DEVELOPER':       ['IN_PROGRESS'],
    'PROJECT_MANAGER': ['IN_PROGRESS', 'CLOSED'],
    'ADMIN':           ['IN_PROGRESS', 'TESTING_L2', 'CLOSED'],
  },
  'DELIVERY_COMPLETED': {
    'ADMIN': ['CLOSED'],
  },
  'CLOSED': {
    'ADMIN': ['NEW'],   # reopen only by admin
  },
}


def _can_transition(current: str, new: str, role: str) -> bool:
  return new in ALLOWED_TRANSITIONS.get(current, {}).get(role, [])


def _get_task_or_404(task_id: int, db: Session) -> CompanyTask:
  task = db.get(CompanyTask, task_id)
  if not task:
    raise HTTPException(status_code=404, detail='Task not found.')
  return task


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get('', response_model=list[CompanyTaskListRead])
def list_tasks(
  status: str | None = Query(default=None),
  priority: str | None = Query(default=None),
  severity: str | None = Query(default=None),
  project_id: int | None = Query(default=None),
  assigned_to_me: bool = Query(default=False),
  context: AuthContext = Depends(get_auth_context),
  db: Session = Depends(get_db),
):
  """List tasks. Developers only see their own tasks by default."""
  stmt = select(CompanyTask)
  role = context.operator.role

  if role == 'DEVELOPER':
    stmt = stmt.where(CompanyTask.assigned_developer_id == context.operator.id)
  elif role == 'TESTER':
    # Testers see tasks assigned to them + all DEVELOPER_COMPLETED / TESTING_L2
    stmt = stmt.where(
      (CompanyTask.assigned_tester_id == context.operator.id) |
      CompanyTask.status.in_(['DEVELOPER_COMPLETED', 'TESTING_L2', 'TEST_APPROVED'])
    )
  elif assigned_to_me:
    stmt = stmt.where(CompanyTask.assigned_developer_id == context.operator.id)

  if status:
    stmt = stmt.where(CompanyTask.status == status.upper())
  if priority:
    stmt = stmt.where(CompanyTask.priority == priority.upper())
  if severity:
    stmt = stmt.where(CompanyTask.severity == severity.upper())
  if project_id:
    stmt = stmt.where(CompanyTask.project_id == project_id)

  return list(db.scalars(stmt.order_by(CompanyTask.updated_at.desc())))


@router.get('/my-tasks', response_model=list[CompanyTaskListRead])
def get_my_tasks(
  context: AuthContext = Depends(require_roles('DEVELOPER', 'ADMIN')),
  db: Session = Depends(get_db),
):
  """Developer: all active tasks assigned to me."""
  stmt = (
    select(CompanyTask)
    .where(CompanyTask.assigned_developer_id == context.operator.id)
    .where(CompanyTask.status.not_in(['DELIVERY_COMPLETED', 'CLOSED']))
    .order_by(CompanyTask.updated_at.desc())
  )
  return list(db.scalars(stmt))


@router.get('/pending-approval', response_model=list[CompanyTaskListRead])
def get_pending_approval(
  context: AuthContext = Depends(require_roles('TESTER', 'APPROVER', 'ADMIN')),
  db: Session = Depends(get_db),
):
  """Tester: tasks ready for review (DEVELOPER_COMPLETED or TESTING_L2)."""
  stmt = (
    select(CompanyTask)
    .where(CompanyTask.status.in_(['DEVELOPER_COMPLETED', 'TESTING_L2']))
    .order_by(CompanyTask.developer_completed_at.asc().nullsfirst())
  )
  return list(db.scalars(stmt))


@router.get('/{task_id}', response_model=CompanyTaskRead)
def get_task(
  task_id: int,
  context: AuthContext = Depends(get_auth_context),
  db: Session = Depends(get_db),
):
  task = _get_task_or_404(task_id, db)
  role = context.operator.role
  if role == 'DEVELOPER' and task.assigned_developer_id != context.operator.id:
    raise HTTPException(status_code=403, detail='You can only view your own tasks.')
  return task


@router.get('/{task_id}/run-status', response_model=AutoQARunStatusRead)
def get_task_run_status(
  task_id: int,
  context: AuthContext = Depends(get_auth_context),
  db: Session = Depends(get_db),
):
  """
  Live poll endpoint — returns current AutoQA execution progress.
  Frontend polls this every 2s while task.status == AUTOQA_RUNNING.
  """
  task = _get_task_or_404(task_id, db)
  run: AutomatedRun | None = None
  artifact_count = 0

  if task.autoqa_run_id:
    run = db.get(AutomatedRun, task.autoqa_run_id)
    if run:
      artifact_count = db.scalar(
        select(ExecutionArtifact).where(ExecutionArtifact.run_id == run.id).with_only_columns(
          __import__('sqlalchemy').func.count(ExecutionArtifact.id)
        )
      ) or 0

  from app.services.automated_execution import progress as run_progress
  return AutoQARunStatusRead(
    task_id=task_id,
    task_status=task.status,
    autoqa_run_id=task.autoqa_run_id,
    run_status=run.status if run else None,
    progress=run_progress(run) if run else None,
    completed_steps=run.completed_steps if run else 0,
    failed_steps=run.failed_steps if run else 0,
    total_steps=run.total_steps if run else 0,
    autoqa_result=task.autoqa_result,
    autoqa_notes=task.autoqa_notes,
    artifact_count=artifact_count,
  )


@router.post('', response_model=CompanyTaskRead, status_code=201)
def create_task(
  payload: CompanyTaskCreate,
  context: AuthContext = Depends(require_csrf),
  db: Session = Depends(get_db),
):
  """PM or Admin creates a task (status starts as NEW)."""
  if context.operator.role not in ('PROJECT_MANAGER', 'ADMIN'):
    raise HTTPException(status_code=403, detail='Only Project Managers and Admins can create tasks.')

  now = datetime.utcnow()
  initial_status = 'ASSIGNED' if payload.assigned_developer_id else 'NEW'

  task = CompanyTask(
    title=payload.title.strip(),
    module=payload.module,
    feature=payload.feature,
    description=payload.description,
    target_url=payload.target_url,
    expected_flow=payload.expected_flow,
    acceptance_criteria=payload.acceptance_criteria,
    expected_result=payload.expected_result,
    api_endpoint=payload.api_endpoint,
    browser=payload.browser.value,
    environment=payload.environment,
    reference_screenshot_url=payload.reference_screenshot_url,
    priority=payload.priority.value,
    severity=payload.severity.value,
    estimated_hours=payload.estimated_hours,
    target_date=payload.target_date,
    project_id=payload.project_id,
    assigned_developer_id=payload.assigned_developer_id,
    assigned_tester_id=payload.assigned_tester_id,
    created_by=context.operator.id,
    status=initial_status,
    assigned_at=now if payload.assigned_developer_id else None,
  )
  db.add(task)
  db.flush()
  append_event(
    db, 'COMPANY_TASK_CREATED',
    operator_id=context.operator.id,
    resource_type='COMPANY_TASK',
    resource_id=str(task.id),
    metadata={'title': task.title, 'status': task.status, 'priority': task.priority},
  )
  db.commit()
  db.refresh(task)
  return task


@router.patch('/{task_id}', response_model=CompanyTaskRead)
def update_task(
  task_id: int,
  payload: CompanyTaskUpdate,
  context: AuthContext = Depends(require_csrf),
  db: Session = Depends(get_db),
):
  """PM or Admin updates task metadata (does not change status)."""
  if context.operator.role not in ('PROJECT_MANAGER', 'ADMIN'):
    raise HTTPException(status_code=403, detail='Only Project Managers and Admins can update task details.')
  task = _get_task_or_404(task_id, db)
  for field, value in payload.model_dump(exclude_none=True).items():
    if field in ('priority', 'severity', 'browser') and value:
      setattr(task, field, value.value if hasattr(value, 'value') else value)
    else:
      setattr(task, field, value)
  append_event(db, 'COMPANY_TASK_UPDATED', operator_id=context.operator.id, resource_type='COMPANY_TASK', resource_id=str(task.id))
  db.commit()
  db.refresh(task)
  return task


@router.post('/{task_id}/assign', response_model=CompanyTaskRead)
def assign_developer(
  task_id: int,
  payload: TaskAssignRequest,
  context: AuthContext = Depends(require_csrf),
  db: Session = Depends(get_db),
):
  """PM or Admin assigns a developer to a task."""
  if context.operator.role not in ('PROJECT_MANAGER', 'ADMIN'):
    raise HTTPException(status_code=403, detail='Only Project Managers and Admins can assign tasks.')
  task = _get_task_or_404(task_id, db)
  developer = db.get(Operator, payload.developer_id)
  if not developer or developer.role not in ('DEVELOPER', 'ADMIN'):
    raise HTTPException(status_code=400, detail='Invalid developer: not found or wrong role.')
  if not developer.is_active:
    raise HTTPException(status_code=400, detail='Cannot assign to an inactive operator.')

  task.assigned_developer_id = payload.developer_id
  if task.status == 'NEW':
    task.status = 'ASSIGNED'
    task.assigned_at = datetime.utcnow()

  append_event(db, 'COMPANY_TASK_ASSIGNED', operator_id=context.operator.id,
               resource_type='COMPANY_TASK', resource_id=str(task.id),
               metadata={'developer_id': payload.developer_id})
  db.commit()
  db.refresh(task)
  return task


@router.post('/{task_id}/assign-tester', response_model=CompanyTaskRead)
def assign_tester(
  task_id: int,
  payload: TaskAssignTesterRequest,
  context: AuthContext = Depends(require_csrf),
  db: Session = Depends(get_db),
):
  """PM or Admin assigns a tester to a task."""
  if context.operator.role not in ('PROJECT_MANAGER', 'ADMIN'):
    raise HTTPException(status_code=403, detail='Only Project Managers and Admins can assign testers.')
  task = _get_task_or_404(task_id, db)
  tester = db.get(Operator, payload.tester_id)
  if not tester or tester.role not in ('TESTER', 'APPROVER', 'ADMIN'):
    raise HTTPException(status_code=400, detail='Invalid tester: not found or wrong role.')
  if not tester.is_active:
    raise HTTPException(status_code=400, detail='Cannot assign to an inactive operator.')

  task.assigned_tester_id = payload.tester_id
  append_event(db, 'COMPANY_TASK_TESTER_ASSIGNED', operator_id=context.operator.id,
               resource_type='COMPANY_TASK', resource_id=str(task.id),
               metadata={'tester_id': payload.tester_id})
  db.commit()
  db.refresh(task)
  return task


@router.post('/{task_id}/status', response_model=CompanyTaskRead)
def transition_status(
  task_id: int,
  payload: TaskStatusTransition,
  context: AuthContext = Depends(require_csrf),
  db: Session = Depends(get_db),
):
  """Manual status transition (role-based rules enforced)."""
  task = _get_task_or_404(task_id, db)
  role = context.operator.role
  new_status = payload.status.value

  if role == 'DEVELOPER' and task.assigned_developer_id != context.operator.id:
    raise HTTPException(status_code=403, detail='You can only update your own assigned tasks.')

  if not _can_transition(task.status, new_status, role):
    raise HTTPException(
      status_code=400,
      detail=f"Cannot move task from '{task.status}' to '{new_status}' as role '{role}'.",
    )

  now = datetime.utcnow()
  old_status = task.status
  task.status = new_status

  # Set milestone timestamps
  _ts = {
    'ASSIGNED': 'assigned_at',
    'IN_PROGRESS': 'in_progress_at',
    'DEVELOPER_COMPLETED': 'developer_completed_at',
    'TESTING_L2': 'testing_l2_at',
    'TEST_APPROVED': 'test_approved_at',
    'BACK_TO_DEVELOPER': 'back_to_developer_at',
    'DELIVERY_COMPLETED': 'delivery_completed_at',
    'CLOSED': 'closed_at',
  }
  if new_status in _ts:
    setattr(task, _ts[new_status], now)

  if payload.notes:
    task.autoqa_notes = payload.notes

  append_event(
    db, 'COMPANY_TASK_STATUS_CHANGED',
    operator_id=context.operator.id,
    resource_type='COMPANY_TASK',
    resource_id=str(task.id),
    metadata={'from': old_status, 'to': new_status, 'notes': payload.notes},
  )
  db.commit()
  db.refresh(task)
  return task


@router.post('/{task_id}/approve-autoqa', response_model=CompanyTaskRead)
def approve_and_trigger_autoqa(
  task_id: int,
  payload: ApproveAutoQARequest | None = None,
  context: AuthContext = Depends(require_csrf),
  db: Session = Depends(get_db),
):
  """
  Tester approves a TESTING_L2 task and triggers AutoQA execution.
  Phase 3.5: Tester can optionally provide `payload.steps` which are 
  custom edited steps from the UI (Test Case Editor).
  Non-blocking: returns immediately, Playwright runs in background thread.
  """
  if context.operator.role not in ('TESTER', 'APPROVER', 'ADMIN'):
    raise HTTPException(status_code=403, detail='Only Testers and Admins can approve tasks for AutoQA.')

  task = _get_task_or_404(task_id, db)

  # Pass optional custom steps down to the autoqa engine
  custom_steps = payload.steps if payload else None
  trigger_autoqa_for_task(db, task, context.operator.id, custom_steps)

  db.refresh(task)
  return task


@router.post('/{task_id}/preview-autoqa')
def preview_autoqa_plan(
  task_id: int,
  context: AuthContext = Depends(require_csrf),
  db: Session = Depends(get_db),
) -> list[dict]:
  """
  Tester generates an AI Test Plan preview based on the Expected Flow.
  Phase 3.5: Runs Website Discovery first to extract real DOM selectors,
  then generates the plan using the Navigation Map.
  """
  if context.operator.role not in ('TESTER', 'APPROVER', 'ADMIN'):
    raise HTTPException(status_code=403, detail='Only Testers and Admins can generate AutoQA plans.')
    
  task = _get_task_or_404(task_id, db)
  if not task.target_url:
    raise HTTPException(status_code=400, detail='Task has no Target URL.')
    
  # Phase 3.5: Run Discovery
  from app.services.website_discovery import scan_website
  nav_map = scan_website(task.target_url)
  
  steps = parse_expected_flow_to_steps(task, nav_map)
  
  # The steps contain action as a JSON string. We want to return it parsed for the frontend.
  import json
  preview_steps = []
  for step in steps:
    action_dict = json.loads(step['action'])
    preview_steps.append({
      'step_number': step['step_number'],
      'action_type': action_dict.get('action'),
      'target': action_dict.get('selector') or action_dict.get('path') or action_dict.get('expected') or '',
      'risk_level': action_dict.get('risk_level', 'UNKNOWN'),
      'expected_result': step['expected_result'],
    })
    
  return preview_steps


@router.post('/{task_id}/delivery-complete', response_model=CompanyTaskRead)
def mark_delivery_complete(
  task_id: int,
  context: AuthContext = Depends(require_csrf),
  db: Session = Depends(get_db),
):
  """PM or Admin marks a PASSED task as DELIVERY_COMPLETED."""
  if context.operator.role not in ('PROJECT_MANAGER', 'ADMIN'):
    raise HTTPException(status_code=403, detail='Only Project Managers can mark delivery complete.')
  task = _get_task_or_404(task_id, db)
  if task.status != 'PASSED':
    raise HTTPException(status_code=400, detail=f'Task must be PASSED to mark as delivered. Current: {task.status}')
  task.status = 'DELIVERY_COMPLETED'
  task.delivery_completed_at = datetime.utcnow()
  append_event(db, 'COMPANY_TASK_DELIVERY_COMPLETED', operator_id=context.operator.id,
               resource_type='COMPANY_TASK', resource_id=str(task.id))
  db.commit()
  db.refresh(task)
  return task


@router.delete('/{task_id}', status_code=204)
def delete_task(
  task_id: int,
  context: AuthContext = Depends(require_csrf),
  db: Session = Depends(get_db),
):
  """Admin only: permanently delete a task."""
  if context.operator.role != 'ADMIN':
    raise HTTPException(status_code=403, detail='Only Admins can delete tasks.')
  task = _get_task_or_404(task_id, db)
  append_event(db, 'COMPANY_TASK_DELETED', operator_id=context.operator.id,
               resource_type='COMPANY_TASK', resource_id=str(task.id))
  db.delete(task)
  db.commit()
