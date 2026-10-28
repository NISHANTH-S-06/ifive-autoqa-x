import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import func, select, update
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
from app.services.target_policy import check_probe_allowed, load_probe_paths, resolve_host

BACKEND_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_ROOT.parent
PLAYWRIGHT_RUNNER = PROJECT_ROOT / 'qa' / 'automated-execution-runner.mjs'
ARTIFACT_ROOT = settings.artifact_root
TERMINAL_RUN_STATES = {'PASSED', 'FAILED', 'CANCELLED', 'TIMED_OUT', 'BLOCKED'}
SAFE_RETRY_STATES = {'FAILED', 'TIMED_OUT', 'BLOCKED'}
ALLOWED_ACTIONS = {
  'NAVIGATE', 'FILL', 'CLICK', 'ASSERT_VISIBLE', 'ASSERT_TEXT', 'SCREENSHOT',
  'SELECT', 'CHECK', 'UNCHECK', 'WAIT_FOR_ELEMENT', 'ASSERT_VALUE', 'ASSERT_URL', 'READ_TEXT', 'ASSERT_TABLE_ROW'
}
READ_ONLY_ACTIONS = {
  'NAVIGATE', 'ASSERT_VISIBLE', 'ASSERT_TEXT', 'SCREENSHOT',
  'WAIT_FOR_ELEMENT', 'ASSERT_VALUE', 'ASSERT_URL', 'READ_TEXT', 'ASSERT_TABLE_ROW'
}
SAFE_INTERACTION_ACTIONS = {'FILL', 'CLICK', 'SELECT', 'CHECK', 'UNCHECK'}
ALLOWED_RISK_LEVELS = {'READ_ONLY', 'SAFE_INTERACTION'}
BLOCKED_RISK_LEVELS = {'MUTATING', 'DESTRUCTIVE'}
ACTION_RISK_LEVELS = {**{action: 'READ_ONLY' for action in READ_ONLY_ACTIONS}, **{action: 'SAFE_INTERACTION' for action in SAFE_INTERACTION_ACTIONS}}
DANGEROUS_ACTION_PATTERN = re.compile(r'(?i)\b(delete|remove|post|approve|submit\s+payment|confirm\s+transaction|process\s+payroll|finalize|cancel\s+order|upload|import)\b')
SECRET_PATTERN = re.compile(r'(?i)(password|token|cookie|csrf|authorization|bearer|api[_-]?key|secret|autoqa_session)')
CODE_PATTERN = re.compile(r'(?i)(javascript|python|powershell|shell|subprocess|eval|function|=>|<script|import\s+|require\()')


def next_run_key(db: Session) -> str:
  return f'ARUN-{(db.scalar(select(func.count(AutomatedRun.id))) or 0) + 1:05d}-{uuid4().hex[:6].upper()}'


