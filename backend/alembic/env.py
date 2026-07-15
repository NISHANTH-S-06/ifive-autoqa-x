from __future__ import annotations

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.migration_config import configured_migration_url
from app.migration_metadata import get_migration_metadata


config = context.config
if config.config_file_name:
  fileConfig(config.config_file_name)

database_url = configured_migration_url(config.get_main_option('sqlalchemy.url'))
config.set_main_option('sqlalchemy.url', database_url.replace('%', '%%'))
target_metadata = get_migration_metadata()


def _context_options(connection=None) -> dict:
  dialect_name = connection.dialect.name if connection is not None else database_url.split(':', 1)[0].split('+', 1)[0]
  return {
    'connection': connection,
    'url': None if connection is not None else database_url,
    'target_metadata': target_metadata,
    'literal_binds': connection is None,
    'dialect_opts': {'paramstyle': 'named'},
    'render_as_batch': dialect_name == 'sqlite',
    'compare_type': True,
    'compare_server_default': True,
    'transaction_per_migration': True,
  }


def run_migrations_offline() -> None:
  context.configure(**_context_options())
  with context.begin_transaction():
    context.run_migrations()


def run_migrations_online() -> None:
  connectable = engine_from_config(
    config.get_section(config.config_ini_section, {}),
    prefix='sqlalchemy.',
    poolclass=pool.NullPool,
  )
  with connectable.connect() as connection:
    if connection.dialect.name == 'sqlite':
      connection.exec_driver_sql('PRAGMA foreign_keys=ON')
      connection.exec_driver_sql('PRAGMA busy_timeout=30000')
      # SQLAlchemy 2.x autobegins on the PRAGMA calls. End that setup
      # transaction so Alembic owns and commits its migration transaction.
      connection.commit()
    context.configure(**_context_options(connection))
    with context.begin_transaction():
      context.run_migrations()
  connectable.dispose()


if context.is_offline_mode():
  run_migrations_offline()
else:
  run_migrations_online()
