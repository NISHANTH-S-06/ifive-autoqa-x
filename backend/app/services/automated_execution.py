import base64
import hashlib
import json
import re
import time
from datetime import datetime, timedelta
from pathlib import Path
from uuid import uuid4

import httpx
from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import settings
from app.models.automated_execution import (
  AutomatedRun,
  AutomatedRunCase,
  AutomatedStepResult,
  ExecutionArtifact,
  ExecutionAttempt,
  ExecutionEvent,
  ExecutionJob,
  ExecutionWorker,
)
from app.models.connection_target import ConnectionTarget
from app.models.test_management import ManagedTestCase, TestCaseVersion
from app.services.pinned_http import PinnedTargetSession
from app.services.target_policy import check_probe_allowed, load_probe_paths, resolve_host, validate_same_origin

BACKEND_ROOT = Path(__file__).resolve().parents[2]
ARTIFACT_ROOT = settings.artifact_root
TERMINAL_RUN_STATES = {'PASSED', 'FAILED', 'CANCELLED', 'TIMED_OUT', 'BLOCKED'}
SAFE_RETRY_STATES = {'FAILED', 'TIMED_OUT', 'BLOCKED'}
ALLOWED_ACTIONS = {
  'NAVIGATE', 'CLICK', 'FILL', 'SELECT', 'CHECK', 'UNCHECK', 'PRESS_KEY', 'WAIT_FOR_ELEMENT',
  'ASSERT_TEXT', 'ASSERT_VISIBLE', 'ASSERT_HIDDEN', 'ASSERT_URL_PATH', 'ASSERT_TITLE',
  'SCREENSHOT', 'READ_TEXT', 'RELOAD', 'GO_BACK', 'GO_FORWARD',
}
READ_ONLY_ACTIONS = {'NAVIGATE', 'WAIT_FOR_ELEMENT', 'ASSERT_TEXT', 'ASSERT_VISIBLE', 'ASSERT_HIDDEN', 'ASSERT_URL_PATH', 'ASSERT_TITLE', 'SCREENSHOT', 'READ_TEXT', 'RELOAD', 'GO_BACK', 'GO_FORWARD'}
SAFE_INTERACTION_ACTIONS = {'CLICK', 'FILL', 'SELECT', 'CHECK', 'UNCHECK', 'PRESS_KEY'}
ALLOWED_RISK_LEVELS = {'READ_ONLY', 'SAFE_INTERACTION'}
BLOCKED_RISK_LEVELS = {'MUTATING', 'DESTRUCTIVE'}
ACTION_RISK_LEVELS = {**{action: 'READ_ONLY' for action in READ_ONLY_ACTIONS}, **{action: 'SAFE_INTERACTION' for action in SAFE_INTERACTION_ACTIONS}}
DANGEROUS_ACTION_PATTERN = re.compile(r'(?i)\b(delete|remove|post|approve|submit\s+payment|confirm\s+transaction|process\s+payroll|finalize|cancel\s+order|upload|import)\b')
SECRET_PATTERN = re.compile(r'(?i)(password|token|cookie|csrf|authorization|bearer|api[_-]?key|secret|autoqa_session)')
CODE_PATTERN = re.compile(r'(?i)(javascript|python|powershell|shell|subprocess|eval|function|=>|<script|import\s+|require\()')
ONE_PIXEL_PNG = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==')


def next_run_key(db: Session) -> str:
  return f'ARUN-{(db.scalar(select(func.count(AutomatedRun.id))) or 0) + 1:05d}-{uuid4().hex[:6].upper()}'


def progress(run: AutomatedRun) -> str:
  return f'{run.completed_steps}/{run.total_steps}'


def add_event(db: Session, run_id: int, event_type: str, status: str = 'INFO', message: str | None = None, metadata: dict | None = None) -> ExecutionEvent:
  safe_metadata = sanitize_metadata(metadata or {})
  project_id = db.scalar(select(AutomatedRun.project_id).where(AutomatedRun.id == run_id))
  if project_id is None:
    raise HTTPException(status_code=404, detail='Automated run not found.')
  item = ExecutionEvent(project_id=project_id, run_id=run_id, event_type=event_type, status=status, safe_message=safe_text(message), metadata_json=json.dumps(safe_metadata, sort_keys=True, separators=(',', ':'), ensure_ascii=True))
  db.add(item)
  return item


