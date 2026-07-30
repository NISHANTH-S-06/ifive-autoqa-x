"""Service logic for External Task Import, Template Plan Generation, Approval, and Execution Callback."""
from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session as DBSession

from app.connectors.mock_task_portal import MockTaskPortalConnector
from app.config import settings
from app.models.automated_execution import AutomatedRun
from app.models.connection_target import ConnectionTarget
from app.models.defect import Defect
from app.models.external_task_import import ExternalTaskImport
from app.models.project import Project
from app.models.test_management import ManagedTestCase, ManagedTestSuite, TestCaseVersion, TestModule, TestProject
from app.services import automated_execution

ALLOWED_DEMO_PATHS = [
    '/login',
    '/dashboard',
    '/employees',
    '/employees/new',
    '/hr/employees',
    '/hr/employees/new',
    '/inventory',
    '/inventory/products',
    '/inventory/stock-count',
]

ALLOWED_IFIVE_PATHS = [
    '/',
    '/products/iot',
    '/products/erp',
    '/products/hrms',
    '/products/crm',
    '/otherproducts',
    '/solutions/iiot-4-0',
]


def _get_demo_project(db: DBSession) -> Project:
    project = db.scalar(select(Project).where(Project.name == 'Demo ERP'))
    if not project:
        project = db.scalar(select(Project).where(Project.product_code == 'ERP'))
    if not project:
        project = Project(
            name='Demo ERP',
            product_code='ERP',
            description='Local demo product website project for Phase 3 integration',
            base_url=settings.demo_product_url,
            environment='local',
            is_active=True,
        )
        db.add(project)
        db.flush()
        
    test_proj = db.scalar(select(TestProject).where(TestProject.id == project.id))
    if not test_proj:
        from app.models.operator import Operator
        op = db.query(Operator).first()
        op_id = op.id if op else 1
        test_proj = TestProject(
            id=project.id,
            access_project_id=project.id,
            name=f'{project.name} Test Project',
            code=f'TEST-{project.id}',
            description=f'Tests for {project.name}',
            status='ACTIVE',
            created_by=op_id
        )
        db.add(test_proj)
        db.flush()
        
    return project


def _ensure_demo_target(db: DBSession, project_id: int) -> ConnectionTarget:
    project = db.get(Project, project_id)
    target = db.scalar(
        select(ConnectionTarget).where(
            ConnectionTarget.project_id == project_id,
        )
    )

    is_ifive = project and ('ifive.in' in (project.base_url or '').lower() or 'ifive' in project.name.lower())
    base_url = 'https://ifive.in' if is_ifive else settings.demo_product_url
    probe_paths = ALLOWED_IFIVE_PATHS if is_ifive else ALLOWED_DEMO_PATHS
    scheme = 'https' if is_ifive else 'http'
    host = 'ifive.in' if is_ifive else '127.0.0.1'
    port = 443 if is_ifive else 5175

    if not target:
        from app.models.operator import Operator
        op_row = db.query(Operator.id).first()
        first_operator_id = op_row[0] if op_row else 1
        target = ConnectionTarget(
            project_id=project_id,
            target_key=f'TARGET-PRJ-{project_id}',
            name=f'{project.name if project else "Demo"} Target',
            description=f'Auto-created target for {project.name if project else "Demo"}',
            environment_type='LOCAL',
            base_url=base_url,
            normalized_scheme=scheme,
            normalized_host=host,
            normalized_port=port,
            normalized_origin=base_url,
            allowed_probe_paths_json=json.dumps(probe_paths),
            tls_required=is_ifive,
            tls_verify=True,
            connection_timeout_seconds=10,
            lifecycle_state='APPROVED',
            enabled=True,
            execution_enabled=True,
            execution_approved_by=first_operator_id,
            created_by=first_operator_id,
        )
        db.add(target)
        db.flush()
    else:
        target.allowed_probe_paths_json = json.dumps(probe_paths)
        target.base_url = base_url
        target.normalized_scheme = scheme
        target.normalized_host = host
        target.normalized_port = port
        target.normalized_origin = base_url
        target.enabled = True
        target.execution_enabled = True
        target.lifecycle_state = 'APPROVED'
        db.flush()
    return target



