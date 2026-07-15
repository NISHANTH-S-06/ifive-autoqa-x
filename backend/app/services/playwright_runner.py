import json
import os
import re
import subprocess
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Callable

from sqlalchemy.orm import Session

from app.config import settings
from app.database import SessionLocal
from app.models.test_run import TestRun
from app.repositories.result_repository import ResultRepository
from app.repositories.run_repository import RunRepository
from app.schemas.test_run import TestRunStatus
from app.services.suite_registry import get_allowed_suite
from app.services.audit_service import append_event

PROJECT_ROOT = Path(__file__).resolve().parents[3]
QA_ROOT = PROJECT_ROOT / 'qa'
PLAYWRIGHT_EXECUTABLE = QA_ROOT / 'node_modules' / '.bin' / 'playwright.cmd'
RUNS_ROOT = settings.qa_runs_root
MAX_LOG_BYTES = 1_000_000
SECRET_PATTERN = re.compile(r'(?i)(password|token|secret|authorization)(\s*[:=]\s*)([^\s,;]+)')


class RunnerValidationError(ValueError):
  pass


def sanitize_run_code(run_code: str) -> str:
  if not re.fullmatch(r'[A-Za-z0-9_-]{1,64}', run_code):
    raise RunnerValidationError('Invalid run code.')
  return run_code


def redact_secrets(value: str) -> str:
  return SECRET_PATTERN.sub(r'\1\2[REDACTED]', value)


def parse_playwright_json(path: Path) -> list[dict]:
  if not path.is_file():
    return []
  payload = json.loads(path.read_text(encoding='utf-8'))
  parsed: list[dict] = []

  def walk(suites: list[dict], inherited_file: str = '') -> None:
    for suite in suites:
      test_file = suite.get('file') or inherited_file
      for spec in suite.get('specs', []):
        for test in spec.get('tests', []):
          results = test.get('results', [])
          result = results[-1] if results else {}
          raw_status = result.get('status', 'failed')
          status = {'passed': 'PASSED', 'failed': 'FAILED', 'skipped': 'SKIPPED', 'timedOut': 'TIMED_OUT'}.get(raw_status, 'FAILED')
          error = result.get('error') or {}
          parsed.append({
            'test_name': spec.get('title', 'Unnamed test'),
            'test_file': test_file or 'unknown',
            'status': status,
            'duration_seconds': round((result.get('duration') or 0) / 1000, 3),
            'error_message': (error.get('message') or None),
          })
      walk(suite.get('suites', []), test_file)

  walk(payload.get('suites', []))
  return parsed


