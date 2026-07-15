import json
import logging
import re
from contextvars import ContextVar
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler

from app.config import settings


correlation_id_var: ContextVar[str] = ContextVar('autoqa_correlation_id', default='')
SECRET_PATTERN = re.compile(
  r'(?i)(authorization|proxy-authorization|password|passwd|token|cookie|csrf|api[_-]?key|secret|browser[_-]?storage)'
  r'(\s*[=:]\s*|\s+)([^\s,;]+)'
)
BEARER_PATTERN = re.compile(r'(?i)\bbearer\s+[a-z0-9._~+/-]+=*')


def redact_log_value(value: object) -> str:
  text = str(value)
  text = BEARER_PATTERN.sub('Bearer [REDACTED]', text)
  return SECRET_PATTERN.sub(lambda match: f'{match.group(1)}{match.group(2)}[REDACTED]', text)


class SafeJsonFormatter(logging.Formatter):
  def format(self, record: logging.LogRecord) -> str:
    payload = {
      'timestamp': datetime.now(timezone.utc).isoformat(),
      'level': record.levelname,
      'logger': record.name,
      'category': getattr(record, 'category', 'APPLICATION'),
      'correlation_id': getattr(record, 'correlation_id', None) or correlation_id_var.get() or None,
      'message': redact_log_value(record.getMessage())[:2000],
    }
    if record.exc_info:
      payload['error'] = record.exc_info[0].__name__ if record.exc_info[0] else 'Exception'
    return json.dumps(payload, sort_keys=True, separators=(',', ':'), ensure_ascii=True)


def configure_logging() -> None:
  settings.log_root.mkdir(parents=True, exist_ok=True)
  handler = RotatingFileHandler(
    settings.log_root / 'autoqa.jsonl',
    maxBytes=settings.log_max_bytes,
    backupCount=settings.log_backup_count,
    encoding='utf-8',
  )
  handler.setFormatter(SafeJsonFormatter())
  root = logging.getLogger()
  for existing in list(root.handlers):
    if getattr(existing, '_autoqa_handler', False):
      root.removeHandler(existing)
      existing.close()
  handler._autoqa_handler = True  # type: ignore[attr-defined]
  root.addHandler(handler)
  root.setLevel(logging.DEBUG if settings.debug else logging.INFO)
  logging.getLogger('httpx').setLevel(logging.WARNING)
  logging.getLogger('uvicorn.access').setLevel(logging.WARNING)
