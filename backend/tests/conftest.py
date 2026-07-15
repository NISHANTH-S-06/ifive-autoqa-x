import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.auth import AuthContext, get_auth_context, require_csrf
from app.models.operator import Operator
from app.models.operator_session import OperatorSession
from app.services.password_service import hash_password
from app.migrations import install_audit_protection
from datetime import datetime, timedelta

FIXTURE_HASH = hash_password('Fixture!Admin123')


@pytest.fixture
def db(tmp_path):
  engine = create_engine(f'sqlite:///{tmp_path / "test.db"}', connect_args={'check_same_thread': False})
  Base.metadata.create_all(engine)
  install_audit_protection(engine)
  session = sessionmaker(bind=engine, autocommit=False, autoflush=False)()
  try:
    yield session
  finally:
    session.close()
    engine.dispose()


@pytest.fixture
def client(db):
  def override_db():
    yield db

  app.dependency_overrides[get_db] = override_db
  operator = Operator(username='fixture-admin', display_name='Fixture Admin', password_hash=FIXTURE_HASH, role='ADMIN', is_active=True)
  db.add(operator); db.flush()
  session = OperatorSession(operator_id=operator.id, token_hash='fixture', csrf_hash='fixture', expires_at=datetime.utcnow() + timedelta(hours=1), last_seen_at=datetime.utcnow())
  db.add(session); db.commit(); context = AuthContext(operator, session)
  app.dependency_overrides[get_auth_context] = lambda: context
  app.dependency_overrides[require_csrf] = lambda: context
  with TestClient(app) as test_client:
    yield test_client
  app.dependency_overrides.clear()


@pytest.fixture
def auth_client(db):
  def override_db(): yield db
  app.dependency_overrides[get_db] = override_db
  with TestClient(app) as test_client: yield test_client
  app.dependency_overrides.clear()


@pytest.fixture
def project_payload():
  return {
    'name': 'Local Test Project',
    'product_code': 'AUTOQA',
    'description': 'Temporary isolated test data.',
    'environment': 'local',
  }
