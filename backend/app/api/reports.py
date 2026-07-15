import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import AuthContext, get_auth_context, require_csrf
from app.database import get_db
from app.models.reporting import ReportDefinition, ReportExport
from app.schemas.test_management import Page
from app.services.audit_service import append_event
from app.services.report_service import (
  VALID_FORMATS,
  VALID_REPORT_TYPES,
  export_path,
  export_report,
  next_run_at,
  parse_filters,
  public_filters,
  report_payload,
)

router = APIRouter(tags=['reports'], dependencies=[Depends(get_auth_context)])


class ReportExportCreate(BaseModel):
  report_type: str = Field(max_length=40)
  export_format: str = Field(default='csv', max_length=10)
  filters: dict = Field(default_factory=dict)

  @field_validator('report_type')
  @classmethod
  def validate_report_type(cls, value: str) -> str:
    value = value.strip().lower()
    if value not in VALID_REPORT_TYPES:
      raise ValueError('unsupported report type')
    return value

  @field_validator('export_format')
  @classmethod
  def validate_export_format(cls, value: str) -> str:
    value = value.strip().lower()
    if value not in VALID_FORMATS:
      raise ValueError('unsupported export format')
    return value


class ReportDefinitionCreate(BaseModel):
  name: str = Field(min_length=1, max_length=160)
  report_type: str = Field(max_length=40)
  filters: dict = Field(default_factory=dict)
  frequency: str = Field(max_length=20)
  enabled: bool = True

  @field_validator('name')
  @classmethod
  def strip_name(cls, value: str) -> str:
    value = value.strip()
    if not value:
      raise ValueError('name is required')
    return value

  @field_validator('report_type')
  @classmethod
  def validate_type(cls, value: str) -> str:
    value = value.strip().lower()
    if value not in VALID_REPORT_TYPES:
      raise ValueError('unsupported report type')
    return value

  @field_validator('frequency')
  @classmethod
  def validate_frequency(cls, value: str) -> str:
    value = value.strip().upper()
    if value not in {'DAILY', 'WEEKLY', 'MONTHLY'}:
      raise ValueError('unsupported frequency')
    return value


class ReportDefinitionPatch(BaseModel):
  name: str | None = Field(default=None, min_length=1, max_length=160)
  filters: dict | None = None
  frequency: str | None = Field(default=None, max_length=20)
  enabled: bool | None = None

  @field_validator('frequency')
  @classmethod
  def validate_frequency(cls, value: str | None) -> str | None:
    if value is None:
      return None
    value = value.strip().upper()
    if value not in {'DAILY', 'WEEKLY', 'MONTHLY'}:
      raise ValueError('unsupported frequency')
    return value


def _filters(
  project_id: int | None = None,
  module_id: int | None = None,
  suite_id: int | None = None,
  test_case_id: int | None = None,
  run_type: str | None = None,
  run_status: str | None = None,
  defect_status: str | None = None,
  severity: str | None = None,
  priority: str | None = None,
  assignee_id: int | None = None,
  target_id: int | None = None,
  environment: str | None = None,
  date_range: str = 'last_30_days',
  start_date: str | None = None,
  end_date: str | None = None,
) -> dict:
  return parse_filters({
    'project_id': project_id,
    'module_id': module_id,
    'suite_id': suite_id,
    'test_case_id': test_case_id,
    'run_type': run_type,
    'run_status': run_status,
    'defect_status': defect_status,
    'severity': severity,
    'priority': priority,
    'assignee_id': assignee_id,
    'target_id': target_id,
    'environment': environment,
    'date_range': date_range,
    'start_date': start_date,
    'end_date': end_date,
  })


def _export_read(item: ReportExport) -> dict:
  return {
    'id': item.id,
    'export_key': item.export_key,
    'report_type': item.report_type,
    'export_format': item.export_format,
    'original_filename': item.original_filename,
    'mime_type': item.mime_type,
    'size_bytes': item.size_bytes,
    'sha256': item.sha256,
    'row_count': item.row_count,
    'created_by': item.created_by,
    'created_at': item.created_at,
    'expires_at': item.expires_at,
  }


