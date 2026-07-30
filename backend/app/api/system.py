from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.auth import AuthContext, get_auth_context, require_csrf
from app.config import settings
from app.database import get_db
from app.services.audit_service import append_event
from app.services.backup_service import create_backup, validate_backup
from app.services.diagnostics import health_snapshot
from app.services.retention_service import CONFIRMATION, cleanup_retention


router = APIRouter(prefix='/system', tags=['system'])


class Confirmation(BaseModel):
  confirmation: str = Field(min_length=1, max_length=120)


def _require_admin(context: AuthContext) -> None:
  if context.operator.role != 'ADMIN':
    raise HTTPException(status_code=403, detail='ADMIN role is required.')


@router.get('/health')
def system_health(_: AuthContext = Depends(get_auth_context), db: Session = Depends(get_db)):
  return health_snapshot(db)


@router.get('/backups')
def list_backups(context: AuthContext = Depends(get_auth_context)):
  _require_admin(context)
  items = []
  if settings.backup_root.is_dir():
    for path in sorted(settings.backup_root.iterdir(), reverse=True):
      if not path.is_dir():
        continue
      try:
        validated = validate_backup(path)
        items.append({'backup_id': validated['backup_id'], 'file_count': validated['file_count'], 'valid': True})
      except ValueError:
        items.append({'backup_id': path.name, 'file_count': 0, 'valid': False})
  return items[:50]


@router.post('/backups', status_code=201)
def backup_now(payload: Confirmation, context: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)):
  _require_admin(context)
  if payload.confirmation != 'CREATE LOCAL BACKUP':
    raise HTTPException(status_code=422, detail='Backup confirmation is required.')
  try:
    result = create_backup()
  except (OSError, ValueError) as exc:
    raise HTTPException(status_code=409, detail='Local backup could not be completed safely.') from exc
  append_event(db, 'LOCAL_BACKUP_CREATED', operator_id=context.operator.id, resource_type='BACKUP', resource_id=result['backup_id'], metadata={'file_count': result['file_count'], 'total_bytes': result['total_bytes']})
  db.commit()
  return result


@router.get('/cleanup-preview')
def cleanup_preview(context: AuthContext = Depends(get_auth_context), db: Session = Depends(get_db)):
  _require_admin(context)
  result = cleanup_retention(db, dry_run=True, operator_id=context.operator.id)
  db.commit()
  return result


@router.post('/cleanup')
def cleanup_now(payload: Confirmation, context: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)):
  _require_admin(context)
  if payload.confirmation != CONFIRMATION:
    raise HTTPException(status_code=422, detail='Cleanup confirmation is required.')
  try:
    result = cleanup_retention(db, dry_run=False, confirmation=payload.confirmation, operator_id=context.operator.id)
  except (OSError, ValueError) as exc:
    db.rollback()
    raise HTTPException(status_code=409, detail='Retention cleanup could not be completed safely.') from exc
  db.commit()
  return result


