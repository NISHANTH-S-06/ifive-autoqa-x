import csv
import hashlib
import json
from datetime import datetime, timedelta
from io import StringIO
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import and_, case, func, select
from sqlalchemy.orm import Session

from app.config import settings
from app.models.automated_execution import AutomatedRun, AutomatedRunCase, AutomatedStepResult, ExecutionWorker
from app.models.connection_target import ConnectionCheck, ConnectionTarget
from app.models.defect import Defect, DefectRetest
from app.models.operator import Operator
from app.models.reporting import ReportExport
from app.models.test_management import ManagedTestCase, ManagedTestSuite, ManualTestRun, ManualTestRunCase, TestModule, TestProject
from app.models.test_run import TestRun
from app.services.test_management import safe_csv

REPORT_EXPORT_ROOT = settings.export_root
MAX_EXPORT_ROWS = 500
VALID_REPORT_TYPES = {'dashboard', 'executions', 'defects', 'trends', 'quality', 'traceability', 'targets', 'workers'}
VALID_FORMATS = {'csv', 'json'}
VALID_DATE_RANGES = {'today', 'last_7_days', 'last_30_days', 'custom'}
VALID_RUN_TYPES = {'MANUAL', 'AUTOMATED', 'ALL'}
VALID_MANUAL_STATUSES = {'PLANNED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED'}
VALID_AUTOMATED_STATUSES = {'DRAFT', 'SUBMITTED', 'APPROVED', 'QUEUED', 'RUNNING', 'PASSED', 'FAILED', 'CANCELLED', 'TIMED_OUT', 'BLOCKED'}
VALID_RESULT_STATUSES = {'NOT_RUN', 'IN_PROGRESS', 'PASSED', 'FAILED', 'BLOCKED', 'SKIPPED'}
VALID_DEFECT_STATUSES = {'NEW', 'TRIAGED', 'ASSIGNED', 'IN_PROGRESS', 'FIXED', 'READY_FOR_RETEST', 'RETEST_PASSED', 'REOPENED', 'CLOSED', 'REJECTED', 'DUPLICATE'}
VALID_LEVELS = {'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'}
SENSITIVE_KEYS = {'password', 'token', 'cookie', 'csrf', 'hash', 'session', 'authorization', 'secret', 'absolute_path', 'relative_path'}


def calculate_pass_rate(total_tests: int, failed_tests: int) -> float:
  if total_tests <= 0:
    return 0.0
  return round(((total_tests - failed_tests) / total_tests) * 100, 2)


def percentage(part: int | float, total: int | float) -> float:
  if not total:
    return 0.0
  return round((float(part) / float(total)) * 100, 2)


def sanitize_row(row: dict) -> dict:
  safe = {}
  for key, value in row.items():
    lowered = key.lower()
    if any(term in lowered for term in SENSITIVE_KEYS):
      continue
    if isinstance(value, str) and (':\\' in value or value.startswith('/')):
      continue
    safe[key] = value
  return safe