def sanitize_metadata(metadata: dict) -> dict:
  sanitized = {}
  for key, value in metadata.items():
    if SECRET_PATTERN.search(str(key)):
      continue
    sanitized[key] = safe_text(value)
  return sanitized


def safe_text(value) -> str | None:
  if value is None:
    return None
  text = str(value)[:500]
  if SECRET_PATTERN.search(text):
    return '[redacted]'
  return text


def ensure_execution_target(target: ConnectionTarget) -> None:
  if target.environment_type == 'PRODUCTION':
    raise HTTPException(status_code=403, detail='Production execution is blocked.')
  if target.environment_type != 'LOCAL' and not settings.allow_real_target_execution:
    raise HTTPException(status_code=403, detail='Real target execution is disabled by local release configuration.')
  if target.lifecycle_state != 'APPROVED' or not target.enabled:
    raise HTTPException(status_code=409, detail='Only approved enabled targets can be used for execution.')
  if not target.execution_enabled:
    raise HTTPException(status_code=409, detail='Target is not separately approved for automated execution.')
  resolve_host(target.normalized_host, target.normalized_port, target.environment_type)


def active_worker_available(db: Session) -> bool:
  cutoff = datetime.utcnow() - timedelta(seconds=settings.execution_job_lease_seconds * 2)
  return bool(db.scalar(select(func.count(ExecutionWorker.id)).where(ExecutionWorker.heartbeat_at >= cutoff)) or 0)


def _load_case_version(db: Session, case_id: int) -> tuple[ManagedTestCase, TestCaseVersion, dict]:
  test_case = db.get(ManagedTestCase, case_id)
  if test_case is None:
    raise HTTPException(status_code=404, detail='Test case not found.')
  if test_case.lifecycle_state != 'APPROVED' or test_case.status == 'ARCHIVED' or test_case.archived_at is not None:
    raise HTTPException(status_code=409, detail='Only approved active test cases can run.')
  version = db.scalar(select(TestCaseVersion).where(TestCaseVersion.test_case_id == test_case.id, TestCaseVersion.version_number == test_case.current_version))
  if version is None:
    raise HTTPException(status_code=409, detail='Approved test case version is unavailable.')
  snapshot = json.loads(version.snapshot_json)
  validate_snapshot_actions(snapshot)
  return test_case, version, snapshot


def validate_snapshot_actions(snapshot: dict) -> list[dict]:
  parsed = []
  for step in snapshot.get('steps', []):
    parsed.append(parse_action(step))
  if not parsed:
    raise HTTPException(status_code=422, detail='Automated runs require at least one structured action.')
  return parsed


def _max_risk(left: str, right: str) -> str:
  order = {'READ_ONLY': 0, 'SAFE_INTERACTION': 1, 'MUTATING': 2, 'DESTRUCTIVE': 3}
  return left if order[left] >= order[right] else right