@router.post('/seed-test-data')
def seed_test_data(db: Session = Depends(get_db)):
  if settings.app_env not in {'local', 'development', 'test', 'local-release'} or settings.allow_real_target_execution:
    raise HTTPException(status_code=403, detail="Only available in local/test environments.")

  from app.models.operator import Operator
  from app.models.project import Project
  from app.models.project_membership import ProjectMember
  from app.services.password_service import hash_password
  import datetime

  # Ensure admin exists
  admin = db.query(Operator).filter_by(username='admin').first()
  if not admin:
    admin = Operator(
      username='admin',
      display_name='Admin User',
      password_hash=hash_password('autoqa2026'),
      role='ADMIN',
      is_active=True
    )
    db.add(admin)
  else:
    admin.password_hash = hash_password('autoqa2026')

  # Ensure approver exists
  approver = db.query(Operator).filter_by(username='approver').first()
  if not approver:
    approver = Operator(
      username='approver',
      display_name='Approver User',
      password_hash=hash_password('Approver123'),
      role='ADMIN',
      is_active=True
    )
    db.add(approver)
  else:
    approver.password_hash = hash_password('Approver123')

  # Ensure viewer exists
  viewer = db.query(Operator).filter_by(username='viewer').first()
  if not viewer:
    viewer = Operator(
      username='viewer',
      display_name='Viewer User',
      password_hash=hash_password('Viewer123'),
      role='VIEWER',
      is_active=True
    )
    db.add(viewer)
  else:
    viewer.password_hash = hash_password('Viewer123')

  # Ensure dev1 exists
  dev1 = db.query(Operator).filter_by(username='dev1').first()
  if not dev1:
    dev1 = Operator(
      username='dev1',
      display_name='Developer 1',
      password_hash=hash_password('DevPass123'),
      role='DEVELOPER',
      is_active=True
    )
    db.add(dev1)
  else:
    dev1.password_hash = hash_password('DevPass123')

  # Ensure project2_user exists
  p2_user = db.query(Operator).filter_by(username='project2_user').first()
  if not p2_user:
    p2_user = Operator(
      username='project2_user',
      display_name='Project 2 User',
      password_hash=hash_password('Project2Pass123'),
      role='ADMIN',
      is_active=True
    )
    db.add(p2_user)
  else:
    p2_user.password_hash = hash_password('Project2Pass123')

  db.flush()

  # Ensure project exists
  project = db.query(Project).filter_by(name='Demo ERP').first()
  if not project:
    project = Project(
        name='Demo ERP',
        product_code='ERP',
        description='Demo ERP system',
        environment='test',
        is_active=True
    )
    db.add(project)
    db.flush()

  # Ensure project 2 exists for isolation testing
  project2 = db.query(Project).filter_by(name='Isolated Project').first()
  if not project2:
    project2 = Project(
        name='Isolated Project',
        product_code='ISO',
        description='Isolated test project for security testing',
        environment='test',
        is_active=True
    )
    db.add(project2)
    db.flush()

  # Ensure TestProjects exist for FK relationships
  from app.models.test_management import TestProject
  tp1 = db.query(TestProject).filter_by(id=1).first()
  if not tp1:
    tp1 = TestProject(id=1, access_project_id=project.id, name='Demo ERP', code='DEMO', created_by=admin.id)
    db.add(tp1)

  tp2 = db.query(TestProject).filter_by(id=2).first()
  if not tp2:
    tp2 = TestProject(id=2, access_project_id=project2.id, name='Isolated Project', code='ISO', created_by=p2_user.id)
    db.add(tp2)
  db.flush()

  # Grant memberships for Project 1
  role_map = {"admin": "ADMIN", "approver": "APPROVER", "viewer": "VIEWER", "dev1": "TESTER"}
  for op in [admin, approver, viewer, dev1]:
    if not db.query(ProjectMember).filter_by(project_id=project.id, operator_id=op.id).first():
        db.add(ProjectMember(
            project_id=project.id,
            operator_id=op.id,
            role=role_map.get(op.username, "VIEWER"),
            status="ACTIVE"
        ))

  # Grant membership for Project 2 ONLY to p2_user
  if not db.query(ProjectMember).filter_by(project_id=project2.id, operator_id=p2_user.id).first():
      db.add(ProjectMember(
          project_id=project2.id,
          operator_id=p2_user.id,
          role="ADMIN",
          status="ACTIVE"
      ))

  # Wipe execution runs and test plans in correct FK dependency order
  from app.models.automated_execution import AutomatedRun, AutomatedRunCase, AutomatedStepResult, ExecutionJob, ExecutionAttempt, ExecutionEvent, ExecutionArtifact, ExecutionWorker
  from app.models.test_plan import TestPlan, TestPlanVersion, TestScenario, TestStep
  from app.models.external_task_import import ExternalTaskImport
  from sqlalchemy import text

  # First NULL out FKs from external_task_imports → automated_runs (to allow run deletion)
  db.execute(text('UPDATE external_task_imports SET linked_run_id = NULL'))
  # NULL out ExecutionWorker's current_run_id FK
  db.execute(text('UPDATE execution_workers SET current_run_id = NULL'))

  # Temporarily drop delete triggers on append-only defect tables for test data reset
  db.execute(text("DROP TRIGGER IF EXISTS defect_comments_no_delete"))
  db.execute(text("DROP TRIGGER IF EXISTS defect_history_no_delete"))
  db.execute(text("DROP TRIGGER IF EXISTS defect_evidence_links_no_delete"))
  db.execute(text("DROP TRIGGER IF EXISTS defect_retests_no_delete"))
  db.flush()

  from app.models.advanced_validation import (
      AccessibilityValidationDefinition,
      AdvancedValidationProfile,
      AdvancedValidationResult,
      AdvancedValidationRun,
      ApiValidationDefinition,
      DatabaseValidationDefinition,
      LocalSchedule,
      PerformanceValidationDefinition,
  )
  db.query(AdvancedValidationResult).delete()
  db.query(AdvancedValidationRun).delete()
  db.query(LocalSchedule).delete()
  db.query(ApiValidationDefinition).delete()
  db.query(DatabaseValidationDefinition).delete()
  db.query(AccessibilityValidationDefinition).delete()
  db.query(PerformanceValidationDefinition).delete()
  db.query(AdvancedValidationProfile).delete()

  from app.models.defect import Defect, DefectComment, DefectEvidenceLink, DefectHistory, DefectRetest
  db.query(DefectComment).delete()
  db.query(DefectHistory).delete()
  db.query(DefectEvidenceLink).delete()
  db.query(DefectRetest).delete()
  db.query(Defect).delete()

  db.query(ExecutionArtifact).delete()
  db.query(AutomatedStepResult).delete()
  db.query(AutomatedRunCase).delete()
  db.query(ExecutionJob).delete()
  db.query(ExecutionAttempt).delete()
  db.query(ExecutionEvent).delete()
  db.query(AutomatedRun).delete()
  db.query(TestStep).delete()
  db.query(TestScenario).delete()
  db.query(TestPlanVersion).delete()
  db.query(TestPlan).delete()
  db.query(ExternalTaskImport).delete()

  # Re-create append-only defect triggers after test data deletion
  db.execute(text("CREATE TRIGGER IF NOT EXISTS defect_comments_no_delete BEFORE DELETE ON defect_comments BEGIN SELECT RAISE(ABORT, 'defect_comments are append-only'); END"))
  db.execute(text("CREATE TRIGGER IF NOT EXISTS defect_evidence_links_no_delete BEFORE DELETE ON defect_evidence_links BEGIN SELECT RAISE(ABORT, 'defect_evidence_links are append-only'); END"))
  db.execute(text("CREATE TRIGGER IF NOT EXISTS defect_history_no_delete BEFORE DELETE ON defect_history BEGIN SELECT RAISE(ABORT, 'defect_history is append-only'); END"))
  db.execute(text("CREATE TRIGGER IF NOT EXISTS defect_retests_no_delete BEFORE DELETE ON defect_retests BEGIN SELECT RAISE(ABORT, 'defect_retests are append-only'); END"))

  db.commit()
  return {"status": "ok"}