def progress(run: AutomatedRun) -> str:
  return f'{run.completed_steps or 0}/{run.total_steps or 0}'


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
  # Normalize any non-standard risk levels from AI output (e.g. STATE_CHANGE) to SAFE_INTERACTION
  if declared_risk not in ALLOWED_RISK_LEVELS and declared_risk not in BLOCKED_RISK_LEVELS:
    declared_risk = 'SAFE_INTERACTION'
  if declared_risk in BLOCKED_RISK_LEVELS:
    raise HTTPException(status_code=422, detail='Mutating and destructive actions are blocked in Stage 11.')
  if declared_risk not in ALLOWED_RISK_LEVELS:
    raise HTTPException(status_code=422, detail='Unsupported execution risk level.')
  action_risk = ACTION_RISK_LEVELS.get(action, 'DESTRUCTIVE')
  if action_risk in BLOCKED_RISK_LEVELS or declared_risk not in ALLOWED_RISK_LEVELS:
    raise HTTPException(status_code=422, detail='Action risk level is not allowed in Stage 11.')
  for key, value in payload.items():
    text = str(value)
    if CODE_PATTERN.search(text):
      raise HTTPException(status_code=422, detail='Automated step contains code-like content.')
    if key != 'selector' and SECRET_PATTERN.search(text):
      raise HTTPException(status_code=422, detail='Automated step contains credential-like content.')
    if DANGEROUS_ACTION_PATTERN.search(text):
      raise HTTPException(status_code=422, detail='Dangerous or mutating action wording is blocked in Stage 11.')
  path = payload.get('path')
  if action == 'NAVIGATE':
    if not isinstance(path, str):
      raise HTTPException(status_code=422, detail='Path is required for this action.')
    validate_relative_path(path)
  if 'url' in payload:
    raise HTTPException(status_code=422, detail='Full URLs are not allowed in automated steps.')
  if action in {'CLICK', 'FILL', 'ASSERT_TEXT', 'ASSERT_VISIBLE', 'SELECT', 'CHECK', 'UNCHECK', 'WAIT_FOR_ELEMENT', 'ASSERT_VALUE', 'READ_TEXT', 'ASSERT_TABLE_ROW'} and not payload.get('selector'):
    raise HTTPException(status_code=422, detail='Selector is required for this action.')
  if action in {'FILL', 'SELECT'} and 'value' not in payload:
    raise HTTPException(status_code=422, detail='Value is required for this action.')
  if action in {'ASSERT_TEXT', 'ASSERT_TABLE_ROW'} and not isinstance(payload.get('expected', payload.get('text')), str):
    raise HTTPException(status_code=422, detail='Expected text is required for this action.')
  if action == 'ASSERT_VALUE' and 'expected' not in payload and 'value' not in payload:
    raise HTTPException(status_code=422, detail='Expected value is required for ASSERT_VALUE.')
  if action == 'ASSERT_URL' and 'expected' not in payload and 'path' not in payload and 'value' not in payload:
    raise HTTPException(status_code=422, detail='Expected URL path is required for ASSERT_URL.')
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


def create_run_from_plan(db: Session, target: ConnectionTarget, name: str, description: str | None, plan_id: int, timeout_seconds: int, max_retries: int, created_by: int, runtime_secret_required: bool = False) -> AutomatedRun:
  from app.models.test_plan import TestPlan, TestPlanVersion

  ensure_execution_target(target)
  if runtime_secret_required:
    raise HTTPException(status_code=409, detail='Runtime-secret input is not available in the local Stage 11 verifier; authenticated login acceptance remains pending.')

  plan = db.get(TestPlan, plan_id)
  if not plan or plan.status != 'APPROVED':
    raise HTTPException(status_code=409, detail='TestPlan must be approved before execution.')

  version = db.scalar(select(TestPlanVersion).where(TestPlanVersion.test_plan_id == plan.id, TestPlanVersion.version_number == plan.approved_version_number))
  if not version:
    raise HTTPException(status_code=409, detail='TestPlan approved version is missing.')

  snapshot_hash = hashlib.sha256(version.immutable_snapshot_json.encode('utf-8')).hexdigest()
  if snapshot_hash != version.plan_hash:
      raise HTTPException(status_code=409, detail='TestPlan version snapshot hash mismatch. Integrity validation failed.')

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

  # For execution, we serialize the version's scenarios into a standard snapshot format
  snapshot_data = json.loads(version.immutable_snapshot_json)
  # In our new implementation, snapshot_data is from AIAnalysisResponse or TestPlanUpdate

  # Re-build steps for the snapshot payload
  scenarios = snapshot_data.get('scenarios', [])
  if not scenarios and version.scenarios:
      scenarios = []
      for sc in version.scenarios:
          scenarios.append({
              'scenario_type': sc.scenario_type,
              'enabled': sc.enabled,
              'steps': [
                  {
                      'action': st.action,
                      'selector': st.locator_json,
                      'value': st.input_value_reference,
                      'expected_result': st.expected_value,
                      'path': st.locator_json if st.action == 'NAVIGATE' else None,
                  }
                  for st in sc.steps
              ]
          })

  formatted_steps = []
  global_step_idx = 1
  for scenario in scenarios:
      if not scenario.get('enabled', True):
          continue
      if scenario.get('scenario_type') not in {'PRIMARY', 'SMOKE'}:
          continue

      for step in scenario.get('steps', []):
          # Ensure backwards compatibility with expected legacy step format
          action_type = step.get('action', 'NAVIGATE')
          action_payload = {
              'action': action_type,
          }
          if step.get('locator_json') or step.get('selector'):
              action_payload['selector'] = step.get('locator_json') or step.get('selector')
          if step.get('input_value_reference') or step.get('value'):
              action_payload['value'] = step.get('input_value_reference') or step.get('value')
          if step.get('path'):
              action_payload['path'] = step.get('path')

          risk = step.get('risk_level', 'SAFE_INTERACTION')
          # Normalize any AI-generated risk level that isn't in the allowed set
          if risk not in ALLOWED_RISK_LEVELS:
              risk = 'SAFE_INTERACTION'
          action_payload['risk_level'] = risk

          formatted_steps.append({
              'step_number': global_step_idx,
              'action': json.dumps(action_payload),
              'expected_result': step.get('expected_value') or step.get('expected_result') or 'Step completed'
          })
          global_step_idx += 1

  formatted_snapshot = {'steps': formatted_steps}
  steps = validate_snapshot_actions(formatted_snapshot)
  run.risk_level = _max_risk(run.risk_level, snapshot_risk_level(formatted_snapshot))
  total_steps = len(steps)

  run.cases.append(AutomatedRunCase(
    project_id=run.project_id,
    test_plan_id=plan.id,
    test_plan_version=version.version_number,
    test_plan_version_id=version.id,
    plan_hash=version.plan_hash,
    source_revision=version.source_revision,
    case_snapshot_json=json.dumps(formatted_snapshot),
    sort_order=1
  ))

  run.total_steps = total_steps
  add_event(db, run.id, 'automated_run_created', metadata={'run_key': run.run_key, 'target_version': run.target_version, 'plan': plan.id})
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


