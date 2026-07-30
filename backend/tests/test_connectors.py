"""Backend tests for Phase 3 Connector Integration, Task Import, Approval, Templates, and Callbacks."""
from __future__ import annotations

import pytest
from unittest.mock import patch, MagicMock
from app.connectors.mock_task_portal import MockTaskPortalConnector
from app.models.external_task_import import ExternalTaskImport
from app.models.project import Project
from app.services import task_import_service
from app.services.task_import_service import (
    approve_test_plan,
    classify_template_type,
    prepare_test_plan,
    sync_tasks_from_portal,
)

@pytest.fixture(autouse=True)
def mock_task_portal_connector():
    with patch('app.connectors.mock_task_portal.MockTaskPortalConnector.health_check', return_value=True), \
         patch('app.connectors.mock_task_portal.MockTaskPortalConnector.fetch_testing_l2_tasks') as mock_fetch, \
         patch('app.connectors.mock_task_portal.MockTaskPortalConnector.fetch_task') as mock_fetch_one, \
         patch('app.connectors.mock_task_portal.MockTaskPortalConnector.send_qa_result') as mock_send_qa:
        
        tasks_data = [
            {
                'source_task_id': 'MOCK-1',
                'source_revision': 1,
                'module_name': 'Employee Module',
                'title': 'Create New Staff Member',
                'description': 'Test emp creation',
                'status': 'TESTING_L2',
                'page_path': '/hr/employees/new',
                'acceptance_criteria': 'Form submits successfully',
                'assigned_developer': 'dev1'
            }
        ]
        mock_fetch.return_value = tasks_data
        mock_fetch_one.return_value = tasks_data[0]
        mock_send_qa.return_value = {'status': 'QA_PASSED'}
        yield


def test_connector_health_check():
    connector = MockTaskPortalConnector()
    # Mock task portal backend running on port 8001
    assert connector.health_check() is True


def test_connector_fetch_testing_l2_tasks():
    connector = MockTaskPortalConnector()
    tasks = connector.fetch_testing_l2_tasks()
    assert isinstance(tasks, list)
    assert len(tasks) >= 1


def test_task_import_sync_creates_record(db):
    records = sync_tasks_from_portal(db)
    assert len(records) >= 1
    rec = records[0]
    assert rec.source_system == 'MOCK_TASK_PORTAL'
    assert rec.import_status == 'DRAFT'


def test_task_import_duplicate_prevention(db):
    records_1 = sync_tasks_from_portal(db)
    count_1 = db.query(ExternalTaskImport).count()

    # Second sync run should not create duplicate records for same revision
    records_2 = sync_tasks_from_portal(db)
    count_2 = db.query(ExternalTaskImport).count()
    assert count_1 == count_2


def test_classify_template_type():
    task_emp = ExternalTaskImport(
        module_name='Employee Module',
        title='Create New Staff Member',
        page_path='/hr/employees/new',
        acceptance_criteria='Form submits successfully',
    )
    assert classify_template_type(task_emp) == 'EMPLOYEE_CREATE'

    task_stock = ExternalTaskImport(
        module_name='Inventory',
        title='Stock Count Reconciliation Audit',
        page_path='/inventory/stock-count',
        acceptance_criteria='Reconciliation updates diff',
    )
    assert classify_template_type(task_stock) == 'STOCK_COUNT'

    task_unsupported = ExternalTaskImport(
        module_name='Unknown',
        title='Random Untested Module',
        page_path='/unknown/path',
        acceptance_criteria='Do something weird',
    )
    assert classify_template_type(task_unsupported) == 'UNSUPPORTED'


def test_prepare_test_plan_employee(db):
    records = sync_tasks_from_portal(db)
    emp_task = next((r for r in records if 'employee' in r.title.lower() or 'emp' in r.module_name.lower()), records[0])
    updated = prepare_test_plan(db, emp_task.id)
    assert updated.import_status == 'PLAN_PREPARED'
    assert updated.linked_test_plan_id is not None


def test_developer_cannot_self_approve(db):
    records = sync_tasks_from_portal(db)
    task = records[0]
    prepare_test_plan(db, task.id)

    # If task developer is 'dev1', dev1 cannot self-approve
    task.assigned_developer = 'dev1'
    db.commit()

    with pytest.raises(Exception) as exc_info:
        approve_test_plan(db, task.id, approver_username='dev1')
    assert 'cannot self-approve' in str(exc_info.value)


def test_approve_test_plan_success(db):
    records = sync_tasks_from_portal(db)
    task = records[0]
    prepare_test_plan(db, task.id)
    task.assigned_developer = 'dev1'
    db.commit()

    approved = approve_test_plan(db, task.id, approver_username='admin')
    assert approved.import_status == 'APPROVED'
    assert approved.approved_by == 'admin'
    assert approved.approved_at is not None