class PlaywrightRunner:
  def __init__(self, session_factory: Callable[[], Session] = SessionLocal):
    self.session_factory = session_factory
    self._lock = threading.Lock()
    self._processes: dict[int, subprocess.Popen] = {}
    self._threads: dict[int, threading.Thread] = {}

  def is_active(self, run_id: int) -> bool:
    with self._lock:
      return run_id in self._processes or (run_id in self._threads and self._threads[run_id].is_alive())

  def validate_run(self, run: TestRun) -> None:
    self._validate(run)

  def start(self, run_id: int) -> None:
    with self._lock:
      if any(thread.is_alive() for thread in self._threads.values()):
        raise RunnerValidationError('Another local test run is already executing.')
      thread = threading.Thread(target=self._execute, args=(run_id,), daemon=True, name=f'autoqa-run-{run_id}')
      self._threads[run_id] = thread
      thread.start()

  def cancel(self, run_id: int) -> bool:
    with self._lock:
      process = self._processes.get(run_id)
    if process and process.poll() is None:
      self._terminate(process)
      return True
    return False

  def _validate(self, run: TestRun) -> str:
    suite = get_allowed_suite(run.suite_name)
    if run.project.product_code != 'AUTOQA' or run.environment != 'local':
      raise RunnerValidationError('Only local AutoQA suites can be executed in Stage 4.')
    if suite is None:
      raise RunnerValidationError('Test suite is not approved for local execution.')
    if not PLAYWRIGHT_EXECUTABLE.is_file():
      raise RunnerValidationError('Local Playwright executable is missing.')
    if not QA_ROOT.is_dir():
      raise RunnerValidationError('QA working directory is missing.')
    return suite.test_file

  def _execute(self, run_id: int) -> None:
    started = time.monotonic()
    run_dir: Path | None = None
    process: subprocess.Popen | None = None
    try:
      with self.session_factory() as db:
        repository = RunRepository(db)
        run = repository.get(run_id)
        if run is None or run.status != TestRunStatus.APPROVED.value:
          raise RunnerValidationError('Run approval is required before execution.')
        test_file = self._validate(run)
        run_dir = RUNS_ROOT / sanitize_run_code(run.run_code)
        if run_dir.exists():
          raise RunnerValidationError('Run artifact directory already exists.')
        for folder in ('html', 'results', 'screenshots', 'traces', 'videos', 'logs'):
          (run_dir / folder).mkdir(parents=True, exist_ok=False)

        json_path = run_dir / 'results' / 'results.json'
        stdout_path = run_dir / 'logs' / 'stdout.log'
        stderr_path = run_dir / 'logs' / 'stderr.log'
        env = os.environ.copy()
        env.update({
          'AUTOQA_RUN_CODE': run.run_code,
          'AUTOQA_OUTPUT_DIR': str(run_dir / 'traces'),
          'PLAYWRIGHT_HTML_OUTPUT_DIR': str(run_dir / 'html'),
          'PLAYWRIGHT_JSON_OUTPUT_NAME': str(json_path),
          'AUTOQA_QA_BASE_URL': 'http://127.0.0.1:5173',
        })
        run.status = TestRunStatus.RUNNING.value
        run.started_at = datetime.utcnow()
        run.result_json_path = self._relative(json_path)
        run.html_report_path = self._relative(run_dir / 'html' / 'index.html')
        run.stdout_log_path = self._relative(stdout_path)
        run.stderr_log_path = self._relative(stderr_path)
        db.commit()

        command = [str(PLAYWRIGHT_EXECUTABLE), 'test', test_file, '--project=chromium']
        with stdout_path.open('w', encoding='utf-8') as stdout, stderr_path.open('w', encoding='utf-8') as stderr:
          process = subprocess.Popen(command, cwd=QA_ROOT, env=env, stdout=stdout, stderr=stderr, shell=False)
          with self._lock:
            self._processes[run_id] = process
          try:
            exit_code = process.wait(timeout=settings.run_timeout_seconds)
          except subprocess.TimeoutExpired:
            self._terminate(process)
            self._finish(run_id, run_dir, None, TestRunStatus.FAILED, 'Test execution exceeded the configured timeout.', started, audit_action='TEST_RUN_TIMEOUT')
            return

        with self.session_factory() as status_db:
          current = RunRepository(status_db).get(run_id)
          if current and current.status == TestRunStatus.CANCELLED.value:
            self._persist_artifacts(status_db, current, run_dir)
            status_db.commit()
            return
        results = parse_playwright_json(json_path)
        failed = sum(item['status'] in ('FAILED', 'TIMED_OUT') for item in results)
        final = TestRunStatus.PASSED if exit_code == 0 and failed == 0 else TestRunStatus.FAILED
        error = None if final == TestRunStatus.PASSED else 'Local Playwright execution reported test failures.'
        self._finish(run_id, run_dir, exit_code, final, error, started, results, 'TEST_RUN_EXECUTION_COMPLETED' if final == TestRunStatus.PASSED else 'TEST_RUN_EXECUTION_FAILED')
    except Exception as exc:
      if run_dir is not None:
        self._finish(run_id, run_dir, process.poll() if process else None, TestRunStatus.FAILED, str(exc), started)
      else:
        with self.session_factory() as db:
          run = RunRepository(db).get(run_id)
          if run and run.status not in (TestRunStatus.CANCELLED.value, TestRunStatus.PASSED.value, TestRunStatus.FAILED.value):
            RunRepository(db).set_status(run, TestRunStatus.FAILED, error_summary=str(exc), completed_at=datetime.utcnow())
    finally:
      with self._lock:
        self._processes.pop(run_id, None)
        self._threads.pop(run_id, None)

  def _finish(self, run_id: int, run_dir: Path, exit_code: int | None, status: TestRunStatus, error: str | None, started: float, results: list[dict] | None = None, audit_action: str | None = None) -> None:
    with self.session_factory() as db:
      run = RunRepository(db).get(run_id)
      if run is None or run.status == TestRunStatus.CANCELLED.value:
        return
      records = ResultRepository(db).replace_results(run_id, results or [])
      run.total_tests = len(records)
      run.passed_tests = sum(item.status == 'PASSED' for item in records)
      run.failed_tests = sum(item.status in ('FAILED', 'TIMED_OUT') for item in records)
      run.skipped_tests = sum(item.status == 'SKIPPED' for item in records)
      run.duration_seconds = round(time.monotonic() - started, 3)
      run.exit_code = exit_code
      run.status = status.value
      run.error_summary = error[:1000] if error else None
      run.completed_at = datetime.utcnow()
      self._persist_artifacts(db, run, run_dir)
      append_event(db, audit_action or ('TEST_RUN_EXECUTION_COMPLETED' if status == TestRunStatus.PASSED else 'TEST_RUN_EXECUTION_FAILED'), 'SUCCESS' if status == TestRunStatus.PASSED else 'FAILED', actor_type='SYSTEM', resource_type='TEST_RUN', resource_id=str(run.id), metadata={'status': status.value, 'exit_code': exit_code})
      db.commit()

  def _persist_artifacts(self, db: Session, run: TestRun, run_dir: Path) -> None:
    existing = {item.relative_path for item in ResultRepository(db).evidence_by_run(run.id)}
    types = {'.png': 'SCREENSHOT', '.zip': 'TRACE', '.webm': 'VIDEO'}
    items = []
    fixed = [(run_dir / 'html' / 'index.html', 'HTML_REPORT'), (run_dir / 'results' / 'results.json', 'JSON_RESULT'), (run_dir / 'logs' / 'stdout.log', 'STDOUT'), (run_dir / 'logs' / 'stderr.log', 'STDERR')]
    discovered = [(path, types[path.suffix.lower()]) for path in run_dir.rglob('*') if path.is_file() and path.suffix.lower() in types]
    for path, evidence_type in fixed + discovered:
      if not path.is_file(): continue
      if evidence_type in ('STDOUT', 'STDERR'):
        content = redact_secrets(path.read_text(encoding='utf-8', errors='replace'))[:MAX_LOG_BYTES]
        path.write_text(content, encoding='utf-8')
      relative = self._relative(path)
      if relative not in existing:
        items.append({'evidence_type': evidence_type, 'relative_path': relative, 'file_size_bytes': path.stat().st_size})
    ResultRepository(db).add_evidence(run.id, items)

  @staticmethod
  def _relative(path: Path) -> str:
    return path.resolve().relative_to(PROJECT_ROOT.resolve()).as_posix()

  @staticmethod
  def _terminate(process: subprocess.Popen) -> None:
    if os.name == 'nt':
      subprocess.run(['taskkill', '/PID', str(process.pid), '/T', '/F'], shell=False, capture_output=True, timeout=15, check=False)
    else:
      process.terminate()
    try:
      process.wait(timeout=10)
    except subprocess.TimeoutExpired:
      process.kill()


runner = PlaywrightRunner()


def get_runner() -> PlaywrightRunner:
  return runner