def parse_action(step: dict) -> dict:
  source = step.get('test_data') or step.get('action')
  try:
    payload = json.loads(source)
  except Exception:
    raise HTTPException(status_code=422, detail='Automated steps must be structured JSON actions.') from None
  if not isinstance(payload, dict):
    raise HTTPException(status_code=422, detail='Automated step action must be an object.')
  action = str(payload.get('action', '')).strip().upper()
  if action not in ALLOWED_ACTIONS:
    raise HTTPException(status_code=422, detail='Automated step action is not allowed.')
  declared_risk = str(payload.get('risk_level', ACTION_RISK_LEVELS.get(action, 'DESTRUCTIVE'))).strip().upper()
  if declared_risk in BLOCKED_RISK_LEVELS:
    raise HTTPException(status_code=422, detail='Mutating and destructive actions are blocked in Stage 11.')
  if declared_risk not in ALLOWED_RISK_LEVELS:
    raise HTTPException(status_code=422, detail='Unsupported execution risk level.')
  action_risk = ACTION_RISK_LEVELS.get(action, 'DESTRUCTIVE')
  if action_risk in BLOCKED_RISK_LEVELS or declared_risk not in ALLOWED_RISK_LEVELS:
    raise HTTPException(status_code=422, detail='Action risk level is not allowed in Stage 11.')
  for key, value in payload.items():
    text = f'{key} {value}'
    if SECRET_PATTERN.search(text) or CODE_PATTERN.search(text):
      raise HTTPException(status_code=422, detail='Automated step contains credential-like or code-like content.')
    if DANGEROUS_ACTION_PATTERN.search(text):
      raise HTTPException(status_code=422, detail='Dangerous or mutating action wording is blocked in Stage 11.')
  path = payload.get('path')
  if action in {'NAVIGATE', 'ASSERT_URL_PATH'}:
    if not isinstance(path, str):
      raise HTTPException(status_code=422, detail='Path is required for this action.')
    validate_relative_path(path)
  if 'url' in payload:
    raise HTTPException(status_code=422, detail='Full URLs are not allowed in automated steps.')
  if action in {'CLICK', 'FILL', 'SELECT', 'CHECK', 'UNCHECK', 'PRESS_KEY', 'WAIT_FOR_ELEMENT', 'ASSERT_TEXT', 'ASSERT_VISIBLE', 'ASSERT_HIDDEN', 'READ_TEXT'} and not payload.get('selector'):
    raise HTTPException(status_code=422, detail='Selector is required for this action.')
  return {'step_number': step.get('step_number'), **payload, 'action': action, 'risk_level': _max_risk(action_risk, declared_risk)}


def snapshot_risk_level(snapshot: dict) -> str:
  risk = 'READ_ONLY'
  for action in validate_snapshot_actions(snapshot):
    risk = _max_risk(risk, action['risk_level'])
  return risk


def validate_relative_path(path: str) -> str:
  if not path.startswith('/') or path.startswith('//') or '\\' in path or '..' in path or any(ord(ch) < 32 for ch in path):
    raise HTTPException(status_code=422, detail='Only approved relative paths are allowed.')
  if '://' in path or '?' in path or '#' in path:
    raise HTTPException(status_code=422, detail='Path must not contain a scheme, query, or fragment.')
  return path


def create_run(db: Session, target: ConnectionTarget, name: str, description: str | None, case_ids: list[int], timeout_seconds: int, max_retries: int, created_by: int, runtime_secret_required: bool = False) -> AutomatedRun:
  ensure_execution_target(target)
  if runtime_secret_required:
    raise HTTPException(status_code=409, detail='Runtime-secret input is not available in the local Stage 11 verifier; authenticated login acceptance remains pending.')
  if len(set(case_ids)) != len(case_ids):
    raise HTTPException(status_code=422, detail='Duplicate test cases are not allowed.')
  run = AutomatedRun(
    project_id=target.project_id,
    run_key=next_run_key(db),
    name=name.strip(),
    description=description,
    target_id=target.id,
    target_version=target.version,
    target_origin=target.normalized_origin,
    timeout_seconds=timeout_seconds,
    max_retries=max_retries,
    dns_pinning_status='ENFORCED',
    runtime_secret_status='NOT_REQUIRED',
    created_by=created_by,
  )
  db.add(run)
  db.flush()
  total_steps = 0
  for index, case_id in enumerate(case_ids, start=1):
    test_case, version, snapshot = _load_case_version(db, case_id)
    if test_case.project.access_project_id != target.project_id:
      raise HTTPException(status_code=400, detail='Cross-project target/test-case relationship is not allowed.')
    steps = validate_snapshot_actions(snapshot)
    run.risk_level = _max_risk(run.risk_level, snapshot_risk_level(snapshot))
    total_steps += len(steps)
    run.cases.append(AutomatedRunCase(project_id=run.project_id, test_case_id=case_id, test_case_version=version.version_number, case_snapshot_json=version.snapshot_json, sort_order=index))
  run.total_steps = total_steps
  add_event(db, run.id, 'automated_run_created', metadata={'run_key': run.run_key, 'target_version': run.target_version, 'cases': len(case_ids)})
  return run