def parse_filters(raw: dict | None) -> dict:
  raw = raw or {}
  filters: dict = {}
  for key in ['project_id', 'module_id', 'suite_id', 'test_case_id', 'assignee_id', 'target_id']:
    value = raw.get(key)
    if value in (None, ''):
      continue
    try:
      filters[key] = int(value)
    except (TypeError, ValueError):
      raise HTTPException(status_code=422, detail=f'Invalid {key}.') from None
  for key, allowed in [
    ('run_type', VALID_RUN_TYPES),
    ('run_status', VALID_MANUAL_STATUSES | VALID_AUTOMATED_STATUSES),
    ('defect_status', VALID_DEFECT_STATUSES),
    ('severity', VALID_LEVELS),
    ('priority', VALID_LEVELS),
  ]:
    value = raw.get(key)
    if value in (None, ''):
      continue
    value = str(value).upper()
    if value not in allowed:
      raise HTTPException(status_code=422, detail=f'Invalid {key}.')
    filters[key] = value
  if filters.get('run_type') is None:
    filters['run_type'] = 'ALL'
  environment = raw.get('environment')
  if environment not in (None, ''):
    value = str(environment).upper()
    if value not in {'LOCAL', 'DEVELOPMENT', 'QA', 'STAGING'}:
      raise HTTPException(status_code=422, detail='Invalid environment.')
    filters['environment'] = value
  date_range = raw.get('date_range') or 'last_30_days'
  if date_range not in VALID_DATE_RANGES:
    raise HTTPException(status_code=422, detail='Invalid date range.')
  end = datetime.utcnow()
  if date_range == 'today':
    start = end.replace(hour=0, minute=0, second=0, microsecond=0)
  elif date_range == 'last_7_days':
    start = end - timedelta(days=7)
  elif date_range == 'last_30_days':
    start = end - timedelta(days=30)
  else:
    try:
      start = datetime.fromisoformat(str(raw.get('start_date')))
      custom_end = datetime.fromisoformat(str(raw.get('end_date')))
    except (TypeError, ValueError):
      raise HTTPException(status_code=422, detail='Custom date range requires valid start_date and end_date.') from None
    if custom_end < start:
      raise HTTPException(status_code=422, detail='end_date must be after start_date.')
    if custom_end - start > timedelta(days=366):
      raise HTTPException(status_code=422, detail='Date range is too large.')
    end = custom_end
  filters['date_range'] = date_range
  filters['start_at'] = start
  filters['end_at'] = end
  return filters


def public_filters(filters: dict) -> dict:
  return {key: (value.isoformat() if isinstance(value, datetime) else value) for key, value in filters.items()}


def _between(column, filters):
  return column >= filters['start_at'], column <= filters['end_at']


def _manual_case_filters(filters):
  conditions = []
  if 'project_id' in filters:
    conditions.append(ManualTestRun.project_id == filters['project_id'])
  if 'suite_id' in filters:
    conditions.append(ManualTestRun.suite_id == filters['suite_id'])
  if 'test_case_id' in filters:
    conditions.append(ManualTestRunCase.test_case_id == filters['test_case_id'])
  if 'assignee_id' in filters:
    conditions.append(ManualTestRunCase.assigned_to == filters['assignee_id'])
  if filters.get('run_status') in VALID_MANUAL_STATUSES:
    conditions.append(ManualTestRun.status == filters['run_status'])
  return conditions


def _automated_case_filters(filters):
  conditions = []
  if 'test_case_id' in filters:
    conditions.append(AutomatedRunCase.test_case_id == filters['test_case_id'])
  if 'target_id' in filters:
    conditions.append(AutomatedRun.target_id == filters['target_id'])
  if filters.get('run_status') in VALID_AUTOMATED_STATUSES:
    conditions.append(AutomatedRun.status == filters['run_status'])
  return conditions


def _defect_filters(filters):
  conditions = []
  for key, column in [('project_id', Defect.project_id), ('module_id', Defect.module_id), ('suite_id', Defect.suite_id), ('test_case_id', Defect.test_case_id), ('assignee_id', Defect.assigned_to), ('target_id', Defect.target_id)]:
    if key in filters:
      conditions.append(column == filters[key])
  if 'defect_status' in filters:
    conditions.append(Defect.status == filters['defect_status'])
  if 'severity' in filters:
    conditions.append(Defect.severity == filters['severity'])
  if 'priority' in filters:
    conditions.append(Defect.priority == filters['priority'])
  return conditions


def count_statuses(db: Session, model, status_column, conditions=None) -> dict[str, int]:
  statement = select(status_column, func.count(model.id)).group_by(status_column)
  for condition in conditions or []:
    statement = statement.where(condition)
  return {status or 'UNKNOWN': count for status, count in db.execute(statement).all()}


