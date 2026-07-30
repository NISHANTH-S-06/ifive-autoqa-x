"""Backend tests for Alembic clean migration & seed idempotency."""
from __future__ import annotations

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.main import ALEMBIC_INI
from app.models import User
from app.seed import seed


def test_alembic_clean_migration(tmp_path):
    db_file = tmp_path / 'clean_migration.db'
    db_url = f'sqlite:///{db_file}'
    cfg = Config(str(ALEMBIC_INI))
    cfg.set_main_option('sqlalchemy.url', db_url.replace('%', '%%'))

    # Run migration head
    command.upgrade(cfg, 'head')

    eng = create_engine(db_url)
    Session = sessionmaker(bind=eng)
    session = Session()

    # Seed
    seed(session)
    admin = session.query(User).filter_by(username='demo_admin').first()
    assert admin is not None

    session.close()
    eng.dispose()


def test_seed_idempotency(db):
    count_before = db.query(User).count()
    # Run seed a second time
    seed(db)
    count_after = db.query(User).count()
    assert count_before == count_after