def _definition_read(item: ReportDefinition) -> dict:
  return {
    'id': item.id,
    'name': item.name,
    'report_type': item.report_type,
    'filters': json.loads(item.filters_json or '{}'),
    'frequency': item.frequency,
    'enabled': item.enabled,
    'owner_operator_id': item.owner_operator_id,
    'last_run_at': item.last_run_at,
    'next_run_at': item.next_run_at,
    'last_error': item.last_error,
    'created_at': item.created_at,
    'updated_at': item.updated_at,
  }


def _require_admin(context: AuthContext) -> None:
  if context.operator.role != 'ADMIN':
    raise HTTPException(status_code=403, detail='You do not have permission to perform this action.')


@router.get('/reports/summary')
def report_metrics(db: Session = Depends(get_db)):
  payload = report_payload(db, 'dashboard', parse_filters({'date_range': 'last_30_days'}))
  summary = payload['summary']
  return [
    {'label': 'Total Tests', 'value': str(summary['result_counts'].get('PASSED', 0) + summary['result_counts'].get('FAILED', 0) + summary['result_counts'].get('BLOCKED', 0) + summary['result_counts'].get('SKIPPED', 0))},
    {'label': 'Pass Rate', 'value': f"{report_payload(db, 'quality', parse_filters({'date_range': 'last_30_days'}))['pass_percentage']}%"},
    {'label': 'Open Defects', 'value': str(summary['open_defects'])},
  ]


@router.get('/reports/dashboard')
def get_dashboard_report(filters: dict = Depends(_filters), db: Session = Depends(get_db)):
  return report_payload(db, 'dashboard', filters)


@router.get('/reports/executions')
def get_execution_report(filters: dict = Depends(_filters), db: Session = Depends(get_db)):
  return report_payload(db, 'executions', filters)


@router.get('/reports/defects')
def get_defect_report(filters: dict = Depends(_filters), db: Session = Depends(get_db)):
  return report_payload(db, 'defects', filters)


@router.get('/reports/trends')
def get_trends_report(filters: dict = Depends(_filters), db: Session = Depends(get_db)):
  return report_payload(db, 'trends', filters)


@router.get('/reports/quality')
def get_quality_report(filters: dict = Depends(_filters), db: Session = Depends(get_db)):
  return report_payload(db, 'quality', filters)


@router.get('/reports/traceability')
def get_traceability_report(filters: dict = Depends(_filters), db: Session = Depends(get_db)):
  return report_payload(db, 'traceability', filters)


@router.get('/reports/targets')
def get_targets_report(filters: dict = Depends(_filters), db: Session = Depends(get_db)):
  return report_payload(db, 'targets', filters)


@router.get('/reports/workers')
def get_workers_report(db: Session = Depends(get_db)):
  return report_payload(db, 'workers', parse_filters({'date_range': 'last_30_days'}))


@router.post('/reports/export', status_code=201)
def create_report_export(payload: ReportExportCreate, context: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)):
  _require_admin(context)
  filters = parse_filters(payload.filters)
  item = export_report(db, payload.report_type, payload.export_format, filters, context.operator.id)
  append_event(db, 'report_export_created', operator_id=context.operator.id, resource_type='REPORT_EXPORT', resource_id=str(item.id), metadata={'report_type': item.report_type, 'format': item.export_format, 'rows': item.row_count})
  db.commit(); db.refresh(item); return _export_read(item)


@router.get('/reports/exports')
def list_report_exports(context: AuthContext = Depends(get_auth_context), limit: int = Query(50, ge=1, le=100), offset: int = Query(0, ge=0), db: Session = Depends(get_db)):
  statement = select(ReportExport).where(ReportExport.deleted_at.is_(None))
  count_statement = select(ReportExport.id).where(ReportExport.deleted_at.is_(None))
  if context.operator.role != 'ADMIN':
    statement = statement.where(ReportExport.created_by == context.operator.id)
    count_statement = count_statement.where(ReportExport.created_by == context.operator.id)
  items = list(db.scalars(statement.order_by(ReportExport.created_at.desc()).offset(offset).limit(limit)))
  total = len(list(db.scalars(count_statement)))
  return {'items': [_export_read(item) for item in items], 'page': Page(limit=limit, offset=offset, total=total)}