def reset_imports_for_testing(db: DBSession) -> int:
    """Reset all external task imports to DRAFT state for E2E test isolation.
    Cancels any QUEUED/RUNNING execution jobs and clears linked run references.
    This endpoint is for local testing ONLY — it must never be called in production.
    """
    from app.models.automated_execution import AutomatedRun, ExecutionJob
    from sqlalchemy import update as sa_update

    now = datetime.utcnow()
    # Cancel all queued/running execution jobs
    db.execute(
        sa_update(ExecutionJob)
        .where(ExecutionJob.status.in_(['QUEUED', 'RUNNING']))
        .values(status='CANCELLED', updated_at=now)
        .execution_options(synchronize_session=False)
    )
    # Abort all DRAFT/QUEUED/RUNNING automated runs
    db.execute(
        sa_update(AutomatedRun)
        .where(AutomatedRun.status.in_(['QUEUED', 'RUNNING', 'DRAFT']))
        .values(status='CANCELLED', updated_at=now)
        .execution_options(synchronize_session=False)
    )
    # Reset all imports to DRAFT and clear linked run
    result = db.execute(
        sa_update(ExternalTaskImport)
        .values(
            import_status='DRAFT',
            linked_run_id=None,
            callback_status=None,
            callback_error=None,
            approved_by=None,
            approved_at=None,
        )
        .execution_options(synchronize_session=False)
    )
    db.commit()
    return result.rowcount



def sync_tasks_from_portal(db: DBSession) -> List[ExternalTaskImport]:
    connector = MockTaskPortalConnector()
    if not connector.health_check():
        raise HTTPException(

            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f'Mock Task Portal service at {settings.mock_task_portal_url} is unreachable.',
        )

    portal_tasks = connector.fetch_testing_l2_tasks()
    imported_records = []

    for item in portal_tasks:
        source_id = str(item.get('source_task_id') or item.get('id'))
        revision = int(item.get('source_revision') or item.get('revision') or 1)
        proj_name = item.get('project_name', 'Demo ERP')

        # Get or create project for item.get('project_name')
        project = db.scalar(select(Project).where(Project.name == proj_name))
        if not project:
            is_ifive = 'ifive' in proj_name.lower() or 'ifive.in' in (item.get('application_url') or '').lower()
            project = Project(
                name=proj_name,
                product_code='IIOT' if is_ifive else 'ERP',
                description=f'Project for {proj_name}',
                base_url='https://ifive.in/' if is_ifive else (item.get('application_url') or settings.demo_product_url),
                environment='local',
                is_active=True,
            )
            db.add(project)
            db.flush()

        test_proj = db.scalar(select(TestProject).where(TestProject.id == project.id))
        if not test_proj:
            from app.models.operator import Operator
            op = db.query(Operator).first()
            op_id = op.id if op else 1
            test_proj = TestProject(
                id=project.id,
                access_project_id=project.id,
                name=f'{project.name} Test Project',
                code=f'TEST-{project.id}',
                description=f'Tests for {project.name}',
                status='ACTIVE',
                created_by=op_id
            )
            db.add(test_proj)
            db.flush()

        _ensure_demo_target(db, project.id)

        # Check unique constraint: project_id + source_system + source_task_id + source_revision
        existing = db.scalar(
            select(ExternalTaskImport).where(
                ExternalTaskImport.project_id == project.id,
                ExternalTaskImport.source_system == 'MOCK_TASK_PORTAL',
                ExternalTaskImport.source_task_id == source_id,
                ExternalTaskImport.source_revision == revision,
            )
        )

        if existing:
            existing.last_synced_at = datetime.utcnow()
            imported_records.append(existing)
            continue

        # Create new immutable import record
        imp = ExternalTaskImport(
            project_id=project.id,
            source_system='MOCK_TASK_PORTAL',
            source_task_id=source_id,
            source_revision=revision,
            source_status=item.get('status', 'TESTING_L2'),
            project_name=item.get('project_name', 'Demo ERP'),
            module_name=item.get('module_name', 'General Module'),
            title=item.get('title', 'Untitled Task'),
            description=item.get('description'),
            application_url=item.get('application_url') or ('https://ifive.in/' if 'ifive' in proj_name.lower() else settings.demo_product_url),
            page_path=item.get('page_path') or '/',
            environment=item.get('environment', 'local'),
            expected_result=item.get('expected_result'),
            acceptance_criteria=item.get('acceptance_criteria'),
            test_data=item.get('test_data'),
            assigned_developer=item.get('assigned_developer'),
            assigned_tester=item.get('assigned_tester'),
            priority=item.get('priority', 'MEDIUM'),
            developer_notes=item.get('developer_notes'),
            imported_at=datetime.utcnow(),
            last_synced_at=datetime.utcnow(),
            import_status='DRAFT',
        )
        db.add(imp)
        db.flush()
        imported_records.append(imp)

    db.commit()
    return imported_records


