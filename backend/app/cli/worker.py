import argparse
import signal
import time
import logging
from pathlib import Path

from app import main as _model_registry
from app.config import PROJECT_ROOT, settings
from app.database import SessionLocal
from app.logging_config import configure_logging
from app.services.automated_execution import execute_next_job, heartbeat


running = True


def _stop(*_) -> None:
  global running
  running = False


def run() -> None:
  parser = argparse.ArgumentParser(description='Run the single-concurrency local AutoQA execution worker.')
  parser.add_argument('--worker-key', default='local-release-worker')
  parser.add_argument('--runtime-marker', required=True)
  args = parser.parse_args()
  if Path(args.runtime_marker).resolve() != PROJECT_ROOT.resolve():
    raise SystemExit('Runtime marker does not match this AutoQA project.')
  settings.prepare_directories()
  configure_logging()
  logger = logging.getLogger('autoqa.worker')
  signal.signal(signal.SIGINT, _stop)
  signal.signal(signal.SIGTERM, _stop)
  while running:
    try:
      with SessionLocal() as db:
        heartbeat(db, args.worker_key)
        db.commit()
        run_item = execute_next_job(db, args.worker_key)
        db.commit()
    except Exception as exc:
      logger.error('worker cycle failed error_category=%s', type(exc).__name__, extra={'category': 'WORKER'})
      run_item = None
      time.sleep(2)
    if run_item is None:
      time.sleep(2)


if __name__ == '__main__':
  run()

