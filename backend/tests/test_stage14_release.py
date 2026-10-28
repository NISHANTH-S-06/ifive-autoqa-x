import json
import socket
import sqlite3
import subprocess
from contextlib import closing
from dataclasses import replace
from datetime import datetime, timedelta
from pathlib import Path

import pytest
from sqlalchemy import func, select

from app.config import PROJECT_ROOT, Settings, settings
from app.logging_config import SafeJsonFormatter
from app.models.audit_event import AuditEvent
from app.models.automated_execution import AutomatedRun, ExecutionArtifact
from app.models.connection_target import ConnectionTarget
from app.models.operator import Operator
from app.models.password_history import PasswordHistory
from app.services.backup_service import create_backup, restore_backup, validate_backup
from app.services.retention_service import CONFIRMATION, cleanup_retention


def isolated_settings(tmp_path: Path) -> Settings:
  data = tmp_path / 'data'
  return replace(
    settings,
    app_env='test',
    data_root=data,
    runtime_root=tmp_path / 'runtime',
    backup_root=tmp_path / 'backups',
    qa_runs_root=tmp_path / 'qa-runs',
    database_url=f'sqlite:///{(data / "autoqa.db").as_posix()}',
    retention_artifact_days=1,
    retention_evidence_days=1,
    retention_export_days=1,
    retention_operational_days=1,
  )


def write_database(path: Path, value: str) -> None:
  path.parent.mkdir(parents=True, exist_ok=True)
  with closing(sqlite3.connect(path)) as connection:
    connection.execute('CREATE TABLE IF NOT EXISTS release_probe (value TEXT NOT NULL)')
    connection.execute('DELETE FROM release_probe')
    connection.execute('INSERT INTO release_probe VALUES (?)', (value,))
    connection.commit()


def read_database(path: Path) -> str:
  with closing(sqlite3.connect(path)) as connection:
    return connection.execute('SELECT value FROM release_probe').fetchone()[0]


def test_environment_validation_fails_closed(monkeypatch):
  monkeypatch.setenv('AUTOQA_SAFE_MODE', 'false')
  unsafe = Settings()
  with pytest.raises(RuntimeError, match='SAFE_MODE'):
    unsafe.validate()
  monkeypatch.setenv('AUTOQA_SAFE_MODE', 'true')
  monkeypatch.setenv('AUTOQA_ALLOW_PRODUCTION_EXECUTION', 'true')
  production = Settings()
  with pytest.raises(RuntimeError, match='PRODUCTION_EXECUTION'):
    production.validate()
  monkeypatch.setenv('AUTOQA_ALLOW_REAL_TARGET_EXECUTION', 'false')
  fresh = Settings()
  assert fresh.allow_real_target_execution is False
  assert fresh.debug is False
  assert fresh.tls_verify is True


def test_backup_checksum_restore_and_rollback_safety(tmp_path, monkeypatch):
  config = isolated_settings(tmp_path)
  config.prepare_directories()
  write_database(config.database_path, 'original')
  (config.evidence_root / 'evidence.txt').write_text('safe evidence', encoding='utf-8')
  (config.artifact_root / 'artifact.json').write_text('{"safe":true}', encoding='utf-8')
  (config.export_root / 'report.csv').write_text('name,status\ncase,PASS\n', encoding='utf-8')
  (config.qa_runs_root / 'RUN-LOCAL' / 'results').mkdir(parents=True)
  (config.qa_runs_root / 'RUN-LOCAL' / 'results' / 'results.json').write_text('{}', encoding='utf-8')
  created = create_backup(config)
  backup_dir = config.backup_root / created['backup_id']
  validated = validate_backup(backup_dir, config)
  assert validated['manifest_sha256'] == created['manifest_sha256']
  manifest = json.loads((backup_dir / 'manifest.json').read_text(encoding='utf-8'))
  assert all('..' not in Path(item['path']).parts for item in manifest['entries'])
  assert all(len(item['sha256']) == 64 for item in manifest['entries'])

  write_database(config.database_path, 'changed')
  restored = restore_backup(backup_dir, f"RESTORE {created['backup_id']}", config)
  assert read_database(config.database_path) == 'original'
  assert validate_backup(config.backup_root / restored['pre_restore_backup_id'], config)

  write_database(config.database_path, 'rollback-value')
  original_replace = Path.replace
  raised = False

  def fail_once(path: Path, target):
    nonlocal raised
    if path.resolve() == config.artifact_root.resolve() and not raised:
      raised = True
      raise OSError('simulated replacement failure')
    return original_replace(path, target)

  monkeypatch.setattr(Path, 'replace', fail_once)
  with pytest.raises(OSError, match='simulated'):
    restore_backup(backup_dir, f"RESTORE {created['backup_id']}", config)
  assert read_database(config.database_path) == 'rollback-value'