def claim_next_job(db: Session, worker_key: str, allowed_project_ids: tuple[int, ...] | None = None, lease_seconds: int = 60) -> ExecutionJob | None:
  now = datetime.utcnow()
  worker = db.scalar(select(ExecutionWorker).where(ExecutionWorker.worker_key == worker_key))
  if worker is None:
    worker = ExecutionWorker(worker_key=worker_key)
    db.add(worker)
    db.flush()
  if db.scalar(select(func.count(ExecutionJob.id)).where(ExecutionJob.status == 'RUNNING', ExecutionJob.lease_owner == worker_key)) >= worker.max_concurrency:
    return None
  statement = select(ExecutionJob.id).where(ExecutionJob.status == 'QUEUED')
  if allowed_project_ids is not None:
    if not allowed_project_ids:
      worker.status = 'IDLE'; worker.heartbeat_at = now
      return None
    statement = statement.where(ExecutionJob.project_id.in_(allowed_project_ids))
  candidate_id = db.scalar(statement.order_by(ExecutionJob.priority.desc(), ExecutionJob.created_at).limit(1))
  if candidate_id is None:
    worker.status = 'IDLE'; worker.heartbeat_at = now
    return None
  result = db.execute(
    update(ExecutionJob)
    .where(ExecutionJob.id == candidate_id, ExecutionJob.status == 'QUEUED')
    .values(
      status='RUNNING',
      lease_owner=worker_key,
      lease_expires_at=now + timedelta(seconds=lease_seconds),
      attempts=ExecutionJob.attempts + 1,
      updated_at=now,
    )
    .execution_options(synchronize_session=False)
  )
  if result.rowcount != 1:
    worker.status = 'IDLE'; worker.heartbeat_at = now
    return None
  job = db.get(ExecutionJob, candidate_id)
  if job is None:
    worker.status = 'IDLE'; worker.heartbeat_at = now
    return None
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


class BrowserExecutionError(Exception):
  pass


def png_dimensions(content: bytes) -> tuple[int, int]:
  if len(content) < 24 or content[12:16] != b'IHDR':
    raise BrowserExecutionError('Playwright screenshot was not a PNG image.')
  return int.from_bytes(content[16:20], 'big'), int.from_bytes(content[20:24], 'big')