def manual_case_statuses(db: Session, conditions=None) -> dict[str, int]:
  statement = select(ManualTestRunCase.status, func.count(ManualTestRunCase.id)).join(ManualTestRun).group_by(ManualTestRunCase.status)
  for condition in conditions or []:
    statement = statement.where(condition)
  return {status or 'UNKNOWN': count for status, count in db.execute(statement).all()}


def automated_case_statuses(db: Session, conditions=None) -> dict[str, int]:
  statement = select(AutomatedRunCase.status, func.count(AutomatedRunCase.id)).join(AutomatedRun).group_by(AutomatedRunCase.status)
  for condition in conditions or []:
    statement = statement.where(condition)
  return {status or 'UNKNOWN': count for status, count in db.execute(statement).all()}


def dashboard_report(db: Session, filters: dict) -> dict:
  manual_conditions = [*(_between(ManualTestRun.created_at, filters)), *_manual_case_filters(filters)]
  automated_conditions = [*(_between(AutomatedRun.created_at, filters)), *_automated_case_filters(filters)]
  defect_conditions = [*(_between(Defect.created_at, filters)), *_defect_filters(filters)]
  if filters.get('run_type') == 'MANUAL':
    automated_conditions.append(AutomatedRun.id == -1)
  if filters.get('run_type') == 'AUTOMATED':
    manual_conditions.append(ManualTestRun.id == -1)

  manual_runs = db.scalar(select(func.count(func.distinct(ManualTestRun.id))).join(ManualTestRunCase, isouter=True).where(*manual_conditions)) or 0
  automated_runs = db.scalar(select(func.count(func.distinct(AutomatedRun.id))).join(AutomatedRunCase, isouter=True).where(*automated_conditions)) or 0
  manual_case_counts = manual_case_statuses(db, manual_conditions)
  automated_case_counts = automated_case_statuses(db, automated_conditions)
  result_counts = {status: manual_case_counts.get(status, 0) + automated_case_counts.get(status, 0) for status in sorted(VALID_RESULT_STATUSES | {'PASSED', 'FAILED', 'BLOCKED', 'SKIPPED'})}
  defect_statuses = count_statuses(db, Defect, Defect.status, defect_conditions)
  target_statuses = count_statuses(db, ConnectionCheck, ConnectionCheck.status, list(_between(ConnectionCheck.created_at, filters)))
  worker_statuses = count_statuses(db, ExecutionWorker, ExecutionWorker.status, [])
  total_cases = db.scalar(select(func.count(ManagedTestCase.id)).where(ManagedTestCase.status == 'ACTIVE')) or 0
  approved_cases = db.scalar(select(func.count(ManagedTestCase.id)).where(ManagedTestCase.lifecycle_state == 'APPROVED', ManagedTestCase.status == 'ACTIVE')) or 0
  recent = recent_activity(db, filters)
  return {
    'filters': public_filters(filters),
    'summary': {
      'test_projects': db.scalar(select(func.count(TestProject.id)).where(TestProject.status == 'ACTIVE')) or 0,
      'test_cases': total_cases,
      'approved_test_cases': approved_cases,
      'manual_runs': manual_runs,
      'automated_runs': automated_runs,
      'result_counts': result_counts,
      'defects': sum(defect_statuses.values()),
      'open_defects': sum(count for status, count in defect_statuses.items() if status not in {'CLOSED', 'REJECTED', 'DUPLICATE'}),
      'closed_defects': defect_statuses.get('CLOSED', 0),
      'duplicate_defects': defect_statuses.get('DUPLICATE', 0),
      'retest_results': count_statuses(db, DefectRetest, DefectRetest.result_status, list(_between(DefectRetest.created_at, filters))),
      'target_health': target_statuses,
      'worker_status': worker_statuses,
    },
    'recent_activity': recent,
  }