def test_retention_dry_run_containment_active_protection_and_history_preservation(db, tmp_path):
  config = isolated_settings(tmp_path)
  config.prepare_directories()
  old = datetime.utcnow() - timedelta(days=10)
  operator = Operator(username='stage14-owner', display_name='Stage 14 Owner', password_hash='fixture-hash', role='TESTER', is_active=True)
  db.add(operator); db.flush()
  db.add(PasswordHistory(operator_id=operator.id, password_hash='history-hash', password_version=1, changed_at=old, change_reason='BOOTSTRAP'))
  target = ConnectionTarget(target_key='S14-LOCAL', name='Stage 14 Local', environment_type='LOCAL', base_url='http://127.0.0.1:45555', normalized_scheme='http', normalized_host='127.0.0.1', normalized_port=45555, normalized_origin='http://127.0.0.1:45555', allowed_probe_paths_json='["/"]', tls_required=False, tls_verify=True, created_by=operator.id)
  db.add(target); db.flush()
  terminal = AutomatedRun(run_key='S14-TERMINAL', name='Terminal', target_id=target.id, target_version=1, target_origin=target.normalized_origin, status='PASSED', created_by=operator.id, created_at=old, completed_at=old)
  active = AutomatedRun(run_key='S14-ACTIVE', name='Active', target_id=target.id, target_version=1, target_origin=target.normalized_origin, status='RUNNING', created_by=operator.id, created_at=old)
  db.add_all([terminal, active]); db.flush()
  terminal_path = config.artifact_root / 'terminal.json'
  active_path = config.artifact_root / 'active.json'
  terminal_path.write_text('{}', encoding='utf-8'); active_path.write_text('{}', encoding='utf-8')
  db.add_all([
    ExecutionArtifact(run_id=terminal.id, artifact_type='SUMMARY', original_filename='terminal.json', stored_filename='s14-terminal.json', relative_path='stage10_artifacts/terminal.json', mime_type='application/json', size_bytes=2, sha256='a' * 64, created_at=old),
    ExecutionArtifact(run_id=active.id, artifact_type='SUMMARY', original_filename='active.json', stored_filename='s14-active.json', relative_path='stage10_artifacts/active.json', mime_type='application/json', size_bytes=2, sha256='b' * 64, created_at=old),
  ])
  db.commit()
  history_before = db.scalar(select(func.count(PasswordHistory.id)))
  preview = cleanup_retention(db, dry_run=True, config=config)
  assert preview['candidate_files'] == 1
  assert terminal_path.is_file() and active_path.is_file()
  with pytest.raises(ValueError, match='confirmation'):
    cleanup_retention(db, dry_run=False, config=config)
  applied = cleanup_retention(db, dry_run=False, confirmation=CONFIRMATION, config=config)
  db.commit()
  assert applied['deleted_files'] == 1
  assert not terminal_path.exists() and active_path.is_file()
  assert db.scalar(select(func.count(ExecutionArtifact.id))) == 2
  assert db.scalar(select(func.count(PasswordHistory.id))) == history_before
  assert db.scalar(select(func.count(AuditEvent.id))) >= 2


def test_logging_and_health_are_secret_and_path_sanitized(client):
  import logging
  record = logging.LogRecord('stage14', logging.ERROR, __file__, 1, 'password=Alpha token:Beta Authorization=Bearer-Gamma cookie=session-id', (), None)
  payload = SafeJsonFormatter().format(record)
  for value in ('Alpha', 'Beta', 'Bearer-Gamma', 'session-id'):
    assert value not in payload
  response = client.get('/api/system/health')
  assert response.status_code == 200
  body = json.dumps(response.json()).lower()
  assert response.json()['production_execution_enabled'] is False
  assert response.json()['database']['ready'] is True
  for forbidden in ('d:\\', str(PROJECT_ROOT).lower(), 'password_hash', 'token', 'cookie', 'traceback'):
    assert forbidden not in body


def test_start_stop_and_port_conflict_scripts_are_fail_safe():
  scripts = PROJECT_ROOT / 'scripts'
  combined = '\n'.join((scripts / name).read_text(encoding='utf-8') for name in ('start_backend.ps1', 'start_frontend.ps1', 'start_worker.ps1', 'stop_local_system.ps1', 'lib/AutoQa.Runtime.ps1'))
  assert 'Get-NetTCPConnection' in combined
  assert 'Test-AutoQaOwnedProcess' in combined
  assert 'start_time_utc' in combined and 'expected_marker' in combined
  assert 'create_local_operator' not in combined.lower()
  assert 'password' not in '\n'.join((scripts / name).read_text(encoding='utf-8').lower() for name in ('start_backend.ps1', 'start_frontend.ps1', 'start_worker.ps1'))
  with socket.socket() as listener:
    listener.bind(('127.0.0.1', 0)); listener.listen()
    port = listener.getsockname()[1]
    command = f". '{scripts / 'lib/AutoQa.Runtime.ps1'}'; try {{ Assert-AutoQaPortAvailable -Port {port}; exit 0 }} catch {{ exit 7 }}"
    result = subprocess.run(['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-Command', command], check=False, capture_output=True, text=True, timeout=20)
  assert result.returncode == 7


def test_release_package_excludes_runtime_data_and_has_valid_checksums():
  result = subprocess.run(['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', str(PROJECT_ROOT / 'scripts' / 'build_release.ps1')], cwd=PROJECT_ROOT, check=True, capture_output=True, text=True, timeout=120)
  package = sorted((PROJECT_ROOT / 'release' / 'stage14').glob('*/iFive-AutoQA'))[-1]
  assert package.as_posix() in result.stdout.replace('\\', '/')
  files = [path for path in package.rglob('*') if path.is_file()]
  forbidden_parts = {'.venv', 'node_modules', 'test-results', 'playwright-report', 'runtime', 'backups', 'logs', 'pids', 'local-ai'}
  assert not any(path.relative_to(package).parts[0] in forbidden_parts for path in files)
  assert not any(path.suffix.lower() in {'.db', '.sqlite', '.sqlite3', '.log'} or path.name == '.env' for path in files)
  checksums = (package / 'SHA256SUMS.txt').read_text(encoding='ascii').splitlines()
  assert checksums and (package / 'release-manifest.json').is_file()
  import hashlib
  for line in checksums:
    digest, relative = line.split('  ', 1)
    assert hashlib.sha256((package / relative).read_bytes()).hexdigest() == digest


def test_no_default_admin_is_created(db):
  assert db.scalar(select(func.count(Operator.id)).where(Operator.role == 'ADMIN', Operator.is_active.is_(True))) == 0
