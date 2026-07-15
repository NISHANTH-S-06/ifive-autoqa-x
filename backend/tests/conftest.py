import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, select, text
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.auth import AuthContext, get_auth_context, require_csrf
from app.models.operator import Operator
from app.models.operator_session import OperatorSession
from app.models.project import Project
from app.models.project_membership import ProjectMember
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
  @event.listens_for(session, 'before_flush')
  def scope_legacy_test_rows(current_session, _flush_context, _instances):
    # Pre-B2B tests construct records directly. Keep those fixtures explicit
    # to one isolated project without changing production fallback behavior.
    pending = [item for item in current_session.new if not isinstance(item, (Project, ProjectMember))]
    compatibility_project_id = current_session.scalar(select(Project.id).order_by(Project.id).limit(1))
    if compatibility_project_id is None and any(hasattr(item, 'project_id') or hasattr(item, 'access_project_id') for item in pending):
      result = current_session.connection().execute(text(
        "INSERT INTO projects (name, product_code, description, environment, is_active, created_at, updated_at) "
        "VALUES ('Legacy direct-fixture project', 'AUTOQA', 'Test-only scope for pre-B2B direct fixtures.', 'local', 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
      ))
      compatibility_project_id = result.lastrowid
    for item in pending:
      if compatibility_project_id is None:
        continue
      if hasattr(item, 'access_project_id') and getattr(item, 'access_project_id') is None:
        item.access_project_id = compatibility_project_id
      table = getattr(item, '__tablename__', '')
      if hasattr(item, 'project_id') and getattr(item, 'project_id') is None and table not in {
        'test_projects', 'test_modules', 'managed_test_suites', 'managed_test_cases',
        'manual_test_runs', 'project_backfill_reports',
      }:
        item.project_id = compatibility_project_id

  @event.listens_for(session, 'after_flush')
  def grant_legacy_test_memberships(current_session, _flush_context):
    # Existing stage tests predate project membership. Grant only their local
    # synthetic operators to local synthetic projects; isolation tests create
    # separate projects and memberships explicitly.
    if any(isinstance(item, Operator) for item in current_session.new):
      current_session.connection().execute(text(
        "INSERT OR IGNORE INTO project_members "
        "(project_id, operator_id, role, status, created_by, joined_at, created_at, updated_at) "
        "SELECT p.id, o.id, CASE o.role WHEN 'ADMIN' THEN 'ADMIN' WHEN 'APPROVER' THEN 'APPROVER' "
        "WHEN 'VIEWER' THEN 'VIEWER' ELSE 'TESTER' END, 'ACTIVE', o.id, "
        "CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP FROM projects p, operators o "
        "WHERE p.name NOT LIKE 'Isolation %' AND o.is_active = 1"
      ))
    for project in (item for item in current_session.new if isinstance(item, Project) and not item.name.startswith('Isolation ')):
      current_session.connection().execute(text(
        "INSERT OR IGNORE INTO project_members "
        "(project_id, operator_id, role, status, created_by, joined_at, created_at, updated_at) "
        "SELECT :project_id, o.id, CASE o.role WHEN 'ADMIN' THEN 'ADMIN' WHEN 'APPROVER' THEN 'APPROVER' "
        "WHEN 'VIEWER' THEN 'VIEWER' ELSE 'TESTER' END, 'ACTIVE', o.id, "
        "CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP FROM operators o WHERE o.is_active = 1"
      ), {'project_id': project.id})
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
  # Do not enter TestClient's application lifespan here: the production
  # lifespan owns the active database engine, while these tests override the
  # request session with the isolated tmp_path database above.
  test_client = TestClient(app)
  try:
    yield test_client
  finally:
    test_client.close()
  app.dependency_overrides.clear()


@pytest.fixture
def auth_client(db):
  compatibility_project = Project(name='Legacy test compatibility project', product_code='AUTOQA', description='Scoped compatibility fixture.', environment='local', is_active=True)
  db.add(compatibility_project); db.commit()
  def override_db(): yield db
  app.dependency_overrides[get_db] = override_db
  test_client = TestClient(app)
  try:
    yield test_client
  finally:
    test_client.close()
  app.dependency_overrides.clear()


@pytest.fixture
def project_payload():
  return {
    'name': 'Local Test Project',
    'product_code': 'AUTOQA',
    'description': 'Temporary isolated test data.',
    'environment': 'local',
  }