def execution_report(db: Session, filters: dict) -> dict:
  manual_conditions = [*(_between(ManualTestRun.created_at, filters)), *_manual_case_filters(filters)]
  automated_conditions = [*(_between(AutomatedRun.created_at, filters)), *_automated_case_filters(filters)]
  if filters.get('run_type') == 'MANUAL':
    automated_conditions.append(AutomatedRun.id == -1)
  if filters.get('run_type') == 'AUTOMATED':
    manual_conditions.append(ManualTestRun.id == -1)
  manual_status = manual_case_statuses(db, manual_conditions)
  automated_status = automated_case_statuses(db, automated_conditions)
  failure_categories = dict(db.execute(select(AutomatedRun.failure_classification, func.count(AutomatedRun.id)).where(*automated_conditions).group_by(AutomatedRun.failure_classification)).all())
  project_rows = db.execute(select(TestProject.id, TestProject.code, func.count(func.distinct(ManualTestRun.id))).join(ManualTestRun, ManualTestRun.project_id == TestProject.id, isouter=True).group_by(TestProject.id, TestProject.code).limit(100)).all()
  operator_rows = db.execute(select(Operator.id, Operator.username, func.count(ManualTestRunCase.id)).join(ManualTestRunCase, ManualTestRunCase.executed_by == Operator.id, isouter=True).group_by(Operator.id, Operator.username).limit(100)).all()
  env_rows = db.execute(select(AutomatedRun.target_origin, func.count(AutomatedRun.id)).where(*automated_conditions).group_by(AutomatedRun.target_origin).limit(100)).all()
  return {
    'filters': public_filters(filters),
    'manual': {'run_count': db.scalar(select(func.count(func.distinct(ManualTestRun.id))).join(ManualTestRunCase, isouter=True).where(*manual_conditions)) or 0, 'case_statuses': manual_status},
    'automated': {'run_count': db.scalar(select(func.count(func.distinct(AutomatedRun.id))).join(AutomatedRunCase, isouter=True).where(*automated_conditions)) or 0, 'case_statuses': automated_status, 'failure_categories': {key or 'UNCLASSIFIED': value for key, value in failure_categories.items()}},
    'project_results': [{'project_id': item[0], 'project_code': item[1], 'manual_runs': item[2]} for item in project_rows],
    'operator_execution': [{'operator_id': item[0], 'username': item[1], 'manual_cases': item[2]} for item in operator_rows],
    'environment_results': [{'target_origin': 'sanitized-local-target' if item[0] else 'NONE', 'automated_runs': item[1]} for item in env_rows],
  }


def defect_report(db: Session, filters: dict) -> dict:
  conditions = [*(_between(Defect.created_at, filters)), *_defect_filters(filters)]
  rows_by_project = db.execute(select(Defect.project_id, func.count(Defect.id)).where(*conditions).group_by(Defect.project_id).limit(100)).all()
  now = datetime.utcnow()
  closed_rows = db.execute(select(Defect.created_at, Defect.closed_at).where(Defect.closed_at.is_not(None), *conditions)).all()
  close_hours = [(closed - created).total_seconds() / 3600 for created, closed in closed_rows if closed and created]
  return {
    'filters': public_filters(filters),
    'by_status': count_statuses(db, Defect, Defect.status, conditions),
    'by_severity': count_statuses(db, Defect, Defect.severity, conditions),
    'by_priority': count_statuses(db, Defect, Defect.priority, conditions),
    'by_project': [{'project_id': project_id, 'defects': count} for project_id, count in rows_by_project],
    'ageing': {'open_older_than_7_days': db.scalar(select(func.count(Defect.id)).where(Defect.status.not_in(['CLOSED', 'REJECTED', 'DUPLICATE']), Defect.created_at < now - timedelta(days=7), *conditions)) or 0},
    'reopened': db.scalar(select(func.count(Defect.id)).where(Defect.status == 'REOPENED', *conditions)) or 0,
    'duplicates': db.scalar(select(func.count(Defect.id)).where(Defect.status == 'DUPLICATE', *conditions)) or 0,
    'retest_results': count_statuses(db, DefectRetest, DefectRetest.result_status, list(_between(DefectRetest.created_at, filters))),
    'average_time_to_close_hours': round(sum(close_hours) / len(close_hours), 2) if close_hours else 0.0,
    'traceability': traceability_report(db, filters)['items'][:50],
  }