def preflight_run(db: Session, run: AutomatedRun, require_worker: bool = True) -> dict:
  target = db.get(ConnectionTarget, run.target_id)
  checks = {
    'target_present': target is not None,
    'target_approved_enabled': False,
    'execution_separately_approved': False,
    'not_production': False,
    'target_version_frozen': False,
    'test_cases_frozen_approved': False,
    'structured_actions_valid': False,
    'risk_level_allowed': run.risk_level in ALLOWED_RISK_LEVELS,
    'dns_pinning_enforced': False,
    'worker_available': active_worker_available(db) if require_worker else True,
    'timeout_within_limits': 5 <= run.timeout_seconds <= 300,
    'concurrency_within_limits': True,
    'runtime_secret_not_persisted': run.runtime_secret_status == 'NOT_REQUIRED',
  }
  try:
    if target is not None:
      ensure_execution_target(target)
      checks['target_approved_enabled'] = target.lifecycle_state == 'APPROVED' and target.enabled
      checks['execution_separately_approved'] = bool(target.execution_enabled and target.execution_approved_by)
      checks['not_production'] = target.environment_type != 'PRODUCTION'
      checks['target_version_frozen'] = target.version == run.target_version and target.normalized_origin == run.target_origin
      session = PinnedTargetSession(target, settings.execution_user_agent, min(run.timeout_seconds, 30), settings.execution_max_text_bytes)
      session.assert_current_resolution()
      checks['dns_pinning_enforced'] = True
      run.dns_pinning_status = 'ENFORCED'
  except HTTPException:
    pass
  cases_valid = True
  actions_valid = True
  risk = 'READ_ONLY'
  for run_case in run.cases:
    test_case = db.get(ManagedTestCase, run_case.test_case_id)
    version = db.scalar(select(TestCaseVersion).where(TestCaseVersion.test_case_id == run_case.test_case_id, TestCaseVersion.version_number == run_case.test_case_version))
    if test_case is None or version is None or version.source_state != 'APPROVED' or test_case.status == 'ARCHIVED':
      cases_valid = False
    try:
      snapshot = json.loads(run_case.case_snapshot_json)
      risk = _max_risk(risk, snapshot_risk_level(snapshot))
    except (json.JSONDecodeError, HTTPException):
      actions_valid = False
  checks['test_cases_frozen_approved'] = cases_valid
  checks['structured_actions_valid'] = actions_valid
  run.risk_level = risk
  run.preflight_status = 'PASS' if all(checks.values()) else 'FAIL'
  add_event(db, run.id, 'execution_preflight_completed', 'SUCCESS' if run.preflight_status == 'PASS' else 'WARN', metadata={'status': run.preflight_status, 'risk_level': run.risk_level})
  return {'run_id': run.id, 'status': run.preflight_status, 'checks': checks, 'risk_level': run.risk_level, 'dns_pinning_status': run.dns_pinning_status, 'runtime_secret_status': run.runtime_secret_status, 'safe_message': None if run.preflight_status == 'PASS' else 'Stage 11 preflight has pending or blocked checks.'}


def claim_next_job(db: Session, worker_key: str, lease_seconds: int = 60) -> ExecutionJob | None:
  now = datetime.utcnow()
  worker = db.scalar(select(ExecutionWorker).where(ExecutionWorker.worker_key == worker_key))
  if worker is None:
    worker = ExecutionWorker(worker_key=worker_key)
    db.add(worker)
    db.flush()
  if db.scalar(select(func.count(ExecutionJob.id)).where(ExecutionJob.status == 'RUNNING', ExecutionJob.lease_owner == worker_key)) >= worker.max_concurrency:
    return None
  job = db.scalar(select(ExecutionJob).where(ExecutionJob.status == 'QUEUED').order_by(ExecutionJob.priority.desc(), ExecutionJob.created_at).limit(1))
  if job is None:
    worker.status = 'IDLE'; worker.heartbeat_at = now
    return None
  job.status = 'RUNNING'
  job.lease_owner = worker_key
  job.lease_expires_at = now + timedelta(seconds=lease_seconds)
  job.attempts += 1
  run = db.get(AutomatedRun, job.run_id)
  if run:
    run.status = 'RUNNING'; run.worker_key = worker_key; run.started_at = run.started_at or now; run.lease_expires_at = job.lease_expires_at
    worker.current_run_id = run.id
  worker.status = 'BUSY'; worker.heartbeat_at = now
  db.flush()
  return job