@router.get('/reports/exports/{export_id}/download')
def download_report_export(export_id: int, context: AuthContext = Depends(get_auth_context), db: Session = Depends(get_db)):
  item = db.get(ReportExport, export_id)
  if item is None or item.deleted_at is not None:
    raise HTTPException(status_code=404, detail='Report export not found.')
  if context.operator.role != 'ADMIN' and item.created_by != context.operator.id:
    raise HTTPException(status_code=403, detail='You do not have permission to perform this action.')
  path = export_path(item)
  if not path.is_file():
    raise HTTPException(status_code=404, detail='Report export file is unavailable.')
  append_event(db, 'report_export_downloaded', operator_id=context.operator.id, resource_type='REPORT_EXPORT', resource_id=str(item.id))
  db.commit()
  return FileResponse(path, media_type=item.mime_type, filename=item.original_filename)


@router.get('/report-definitions')
def list_report_definitions(context: AuthContext = Depends(get_auth_context), db: Session = Depends(get_db)):
  _require_admin(context)
  return [_definition_read(item) for item in db.scalars(select(ReportDefinition).order_by(ReportDefinition.created_at.desc()))]


@router.post('/report-definitions', status_code=201)
def create_report_definition(payload: ReportDefinitionCreate, context: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)):
  _require_admin(context)
  filters = parse_filters(payload.filters)
  item = ReportDefinition(name=payload.name, report_type=payload.report_type, filters_json=json.dumps(public_filters(filters), sort_keys=True, separators=(',', ':')), frequency=payload.frequency, enabled=payload.enabled, owner_operator_id=context.operator.id, next_run_at=next_run_at(payload.frequency))
  db.add(item)
  append_event(db, 'report_definition_created', operator_id=context.operator.id, resource_type='REPORT_DEFINITION', metadata={'report_type': item.report_type, 'frequency': item.frequency})
  db.commit(); db.refresh(item); return _definition_read(item)


@router.patch('/report-definitions/{definition_id}')
def patch_report_definition(definition_id: int, payload: ReportDefinitionPatch, context: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)):
  _require_admin(context)
  item = db.get(ReportDefinition, definition_id)
  if item is None:
    raise HTTPException(status_code=404, detail='Report definition not found.')
  if payload.name is not None:
    item.name = payload.name.strip()
  if payload.filters is not None:
    item.filters_json = json.dumps(public_filters(parse_filters(payload.filters)), sort_keys=True, separators=(',', ':'))
  if payload.frequency is not None:
    item.frequency = payload.frequency
    item.next_run_at = next_run_at(payload.frequency)
  if payload.enabled is not None:
    item.enabled = payload.enabled
  item.updated_at = datetime.utcnow()
  append_event(db, 'report_definition_updated', operator_id=context.operator.id, resource_type='REPORT_DEFINITION', resource_id=str(item.id))
  db.commit(); db.refresh(item); return _definition_read(item)


@router.post('/report-definitions/{definition_id}/run')
def run_report_definition(definition_id: int, context: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)):
  _require_admin(context)
  item = db.get(ReportDefinition, definition_id)
  if item is None:
    raise HTTPException(status_code=404, detail='Report definition not found.')
  if not item.enabled:
    raise HTTPException(status_code=409, detail='Report definition is disabled.')
  try:
    filters = parse_filters(json.loads(item.filters_json or '{}'))
    export = export_report(db, item.report_type, 'csv', filters, context.operator.id)
    item.last_run_at = datetime.utcnow()
    item.next_run_at = next_run_at(item.frequency, item.last_run_at)
    item.last_error = None
    append_event(db, 'report_definition_run', operator_id=context.operator.id, resource_type='REPORT_DEFINITION', resource_id=str(item.id), metadata={'export_key': export.export_key})
    db.commit(); db.refresh(export); return _export_read(export)
  except HTTPException as exc:
    item.last_error = str(exc.detail)[:500]
    db.commit()
    raise


@router.post('/report-definitions/{definition_id}/disable')
def disable_report_definition(definition_id: int, context: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)):
  _require_admin(context)
  item = db.get(ReportDefinition, definition_id)
  if item is None:
    raise HTTPException(status_code=404, detail='Report definition not found.')
  item.enabled = False
  item.updated_at = datetime.utcnow()
  append_event(db, 'report_definition_disabled', operator_id=context.operator.id, resource_type='REPORT_DEFINITION', resource_id=str(item.id))
  db.commit(); db.refresh(item); return _definition_read(item)
