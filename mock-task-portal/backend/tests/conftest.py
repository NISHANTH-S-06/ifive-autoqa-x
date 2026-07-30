"""pytest conftest for Mock Task Portal backend tests."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.auth import AuthContext, get_auth_context, hash_password
from app.database import Base, get_db
from app.main import app
from app.models.task import Task
from app.models.task_history import TaskHistory
from app.models.user import User, UserSession


def make_engine(tmp_path):
    return create_engine(
        f'sqlite:///{tmp_path / "test_portal.db"}',
        connect_args={'check_same_thread': False},
    )


@pytest.fixture
def db(tmp_path):
    eng = make_engine(tmp_path)
    Base.metadata.create_all(eng)
    SessionFactory = sessionmaker(bind=eng, autocommit=False, autoflush=False)
    session = SessionFactory()
    try:
        yield session
    finally:
        session.close()
        eng.dispose()


def _create_user(db: Session, username: str, role: str, password: str = 'Test@123') -> User:
    user = User(
        username=username,
        display_name=username.title(),
        role=role,
        password_hash=hash_password(password),
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(user)
    db.flush()
    return user


def _make_client(db: Session, user: User) -> TestClient:
    """Create a TestClient with the given user as the authenticated context.
    
    Each call produces an independent override mapping so multiple users
    can be used in the same test without stomping on each other.
    """
    def override_db():
        yield db

    def override_auth():
        return AuthContext(user)

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_auth_context] = override_auth
    return TestClient(app, raise_server_exceptions=True)


class MultiUserTestClients:
    """Container for multiple role clients that share a DB session."""

    def __init__(self, db: Session):
        self._db = db
        self._users: dict[str, User] = {}
        self._clients: dict[str, TestClient] = {}

    def _ensure_user(self, username: str, role: str) -> User:
        if username not in self._users:
            self._users[username] = _create_user(self._db, username, role)
            self._db.commit()
        return self._users[username]

    def get_client(self, username: str, role: str) -> tuple[TestClient, str]:
        """Return (client, username) that authenticates as the given user.
        
        Note: Since FastAPI TestClient uses app.dependency_overrides globally,
        only ONE user can be "active" at a time per test. Call get_client()
        again to switch the active user before making requests.
        """
        self._ensure_user(username, role)
        user = self._users[username]
        client = _make_client(self._db, user)
        return client, username

    def switch(self, username: str, role: str) -> tuple[TestClient, str]:
        """Switch the active auth user and return new client."""
        return self.get_client(username, role)


@pytest.fixture
def admin_client(db):
    user = _create_user(db, 'admin', 'SUPERADMIN')
    db.commit()
    client = _make_client(db, user)
    yield client, user.username
    app.dependency_overrides.clear()


@pytest.fixture
def dev_client(db):
    user = _create_user(db, 'dev1', 'DEVELOPER')
    db.commit()
    client = _make_client(db, user)
    yield client, user.username
    app.dependency_overrides.clear()


@pytest.fixture
def tester_client(db):
    user = _create_user(db, 'tester1', 'TESTER')
    db.commit()
    client = _make_client(db, user)
    yield client, user.username
    app.dependency_overrides.clear()


@pytest.fixture
def delivery_client(db):
    user = _create_user(db, 'delivery1', 'DELIVERY')
    db.commit()
    client = _make_client(db, user)
    yield client, user.username
    app.dependency_overrides.clear()


@pytest.fixture
def viewer_client(db):
    user = _create_user(db, 'viewer1', 'VIEWER')
    db.commit()
    client = _make_client(db, user)
    yield client, user.username
    app.dependency_overrides.clear()


@pytest.fixture
def multi_client(db):
    """Fixture for tests that need multiple users.
    
    Usage in test:
        def test_foo(multi_client):
            admin, admin_name = multi_client.switch('admin', 'SUPERADMIN')
            dev, dev_name = multi_client.switch('dev1', 'DEVELOPER')
            # Use admin first — MUST re-call switch() before each request group
    """
    clients = MultiUserTestClients(db)
    yield clients
    app.dependency_overrides.clear()


def make_task(db: Session, **kwargs) -> Task:
    defaults = dict(
        task_code='TEST-001',
        project_name='Demo ERP',
        module_name='HR Module',
        title='Test Task',
        status='CREATED',
        priority='MEDIUM',
        environment='local',
        revision=0,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    defaults.update(kwargs)
    task = Task(**defaults)
    db.add(task)
    db.flush()
    db.add(TaskHistory(
        task_id=task.id,
        previous_status=None,
        new_status=defaults['status'],
        changed_by='fixture',
        timestamp=datetime.utcnow(),
    ))
    db.commit()
    return task
