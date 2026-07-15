import shutil
import socket
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlparse

from sqlalchemy import inspect, select, text
from sqlalchemy.orm import Session

from app.config import PROJECT_ROOT, Settings, settings
from app.database import Base
from app.models.automated_execution import ExecutionJob, ExecutionWorker


def _directory_writable(path: Path) -> bool:
  try:
    path.mkdir(parents=True, exist_ok=True)
    probe = path / '.autoqa-health-probe'
    probe.write_bytes(b'')
    probe.unlink()
    return True
  except OSError:
    return False


def _frontend_available(url: str) -> bool:
  parsed = urlparse(url)
  if parsed.hostname not in {'127.0.0.1', 'localhost', '::1'}:
    return False
  try:
    with socket.create_connection((parsed.hostname, parsed.port or (443 if parsed.scheme == 'https' else 80)), timeout=0.15):
      return True
  except OSError:
    return False


def _chromium_available() -> tuple[bool, bool]:
  playwright = PROJECT_ROOT / 'qa' / 'node_modules' / '.bin' / 'playwright.cmd'
  common = [
    Path.home() / 'AppData' / 'Local' / 'Google' / 'Chrome' / 'Application' / 'chrome.exe',
    Path('C:/Program Files/Google/Chrome/Application/chrome.exe'),
    Path('C:/Program Files (x86)/Google/Chrome/Application/chrome.exe'),
  ]
  cache = Path.home() / 'AppData' / 'Local' / 'ms-playwright'
  try:
    cached = cache.is_dir() and any(path.name.startswith('chromium') for path in cache.iterdir())
  except OSError:
    cached = False
  return playwright.is_file(), cached or any(path.is_file() for path in common)


def health_snapshot(db: Session, config: Settings = settings) -> dict:
  database_ready = False
  tables_ready = False
  immutable_trigger_count = 0
  try:
    database_ready = db.execute(text('SELECT 1')).scalar_one() == 1
    inspector = inspect(db.bind)
    actual_tables = set(inspector.get_table_names())
    required_tables = set(Base.metadata.tables)
    tables_ready = required_tables <= actual_tables
    if db.bind and db.bind.dialect.name == 'sqlite':
      immutable_trigger_count = int(db.execute(text("SELECT COUNT(*) FROM sqlite_master WHERE type='trigger' AND name LIKE '%immutable%' OR type='trigger' AND name LIKE '%append_only%' OR type='trigger' AND name LIKE 'audit_events_%' ")).scalar() or 0)
  except Exception:
    database_ready = False
  directory_access = {
    'execution_artifacts': _directory_writable(config.artifact_root),
    'evidence': _directory_writable(config.evidence_root),
    'report_exports': _directory_writable(config.export_root),
    'runtime': _directory_writable(config.runtime_root),
    'backups': _directory_writable(config.backup_root),
  }
  now = datetime.utcnow()
  heartbeat_cutoff = now - timedelta(seconds=config.execution_job_lease_seconds * 2)
  active_workers = len(list(db.scalars(select(ExecutionWorker.id).where(ExecutionWorker.heartbeat_at >= heartbeat_cutoff)))) if database_ready else 0
  queue = {'queued': 0, 'running': 0, 'terminal': 0}
  if database_ready:
    statuses = list(db.scalars(select(ExecutionJob.status)))
    queue = {
      'queued': sum(status == 'QUEUED' for status in statuses),
      'running': sum(status == 'RUNNING' for status in statuses),
      'terminal': sum(status not in {'QUEUED', 'RUNNING'} for status in statuses),
    }
  playwright_installed, chromium_available = _chromium_available()
  disk = shutil.disk_usage(config.data_root)
  disk_free_mb = disk.free // (1024 * 1024)
  critical_ready = database_ready and tables_ready and all(directory_access.values())
  return {
    'status': 'ok' if critical_ready else 'degraded',
    'environment': config.app_env,
    'safe_mode': config.safe_mode,
    'debug': config.debug,
    'production_execution_enabled': False,
    'real_target_execution_enabled': config.allow_real_target_execution,
    'tls_verification_enabled': config.tls_verify,
    'database': {'ready': database_ready, 'migrations_current': tables_ready, 'immutable_triggers_installed': immutable_trigger_count > 0},
    'storage': directory_access,
    'worker': {'active_count': active_workers, 'heartbeat_ok': active_workers > 0},
    'queue': queue,
    'frontend': {'available': _frontend_available(config.frontend_url)},
    'disk': {'warning': disk_free_mb < config.disk_warning_mb, 'free_mb': disk_free_mb},
    'playwright': {'installed': playwright_installed, 'chromium_available': chromium_available},
  }