def classify_template_type(task: ExternalTaskImport) -> str:
    combined = f"{task.module_name} {task.title} {task.page_path or ''} {task.acceptance_criteria or ''} {task.description or ''}".lower()
    if 'employee' in combined or 'hr' in combined or 'l2 queue' in combined:
        return 'EMPLOYEE_CREATE'
    if 'stock' in combined or 'inventory' in combined or 'reconciliation' in combined or 'e2e' in combined:
        return 'STOCK_COUNT'
    if 'iot' in combined or 'ifive' in combined or 'product' in combined:
        return 'IFIVE_IOT_NAV'
    return 'UNSUPPORTED'


def build_employee_create_steps(task: ExternalTaskImport, run_tag: str) -> List[Dict[str, Any]]:
    emp_email = f'autoqa_{run_tag}@demo.local'
    emp_name = f'AutoQA {run_tag}'
    return [
        {'step_number': 1, 'action': 'NAVIGATE', 'path': '/login', 'risk_level': 'READ_ONLY'},
        {'step_number': 2, 'action': 'FILL', 'selector': '[data-testid="login-username"]', 'value': 'demo_hr_user', 'risk_level': 'SAFE_INTERACTION'},
        {'step_number': 3, 'action': 'FILL', 'selector': '[data-testid="login-password"]', 'value': 'Hr@Demo123', 'risk_level': 'SAFE_INTERACTION'},
        {'step_number': 4, 'action': 'CLICK', 'selector': '[data-testid="login-submit"]', 'risk_level': 'SAFE_INTERACTION'},
        {'step_number': 5, 'action': 'ASSERT_URL', 'expected': '/dashboard', 'risk_level': 'READ_ONLY'},
        {'step_number': 6, 'action': 'NAVIGATE', 'path': '/hr/employees/new', 'risk_level': 'READ_ONLY'},
        {'step_number': 7, 'action': 'FILL', 'selector': '[data-testid="employee-name"]', 'value': emp_name, 'risk_level': 'SAFE_INTERACTION'},
        {'step_number': 8, 'action': 'FILL', 'selector': '[data-testid="employee-email"]', 'value': emp_email, 'risk_level': 'SAFE_INTERACTION'},
        {'step_number': 9, 'action': 'SELECT', 'selector': '[data-testid="employee-department"]', 'value': '1', 'risk_level': 'SAFE_INTERACTION'},
        {'step_number': 10, 'action': 'FILL', 'selector': '[data-testid="employee-joining-date"]', 'value': '2026-03-01', 'risk_level': 'SAFE_INTERACTION'},
        {'step_number': 11, 'action': 'CHECK', 'selector': '[data-testid="employee-active"]', 'risk_level': 'SAFE_INTERACTION'},
        {'step_number': 12, 'action': 'FILL', 'selector': '[data-testid="employee-notes"]', 'value': f'Imported Task #{task.source_task_id} Rev {task.source_revision}', 'risk_level': 'SAFE_INTERACTION'},
        {'step_number': 13, 'action': 'SCREENSHOT', 'risk_level': 'READ_ONLY'},
        {'step_number': 14, 'action': 'CLICK', 'selector': '[data-testid="employee-save"]', 'risk_level': 'SAFE_INTERACTION'},
        {'step_number': 15, 'action': 'ASSERT_VISIBLE', 'selector': '[data-testid="employee-success"]', 'risk_level': 'READ_ONLY'},
        {'step_number': 16, 'action': 'ASSERT_TEXT', 'selector': '[data-testid="employee-success"]', 'expected': 'created successfully', 'risk_level': 'READ_ONLY'},
        {'step_number': 17, 'action': 'ASSERT_TABLE_ROW', 'selector': '[data-testid="employee-table"]', 'expected': emp_email, 'risk_level': 'READ_ONLY'},
        {'step_number': 18, 'action': 'SCREENSHOT', 'risk_level': 'READ_ONLY'},
    ]


