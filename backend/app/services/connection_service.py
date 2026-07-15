import json
import time
from datetime import datetime
from uuid import uuid4

import httpx
from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import settings
from app.models.connection_target import ConnectionCheck, ConnectionTarget, ConnectionTargetVersion
from app.services.pinned_http import PinnedTargetSession
from app.services.target_policy import check_probe_allowed, load_probe_paths, validate_same_origin

SENSITIVE_HEADERS = {'set-cookie', 'cookie', 'authorization', 'proxy-authorization', 'x-csrf-token', 'x-xsrf-token'}
SAFE_HEADERS = {'content-type', 'content-length', 'server', 'date', 'location', 'strict-transport-security', 'x-frame-options', 'x-content-type-options'}


def sanitize_headers(headers: httpx.Headers) -> dict[str, str]:
  sanitized: dict[str, str] = {}
  for key, value in headers.items():
    lowered = key.lower()
    if lowered in SENSITIVE_HEADERS:
      continue
    if lowered in SAFE_HEADERS or lowered.startswith('x-'):
      sanitized[key] = value[:300]
  return sanitized


def target_snapshot(target: ConnectionTarget) -> dict:
  return {
    'id': target.id,
    'project_id': target.project_id,
    'target_key': target.target_key,
    'name': target.name,
    'description': target.description,
    'environment_type': target.environment_type,
    'normalized_scheme': target.normalized_scheme,
    'normalized_host': target.normalized_host,
    'normalized_port': target.normalized_port,
    'normalized_origin': target.normalized_origin,
    'allowed_probe_paths': load_probe_paths(target.allowed_probe_paths_json),
    'tls_required': target.tls_required,
    'tls_verify': target.tls_verify,
    'connection_timeout_seconds': target.connection_timeout_seconds,
    'lifecycle_state': target.lifecycle_state,
    'enabled': target.enabled,
    'owner_operator_id': target.owner_operator_id,
    'created_by': target.created_by,
    'approved_by': target.approved_by,
    'version': target.version,
  }


def create_target_version(db: Session, target: ConnectionTarget, created_by: int, summary: str, source_state: str | None = None) -> ConnectionTargetVersion:
  next_number = (db.scalar(select(func.max(ConnectionTargetVersion.version_number)).where(ConnectionTargetVersion.target_id == target.id)) or 0) + 1
  target.version = next_number
  version = ConnectionTargetVersion(
    project_id=target.project_id,
    target_id=target.id,
    version_number=next_number,
    snapshot_json=json.dumps(target_snapshot(target), sort_keys=True, separators=(',', ':'), ensure_ascii=True),
    change_summary=summary[:500],
    created_by=created_by,
    source_state=source_state or target.lifecycle_state,
  )
  db.add(version)
  db.flush()
  return version


def target_read(target: ConnectionTarget) -> dict:
  payload = target_snapshot(target)
  payload.update({
    'base_url': target.base_url,
    'reviewed_by': target.reviewed_by,
    'created_at': target.created_at,
    'updated_at': target.updated_at,
    'submitted_at': target.submitted_at,
    'approved_at': target.approved_at,
    'rejected_at': target.rejected_at,
    'disabled_at': target.disabled_at,
    'archived_at': target.archived_at,
    'rejection_reason': target.rejection_reason,
    'last_check_at': target.last_check_at,
    'last_check_status': target.last_check_status,
    'execution_enabled': target.execution_enabled,
    'execution_submitted_by': target.execution_submitted_by,
    'execution_submitted_at': target.execution_submitted_at,
    'execution_approved_by': target.execution_approved_by,
    'execution_approved_at': target.execution_approved_at,
  })
  return payload


def check_read(check: ConnectionCheck) -> dict:
  return {
    'id': check.id,
    'check_key': check.check_key,
    'target_id': check.target_id,
    'target_version': check.target_version,
    'probe_path': check.probe_path,
    'method': check.method,
    'requested_origin': check.requested_origin,
    'resolved_addresses': json.loads(check.resolved_addresses_json or '[]'),
    'started_at': check.started_at,
    'completed_at': check.completed_at,
    'duration_ms': check.duration_ms,
    'status': check.status,
    'http_status': check.http_status,
    'final_origin': check.final_origin,
    'redirect_count': check.redirect_count,
    'tls_protocol': check.tls_protocol,
    'tls_certificate_summary': json.loads(check.tls_certificate_summary_json) if check.tls_certificate_summary_json else None,
    'response_headers': json.loads(check.response_headers_json or '{}'),
    'response_size_bytes': check.response_size_bytes,
    'error_category': check.error_category,
    'safe_error_message': check.safe_error_message,
    'initiated_by': check.initiated_by,
    'created_at': check.created_at,
  }