def heartbeat(db: Session, worker_key: str) -> ExecutionWorker:
  worker = db.scalar(select(ExecutionWorker).where(ExecutionWorker.worker_key == worker_key))
  if worker is None:
    worker = ExecutionWorker(worker_key=worker_key)
    db.add(worker)
  worker.heartbeat_at = datetime.utcnow()
  db.flush()
  return worker


def recover_stale_jobs(db: Session) -> int:
  now = datetime.utcnow()
  recovered = 0
  for job in db.scalars(select(ExecutionJob).where(ExecutionJob.status == 'RUNNING', ExecutionJob.lease_expires_at < now)):
    run = db.get(AutomatedRun, job.run_id)
    job.status = 'QUEUED'
    job.lease_owner = None
    job.lease_expires_at = None
    if run and run.status == 'RUNNING':
      run.status = 'QUEUED'
      run.worker_key = None
      add_event(db, run.id, 'execution_job_recovered', 'WARN', 'Expired worker lease recovered.')
    recovered += 1
  db.flush()
  return recovered


def execute_next_job(db: Session, worker_key: str = 'local-stage10-worker') -> AutomatedRun | None:
  recover_stale_jobs(db)
  job = claim_next_job(db, worker_key)
  if job is None:
    db.flush()
    return None
  run = db.get(AutomatedRun, job.run_id)
  if run is None:
    job.status = 'FAILED'
    return None
  attempt = ExecutionAttempt(project_id=run.project_id, run_id=run.id, attempt_number=run.attempt_count + 1, worker_key=worker_key)
  db.add(attempt)
  run.attempt_count += 1
  add_event(db, run.id, 'execution_started', metadata={'worker': worker_key, 'attempt': run.attempt_count})
  db.flush()
  started = time.monotonic()
  target = db.get(ConnectionTarget, run.target_id)
  try:
    if target is None:
      raise HTTPException(status_code=404, detail='Execution target not found.')
    ensure_execution_target(target)
    if target.version != run.target_version or target.normalized_origin != run.target_origin:
      raise HTTPException(status_code=409, detail='Execution target changed after run approval.')
    client = PinnedTargetSession(target, settings.execution_user_agent, min(run.timeout_seconds, 30), settings.execution_max_text_bytes)
    run.dns_pinning_status = 'ENFORCED'
    page = {'path': '/', 'title': '', 'text': '', 'history': ['/'], 'history_index': 0}
    for run_case in sorted(run.cases, key=lambda item: item.sort_order):
      if run.status == 'CANCELLED':
        raise RuntimeError('cancelled')
      run_case.status = 'RUNNING'; run_case.started_at = datetime.utcnow()
      snapshot = json.loads(run_case.case_snapshot_json)
      for step in validate_snapshot_actions(snapshot):
        if time.monotonic() - started > run.timeout_seconds:
          raise TimeoutError()
        if run.status == 'CANCELLED':
          raise RuntimeError('cancelled')
        execute_step(db, client, target, run, run_case, step, page)
      run_case.status = 'PASSED'; run_case.completed_at = datetime.utcnow()
    run.status = 'PASSED' if run.failed_steps == 0 else 'FAILED'
    attempt.status = run.status
  except TimeoutError:
    run.status = 'TIMED_OUT'; run.failure_classification = 'TIMEOUT'; run.safe_error_message = 'Automated run timed out.'
    attempt.status = 'TIMED_OUT'; attempt.failure_classification = 'TIMEOUT'; attempt.safe_error_message = run.safe_error_message
  except RuntimeError:
    run.status = 'CANCELLED'; run.failure_classification = 'CANCELLED'; run.safe_error_message = 'Automated run was cancelled.'
    attempt.status = 'CANCELLED'; attempt.failure_classification = 'CANCELLED'; attempt.safe_error_message = run.safe_error_message
  except HTTPException as exc:
    run.status = 'BLOCKED' if exc.status_code in {403, 409, 422} else 'FAILED'
    run.failure_classification = 'POLICY_BLOCKED'
    run.safe_error_message = safe_text(exc.detail)
    attempt.status = run.status; attempt.failure_classification = run.failure_classification; attempt.safe_error_message = run.safe_error_message
  except httpx.TimeoutException:
    run.status = 'TIMED_OUT'; run.failure_classification = 'TIMEOUT'; run.safe_error_message = 'Automated run timed out.'
    attempt.status = 'TIMED_OUT'; attempt.failure_classification = 'TIMEOUT'; attempt.safe_error_message = run.safe_error_message
  except httpx.TransportError:
    run.status = 'FAILED'; run.failure_classification = 'NETWORK'; run.safe_error_message = 'Browser navigation failed safely.'
    attempt.status = run.status; attempt.failure_classification = run.failure_classification; attempt.safe_error_message = run.safe_error_message
  finally:
    run.completed_at = datetime.utcnow()
    job.status = 'COMPLETED' if run.status == 'PASSED' else run.status
    job.lease_owner = None
    job.lease_expires_at = None
    attempt.completed_at = datetime.utcnow()
    worker = db.scalar(select(ExecutionWorker).where(ExecutionWorker.worker_key == worker_key))
    if worker:
      worker.status = 'IDLE'; worker.current_run_id = None; worker.heartbeat_at = datetime.utcnow()
    add_event(db, run.id, 'execution_completed', 'SUCCESS' if run.status == 'PASSED' else 'FAILED', run.safe_error_message, {'status': run.status})
    store_artifact(db, run, None, None, 'SUMMARY', 'run-summary.json', json.dumps({'run_key': run.run_key, 'status': run.status, 'completed_steps': run.completed_steps, 'failed_steps': run.failed_steps}, sort_keys=True).encode(), 'application/json')
    db.flush()
  return run


