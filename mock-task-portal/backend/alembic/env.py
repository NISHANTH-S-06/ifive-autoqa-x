"""Alembic env.py for Mock Task Portal."""
from __future__ import annotations

import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import Base from the app so Alembic sees all models
from app.database import Base  # noqa: E402
import app.models.user  # noqa: F401
import app.models.task  # noqa: F401
import app.models.task_history  # noqa: F401

target_metadata = Base.metadata


def get_url() -> str:
    url = config.get_main_option('sqlalchemy.url', '')
    if url:
        return url
    db_path = os.environ.get('MOCK_PORTAL_DB', 'data/portal.db')
    return f'sqlite:///{db_path}'


def run_migrations_offline() -> None:
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={'paramstyle': 'named'},
        render_as_batch=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    url = get_url()
    configuration = config.get_section(config.config_ini_section, {})
    configuration['sqlalchemy.url'] = url
    connectable = engine_from_config(
        configuration,
        prefix='sqlalchemy.',
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