def run_connection_check(db: Session, target: ConnectionTarget, method: str, probe_path: str, initiated_by: int) -> ConnectionCheck:
  if target.lifecycle_state != 'APPROVED' or not target.enabled:
    raise HTTPException(status_code=409, detail='Only approved and enabled targets can be checked.')
  allowed_paths = load_probe_paths(target.allowed_probe_paths_json)
  path = check_probe_allowed(probe_path, allowed_paths)
  method = method.upper()
  if method not in {'HEAD', 'GET'}:
    raise HTTPException(status_code=422, detail='Only HEAD and GET checks are allowed.')
  started_at = datetime.utcnow()
  started = time.monotonic()
  addresses: list[str] = []
  check = ConnectionCheck(
    project_id=target.project_id,
    check_key=f'CONN-{uuid4().hex[:12].upper()}',
    target_id=target.id,
    target_version=target.version,
    probe_path=path,
    method=method,
    requested_origin=target.normalized_origin,
    resolved_addresses_json='[]',
    started_at=started_at,
    status='RUNNING',
    initiated_by=initiated_by,
  )
  db.add(check)
  db.flush()

  try:
    session = PinnedTargetSession(target, settings.target_user_agent, target.connection_timeout_seconds, settings.target_max_response_bytes)
    addresses = session.addresses
    check.resolved_addresses_json = json.dumps(addresses, separators=(',', ':'))
    response = session.request(method, path, read_body=method == 'GET')
    response_size = len(response.body)
    headers = sanitize_headers(response.headers)
    check.response_headers_json = json.dumps(headers, sort_keys=True, separators=(',', ':'), ensure_ascii=True)
    check.http_status = response.status_code
    check.response_size_bytes = response_size
    if response.is_redirect:
      location = next((value for key, value in response.headers.items() if key.lower() == 'location'), None)
      if not location:
        check.status = 'REDIRECT_BLOCKED'
        check.error_category = 'REDIRECT'
        check.safe_error_message = 'Redirect response did not include a safe Location header.'
      else:
        try:
          absolute = session.redirect_location(response) or ''
          validate_same_origin(absolute, target.normalized_origin)
          check.status = 'REDIRECT_BLOCKED'
          check.error_category = 'REDIRECT'
          check.safe_error_message = 'Redirect was detected and not followed in Stage 9.'
          check.final_origin = target.normalized_origin
          check.redirect_count = 1
        except HTTPException as exc:
          check.status = 'REDIRECT_BLOCKED'
          check.error_category = 'REDIRECT'
          check.safe_error_message = exc.detail
    elif 200 <= response.status_code < 400:
      check.status = 'REACHABLE'
      check.final_origin = target.normalized_origin
    else:
      check.status = 'HTTP_ERROR'
      check.error_category = 'HTTP'
      check.safe_error_message = f'Target returned HTTP {response.status_code}.'
      check.final_origin = target.normalized_origin
    if target.normalized_scheme == 'https':
      check.tls_protocol = 'TLS'
      check.tls_certificate_summary_json = json.dumps({'verified': target.tls_verify}, separators=(',', ':'))
  except HTTPException as exc:
    if exc.status_code == 408:
      check.status = 'TIMEOUT'
      check.error_category = 'TIMEOUT'
    elif exc.status_code == 502:
      check.status = 'DNS_ERROR'
      check.error_category = 'DNS'
    else:
      check.status = 'POLICY_BLOCKED'
      check.error_category = 'POLICY'
    check.safe_error_message = str(exc.detail)
  except httpx.TimeoutException:
    check.status = 'TIMEOUT'
    check.error_category = 'TIMEOUT'
    check.safe_error_message = 'Connection check timed out.'
  except httpx.ConnectError:
    check.status = 'TCP_ERROR'
    check.error_category = 'TCP'
    check.safe_error_message = 'Connection could not be established.'
  except httpx.TransportError:
    check.status = 'UNREACHABLE'
    check.error_category = 'NETWORK'
    check.safe_error_message = 'Connection check failed safely.'
  finally:
    check.completed_at = datetime.utcnow()
    check.duration_ms = int((time.monotonic() - started) * 1000)
    target.last_check_at = check.completed_at
    target.last_check_status = check.status
    if not check.resolved_addresses_json:
      check.resolved_addresses_json = json.dumps(addresses, separators=(',', ':'))
    if not check.response_headers_json:
      check.response_headers_json = '{}'
  db.flush()
  return check
