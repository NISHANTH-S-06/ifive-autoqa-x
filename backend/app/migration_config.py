from __future__ import annotations

import os
from pathlib import Path

from alembic.config import Config
from sqlalchemy.engine import URL, make_url

from app.config import BACKEND_ROOT, settings


ALEMBIC_INI = BACKEND_ROOT / 'alembic.ini'
MIGRATION_URL_ENV = 'AUTOQA_ALEMBIC_DATABASE_URL'
ALLOW_ACTIVE_ENV = 'AUTOQA_ALEMBIC_ALLOW_ACTIVE_DATABASE'


def _sqlite_path(url: URL) -> Path | None:
  if url.get_backend_name() != 'sqlite' or not url.database or url.database == ':memory:':
    return None
  path = Path(url.database)
  if not path.is_absolute():
    path = BACKEND_ROOT / path
  return path.resolve()


def sqlite_path_for_url(raw_url: str) -> Path:
  path = _sqlite_path(make_url(raw_url))
  if path is None:
    raise RuntimeError('This migration safety operation requires a file-backed SQLite URL.')
  return path


def validate_migration_url(raw_url: str, *, allow_active: bool = False) -> str:
  value = raw_url.strip()
  if not value:
    raise RuntimeError(f'{MIGRATION_URL_ENV} is required; Alembic never defaults to the active database.')
  url = make_url(value)
  if url.get_backend_name() not in {'sqlite', 'postgresql'}:
    raise RuntimeError('Alembic supports only SQLite or PostgreSQL database URLs.')
  target_path = _sqlite_path(url)
  if target_path is not None and target_path == settings.database_path and not allow_active:
    raise RuntimeError(
      'Alembic refused the active application database. Rehearse on a copy first; '
      f'set {ALLOW_ACTIVE_ENV}=true only in a separately approved active-database operation.'
    )
  return value


def configured_migration_url(configured_url: str | None = None, *, allow_active: bool = False) -> str:
  raw_url = (configured_url or '').strip() or os.getenv(MIGRATION_URL_ENV, '')
  environment_allows_active = os.getenv(ALLOW_ACTIVE_ENV, '').strip().lower() in {'1', 'true', 'yes', 'on'}
  return validate_migration_url(raw_url, allow_active=allow_active or environment_allows_active)


def make_alembic_config(database_url: str, *, allow_active: bool = False) -> Config:
  validated = validate_migration_url(database_url, allow_active=allow_active)
  config = Config(str(ALEMBIC_INI))
  config.set_main_option('sqlalchemy.url', validated.replace('%', '%%'))
  config.attributes['allow_active_database'] = allow_active
  return config
