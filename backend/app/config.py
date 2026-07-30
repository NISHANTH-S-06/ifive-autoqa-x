import os
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlparse


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / 'backend'


def _get_bool(name: str, default: bool) -> bool:
  value = os.getenv(name)
  if value is None:
    return default
  normalized = value.strip().lower()
  if normalized not in {'1', 'true', 'yes', 'on', '0', 'false', 'no', 'off'}:
    raise RuntimeError(f'{name} must be true or false.')
  return normalized in {'1', 'true', 'yes', 'on'}


def _get_int(name: str, default: int, minimum: int, maximum: int) -> int:
  raw = os.getenv(name, str(default))
  try:
    value = int(raw)
  except ValueError:
    raise RuntimeError(f'{name} must be an integer.') from None
  if not minimum <= value <= maximum:
    raise RuntimeError(f'{name} must be between {minimum} and {maximum}.')
  return value


def _path(name: str, default: Path) -> Path:
  value = Path(os.getenv(name, str(default))).expanduser()
  if not value.is_absolute():
    value = (BACKEND_ROOT / value)
  return value.resolve()


def _csv(name: str, default: str) -> tuple[str, ...]:
  return tuple(item.strip() for item in os.getenv(name, default).split(',') if item.strip())


@dataclass(frozen=True)
class Settings:
  app_env: str = field(default_factory=lambda: os.getenv('APP_ENV', 'local'))
  debug: bool = field(default_factory=lambda: _get_bool('AUTOQA_DEBUG', False))
  safe_mode: bool = field(default_factory=lambda: _get_bool('AUTOQA_SAFE_MODE', True))
  allow_real_target_execution: bool = field(default_factory=lambda: _get_bool('AUTOQA_ALLOW_REAL_TARGET_EXECUTION', False))
  allow_production_execution: bool = field(default_factory=lambda: _get_bool('AUTOQA_ALLOW_PRODUCTION_EXECUTION', False))
  tls_verify: bool = field(default_factory=lambda: _get_bool('AUTOQA_TLS_VERIFY', True))
  data_root: Path = field(default_factory=lambda: _path('AUTOQA_DATA_ROOT', BACKEND_ROOT / 'data'))
  runtime_root: Path = field(default_factory=lambda: _path('AUTOQA_RUNTIME_ROOT', PROJECT_ROOT / 'runtime'))
  backup_root: Path = field(default_factory=lambda: _path('AUTOQA_BACKUP_ROOT', PROJECT_ROOT / 'runtime' / 'backups'))
  qa_runs_root: Path = field(default_factory=lambda: _path('AUTOQA_QA_RUNS_ROOT', PROJECT_ROOT / 'qa' / 'reports' / 'runs'))
  database_url: str = field(default_factory=lambda: os.getenv('DATABASE_URL', 'sqlite:///./data/autoqa.db'))
  frontend_url: str = field(default_factory=lambda: os.getenv('AUTOQA_FRONTEND_URL', 'http://127.0.0.1:5173'))
  mock_task_portal_url: str = field(default_factory=lambda: os.getenv('AUTOQA_MOCK_TASK_PORTAL_URL', 'http://127.0.0.1:8001'))
  demo_product_url: str = field(default_factory=lambda: os.getenv('AUTOQA_DEMO_PRODUCT_URL', 'http://127.0.0.1:5175'))
  backend_self_url: str = field(default_factory=lambda: os.getenv('AUTOQA_BACKEND_SELF_URL', 'http://127.0.0.1:8000'))
  allowed_environments: tuple[str, ...] = field(default_factory=lambda: _csv('AUTOQA_ALLOWED_ENVIRONMENTS', 'local,development,qa,staging'))
  blocked_actions: tuple[str, ...] = field(default_factory=lambda: _csv('AUTOQA_BLOCKED_ACTIONS', 'payment_execution,payroll_execution,record_deletion,approval_execution,iiot_machine_control'))
  run_timeout_seconds: int = field(default_factory=lambda: _get_int('AUTOQA_RUN_TIMEOUT_SECONDS', 900, 5, 3600))
  session_hours: int = field(default_factory=lambda: _get_int('AUTOQA_SESSION_HOURS', 8, 1, 168))
  password_max_age_days: int = field(default_factory=lambda: _get_int('AUTOQA_PASSWORD_MAX_AGE_DAYS', 0, 0, 3650))
  cookie_secure: bool = field(default_factory=lambda: _get_bool('AUTOQA_COOKIE_SECURE', False))
  target_max_probe_paths: int = field(default_factory=lambda: _get_int('AUTOQA_TARGET_MAX_PROBE_PATHS', 10, 1, 50))
  target_max_probe_path_length: int = field(default_factory=lambda: _get_int('AUTOQA_TARGET_MAX_PROBE_PATH_LENGTH', 500, 10, 2000))
  target_max_response_bytes: int = field(default_factory=lambda: _get_int('AUTOQA_TARGET_MAX_RESPONSE_BYTES', 65536, 1024, 1048576))
  target_max_redirects: int = field(default_factory=lambda: _get_int('AUTOQA_TARGET_MAX_REDIRECTS', 3, 0, 10))
  target_user_agent: str = field(default_factory=lambda: os.getenv('AUTOQA_TARGET_USER_AGENT', 'iFive-AutoQA-Stage9-ConnectionCheck/1.0'))
  execution_user_agent: str = field(default_factory=lambda: os.getenv('AUTOQA_EXECUTION_USER_AGENT', 'iFive-AutoQA-Stage10-ChromiumWorker/1.0'))
  execution_max_text_bytes: int = field(default_factory=lambda: _get_int('AUTOQA_EXECUTION_MAX_TEXT_BYTES', 65536, 1024, 1048576))
  execution_max_artifact_bytes_per_run: int = field(default_factory=lambda: _get_int('AUTOQA_EXECUTION_MAX_ARTIFACT_BYTES_PER_RUN', 10 * 1024 * 1024, 1024, 100 * 1024 * 1024))
  execution_job_lease_seconds: int = field(default_factory=lambda: _get_int('AUTOQA_EXECUTION_JOB_LEASE_SECONDS', 60, 15, 600))
  log_max_bytes: int = field(default_factory=lambda: _get_int('AUTOQA_LOG_MAX_BYTES', 5 * 1024 * 1024, 65536, 100 * 1024 * 1024))
  log_backup_count: int = field(default_factory=lambda: _get_int('AUTOQA_LOG_BACKUP_COUNT', 5, 1, 30))
  retention_artifact_days: int = field(default_factory=lambda: _get_int('AUTOQA_RETENTION_ARTIFACT_DAYS', 30, 1, 3650))
  retention_evidence_days: int = field(default_factory=lambda: _get_int('AUTOQA_RETENTION_EVIDENCE_DAYS', 90, 1, 3650))
  retention_export_days: int = field(default_factory=lambda: _get_int('AUTOQA_RETENTION_EXPORT_DAYS', 30, 1, 3650))
  retention_operational_days: int = field(default_factory=lambda: _get_int('AUTOQA_RETENTION_OPERATIONAL_DAYS', 30, 1, 3650))
  disk_warning_mb: int = field(default_factory=lambda: _get_int('AUTOQA_DISK_WARNING_MB', 1024, 64, 1048576))

  @property
  def database_path(self) -> Path:
    if not self.database_url.startswith('sqlite:///'):
      raise RuntimeError('Stage 14 local release supports SQLite DATABASE_URL values only.')
    raw = self.database_url.removeprefix('sqlite:///')
    if raw == ':memory:':
      return Path(':memory:')
    path = Path(raw)
    if not path.is_absolute():
      path = BACKEND_ROOT / path
    return path.resolve()

  @property
  def artifact_root(self) -> Path:
    return self.data_root / 'stage10_artifacts'

  @property
  def evidence_root(self) -> Path:
    return self.data_root / 'stage8_evidence'

  @property
  def export_root(self) -> Path:
    return self.data_root / 'stage13_exports'

  @property
  def log_root(self) -> Path:
    return self.runtime_root / 'logs'

  @property
  def pid_root(self) -> Path:
    return self.runtime_root / 'pids'

  @property
  def temp_root(self) -> Path:
    return self.runtime_root / 'tmp'

  def validate(self) -> None:
    errors: list[str] = []
    if self.app_env not in {'local', 'development', 'test', 'local-release'}:
      errors.append('APP_ENV must be local, development, test, or local-release.')
    if not self.safe_mode:
      errors.append('AUTOQA_SAFE_MODE must remain true.')
    if self.allow_production_execution:
      errors.append('AUTOQA_ALLOW_PRODUCTION_EXECUTION must remain false.')
    if not self.tls_verify:
      errors.append('AUTOQA_TLS_VERIFY must remain true.')
    if self.app_env == 'local-release' and self.debug:
      errors.append('AUTOQA_DEBUG must be false for local-release.')
    if self.app_env == 'local-release' and not self.cookie_secure:
      # Local HTTP is supported, but the setting must remain explicit in the release template.
      pass
    parsed_frontend = urlparse(self.frontend_url)
    if parsed_frontend.scheme not in {'http', 'https'} or parsed_frontend.hostname not in {'127.0.0.1', 'localhost', '::1'}:
      errors.append('AUTOQA_FRONTEND_URL must use a local loopback HTTP(S) URL.')
    try:
      database_path = self.database_path
      if database_path != Path(':memory:'):
        database_path.relative_to(self.data_root)
    except (RuntimeError, ValueError) as exc:
      errors.append(str(exc) if isinstance(exc, RuntimeError) else 'DATABASE_URL must resolve inside AUTOQA_DATA_ROOT.')
    source_roots = [BACKEND_ROOT / 'app', PROJECT_ROOT / 'frontend' / 'src', PROJECT_ROOT / 'qa' / 'tests', PROJECT_ROOT / 'scripts', PROJECT_ROOT / 'docs', PROJECT_ROOT / 'config']
    for label, path in {'runtime': self.runtime_root, 'backup': self.backup_root, 'qa_runs': self.qa_runs_root}.items():
      if path in {PROJECT_ROOT, BACKEND_ROOT, PROJECT_ROOT / 'frontend', PROJECT_ROOT / 'qa'} or any(path == root or root in path.parents for root in source_roots):
        errors.append(f'AUTOQA_{label.upper()}_ROOT must not be a source directory.')
    if self.backup_root == self.data_root or self.data_root in self.backup_root.parents:
      errors.append('AUTOQA_BACKUP_ROOT must be outside AUTOQA_DATA_ROOT.')
    if errors:
      raise RuntimeError('Invalid AutoQA environment configuration: ' + ' '.join(errors))

  @property
  def visual_baselines_root(self) -> Path:
    return self.data_root / 'visual_baselines'

  @property
  def visual_runs_root(self) -> Path:
    return self.data_root / 'visual_runs'

  def prepare_directories(self) -> None:
    self.validate()
    for path in (self.data_root, self.artifact_root, self.evidence_root, self.export_root, self.visual_baselines_root, self.visual_runs_root, self.qa_runs_root, self.runtime_root, self.log_root, self.pid_root, self.temp_root, self.backup_root):
      path.mkdir(parents=True, exist_ok=True)



settings = Settings()
