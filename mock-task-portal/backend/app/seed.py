"""Demo seed data for Mock Task Portal.

Uses only local disposable values — no real company credentials.
"""
from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.auth import hash_password
from app.models.task import Task
from app.models.task_history import TaskHistory
from app.models.user import User


DEMO_USERS = [
    {'username': 'admin',     'display_name': 'Demo Admin',     'role': 'SUPERADMIN', 'password': 'Admin@Demo123'},
    {'username': 'dev1',      'display_name': 'Demo Developer',  'role': 'DEVELOPER',  'password': 'Dev@Demo123'},
    {'username': 'tester1',   'display_name': 'Demo Tester',    'role': 'TESTER',     'password': 'Test@Demo123'},
    {'username': 'delivery1', 'display_name': 'Demo Delivery',  'role': 'DELIVERY',   'password': 'Del@Demo123'},
    {'username': 'viewer1',   'display_name': 'Demo Viewer',    'role': 'VIEWER',     'password': 'View@Demo123'},
]


def seed(db: Session) -> None:
    """Seed demo users and tasks if not already seeded."""
    existing = db.query(User).filter_by(username='admin').first()
    if existing:
        return  # Already seeded

    # ── Users ──
    user_map: dict[str, User] = {}
    for u in DEMO_USERS:
        user = User(
            username=u['username'],
            display_name=u['display_name'],
            role=u['role'],
            password_hash=hash_password(u['password']),
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(user)
        user_map[u['username']] = user
    db.flush()

    # ── Task 1: Employee Form Save Button — in ASSIGNED state ──
    task1 = Task(
        task_code='DEMO-001',
        project_name='Demo ERP',
        module_name='HR Module',
        title='Employee Form Save Button',
        description='Verify that the Employee Form save button correctly persists data to the database.',
        assigned_developer='dev1',
        assigned_tester='tester1',
        task_given_by='admin',
        target_date=(datetime.utcnow() + timedelta(days=7)).strftime('%Y-%m-%d'),
        priority='HIGH',
        application_url='http://localhost:3000',
        page_path='/hr/employees/new',
        environment='local',
        expected_result='Employee record is saved successfully. Success toast is shown.',
        acceptance_criteria='Given valid employee data, when user clicks Save, then record is created and confirmation shown.',
        test_data='name=John Demo, department=Engineering, start_date=2026-01-15',
        status='ASSIGNED',
        revision=0,
        created_at=datetime.utcnow() - timedelta(days=2),
        updated_at=datetime.utcnow() - timedelta(days=1),
    )
    db.add(task1)
    db.flush()
    db.add(TaskHistory(task_id=task1.id, previous_status=None, new_status='CREATED', changed_by='admin', reason='Task created', timestamp=datetime.utcnow() - timedelta(days=2)))
    db.add(TaskHistory(task_id=task1.id, previous_status='CREATED', new_status='ASSIGNED', changed_by='admin', reason='Assigned to dev1', timestamp=datetime.utcnow() - timedelta(days=1)))

    # ── Task 2: Already in TESTING_L2 ──
    task2 = Task(
        task_code='DEMO-002',
        project_name='Demo ERP',
        module_name='Inventory Module',
        title='Stock Count Reconciliation',
        description='Verify that the stock count reconciliation correctly adjusts inventory levels.',
        assigned_developer='dev1',
        assigned_tester='tester1',
        task_given_by='admin',
        target_date=(datetime.utcnow() + timedelta(days=3)).strftime('%Y-%m-%d'),
        priority='CRITICAL',
        application_url='http://localhost:3000',
        page_path='/inventory/stock-count',
        environment='local',
        expected_result='Stock count reconciliation updates inventory levels accurately.',
        acceptance_criteria='Given stock count data, when submitted, then inventory levels update and audit log created.',
        test_data='item=SKU-001, counted=50, system=45, adjustment=+5',
        developer_notes='Tested locally in Chrome. All edge cases handled. Rounding fix applied in commit abc123.',
        status='TESTING_L2',
        revision=1,
        created_at=datetime.utcnow() - timedelta(days=5),
        updated_at=datetime.utcnow() - timedelta(hours=3),
        testing_l2_at=datetime.utcnow() - timedelta(hours=3),
    )
    db.add(task2)
    db.flush()
    db.add(TaskHistory(task_id=task2.id, previous_status=None, new_status='CREATED', changed_by='admin', reason='Task created', timestamp=datetime.utcnow() - timedelta(days=5)))
    db.add(TaskHistory(task_id=task2.id, previous_status='CREATED', new_status='ASSIGNED', changed_by='admin', reason='Assigned', timestamp=datetime.utcnow() - timedelta(days=4)))
    db.add(TaskHistory(task_id=task2.id, previous_status='ASSIGNED', new_status='IN_PROGRESS', changed_by='dev1', reason=None, timestamp=datetime.utcnow() - timedelta(days=3)))
    db.add(TaskHistory(task_id=task2.id, previous_status='IN_PROGRESS', new_status='TESTING_L1', changed_by='dev1', reason=None, timestamp=datetime.utcnow() - timedelta(days=2)))
    db.add(TaskHistory(task_id=task2.id, previous_status='TESTING_L1', new_status='TESTING_L2', changed_by='dev1', reason='Ready for L2 QA', timestamp=datetime.utcnow() - timedelta(hours=3)))

    # ── Task 3: Generic form without expected result (For missing info gate) ──
    task3 = Task(
        task_code='DEMO-003',
        project_name='Demo ERP',
        module_name='E2E',
        title='Generic form without expected result',
        description='A generic task that lacks enough info for AI.',
        assigned_developer='dev1',
        assigned_tester='tester1',
        task_given_by='admin',
        target_date=(datetime.utcnow() + timedelta(days=3)).strftime('%Y-%m-%d'),
        priority='LOW',
        application_url='http://localhost:3000',
        page_path='/',
        environment='local',
        expected_result='',
        acceptance_criteria='',
        test_data='',
        status='TESTING_L2',
        revision=0,
        created_at=datetime.utcnow() - timedelta(days=5),
        updated_at=datetime.utcnow() - timedelta(hours=3),
        testing_l2_at=datetime.utcnow() - timedelta(hours=3),
    )
    db.add(task3)

    # ── Task 4: Unsafe script execution ──
    task4 = Task(
        task_code='DEMO-004',
        project_name='Demo ERP',
        module_name='E2E',
        title='Unsafe script execution',
        description='Delete all records in the database bypass.',
        assigned_developer='dev1',
        assigned_tester='tester1',
        task_given_by='admin',
        target_date=(datetime.utcnow() + timedelta(days=3)).strftime('%Y-%m-%d'),
        priority='HIGH',
        application_url='http://localhost:3000',
        page_path='/',
        environment='local',
        expected_result='Script execution succeeds.',
        acceptance_criteria='',
        test_data='',
        status='TESTING_L2',
        revision=0,
        created_at=datetime.utcnow() - timedelta(days=5),
        updated_at=datetime.utcnow() - timedelta(hours=3),
        testing_l2_at=datetime.utcnow() - timedelta(hours=3),
    )
    db.add(task4)

    # ── Task 5: Employee Real Flow Test ──
    task5 = Task(
        task_code='DEMO-005',
        project_name='Demo ERP',
        module_name='E2E',
        title='Create Employee',
        description='Normal E2E test. Requires admin role.',
        assigned_developer='dev1',
        assigned_tester='tester1',
        task_given_by='admin',
        target_date=(datetime.utcnow() + timedelta(days=3)).strftime('%Y-%m-%d'),
        priority='HIGH',
        application_url='http://localhost:3000',
        page_path='/',
        environment='local',
        expected_result='Passes successfully.',
        acceptance_criteria='',
        test_data='',
        status='TESTING_L2',
        revision=0,
        created_at=datetime.utcnow() - timedelta(days=5),
        updated_at=datetime.utcnow() - timedelta(hours=3),
        testing_l2_at=datetime.utcnow() - timedelta(hours=3),
    )
    db.add(task5)

    # ── Task 6: iFive Corporate Website - Verify iFive IoT Navigation ──
    task6 = Task(
        task_code='IFIVE-001',
        project_name='iFive Corporate Website',
        module_name='Products',
        title='Verify iFive IoT Navigation',
        description='Verify that a user can successfully navigate from the iFive homepage to the Products section and open the "iFive IoT" product page.',
        assigned_developer='dev1',
        assigned_tester='Superadmin',
        task_given_by='admin',
        target_date=(datetime.utcnow() + timedelta(days=7)).strftime('%Y-%m-%d'),
        priority='Medium',
        application_url='https://ifive.in/',
        page_path='/',
        environment='Production (Read Only)',
        expected_result='User should be able to Open https://ifive.in/ -> Navigate to Products -> Click "iFive IoT" -> iFive IoT page should open successfully -> HTTP response should be successful -> No browser errors -> Evidence should be captured',
        acceptance_criteria='Given website https://ifive.in/, Module: Products, Feature: iFive IoT Navigation. Flow: Homepage -> Products -> iFive IoT. Risk: Low.',
        test_data='',
        status='TESTING_L2',
        revision=1,
        created_at=datetime.utcnow() - timedelta(days=1),
        updated_at=datetime.utcnow(),
        testing_l2_at=datetime.utcnow(),
    )
    db.add(task6)

    db.commit()
    print('[seed] Demo data seeded: 5 users, 6 tasks.')
