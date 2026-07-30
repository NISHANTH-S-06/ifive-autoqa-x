"""Seed data for Demo Product Website.

Uses local disposable demo fixtures — no real credentials or systems.
Idempotent execution.
"""
from __future__ import annotations

from datetime import datetime
from sqlalchemy.orm import Session as DBSession

from app.auth import hash_password
from app.models import Department, DemoSetting, Employee, Product, User

DEMO_USERS = [
    {'username': 'demo_admin',          'display_name': 'Demo Administrator', 'role': 'DEMO_ADMIN',      'password': 'Admin@Demo123'},
    {'username': 'demo_hr_user',        'display_name': 'Demo HR Specialist', 'role': 'HR_USER',         'password': 'Hr@Demo123'},
    {'username': 'demo_inventory_user', 'display_name': 'Demo Inventory Lead', 'role': 'INVENTORY_USER',  'password': 'Inv@Demo123'},
    {'username': 'demo_viewer',         'display_name': 'Demo System Viewer', 'role': 'VIEWER',          'password': 'View@Demo123'},
]

DEMO_DEPTS = ['Development', 'HR', 'Testing', 'Sales']

DEMO_PRODUCTS = [
    {'code': 'PRD-001', 'name': 'Enterprise ERP License',    'qty': 100},
    {'code': 'PRD-002', 'name': 'Industrial IoT Gateway',    'qty': 45},
    {'code': 'PRD-003', 'name': 'Handheld Barcode Scanner',  'qty': 25},
]

KNOWN_BUG_KEYS = [
    'employee_save_failure',
    'employee_success_message_missing',
    'employee_table_refresh_failure',
    'stock_difference_error',
    'api_delay',
    'login_failure_mode',
]


def seed(db: DBSession) -> None:
    """Seed demo data idempotently."""
    # 1. Users
    existing_user = db.query(User).filter_by(username='demo_admin').first()
    if not existing_user:
        for u in DEMO_USERS:
            db.add(User(
                username=u['username'],
                display_name=u['display_name'],
                role=u['role'],
                password_hash=hash_password(u['password']),
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            ))
        db.flush()

    # 2. Departments
    dept_map = {}
    for dname in DEMO_DEPTS:
        dept = db.query(Department).filter_by(name=dname).first()
        if not dept:
            dept = Department(name=dname)
            db.add(dept)
            db.flush()
        dept_map[dname] = dept.id

    # 3. Products
    for p in DEMO_PRODUCTS:
        prod = db.query(Product).filter_by(product_code=p['code']).first()
        if not prod:
            db.add(Product(
                product_code=p['code'],
                name=p['name'],
                current_quantity=p['qty'],
            ))
        db.flush()

    # 4. Demo Settings (bug toggles)
    for key in KNOWN_BUG_KEYS:
        setting = db.get(DemoSetting, key)
        if not setting:
            db.add(DemoSetting(
                key=key,
                enabled=False,
                value=None,
                updated_at=datetime.utcnow(),
            ))

    # 5. Initial Sample Employee
    hr_dept_id = dept_map.get('HR', 1)
    existing_emp = db.query(Employee).filter_by(email='john.doe@demo.local').first()
    if not existing_emp:
        db.add(Employee(
            employee_code='EMP-001',
            name='John Doe',
            email='john.doe@demo.local',
            department_id=hr_dept_id,
            joining_date='2026-01-15',
            active=True,
            notes='Initial demo employee record',
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        ))

    db.commit()
    print('[seed] Demo Product data seeded idempotently.')
