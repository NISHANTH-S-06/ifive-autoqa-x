from alembic import command

from app.config import settings
from app.migration_config import make_alembic_config
from app.migration_safety import assert_database_at_head


def run() -> None:
  settings.prepare_directories()
  command.upgrade(make_alembic_config(settings.database_url, allow_active=True), 'head')
  revision = assert_database_at_head(settings.database_url, allow_active=True)
  print(f'AutoQA Alembic migrations completed safely at {revision}.')


if __name__ == '__main__':
  run()