def build_stock_count_steps(task: ExternalTaskImport, run_tag: str) -> List[Dict[str, Any]]:
    return [
        {'step_number': 1, 'action': 'NAVIGATE', 'path': '/login', 'risk_level': 'READ_ONLY'},
        {'step_number': 2, 'action': 'FILL', 'selector': '[data-testid="login-username"]', 'value': 'demo_inventory_user', 'risk_level': 'SAFE_INTERACTION'},
        {'step_number': 3, 'action': 'FILL', 'selector': '[data-testid="login-password"]', 'value': 'Inv@Demo123', 'risk_level': 'SAFE_INTERACTION'},
        {'step_number': 4, 'action': 'CLICK', 'selector': '[data-testid="login-submit"]', 'risk_level': 'SAFE_INTERACTION'},
        {'step_number': 5, 'action': 'ASSERT_URL', 'expected': '/dashboard', 'risk_level': 'READ_ONLY'},
        {'step_number': 6, 'action': 'NAVIGATE', 'path': '/inventory/stock-count', 'risk_level': 'READ_ONLY'},
        {'step_number': 7, 'action': 'SELECT', 'selector': '[data-testid="stock-product"]', 'value': '1', 'risk_level': 'SAFE_INTERACTION'},
        {'step_number': 8, 'action': 'READ_TEXT', 'selector': '[data-testid="stock-current-quantity"]', 'risk_level': 'READ_ONLY'},
        {'step_number': 9, 'action': 'FILL', 'selector': '[data-testid="stock-counted-quantity"]', 'value': '120', 'risk_level': 'SAFE_INTERACTION'},
        {'step_number': 10, 'action': 'ASSERT_VISIBLE', 'selector': '[data-testid="stock-difference"]', 'risk_level': 'READ_ONLY'},
        {'step_number': 11, 'action': 'SCREENSHOT', 'risk_level': 'READ_ONLY'},
        {'step_number': 12, 'action': 'FILL', 'selector': '[data-testid="stock-notes"]', 'value': f'Audit task #{task.source_task_id} {run_tag}', 'risk_level': 'SAFE_INTERACTION'},
        {'step_number': 13, 'action': 'CLICK', 'selector': '[data-testid="stock-submit"]', 'risk_level': 'SAFE_INTERACTION'},
        {'step_number': 14, 'action': 'ASSERT_TABLE_ROW', 'selector': '[data-testid="stock-history-table"]', 'expected': '120', 'risk_level': 'READ_ONLY'},
        {'step_number': 15, 'action': 'SCREENSHOT', 'risk_level': 'READ_ONLY'},
    ]


def build_ifive_iot_nav_steps(task: ExternalTaskImport, run_tag: str) -> List[Dict[str, Any]]:
    return [
        {'step_number': 1, 'action': 'NAVIGATE', 'path': '/', 'risk_level': 'READ_ONLY', 'expected': 'Homepage loads successfully.'},
        {'step_number': 2, 'action': 'ASSERT_VISIBLE', 'selector': 'button:has-text("Products")', 'risk_level': 'READ_ONLY', 'expected': 'Main navigation visible.'},
        {'step_number': 3, 'action': 'SCREENSHOT', 'risk_level': 'READ_ONLY'},
        {'step_number': 4, 'action': 'CLICK', 'selector': 'button:has-text("Products")', 'risk_level': 'SAFE_INTERACTION', 'expected': 'Products menu opens.'},
        {'step_number': 5, 'action': 'CLICK', 'selector': 'a[href="/products/iot"]', 'risk_level': 'SAFE_INTERACTION', 'expected': 'iFive IoT page opens.'},
        {'step_number': 6, 'action': 'ASSERT_URL', 'expected': '/products/iot', 'risk_level': 'READ_ONLY'},
        {'step_number': 7, 'action': 'ASSERT_VISIBLE', 'selector': 'a[href="/products/iot"]', 'risk_level': 'READ_ONLY'},
        {'step_number': 8, 'action': 'SCREENSHOT', 'risk_level': 'READ_ONLY'},
    ]


