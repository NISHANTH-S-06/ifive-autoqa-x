"""SQLAlchemy database setup for Demo Product Website."""
from __future__ import annotations

import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

BACKEND_ROOT = Path(__file__).parent.parent
DATA_DIR = BACKEND_ROOT.parent / 'data'
DATA_DIR.mkdir(parents=True, exist_ok=True)

_DEFAULT_DB_PATH = str(DATA_DIR / 'demo_product.db')
DATABASE_URL = os.environ.get('DEMO_PRODUCT_DB_URL', f'sqlite:///{_DEFAULT_DB_PATH}')

engine = create_engine(
    DATABASE_URL,
    connect_args={'check_same_thread': False},
    echo=False,
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
