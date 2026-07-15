from app import main as _model_registry
from app.config import settings
from app.database import Base, engine
from app.migrations import (
  install_audit_protection,
  migrate_stage4_schema,
  migrate_stage6_schema,
  migrate_stage8_schema,
  migrate_stage9_schema,
  migrate_stage10_schema,
  migrate_stage11_schema,
  migrate_stage12_schema,
  migrate_stage13_schema,
)


def run() -> None:
  settings.prepare_directories()
  for migration in (migrate_stage4_schema, migrate_stage6_schema, migrate_stage8_schema, migrate_stage9_schema, migrate_stage10_schema, migrate_stage11_schema, migrate_stage12_schema, migrate_stage13_schema):
    migration(engine)
  Base.metadata.create_all(bind=engine)
  install_audit_protection(engine)
  print('AutoQA database migrations completed safely.')


if __name__ == '__main__':
  run()