def prepare_test_plan(db: DBSession, import_id: int) -> ExternalTaskImport:
    task = db.get(ExternalTaskImport, import_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Import {import_id} not found.')

    template_type = classify_template_type(task)
    task.template_type = template_type

    if template_type == 'UNSUPPORTED':
        task.import_status = 'NEED_CLARITY'
        db.commit()
        db.refresh(task)
        return task

    from app.models.operator import Operator
    op_row = db.query(Operator.id).first()
    op_id = op_row[0] if op_row else 1

    # Find or create TestProject
    test_project = db.scalar(
        select(TestProject).where(TestProject.access_project_id == task.project_id)
    )
    if not test_project:
        test_project = TestProject(
            access_project_id=task.project_id,
            name=task.project_name,
            code=f'PRJ-{task.project_id}',
            created_by=op_id,
        )
        db.add(test_project)
        db.flush()

    # Find or create TestModule
    module = db.scalar(
        select(TestModule).where(
            TestModule.project_id == test_project.id,
            TestModule.name == task.module_name,
        )
    )
    mod_code = task.module_name[:20].upper().replace(' ', '_') or 'MOD_GENERAL'
    if not module:
        module = TestModule(
            access_project_id=task.project_id,
            project_id=test_project.id,
            name=task.module_name,
            code=mod_code,
            description=f'Module for {task.module_name}',
            created_by=op_id,
        )
        db.add(module)
        db.flush()

    # Find or create Suite
    suite = db.scalar(
        select(ManagedTestSuite).where(
            ManagedTestSuite.project_id == test_project.id,
            ManagedTestSuite.module_id == module.id,
        )
    )
    if not suite:
        suite = ManagedTestSuite(
            access_project_id=task.project_id,
            project_id=test_project.id,
            module_id=module.id,
            name=f'{task.module_name} Suite',
            code=f'STE-{module.id}',
            created_by=op_id,
        )
        db.add(suite)
        db.flush()

    run_tag = f'{task.source_task_id}_r{task.source_revision}'
    if template_type == 'EMPLOYEE_CREATE':
        raw_steps = build_employee_create_steps(task, run_tag)
    elif template_type == 'IFIVE_IOT_NAV':
        raw_steps = build_ifive_iot_nav_steps(task, run_tag)
    else:
        raw_steps = build_stock_count_steps(task, run_tag)

    formatted_steps = []
    for step in raw_steps:
        payload = {k: v for k, v in step.items() if k != 'step_number'}
        formatted_steps.append({
            'step_number': step['step_number'],
            'action': json.dumps(payload),
            'expected_result': step.get('expected') or step.get('path') or step.get('value') or 'Step completed',
        })

    snapshot_json = json.dumps({'steps': formatted_steps})

    test_case = db.scalar(
        select(ManagedTestCase).where(
            ManagedTestCase.access_project_id == task.project_id,
            ManagedTestCase.title == f'Import #{task.source_task_id} Rev {task.source_revision}: {task.title}',
        )
    )
    if not test_case:
        test_case = ManagedTestCase(
            access_project_id=task.project_id,
            project_id=test_project.id,
            module_id=module.id,
            suite_id=suite.id,
            case_key=f'IMP-{task.source_task_id}-{task.source_revision}',
            title=f'Import #{task.source_task_id} Rev {task.source_revision}: {task.title}',
            objective=task.description or 'Imported from Mock Task Portal',
            lifecycle_state='APPROVED',
            current_version=1,
            created_by=op_id,
        )
        db.add(test_case)
        db.flush()

        version = TestCaseVersion(
            access_project_id=task.project_id,
            test_case_id=test_case.id,
            version_number=1,
            snapshot_json=snapshot_json,
            change_summary='Generated from deterministic template',
            source_state='APPROVED',
            created_by=op_id,
        )
        db.add(version)
        db.flush()

    task.linked_test_plan_id = test_case.id
    task.import_status = 'PLAN_PREPARED'
    db.commit()
    db.refresh(task)
    return task


def approve_test_plan(db: DBSession, import_id: int, approver_username: str) -> ExternalTaskImport:
    task = db.get(ExternalTaskImport, import_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Import {import_id} not found.')

    if task.import_status not in {'PLAN_PREPARED', 'DRAFT'}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Task cannot be approved in state {task.import_status}. Prepare plan first.',
        )

    # Developer protection: assigned developer cannot approve own task
    if task.assigned_developer and task.assigned_developer.lower() == approver_username.lower():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f'Developer {approver_username!r} cannot self-approve their own task.',
        )

    task.import_status = 'APPROVED'
    task.approved_by = approver_username
    task.approved_at = datetime.utcnow()
    db.commit()
    db.refresh(task)
    return task


