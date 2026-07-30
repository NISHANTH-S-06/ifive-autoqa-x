"""Backend tests for Authentication & Authorization."""
from __future__ import annotations

from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db
from app.auth import get_auth_context
from app.services.demo_setting_service import update_setting


def test_login_success(db):
    def override_db():
        yield db

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides.pop(get_auth_context, None)
    client = TestClient(app)

    resp = client.post('/api/auth/login', json={'username': 'demo_admin', 'password': 'Admin@Demo123'})
    assert resp.status_code == 200
    data = resp.json()
    assert 'access_token' in data
    assert data['user']['username'] == 'demo_admin'
    assert data['user']['role'] == 'DEMO_ADMIN'
    app.dependency_overrides.clear()


def test_login_invalid_password(db):
    def override_db():
        yield db

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides.pop(get_auth_context, None)
    client = TestClient(app)

    resp = client.post('/api/auth/login', json={'username': 'demo_admin', 'password': 'WrongPassword'})
    assert resp.status_code == 401
    app.dependency_overrides.clear()


def test_login_failure_mode_toggle(db):
    def override_db():
        yield db

    update_setting(db, 'login_failure_mode', enabled=True)

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides.pop(get_auth_context, None)
    client = TestClient(app)

    resp = client.post('/api/auth/login', json={'username': 'demo_admin', 'password': 'Admin@Demo123'})
    assert resp.status_code == 503
    assert 'unavailable' in resp.json()['detail'].lower()
    app.dependency_overrides.clear()


def test_auth_me_endpoint(admin_client):
    client, username = admin_client
    resp = client.get('/api/auth/me')
    assert resp.status_code == 200
    assert resp.json()['username'] == username
