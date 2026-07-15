from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings


class Base(DeclarativeBase):
  pass


if settings.database_url.startswith('sqlite:///'):
  database_path = settings.database_path
  if database_path != Path(':memory:'):
    database_path.parent.mkdir(parents=True, exist_ok=True)

connect_args = {'check_same_thread': False, 'timeout': 30} if settings.database_url.startswith('sqlite') else {}

engine_url = settings.database_url
if settings.database_url.startswith('sqlite:///') and settings.database_path != Path(':memory:'):
  engine_url = f'sqlite:///{settings.database_path.as_posix()}'
engine = create_engine(engine_url, connect_args=connect_args, pool_pre_ping=True)


if settings.database_url.startswith('sqlite'):
  @event.listens_for(engine, 'connect')
  def configure_sqlite(dbapi_connection, _connection_record) -> None:
    cursor = dbapi_connection.cursor()
    try:
      cursor.execute('PRAGMA foreign_keys=ON')
      cursor.execute('PRAGMA busy_timeout=30000')
      if settings.database_path != Path(':memory:'):
        cursor.execute('PRAGMA journal_mode=WAL')
        cursor.execute('PRAGMA synchronous=NORMAL')
    finally:
      cursor.close()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()