def trends_report(db: Session, filters: dict) -> dict:
  def bucket_rows(model, date_column, status_column=None, conditions=None):
    rows = db.execute(select(func.date(date_column), status_column if status_column is not None else func.count(model.id), func.count(model.id)).where(*(conditions or [])).group_by(func.date(date_column), status_column if status_column is not None else func.date(date_column)).order_by(func.date(date_column))).all()
    result = {}
    for row in rows:
      day = row[0]
      if status_column is None:
        result.setdefault(day, {'total': row[1]})
      else:
        result.setdefault(day, {})[row[1] or 'UNKNOWN'] = row[2]
    return result
  manual = bucket_rows(ManualTestRunCase, ManualTestRunCase.created_at, ManualTestRunCase.status, list(_between(ManualTestRunCase.created_at, filters)))
  automated = bucket_rows(AutomatedRun, AutomatedRun.created_at, AutomatedRun.status, list(_between(AutomatedRun.created_at, filters)))
  defects_created = bucket_rows(Defect, Defect.created_at, None, list(_between(Defect.created_at, filters)))
  defects_closed = bucket_rows(Defect, Defect.closed_at, None, [Defect.closed_at.is_not(None), *_between(Defect.closed_at, filters)])
  target_health = bucket_rows(ConnectionCheck, ConnectionCheck.created_at, ConnectionCheck.status, list(_between(ConnectionCheck.created_at, filters)))
  durations = db.execute(select(func.date(AutomatedRun.created_at), func.avg(func.coalesce(AutomatedRun.completed_steps, 0))).where(*_between(AutomatedRun.created_at, filters)).group_by(func.date(AutomatedRun.created_at))).all()
  return {'filters': public_filters(filters), 'manual_execution': manual, 'automated_execution': automated, 'defects_created': defects_created, 'defects_closed': defects_closed, 'target_health': target_health, 'execution_duration_proxy': {day: round(value or 0, 2) for day, value in durations}}


def quality_report(db: Session, filters: dict) -> dict:
  dashboard = dashboard_report(db, filters)['summary']
  results = dashboard['result_counts']
  total_results = sum(results.values())
  failures = results.get('FAILED', 0)
  blocked = results.get('BLOCKED', 0)
  passed = results.get('PASSED', 0)
  skipped = results.get('SKIPPED', 0)
  total_cases = dashboard['test_cases']
  automated_case_count = db.scalar(select(func.count(func.distinct(AutomatedRunCase.test_case_id)))) or 0
  retests = dashboard['retest_results']
  retest_total = sum(retests.values())
  duplicate_safe_defects = dashboard['defects'] - dashboard.get('duplicate_defects', 0)
  reopened_defects = defect_report(db, filters)['reopened']
  return {
    'filters': public_filters(filters),
    'pass_percentage': percentage(passed, total_results),
    'failure_percentage': percentage(failures, total_results),
    'blocked_percentage': percentage(blocked, total_results),
    'skipped_percentage': percentage(skipped, total_results),
    'test_coverage_count': total_cases,
    'approved_test_case_percentage': percentage(dashboard['approved_test_cases'], total_cases),
    'automation_coverage': percentage(automated_case_count, total_cases),
    'defect_density': round(duplicate_safe_defects / total_cases, 4) if total_cases else 0.0,
    'defect_reopen_rate': percentage(reopened_defects, duplicate_safe_defects),
    'retest_success_rate': percentage(retests.get('PASSED', 0), retest_total),
  }


