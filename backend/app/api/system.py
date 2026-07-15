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