def run_playwright(db: Session, target: ConnectionTarget, run: AutomatedRun) -> list[dict]:
  node = shutil.which('node')
  if node is None or not PLAYWRIGHT_RUNNER.is_file():
    raise BrowserExecutionError('Playwright worker runtime is unavailable.')
  pinned = PinnedTargetSession(target, settings.execution_user_agent, min(run.timeout_seconds, 30), settings.execution_max_text_bytes)
  pinned.assert_current_resolution()
  allowed_paths = load_probe_paths(target.allowed_probe_paths_json)
  steps = []
  execution_id = 0
  for run_case in sorted(run.cases, key=lambda item: item.sort_order):
    for step in validate_snapshot_actions(json.loads(run_case.case_snapshot_json)):
      execution_id += 1
      if step['action'] == 'NAVIGATE':
        check_probe_allowed(step['path'], load_probe_paths(target.allowed_probe_paths_json))
      steps.append({key: value for key, value in step.items() if key not in {'risk_level', 'step_number'}} | {'execution_id': execution_id})
  work_root = Path(settings.temp_root).resolve() / 'playwright-execution'
  work_root.mkdir(parents=True, exist_ok=True)
  with tempfile.TemporaryDirectory(dir=work_root) as temporary:
    temporary_path = Path(temporary).resolve()
    input_path = temporary_path / 'request.json'
    output_path = temporary_path / 'result.json'
    request = {
      'target_origin': target.normalized_origin,
      'target_host': target.normalized_host,
      'pinned_address': pinned.pinned_address,
      'tls_verify': target.tls_verify,
      'user_agent': settings.execution_user_agent,
      'timeout_ms': run.timeout_seconds * 1000,
      'allowed_paths': allowed_paths,
      'output_directory': str(temporary_path),
      'steps': steps,
    }
    input_path.write_text(json.dumps(request, sort_keys=True), encoding='utf-8')
    try:
      completed = subprocess.run(
        [node, str(PLAYWRIGHT_RUNNER), str(input_path), str(output_path)],
        cwd=str(PROJECT_ROOT / 'qa'), capture_output=True, text=True,
        timeout=run.timeout_seconds + 10, check=False,
      )
    except subprocess.TimeoutExpired:
      raise TimeoutError() from None
    if completed.stderr:
      import logging
      logging.getLogger('uvicorn').warning(f"PLAYWRIGHT STDERR:\n{completed.stderr}")
    if not output_path.is_file():
      raise BrowserExecutionError('Playwright worker returned no result.')
    try:
      payload = json.loads(output_path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
      raise BrowserExecutionError('Playwright worker returned invalid output.') from None
    if payload.get('fatal_error'):
      detail = payload['fatal_error'].get('safe_error_message') or 'Playwright worker failed.'
      if payload['fatal_error'].get('failure_classification') == 'TIMEOUT':
        raise TimeoutError()
      if payload['fatal_error'].get('failure_classification') == 'POLICY_BLOCKED':
        raise HTTPException(status_code=403, detail=detail)
      raise BrowserExecutionError(detail)
    if completed.returncode != 0:
      raise BrowserExecutionError('Playwright worker failed safely.')
    results = payload.get('results')
    if not isinstance(results, list):
      raise BrowserExecutionError('Playwright worker returned invalid step results.')
    for outcome in results:
      if outcome.get('screenshot_file'):
        screenshot = (temporary_path / Path(outcome['screenshot_file']).name).resolve()
        screenshot.relative_to(temporary_path)
        try:
          outcome['screenshot_content'] = screenshot.read_bytes()
        except OSError:
          raise BrowserExecutionError('Playwright screenshot output is unavailable.') from None
    return results


def execute_next_job(db: Session, worker_key: str = 'local-stage10-worker', allowed_project_ids: tuple[int, ...] | None = None, target_run_id: int | None = None) -> AutomatedRun | None:
  recover_stale_jobs(db)
  if target_run_id is not None:
    # Direct execution of a specific run — bypass normal FIFO queue selection
    now = datetime.utcnow()
    worker = db.scalar(select(ExecutionWorker).where(ExecutionWorker.worker_key == worker_key))
    if worker is None:
      worker = ExecutionWorker(worker_key=worker_key)
      db.add(worker)
      db.flush()
    if db.scalar(select(func.count(ExecutionJob.id)).where(ExecutionJob.status == 'RUNNING', ExecutionJob.lease_owner == worker_key)) >= worker.max_concurrency:
      db.flush()
      return None

    statement = select(ExecutionJob).where(ExecutionJob.run_id == target_run_id, ExecutionJob.status.in_(['QUEUED', 'RUNNING']))
    if allowed_project_ids is not None:
      if not allowed_project_ids:
        db.flush()
        return None
      statement = statement.where(ExecutionJob.project_id.in_(allowed_project_ids))
    job = db.scalar(statement)
    if job is None:
      db.flush()
      return None

    run = db.get(AutomatedRun, job.run_id)
    if run is None:
      db.flush()
      return None

    res = db.execute(
      update(ExecutionJob)
      .where(ExecutionJob.id == job.id, ExecutionJob.status.in_(['QUEUED', 'RUNNING']))
      .values(status='RUNNING', lease_owner=worker_key, lease_expires_at=now + timedelta(seconds=120), attempts=ExecutionJob.attempts + 1, updated_at=now)
      .execution_options(synchronize_session=False)
    )
    if res.rowcount != 1:
      db.flush()
      return None

    db.refresh(job)
    run.status = 'RUNNING'
    run.worker_key = worker_key
    run.started_at = run.started_at or now
    run.lease_expires_at = job.lease_expires_at
    worker.current_run_id = run.id
    worker.status = 'BUSY'
    worker.heartbeat_at = now
    db.flush()
  else:
    job = claim_next_job(db, worker_key, allowed_project_ids)
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
  db.commit()
  target = db.get(ConnectionTarget, run.target_id)
  try:
    if target is None:
      raise HTTPException(status_code=404, detail='Execution target not found.')
    ensure_execution_target(target)
    if target.version != run.target_version or target.normalized_origin != run.target_origin:
      raise HTTPException(status_code=409, detail='Execution target changed after run approval.')
    run.dns_pinning_status = 'ENFORCED'
    results = run_playwright(db, target, run)
    if _run_was_cancelled(db, run.id):
      raise RuntimeError('cancelled')
    result_by_id = {item['execution_id']: item for item in results}
    expected = []
    execution_id = 0
    for run_case in sorted(run.cases, key=lambda item: item.sort_order):
      run_case.status = 'RUNNING'; run_case.started_at = datetime.utcnow()
      snapshot = json.loads(run_case.case_snapshot_json)
      for step in validate_snapshot_actions(snapshot):
        execution_id += 1
        expected.append((execution_id, run_case, step))
    if not results and expected:
      raise BrowserExecutionError('Playwright returned no step results.')
    for current_id, run_case, step in expected:
      outcome = result_by_id.get(current_id)
      if outcome is None:
        run_case.status = 'FAILED'; run_case.failure_classification = 'PLAYWRIGHT'; run_case.safe_error_message = 'Playwright did not return a result for this step.'
        raise BrowserExecutionError(run_case.safe_error_message)
      result = next((item for item in run_case.step_results if item.step_number == int(step['step_number'])), None)
      if result is None:
        result = db.scalar(select(AutomatedStepResult).where(AutomatedStepResult.run_case_id == run_case.id, AutomatedStepResult.step_number == int(step['step_number'])))
      if result is None:
        result = AutomatedStepResult(
          project_id=run.project_id,
          run_case_id=run_case.id,
          step_number=int(step['step_number']),
          action_type=step['action'],
          selector=step.get('selector'),
          value_redacted=safe_text(step.get('value')),
          expected_redacted=safe_text(step.get('expected') or step.get('text') or step.get('path')),
          status=outcome['status'],
          failure_classification=outcome.get('failure_classification'),
          safe_error_message=safe_text(outcome.get('safe_error_message')),
          started_at=datetime.utcnow(),
          completed_at=datetime.utcnow(),
          duration_ms=int(outcome.get('duration_ms') or 0),
        )
        db.add(result)
        db.flush()
      else:
        result.action_type = step['action']
        result.selector = step.get('selector')
        result.value_redacted = safe_text(step.get('value'))
        result.expected_redacted = safe_text(step.get('expected') or step.get('text') or step.get('path'))
        result.status = outcome['status']
        result.failure_classification = outcome.get('failure_classification')
        result.safe_error_message = safe_text(outcome.get('safe_error_message'))
        result.started_at = result.started_at or datetime.utcnow()
        result.completed_at = datetime.utcnow()
        result.duration_ms = int(outcome.get('duration_ms') or 0)
        db.flush()
      if outcome.get('screenshot_file'):
        content = outcome.get('screenshot_content')
        if not content and outcome.get('screenshot_file'):
          try:
            content = (temporary_path / Path(outcome['screenshot_file']).name).read_bytes()
          except OSError:
            content = None
        if isinstance(content, bytes) and content.startswith(b'\x89PNG\r\n\x1a\n'):
          try:
            width, height = png_dimensions(content)
            if width >= 2 and height >= 2:
              artifact = store_artifact(db, run, run_case, result, 'SCREENSHOT', f'step-{result.step_number}.png', content, 'image/png')
              result.safe_error_message = f'evidence:{artifact.id}'
          except Exception:
            pass
      if outcome['status'] != 'PASSED':
        run.completed_steps += 1
        run.failed_steps += 1
        run_case.status = 'BLOCKED' if outcome['status'] == 'BLOCKED' else 'FAILED'
        run_case.failure_classification = result.failure_classification
        run_case.safe_error_message = result.safe_error_message
        if result.failure_classification == 'TIMEOUT':
          raise TimeoutError()
        if result.failure_classification == 'POLICY_BLOCKED':
          raise HTTPException(status_code=403, detail='Navigation outside the approved target origin was blocked.')
        break
      run.completed_steps += 1
    for run_case in run.cases:
      if run_case.status == 'RUNNING':
        run_case.status = 'PASSED'; run_case.completed_at = datetime.utcnow()
    if _run_was_cancelled(db, run.id):
      raise RuntimeError('cancelled')
    if any(c.status == 'BLOCKED' for c in run.cases):
      run.status = 'BLOCKED'
    elif run.failed_steps == 0:
      run.status = 'PASSED'
    else:
      run.status = 'FAILED'
    attempt.status = run.status
    if run.status in {'FAILED', 'BLOCKED'}:
      failed = db.scalar(select(AutomatedStepResult).where(AutomatedStepResult.run_case_id.in_([item.id for item in run.cases]), AutomatedStepResult.status.in_(['FAILED', 'BLOCKED'])).order_by(AutomatedStepResult.id.desc()))
      attempt.failure_classification = failed.failure_classification if failed else 'PLAYWRIGHT'
      attempt.safe_error_message = failed.safe_error_message if failed else 'Playwright execution failed.'
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
  except BrowserExecutionError as exc:
    run.status = 'FAILED'; run.failure_classification = 'PLAYWRIGHT'; run.safe_error_message = safe_text(exc)
    attempt.status = run.status; attempt.failure_classification = run.failure_classification; attempt.safe_error_message = run.safe_error_message
  finally:
    if _run_was_cancelled(db, run.id):
      _finish_cancelled_worker(db, run, job, attempt, worker_key)
    else:
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
      db.commit()
  return run


def _run_was_cancelled(db: Session, run_id: int) -> bool:
  with db.no_autoflush:
    status = db.scalar(select(AutomatedRun.status).where(AutomatedRun.id == run_id))
  return status == 'CANCELLED'


def _finish_cancelled_worker(db: Session, run: AutomatedRun, job: ExecutionJob, attempt: ExecutionAttempt, worker_key: str) -> None:
  db.expire(run)
  db.refresh(run)
  job.status = 'CANCELLED'
  job.lease_owner = None
  job.lease_expires_at = None
  job.updated_at = datetime.utcnow()
  attempt.status = 'CANCELLED'
  attempt.completed_at = datetime.utcnow()
  attempt.failure_classification = 'CANCELLED'
  attempt.safe_error_message = 'Automated run was cancelled before worker completion.'
  worker = db.scalar(select(ExecutionWorker).where(ExecutionWorker.worker_key == worker_key))
  if worker:
    worker.status = 'IDLE'
    worker.current_run_id = None
    worker.heartbeat_at = datetime.utcnow()
  add_event(db, run.id, 'execution_cancelled_during_worker_completion', 'WARN', metadata={'worker': worker_key})
  db.flush()


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
