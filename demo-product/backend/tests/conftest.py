"""pytest conftest for Demo Product Website backend tests."""
from __future__ import annotations

from datetime import datetime
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session as DBSession

from app.auth import AuthContext, get_auth_context, hash_password
from app.database import Base, get_db
from app.main import app
from app.models import Department, DemoSetting, Employee, Product, User
from app.seed import seed


def make_engine(tmp_path):
    return create_engine(
        f'sqlite:///{tmp_path / "test_demo_product.db"}',
        connect_args={'check_same_thread': False},
    )


@pytest.fixture
def db(tmp_path):
    eng = make_engine(tmp_path)
    Base.metadata.create_all(eng)
    SessionFactory = sessionmaker(bind=eng, autocommit=False, autoflush=False)
    session = SessionFactory()
    seed(session)
    try:
        yield session
    finally:
        session.close()
        eng.dispose()


def _get_user(db: DBSession, username: str) -> User:
    return db.query(User).filter_by(username=username).first()


def _make_client(db: DBSession, user: User) -> TestClient:
    def override_db():
        yield db

    def override_auth():
        return AuthContext(user)

    from app.auth import get_optional_auth_context
    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_auth_context] = override_auth
    app.dependency_overrides[get_optional_auth_context] = override_auth
    return TestClient(app, raise_server_exceptions=True)


class MultiUserClients:
    def __init__(self, db: DBSession):
        self.db = db

    def switch(self, username: str) -> tuple[TestClient, str]:
        user = _get_user(self.db, username)
        if not user:
            raise ValueError(f"User {username} not found")
        client = _make_client(self.db, user)
        return client, username


@pytest.fixture
def admin_client(db):
    user = _get_user(db, 'demo_admin')
    client = _make_client(db, user)
    yield client, user.username
    app.dependency_overrides.clear()


@pytest.fixture
def hr_client(db):
    user = _get_user(db, 'demo_hr_user')
    client = _make_client(db, user)
    yield client, user.username
    app.dependency_overrides.clear()


@pytest.fixture
def inventory_client(db):
    user = _get_user(db, 'demo_inventory_user')
    client = _make_client(db, user)
    yield client, user.username
    app.dependency_overrides.clear()


@pytest.fixture
def viewer_client(db):
    user = _get_user(db, 'demo_viewer')
    client = _make_client(db, user)
    yield client, user.username
    app.dependency_overrides.clear()


@pytest.fixture
def multi_client(db):
    clients = MultiUserClients(db)
    yield clients
    app.dependency_overrides.clear()