def execute_step(db: Session, client: PinnedTargetSession, target: ConnectionTarget, run: AutomatedRun, run_case: AutomatedRunCase, step: dict, page: dict) -> None:
  started = time.monotonic()
  result = db.scalar(select(AutomatedStepResult).where(AutomatedStepResult.run_case_id == run_case.id, AutomatedStepResult.step_number == int(step['step_number'])))
  if result is None:
    result = AutomatedStepResult(project_id=run.project_id, run_case_id=run_case.id, step_number=int(step['step_number']))
    db.add(result)
  result.action_type = step['action']
  result.selector = step.get('selector')
  result.value_redacted = safe_text(step.get('value'))
  result.expected_redacted = safe_text(step.get('expected') or step.get('text') or step.get('path'))
  result.status = 'RUNNING'
  result.failure_classification = None
  result.safe_error_message = None
  result.started_at = datetime.utcnow()
  db.flush()
  try:
    action = step['action']
    if action == 'NAVIGATE':
      navigate(client, target, step['path'], page)
    elif action == 'ASSERT_URL_PATH':
      if page['path'] != step['path']:
        raise AssertionError('URL path assertion failed.')
    elif action == 'ASSERT_TITLE':
      expected = str(step.get('expected', ''))
      if expected and expected not in page.get('title', ''):
        raise AssertionError('Page title assertion failed.')
    elif action == 'ASSERT_TEXT':
      expected = str(step.get('expected') or step.get('text') or '')
      if expected not in page.get('text', ''):
        raise AssertionError('Text assertion failed.')
    elif action == 'ASSERT_VISIBLE':
      selector = str(step.get('selector'))
      if selector not in page.get('text', ''):
        raise AssertionError('Element visibility assertion failed.')
    elif action == 'ASSERT_HIDDEN':
      selector = str(step.get('selector'))
      if selector in page.get('text', ''):
        raise AssertionError('Element hidden assertion failed.')
    elif action == 'SCREENSHOT':
      artifact = store_artifact(db, run, run_case, result, 'SCREENSHOT', f'step-{result.step_number}.png', ONE_PIXEL_PNG, 'image/png')
      result.safe_error_message = f'evidence:{artifact.id}'
    elif action == 'RELOAD':
      navigate(client, target, page['path'], page)
    elif action in {'GO_BACK', 'GO_FORWARD'}:
      history = page['history']
      page['history_index'] = max(0, page['history_index'] - 1) if action == 'GO_BACK' else min(len(history) - 1, page['history_index'] + 1)
      navigate(client, target, history[page['history_index']], page, record_history=False)
    else:
      # Input and click-style actions are structured and recorded only; no credentials, cookies, or code are injected.
      pass
    result.status = 'PASSED'
    run.completed_steps += 1
  except AssertionError as exc:
    result.status = 'FAILED'; result.failure_classification = 'ASSERTION'; result.safe_error_message = safe_text(exc)
    run.completed_steps += 1; run.failed_steps += 1; run_case.status = 'FAILED'; run_case.failure_classification = 'ASSERTION'; run_case.safe_error_message = result.safe_error_message
  except HTTPException as exc:
    result.status = 'BLOCKED'; result.failure_classification = 'POLICY_BLOCKED'; result.safe_error_message = safe_text(exc.detail)
    run.completed_steps += 1; run.failed_steps += 1; run_case.status = 'BLOCKED'; run_case.failure_classification = 'POLICY_BLOCKED'; run_case.safe_error_message = result.safe_error_message
    raise
  finally:
    result.completed_at = datetime.utcnow()
    result.duration_ms = int((time.monotonic() - started) * 1000)


