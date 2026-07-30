"""Backend tests for Mock Task Portal — all required cases.

Multi-user tests use `multi_client` fixture and call .switch() before each
request group because FastAPI dependency_overrides is global.
"""
from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from app.models.task import Task
from app.models.task_history import TaskHistory
from tests.conftest import make_task


# ──────────────────────────────────────────────────────────────────────────────
# 1. Task creation
# ──────────────────────────────────────────────────────────────────────────────

def test_create_task_success(admin_client, db):
    client, _ = admin_client
    resp = client.post('/api/tasks', json={
        'task_code': 'T-001',
        'project_name': 'Demo ERP',
        'module_name': 'HR',
        'title': 'Save Button Test',
        'priority': 'HIGH',
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data['task_code'] == 'T-001'
    assert data['status'] == 'CREATED'
    assert data['revision'] == 0


def test_create_task_duplicate_code_rejected(admin_client, db):
    client, _ = admin_client
    payload = {'task_code': 'T-DUP', 'project_name': 'Demo ERP', 'module_name': 'HR', 'title': 'Dup'}
    client.post('/api/tasks', json=payload)
    resp = client.post('/api/tasks', json=payload)
    assert resp.status_code == 409


def test_create_task_only_superadmin(dev_client, db):
    client, _ = dev_client
    resp = client.post('/api/tasks', json={
        'task_code': 'T-DEV', 'project_name': 'Demo ERP', 'module_name': 'HR', 'title': 'X',
    })
    assert resp.status_code == 403


# ──────────────────────────────────────────────────────────────────────────────
# 2. Assignment
# ──────────────────────────────────────────────────────────────────────────────

def test_assignment_created_to_assigned(admin_client, db):
    client, _ = admin_client
    task = make_task(db, task_code='T-ASSIGN')
    resp = client.patch(f'/api/tasks/{task.id}/status', json={'new_status': 'ASSIGNED', 'reason': 'Ready'})
    assert resp.status_code == 200
    assert resp.json()['status'] == 'ASSIGNED'


# ──────────────────────────────────────────────────────────────────────────────
# 3. Developer access restrictions
# ──────────────────────────────────────────────────────────────────────────────

def test_developer_can_only_see_own_tasks(dev_client, db):
    client, username = dev_client
    # Task assigned to this dev
    own_task = make_task(db, task_code='T-OWN', assigned_developer=username, status='ASSIGNED')
    # Task assigned to another dev
    other_task = make_task(db, task_code='T-OTHER', assigned_developer='other-dev', status='ASSIGNED')
    resp = client.get('/api/tasks')
    ids = [t['id'] for t in resp.json()]
    assert own_task.id in ids
    assert other_task.id not in ids


def test_developer_cannot_access_unassigned_task(dev_client, db):
    client, username = dev_client
    task = make_task(db, task_code='T-DENY', assigned_developer='someone-else', status='ASSIGNED')
    resp = client.get(f'/api/tasks/{task.id}')
    assert resp.status_code == 403


# ──────────────────────────────────────────────────────────────────────────────
# 4. Status transition validation
# ──────────────────────────────────────────────────────────────────────────────

def test_invalid_transition_rejected(admin_client, db):
    client, _ = admin_client
    task = make_task(db, task_code='T-BAD')
    # CREATED → QA_PASSED is not a valid transition
    resp = client.patch(f'/api/tasks/{task.id}/status', json={'new_status': 'QA_PASSED'})
    assert resp.status_code == 422


def test_full_happy_path_transitions(multi_client, db):
    """Test full workflow using multi_client fixture with explicit user switching."""
    # Create all users first
    admin, admin_name = multi_client.switch('admin', 'SUPERADMIN')
    dev, dev_name = multi_client.switch('dev1', 'DEVELOPER')

    task = make_task(db, task_code='T-FLOW', assigned_developer=dev_name, assigned_tester='tester1')

    # SUPERADMIN: CREATED → ASSIGNED (switch to admin first)
    admin, _ = multi_client.switch('admin', 'SUPERADMIN')
    r = admin.patch(f'/api/tasks/{task.id}/status', json={'new_status': 'ASSIGNED'})
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    assert r.json()['status'] == 'ASSIGNED'

    # DEVELOPER: ASSIGNED → IN_PROGRESS
    dev, dev_name = multi_client.switch('dev1', 'DEVELOPER')
    r = dev.patch(f'/api/tasks/{task.id}/status', json={'new_status': 'IN_PROGRESS'})
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    assert r.json()['status'] == 'IN_PROGRESS'

    # DEVELOPER: IN_PROGRESS → TESTING_L1
    dev, _ = multi_client.switch('dev1', 'DEVELOPER')
    r = dev.patch(f'/api/tasks/{task.id}/status', json={'new_status': 'TESTING_L1'})
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    assert r.json()['status'] == 'TESTING_L1'

    # DEVELOPER: TESTING_L1 → TESTING_L2
    dev, _ = multi_client.switch('dev1', 'DEVELOPER')
    r = dev.patch(f'/api/tasks/{task.id}/status', json={'new_status': 'TESTING_L2'})
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    assert r.json()['status'] == 'TESTING_L2'
    assert r.json()['testing_l2_at'] is not None
    assert r.json()['revision'] == 1


# ──────────────────────────────────────────────────────────────────────────────
# 5. Testing L2 task filtering + connector contract
# ──────────────────────────────────────────────────────────────────────────────

def test_testing_l2_filter_returns_connector_contract(admin_client, db):
    client, _ = admin_client
    make_task(db, task_code='T-L2-A', status='TESTING_L2', testing_l2_at=datetime.utcnow())
    make_task(db, task_code='T-L2-B', status='ASSIGNED')  # should not appear
    resp = client.get('/api/tasks?status=TESTING_L2')
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) == 1
    item = items[0]
    # Verify connector contract fields
    assert item['source_system'] == 'MOCK_TASK_PORTAL'
    assert 'source_task_id' in item
    assert 'source_revision' in item
    assert 'application_url' in item
    assert 'acceptance_criteria' in item


# ──────────────────────────────────────────────────────────────────────────────
# 6. Developer notes
# ──────────────────────────────────────────────────────────────────────────────

def test_developer_can_add_notes(dev_client, db):
    client, dev_name = dev_client
    task = make_task(db, task_code='T-NOTES', assigned_developer=dev_name, status='IN_PROGRESS')
    resp = client.post(f'/api/tasks/{task.id}/developer-notes', json={'notes': 'Fixed in commit abc'})
    assert resp.status_code == 200
    assert resp.json()['developer_notes'] == 'Fixed in commit abc'


def test_developer_cannot_add_notes_to_others_task(dev_client, db):
    client, _ = dev_client
    task = make_task(db, task_code='T-NOTES2', assigned_developer='someone-else', status='IN_PROGRESS')
    resp = client.post(f'/api/tasks/{task.id}/developer-notes', json={'notes': 'Hack'})
    assert resp.status_code == 403


# ──────────────────────────────────────────────────────────────────────────────
# 7. Rework remarks
# ──────────────────────────────────────────────────────────────────────────────

def test_tester_can_add_rework_remarks(tester_client, db):
    client, _ = tester_client
    task = make_task(db, task_code='T-RWK', status='QA_FAILED')
    resp = client.post(f'/api/tasks/{task.id}/rework-remarks', json={'remarks': 'Button missing validation'})
    assert resp.status_code == 200
    assert 'Button missing' in resp.json()['rework_remarks']


# ──────────────────────────────────────────────────────────────────────────────
# 8. QA PASS result
# ──────────────────────────────────────────────────────────────────────────────

def test_qa_pass_moves_to_qa_passed(tester_client, db):
    client, _ = tester_client
    task = make_task(db, task_code='T-PASS', status='TESTING_L2', testing_l2_at=datetime.utcnow())
    resp = client.post(f'/api/tasks/{task.id}/qa-result', json={'result': 'PASS'})
    assert resp.status_code == 200
    assert resp.json()['status'] == 'QA_PASSED'


# ──────────────────────────────────────────────────────────────────────────────
# 9. QA FAIL result
# ──────────────────────────────────────────────────────────────────────────────

def test_qa_fail_moves_to_qa_failed(tester_client, db):
    client, _ = tester_client
    task = make_task(db, task_code='T-FAIL', status='TESTING_L2', testing_l2_at=datetime.utcnow())
    resp = client.post(f'/api/tasks/{task.id}/qa-result', json={'result': 'FAIL', 'reason': 'Save fails on empty name'})
    assert resp.status_code == 200
    data = resp.json()
    assert data['status'] == 'QA_FAILED'


# ──────────────────────────────────────────────────────────────────────────────
# 10. BLOCKED result
# ──────────────────────────────────────────────────────────────────────────────

def test_qa_blocked_moves_to_need_clarity(tester_client, db):
    client, _ = tester_client
    task = make_task(db, task_code='T-BLK', status='TESTING_L2', testing_l2_at=datetime.utcnow())
    resp = client.post(f'/api/tasks/{task.id}/qa-result', json={'result': 'BLOCKED', 'reason': 'Environment not ready'})
    assert resp.status_code == 200
    assert resp.json()['status'] == 'NEED_CLARITY'


# ──────────────────────────────────────────────────────────────────────────────
# 11. Delivery workflow
# ──────────────────────────────────────────────────────────────────────────────

def test_delivery_workflow(multi_client, db):
    task = make_task(db, task_code='T-DEL', status='QA_PASSED')

    # SUPERADMIN: QA_PASSED → DELIVERY_READY
    admin, _ = multi_client.switch('admin', 'SUPERADMIN')
    r = admin.patch(f'/api/tasks/{task.id}/status', json={'new_status': 'DELIVERY_READY'})
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    assert r.json()['status'] == 'DELIVERY_READY'

    # DELIVERY: DELIVERY_READY → DELIVERY_COMPLETED
    delivery, _ = multi_client.switch('delivery1', 'DELIVERY')
    r = delivery.patch(f'/api/tasks/{task.id}/status', json={'new_status': 'DELIVERY_COMPLETED'})
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    assert r.json()['status'] == 'DELIVERY_COMPLETED'
    assert r.json()['completed_at'] is not None


# ──────────────────────────────────────────────────────────────────────────────
# 12. Unauthorized transitions
# ──────────────────────────────────────────────────────────────────────────────

def test_viewer_cannot_change_status(viewer_client, db):
    client, _ = viewer_client
    task = make_task(db, task_code='T-VWR', status='CREATED')
    resp = client.patch(f'/api/tasks/{task.id}/status', json={'new_status': 'ASSIGNED'})
    assert resp.status_code == 403


def test_delivery_cannot_change_status_to_non_delivery(delivery_client, db):
    client, _ = delivery_client
    task = make_task(db, task_code='T-DELBAD', status='DELIVERY_READY')
    resp = client.patch(f'/api/tasks/{task.id}/status', json={'new_status': 'DELIVERY_READY'})
    # Same status = invalid transition
    assert resp.status_code in {422, 403}


# ──────────────────────────────────────────────────────────────────────────────
# 13. Status history immutability
# ──────────────────────────────────────────────────────────────────────────────

def test_status_history_is_append_only(admin_client, db):
    client, _ = admin_client
    task = make_task(db, task_code='T-HIST')
    client.patch(f'/api/tasks/{task.id}/status', json={'new_status': 'ASSIGNED'})
    resp = client.get(f'/api/tasks/{task.id}/history')
    assert resp.status_code == 200
    records = resp.json()
    assert len(records) >= 2  # CREATED + ASSIGNED
    # Verify immutability: no DELETE or PUT endpoint exists for history
    del_resp = client.request('DELETE', f'/api/tasks/{task.id}/history')
    assert del_resp.status_code == 405
    put_resp = client.request('PUT', f'/api/tasks/{task.id}/history')
    assert put_resp.status_code == 405


def test_history_records_correct_fields(admin_client, db):
    client, _ = admin_client
    task = make_task(db, task_code='T-HIST2')
    client.patch(f'/api/tasks/{task.id}/status', json={'new_status': 'ASSIGNED', 'reason': 'Ready to assign'})
    resp = client.get(f'/api/tasks/{task.id}/history')
    records = resp.json()
    assigned_record = next(r for r in records if r['new_status'] == 'ASSIGNED')
    assert assigned_record['previous_status'] == 'CREATED'
    assert assigned_record['reason'] == 'Ready to assign'
    assert 'changed_by' in assigned_record
    assert 'timestamp' in assigned_record


# ──────────────────────────────────────────────────────────────────────────────
# 14. Task revision behavior
# ──────────────────────────────────────────────────────────────────────────────

def test_revision_increments_on_rework_cycle(multi_client, db):
    """Test revision increments through TESTING_L2 → QA_FAILED → REWORK cycle."""
    admin, _ = multi_client.switch('admin', 'SUPERADMIN')
    dev, dev_name = multi_client.switch('dev1', 'DEVELOPER')

    task = make_task(db, task_code='T-REV', assigned_developer=dev_name)

    multi_client.switch('admin', 'SUPERADMIN')[0].patch(f'/api/tasks/{task.id}/status', json={'new_status': 'ASSIGNED'})
    multi_client.switch('dev1', 'DEVELOPER')[0].patch(f'/api/tasks/{task.id}/status', json={'new_status': 'IN_PROGRESS'})
    multi_client.switch('dev1', 'DEVELOPER')[0].patch(f'/api/tasks/{task.id}/status', json={'new_status': 'TESTING_L1'})
    multi_client.switch('dev1', 'DEVELOPER')[0].patch(f'/api/tasks/{task.id}/status', json={'new_status': 'TESTING_L2'})

    # Check revision incremented on TESTING_L2
    data = multi_client.switch('admin', 'SUPERADMIN')[0].get(f'/api/tasks/{task.id}').json()
    assert data['revision'] == 1

    # FAIL it
    multi_client.switch('tester1', 'TESTER')[0].post(f'/api/tasks/{task.id}/qa-result', json={'result': 'FAIL'})

    # Rework
    multi_client.switch('tester1', 'TESTER')[0].patch(f'/api/tasks/{task.id}/status', json={'new_status': 'REWORK'})
    data = multi_client.switch('admin', 'SUPERADMIN')[0].get(f'/api/tasks/{task.id}').json()
    assert data['revision'] == 2  # increments again on REWORK


# ──────────────────────────────────────────────────────────────────────────────
# 15. Dashboard summary
# ──────────────────────────────────────────────────────────────────────────────

def test_dashboard_summary(admin_client, db):
    client, _ = admin_client
    make_task(db, task_code='D-1', status='CREATED')
    make_task(db, task_code='D-2', status='TESTING_L2', testing_l2_at=datetime.utcnow())
    make_task(db, task_code='D-3', status='QA_PASSED')
    resp = client.get('/api/dashboard/summary')
    assert resp.status_code == 200
    data = resp.json()
    assert data['counts']['CREATED'] >= 1
    assert data['counts']['TESTING_L2'] >= 1
    assert data['counts']['QA_PASSED'] >= 1


# ──────────────────────────────────────────────────────────────────────────────
# 16. Auth endpoints
# ──────────────────────────────────────────────────────────────────────────────

def test_login_with_invalid_credentials(db):
    from fastapi.testclient import TestClient
    from app.main import app
    from app.database import get_db
    from app.auth import get_auth_context

    def override_db():
        yield db

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides.pop(get_auth_context, None)
    client = TestClient(app, raise_server_exceptions=False)
    resp = client.post('/api/auth/login', json={'username': 'nobody', 'password': 'wrong'})
    assert resp.status_code == 401
    app.dependency_overrides.clear()
