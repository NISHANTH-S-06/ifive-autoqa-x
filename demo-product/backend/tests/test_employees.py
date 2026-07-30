"""Backend tests for Employee management & validation."""
from __future__ import annotations

from app.models import Department
from app.services.demo_setting_service import update_setting


def test_create_employee_success(hr_client, db):
    client, _ = hr_client
    dept = db.query(Department).first()
    resp = client.post('/api/employees', json={
        'name': 'Alice Smith',
        'email': 'alice.smith@demo.local',
        'department_id': dept.id,
        'joining_date': '2026-02-01',
        'active': True,
        'notes': 'Test employee notes',
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data['name'] == 'Alice Smith'
    assert data['email'] == 'alice.smith@demo.local'
    assert data['employee_code'].startswith('EMP-')
    assert data['department_name'] == dept.name


def test_create_employee_invalid_email(hr_client, db):
    client, _ = hr_client
    dept = db.query(Department).first()
    resp = client.post('/api/employees', json={
        'name': 'Bob Smith',
        'email': 'invalid-email-format',
        'department_id': dept.id,
        'joining_date': '2026-02-01',
    })
    assert resp.status_code == 422


def test_create_employee_duplicate_email(hr_client, db):
    client, _ = hr_client
    dept = db.query(Department).first()
    payload = {
        'name': 'Charlie Smith',
        'email': 'charlie.dup@demo.local',
        'department_id': dept.id,
        'joining_date': '2026-02-01',
    }
    r1 = client.post('/api/employees', json=payload)
    assert r1.status_code == 201
    r2 = client.post('/api/employees', json=payload)
    assert r2.status_code == 409


def test_create_employee_role_restriction(viewer_client, db):
    client, _ = viewer_client
    dept = db.query(Department).first()
    resp = client.post('/api/employees', json={
        'name': 'Unauthorized Emp',
        'email': 'unauth@demo.local',
        'department_id': dept.id,
        'joining_date': '2026-02-01',
    })
    assert resp.status_code == 403


def test_employee_save_failure_bug_toggle(hr_client, db):
    client, _ = hr_client
    dept = db.query(Department).first()
    update_setting(db, 'employee_save_failure', enabled=True)

    resp = client.post('/api/employees', json={
        'name': 'Failed Save Emp',
        'email': 'failed.save@demo.local',
        'department_id': dept.id,
        'joining_date': '2026-02-01',
    })
    assert resp.status_code == 500
    assert 'Internal Server Error' in resp.json()['detail']


def test_employee_table_refresh_failure_bug_toggle(hr_client, db):
    client, _ = hr_client
    dept = db.query(Department).first()

    # Create employee 1
    client.post('/api/employees', json={
        'name': 'Emp One', 'email': 'emp1@demo.local', 'department_id': dept.id, 'joining_date': '2026-02-01',
    })

    # Get list without bug: contains at least initial seed + Emp One
    r1 = client.get('/api/employees').json()
    count_before = len(r1)

    # Enable bug toggle
    update_setting(db, 'employee_table_refresh_failure', enabled=True)

    # Get list with bug toggle ON: newest employee is filtered out
    r2 = client.get('/api/employees').json()
    assert len(r2) == count_before - 1