def traceability_report(db: Session, filters: dict) -> dict:
  conditions = _defect_filters(filters)
  rows = list(db.scalars(select(Defect).where(*conditions).order_by(Defect.updated_at.desc()).limit(200)))
  items = []
  for item in rows:
    items.append({
      'defect_id': item.id,
      'defect_key': item.defect_key,
      'status': item.status,
      'project_id': item.project_id,
      'module_id': item.module_id,
      'suite_id': item.suite_id,
      'test_case_id': item.test_case_id,
      'test_case_version': item.test_case_version,
      'manual_run_id': item.manual_run_id,
      'automated_run_id': item.automated_run_id,
      'target_id': item.target_id,
      'target_version': item.target_version,
    })
  return {'filters': public_filters(filters), 'items': items}


def target_report(db: Session, filters: dict) -> dict:
  target_conditions = []
  if 'target_id' in filters:
    target_conditions.append(ConnectionTarget.id == filters['target_id'])
  if 'environment' in filters:
    target_conditions.append(ConnectionTarget.environment_type == filters['environment'])
  checks = count_statuses(db, ConnectionCheck, ConnectionCheck.status, list(_between(ConnectionCheck.created_at, filters)))
  targets = db.execute(select(ConnectionTarget.id, ConnectionTarget.target_key, ConnectionTarget.environment_type, ConnectionTarget.lifecycle_state, ConnectionTarget.enabled, ConnectionTarget.execution_enabled, ConnectionTarget.last_check_status).where(*target_conditions).limit(100)).all()
  return {'filters': public_filters(filters), 'target_health': checks, 'targets': [{'id': row[0], 'target_key': row[1], 'environment_type': row[2], 'lifecycle_state': row[3], 'enabled': row[4], 'execution_enabled': row[5], 'last_check_status': row[6]} for row in targets]}


def worker_report(db: Session) -> dict:
  workers = db.execute(select(ExecutionWorker.id, ExecutionWorker.worker_key, ExecutionWorker.status, ExecutionWorker.max_concurrency, ExecutionWorker.current_run_id, ExecutionWorker.heartbeat_at).order_by(ExecutionWorker.heartbeat_at.desc()).limit(100)).all()
  return {'workers': [{'id': row[0], 'worker_key': row[1], 'status': row[2], 'max_concurrency': row[3], 'current_run_id': row[4], 'heartbeat_at': row[5].isoformat() if row[5] else None} for row in workers], 'status_counts': count_statuses(db, ExecutionWorker, ExecutionWorker.status, [])}


def recent_activity(db: Session, filters: dict) -> list[dict]:
  manual = [{'type': 'manual_run', 'id': row.id, 'label': row.run_key, 'status': row.status, 'created_at': row.created_at.isoformat()} for row in db.scalars(select(ManualTestRun).where(*_between(ManualTestRun.created_at, filters)).order_by(ManualTestRun.created_at.desc()).limit(5))]
  automated = [{'type': 'automated_run', 'id': row.id, 'label': row.run_key, 'status': row.status, 'created_at': row.created_at.isoformat()} for row in db.scalars(select(AutomatedRun).where(*_between(AutomatedRun.created_at, filters)).order_by(AutomatedRun.created_at.desc()).limit(5))]
  defects = [{'type': 'defect', 'id': row.id, 'label': row.defect_key, 'status': row.status, 'created_at': row.created_at.isoformat()} for row in db.scalars(select(Defect).where(*_between(Defect.created_at, filters)).order_by(Defect.created_at.desc()).limit(5))]
  return sorted([*manual, *automated, *defects], key=lambda item: item['created_at'], reverse=True)[:10]