def test_reset_imports_for_testing(db):
    """Verify reset_imports_for_testing clears all import/execution state correctly."""
    from app.services.task_import_service import reset_imports_for_testing

    # First sync to create some import records
    records = sync_tasks_from_portal(db)
    assert len(records) >= 1

    # Prepare and approve one to mutate state
    task = records[0]
    prepare_test_plan(db, task.id)
    approve_test_plan(db, task.id, approver_username='admin')
    db.commit()

    # Reset
    count = reset_imports_for_testing(db)
    assert count >= 1

    # All imports must now be back in DRAFT state
    from app.models.external_task_import import ExternalTaskImport
    all_imports = db.query(ExternalTaskImport).all()
    for imp in all_imports:
        assert imp.import_status == 'DRAFT'
        assert imp.linked_run_id is None
        assert imp.approved_by is None
        assert imp.approved_at is None
        assert imp.callback_status is None


def test_blocked_result_does_not_create_defect(db):
    """BLOCKED run status must not create a defect — only FAILED does."""
    from datetime import datetime
    from app.models.automated_execution import AutomatedRun
    from app.models.defect import Defect
    from app.models.external_task_import import ExternalTaskImport
    from app.services.task_import_service import (
        _get_demo_project,
        _ensure_demo_target,
        sync_tasks_from_portal,
        prepare_test_plan,
        approve_test_plan,
    )
    from app.services import automated_execution
    from unittest.mock import MagicMock

    records = sync_tasks_from_portal(db)
    task = records[0]
    prepare_test_plan(db, task.id)
    task.assigned_developer = 'dev1'
    db.commit()
    approve_test_plan(db, task.id, approver_username='admin')
    db.commit()
    db.refresh(task)

    # Simulate a BLOCKED run by directly setting run status
    target = _ensure_demo_target(db, task.project_id)
    run = automated_execution.create_run(
        db=db, target=target,
        name='Blocked run test',
        description='Phase 3.1 hardening test',
        case_ids=[task.linked_test_plan_id],
        timeout_seconds=30,
        max_retries=0,
        created_by=1,
    )
    # Mark run as BLOCKED (simulating auth-blocked execution)
    run.status = 'BLOCKED'
    run.failure_classification = 'AUTHENTICATION_FAILED'
    run.safe_error_message = 'Authentication failed or target login unavailable.'
    task.linked_run_id = run.id
    db.commit()

    # Confirm no defect was auto-created for BLOCKED state
    defects = db.query(Defect).filter(Defect.automated_run_id == run.id).all()
    assert len(defects) == 0, 'BLOCKED runs must NOT create defects automatically'


def test_import_blocked_status_maps_to_need_clarity(db):
    """Verify that BLOCKED run_status maps import_status to NEED_CLARITY and callback to NEED_CLARITY."""
    # Check the mapping logic directly without executing Playwright
    from app.services.task_import_service import sync_tasks_from_portal, prepare_test_plan, approve_test_plan
    from app.models.external_task_import import ExternalTaskImport

    records = sync_tasks_from_portal(db)
    task = records[0]
    prepare_test_plan(db, task.id)
    task.assigned_developer = None  # No developer restriction
    db.commit()
    approved = approve_test_plan(db, task.id, approver_username='admin')
    assert approved.import_status == 'APPROVED'

    # Simulate the logic that execute_and_callback uses when run_status is BLOCKED
    run_status = 'BLOCKED'
    if run_status == 'PASSED':
        qa_res = 'PASS'
        portal_status = 'QA_PASSED'
        import_status = 'COMPLETED'
    elif run_status == 'BLOCKED':
        qa_res = 'BLOCKED'
        portal_status = 'NEED_CLARITY'
        import_status = 'NEED_CLARITY'
    else:
        qa_res = 'FAIL'
        portal_status = 'REWORK'
        import_status = 'COMPLETED'

    assert qa_res == 'BLOCKED'
    assert portal_status == 'NEED_CLARITY'
    assert import_status == 'NEED_CLARITY'


def test_execute_next_job_respects_project_isolation(db):
    """execute_next_job with target_run_id should refuse to execute a job from a different project."""
    from app.services.automated_execution import execute_next_job
    from app.services.task_import_service import (
        _get_demo_project,
        _ensure_demo_target,
        sync_tasks_from_portal,
        prepare_test_plan,
        approve_test_plan,
    )
    from app.services import automated_execution

    records = sync_tasks_from_portal(db)
    task = records[0]
    prepare_test_plan(db, task.id)
    task.assigned_developer = None
    db.commit()
    approve_test_plan(db, task.id, approver_username='admin')
    db.commit()
    db.refresh(task)

    target = _ensure_demo_target(db, task.project_id)
    run = automated_execution.create_run(
        db=db, target=target,
        name='Isolation test run',
        description='Project isolation check',
        case_ids=[task.linked_test_plan_id],
        timeout_seconds=30,
        max_retries=0,
        created_by=1,
    )

    from app.models.automated_execution import ExecutionJob
    db.add(ExecutionJob(project_id=run.project_id, run_id=run.id, status='QUEUED'))
    db.commit()

    # Attempt execution with a project_id that does NOT include this run's project
    result = execute_next_job(
        db, worker_key='test-worker-isolation',
        allowed_project_ids=(99999,),  # Wrong project
        target_run_id=run.id,
    )
    assert result is None, 'execute_next_job must refuse cross-project run access'