def execute_and_callback(db: DBSession, import_id: int) -> ExternalTaskImport:
    task = db.get(ExternalTaskImport, import_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Import {import_id} not found.')

    if task.import_status != 'APPROVED':
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Task must be APPROVED before running execution.',
        )

    target = _ensure_demo_target(db, task.project_id)
    
    # Check for Phase 5 Test Plan
    from app.models.test_plan import TestPlan
    test_plan = db.query(TestPlan).filter_by(external_task_import_id=import_id).first()
    
    plan_id_for_run = None
    from app.models.operator import Operator
    op_row = db.query(Operator.id).first()
    first_operator_id = op_row[0] if op_row else 1
    if test_plan:
        if test_plan.status != 'APPROVED':
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='TestPlan must be APPROVED before execution.')
        plan_id_for_run = test_plan.id
        
        run = automated_execution.create_run_from_plan(
            db=db,
            target=target,
            name=f'Run Import #{task.source_task_id} Rev {task.source_revision}',
            description=task.title,
            plan_id=plan_id_for_run,
            timeout_seconds=60,
            max_retries=0,
            created_by=first_operator_id,
        )
    else:
        # Legacy Phase 3 path
        if not task.linked_test_plan_id:
            prepare_test_plan(db, import_id)
            db.refresh(task)
            
        run = automated_execution.create_run(
            db=db,
            target=target,
            name=f'Run Import #{task.source_task_id} Rev {task.source_revision}',
            description=task.title,
            case_ids=[task.linked_test_plan_id],
            timeout_seconds=60,
            max_retries=0,
            created_by=first_operator_id,
        )

    # Queue the run for execution
    from app.models.automated_execution import ExecutionJob
    run.status = 'QUEUED'
    db.add(ExecutionJob(project_id=run.project_id, run_id=run.id, status='QUEUED'))

    task.linked_run_id = run.id
    task.import_status = 'RUNNING'
    db.commit()

    # Execute run synchronously via Playwright execution engine (targeted at this specific run)
    completed_run = automated_execution.execute_next_job(db, worker_key='local-stage10-worker', target_run_id=run.id)

    # Evaluate execution status
    run_status = completed_run.status if completed_run else 'FAILED'
    summary_text = (completed_run.safe_error_message if completed_run else 'Execution failed') or 'Execution completed.'

    if run_status == 'PASSED':
        qa_res = 'PASS'
        portal_status = 'QA_PASSED'
        task.import_status = 'COMPLETED'
    elif run_status == 'BLOCKED':
        qa_res = 'BLOCKED'
        portal_status = 'NEED_CLARITY'
        task.import_status = 'NEED_CLARITY'
    else:
        qa_res = 'FAIL'
        portal_status = 'REWORK'
        task.import_status = 'COMPLETED'

    # Defect management: Create/link defect on FAILED (Do NOT create defect on BLOCKED)
    if run_status == 'FAILED' and completed_run:
        existing_defect = db.scalar(
            select(Defect).where(Defect.automated_run_id == completed_run.id)
        )
        if not existing_defect:
            defect_key = f"DEF-T{task.source_task_id}-R{task.source_revision}"
            # Ensure unique key if duplicate exists
            dup = db.scalar(select(Defect).where(Defect.defect_key == defect_key))
            if dup:
                defect_key = f"DEF-T{task.source_task_id}-R{task.source_revision}-{completed_run.id}"
            
            # Lookup the test project ID
            test_project = db.scalar(select(TestProject).where(TestProject.access_project_id == task.project_id))
            test_project_id = test_project.id if test_project else task.project_id

            from app.models.operator import Operator
            op_row = db.query(Operator.id).first()
            first_op_id = op_row[0] if op_row else 1
            defect = Defect(
                access_project_id=task.project_id,
                defect_key=defect_key,
                title=f"Task #{task.source_task_id} Rev {task.source_revision} Failure: {task.title}",
                description=summary_text,
                project_id=test_project_id,
                test_case_id=task.linked_test_plan_id,
                automated_run_id=completed_run.id,
                severity='HIGH',
                priority='HIGH',
                status='NEW',
                reporter_id=first_op_id,
                created_by=first_op_id,
                environment=task.environment or 'local',
                actual_result=summary_text,
                expected_result=task.expected_result or 'All automated steps completed successfully',
            )
            db.add(defect)
            db.flush()

            # Link artifacts
            from app.models.automated_execution import ExecutionArtifact
            artifacts = db.scalars(
                select(ExecutionArtifact).where(ExecutionArtifact.run_id == completed_run.id)
            ).all()
            from app.models.defect import DefectEvidenceLink
            for art in artifacts:
                db.add(DefectEvidenceLink(
                    project_id=task.project_id,
                    defect_id=defect.id,
                    execution_artifact_id=art.id,
                    link_type='SOURCE',
                    created_by=first_op_id,
                ))

    # Perform result callback to Mock Task Portal
    # Stale revision check: reject callback if newer revision exists
    newer_revision = db.scalar(
        select(ExternalTaskImport).where(
            ExternalTaskImport.project_id == task.project_id,
            ExternalTaskImport.source_system == task.source_system,
            ExternalTaskImport.source_task_id == task.source_task_id,
            ExternalTaskImport.source_revision > task.source_revision,
        )
    )

    if newer_revision:
        task.callback_status = 'SKIPPED_STALE'
        task.callback_error = f'Callback skipped because newer revision {newer_revision.source_revision} exists.'
    else:
        connector = MockTaskPortalConnector()
        callback_payload = {
            'source_system': task.source_system,
            'source_task_id': task.source_task_id,
            'source_revision': task.source_revision,
            'autoqa_run_id': completed_run.run_key if completed_run else f'ARUN-{run.id}',
            'qa_result': qa_res,
            'task_status': portal_status,
            'summary': summary_text,
            'severity': 'HIGH' if qa_res == 'FAIL' else None,
            'report_url': f'{settings.backend_self_url}/api/automated-runs/{run.id}',
            'completed_at': datetime.utcnow().isoformat(),
        }

        try:
            connector.send_qa_result(task.source_task_id, task.source_revision, callback_payload)
            task.callback_status = 'SUCCESS'
            task.callback_error = None
        except Exception as err:
            task.callback_status = 'FAILED'
            task.callback_error = str(err)

    db.commit()
    db.refresh(task)
    return task