def report_payload(db: Session, report_type: str, filters: dict) -> dict:
  if report_type == 'dashboard':
    return dashboard_report(db, filters)
  if report_type == 'executions':
    return execution_report(db, filters)
  if report_type == 'defects':
    return defect_report(db, filters)
  if report_type == 'trends':
    return trends_report(db, filters)
  if report_type == 'quality':
    return quality_report(db, filters)
  if report_type == 'traceability':
    return traceability_report(db, filters)
  if report_type == 'targets':
    return target_report(db, filters)
  if report_type == 'workers':
    return worker_report(db)
  raise HTTPException(status_code=422, detail='Unsupported report type.')


def flatten_payload(value, prefix='') -> list[dict]:
  rows: list[dict] = []
  if isinstance(value, dict):
    scalar = {key: item for key, item in value.items() if not isinstance(item, (dict, list))}
    if scalar:
      rows.append(sanitize_row({'section': prefix or 'root', **scalar}))
    for key, item in value.items():
      if isinstance(item, (dict, list)):
        rows.extend(flatten_payload(item, f'{prefix}.{key}' if prefix else key))
  elif isinstance(value, list):
    for item in value:
      if isinstance(item, dict):
        rows.append(sanitize_row({'section': prefix, **item}))
      else:
        rows.append({'section': prefix, 'value': item})
  else:
    rows.append({'section': prefix or 'value', 'value': value})
  return rows[:MAX_EXPORT_ROWS]


def export_report(db: Session, report_type: str, export_format: str, filters: dict, operator_id: int) -> ReportExport:
  if report_type not in VALID_REPORT_TYPES:
    raise HTTPException(status_code=422, detail='Unsupported report type.')
  if export_format not in VALID_FORMATS:
    raise HTTPException(status_code=422, detail='Unsupported export format.')
  payload = report_payload(db, report_type, filters)
  rows = flatten_payload(payload)
  REPORT_EXPORT_ROOT.mkdir(parents=True, exist_ok=True)
  export_key = f'REXP-{uuid4().hex[:12].upper()}'
  stored_filename = f'{export_key}.{export_format}'
  path = REPORT_EXPORT_ROOT / stored_filename
  if export_format == 'json':
    content = json.dumps(rows, indent=2, sort_keys=True, default=str).encode('utf-8')
    mime_type = 'application/json'
  else:
    output = StringIO()
    fieldnames = sorted({key for row in rows for key in row.keys()}) or ['section']
    writer = csv.DictWriter(output, fieldnames=fieldnames, lineterminator='\n')
    writer.writeheader()
    for row in rows:
      writer.writerow({key: safe_csv(row.get(key, '')) for key in fieldnames})
    content = output.getvalue().encode('utf-8')
    mime_type = 'text/csv'
  path.write_bytes(content)
  digest = hashlib.sha256(content).hexdigest()
  item = ReportExport(
    export_key=export_key,
    report_type=report_type,
    export_format=export_format,
    filters_json=json.dumps(public_filters(filters), sort_keys=True, separators=(',', ':')),
    original_filename=f'{report_type}-{export_key}.{export_format}',
    stored_filename=stored_filename,
    relative_path=f'stage13_exports/{stored_filename}',
    mime_type=mime_type,
    size_bytes=len(content),
    sha256=digest,
    row_count=len(rows),
    created_by=operator_id,
    expires_at=datetime.utcnow() + timedelta(days=7),
  )
  db.add(item)
  db.flush()
  return item


def export_path(item: ReportExport) -> Path:
  root = REPORT_EXPORT_ROOT.resolve()
  path = (REPORT_EXPORT_ROOT / item.stored_filename).resolve()
  if root not in path.parents:
    raise HTTPException(status_code=404, detail='Report export is unavailable.')
  return path


def next_run_at(frequency: str, now: datetime | None = None) -> datetime:
  now = now or datetime.utcnow()
  if frequency == 'DAILY':
    return now + timedelta(days=1)
  if frequency == 'WEEKLY':
    return now + timedelta(days=7)
  if frequency == 'MONTHLY':
    return now + timedelta(days=30)
  raise HTTPException(status_code=422, detail='Unsupported frequency.')