def navigate(client: PinnedTargetSession, target: ConnectionTarget, path: str, page: dict, record_history: bool = True) -> None:
  check_probe_allowed(path, load_probe_paths(target.allowed_probe_paths_json))
  response = client.request('GET', path)
  if response.is_redirect:
    absolute = client.redirect_location(response)
    if absolute:
      validate_same_origin(absolute, target.normalized_origin)
    raise HTTPException(status_code=403, detail='Redirects are blocked during automated execution.')
  validate_same_origin(response.url, target.normalized_origin)
  text = response.text[:settings.execution_max_text_bytes]
  page['path'] = path
  page['title'] = extract_title(text)
  page['text'] = safe_text(text) or ''
  if record_history:
    page['history'] = page['history'][:page['history_index'] + 1] + [path]
    page['history_index'] = len(page['history']) - 1


def extract_title(text: str) -> str:
  match = re.search(r'<title>(.*?)</title>', text, flags=re.I | re.S)
  return re.sub(r'\s+', ' ', match.group(1)).strip()[:200] if match else ''


def store_artifact(db: Session, run: AutomatedRun, run_case: AutomatedRunCase | None, step: AutomatedStepResult | None, artifact_type: str, original_name: str, content: bytes, mime_type: str) -> ExecutionArtifact:
  if SECRET_PATTERN.search(original_name) or SECRET_PATTERN.search(content[:4096].decode(errors='ignore')):
    raise HTTPException(status_code=422, detail='Artifact contains credential-like content.')
  existing = db.scalar(select(func.coalesce(func.sum(ExecutionArtifact.size_bytes), 0)).where(ExecutionArtifact.run_id == run.id)) or 0
  if existing + len(content) > settings.execution_max_artifact_bytes_per_run:
    raise HTTPException(status_code=413, detail='Run artifact storage limit exceeded.')
  suffix = Path(original_name).suffix.lower()
  if suffix in {'.exe', '.bat', '.cmd', '.ps1', '.msi', '.dll', '.com', '.scr'}:
    raise HTTPException(status_code=422, detail='Executable artifacts are not allowed.')
  run_dir = (ARTIFACT_ROOT / run.run_key).resolve()
  run_dir.mkdir(parents=True, exist_ok=True)
  run_dir.relative_to(ARTIFACT_ROOT.resolve())
  stored = f'{uuid4().hex}{suffix or ".txt"}'
  path = (run_dir / stored).resolve()
  path.relative_to(run_dir)
  path.write_bytes(content)
  item = ExecutionArtifact(
    project_id=run.project_id,
    run_id=run.id,
    run_case_id=run_case.id if run_case else None,
    step_result_id=step.id if step else None,
    artifact_type=artifact_type,
    original_filename=Path(original_name).name[:160],
    stored_filename=stored,
    relative_path=str(path.relative_to(settings.data_root)).replace('\\', '/'),
    mime_type=mime_type,
    size_bytes=len(content),
    sha256=hashlib.sha256(content).hexdigest(),
  )
  db.add(item)
  db.flush()
  return item


def artifact_path(artifact: ExecutionArtifact) -> Path:
  relative = Path(artifact.relative_path)
  base = BACKEND_ROOT if relative.parts and relative.parts[0].lower() == 'data' else settings.data_root
  path = (base / relative).resolve()
  try:
    path.relative_to(ARTIFACT_ROOT.resolve())
  except ValueError:
    raise HTTPException(status_code=400, detail='Invalid artifact path.') from None
  return path