def retry_callback(db: DBSession, import_id: int) -> ExternalTaskImport:
    task = db.get(ExternalTaskImport, import_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Import {import_id} not found.')

    if task.import_status not in {'COMPLETED', 'NEED_CLARITY'}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Cannot retry callback for task in state {task.import_status}. Must be COMPLETED or NEED_CLARITY.',
        )

    newer_revision = db.scalar(
        select(ExternalTaskImport).where(
            ExternalTaskImport.project_id == task.project_id,
            ExternalTaskImport.source_system == task.source_system,
            ExternalTaskImport.source_task_id == task.source_task_id,
            ExternalTaskImport.source_revision > task.source_revision,
        )
    )

    if newer_revision:
        task.callback_status = 'SKIPPED_STALE'
        task.callback_error = f'Callback skipped because newer revision {newer_revision.source_revision} exists.'
        db.commit()
        db.refresh(task)
        return task

    qa_res = 'PASS' if task.import_status == 'COMPLETED' and not task.callback_error else 'FAIL'
    if task.import_status == 'NEED_CLARITY':
        qa_res = 'BLOCKED'
        portal_status = 'NEED_CLARITY'
    elif task.import_status == 'COMPLETED':
        # Check if linked run passed
        if task.linked_run_id:
            run = db.get(AutomatedRun, task.linked_run_id)
            if run and run.status == 'PASSED':
                qa_res = 'PASS'
                portal_status = 'QA_PASSED'
            else:
                qa_res = 'FAIL'
                portal_status = 'REWORK'
        else:
            portal_status = 'QA_PASSED'
    else:
        portal_status = 'REWORK'

    connector = MockTaskPortalConnector()
    callback_payload = {
        'source_system': task.source_system,
        'source_task_id': task.source_task_id,
        'source_revision': task.source_revision,
        'autoqa_run_id': f'ARUN-{task.linked_run_id}' if task.linked_run_id else 'ARUN-0',
        'qa_result': qa_res,
        'task_status': portal_status,
        'summary': f'Retry callback for task #{task.source_task_id} Rev {task.source_revision}',
        'severity': 'HIGH' if qa_res == 'FAIL' else None,
        'report_url': f'{settings.backend_self_url}/api/task-imports/{task.id}',
        'completed_at': datetime.utcnow().isoformat(),
    }

    try:
        connector.send_qa_result(task.source_task_id, task.source_revision, callback_payload)
        task.callback_status = 'SUCCESS'
        task.callback_error = None
    except Exception as err:
        task.callback_status = 'FAILED'
        task.callback_error = str(err)

    db.commit()
    db.refresh(task)
    return task
