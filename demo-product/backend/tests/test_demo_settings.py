"""Backend tests for Demo Settings (bug toggles)."""
from __future__ import annotations


def test_list_demo_settings(admin_client):
    client, _ = admin_client
    resp = client.get('/api/demo-settings')
    assert resp.status_code == 200
    settings = resp.json()
    keys = {s['key'] for s in settings}
    assert 'employee_save_failure' in keys
    assert 'login_failure_mode' in keys


def test_update_demo_setting_admin(admin_client):
    client, _ = admin_client
    resp = client.patch('/api/demo-settings/employee_save_failure', json={'enabled': True})
    assert resp.status_code == 200
    assert resp.json()['enabled'] is True

    # Revert
    resp2 = client.patch('/api/demo-settings/employee_save_failure', json={'enabled': False})
    assert resp2.status_code == 200
    assert resp2.json()['enabled'] is False


def test_update_demo_setting_non_admin_forbidden(hr_client):
    client, _ = hr_client
    resp = client.patch('/api/demo-settings/employee_save_failure', json={'enabled': True})
    assert resp.status_code == 403


def test_update_unknown_setting_rejected(admin_client):
    client, _ = admin_client
    resp = client.patch('/api/demo-settings/invalid_unknown_key', json={'enabled': True})
    assert resp.status_code == 404
