"""Service for Employee management."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session as DBSession

from app.models.department import Department
from app.models.employee import Employee
from app.schemas.employee import EmployeeCreate, EmployeeOut, EmployeeUpdate
from app.services.demo_setting_service import is_bug_enabled


def list_employees(db: DBSession) -> List[EmployeeOut]:
    employees = db.query(Employee).order_by(Employee.id.desc()).all()

    # Bug toggle: employee_table_refresh_failure
    # If enabled, omit the latest created employee from the returned list
    if is_bug_enabled(db, 'employee_table_refresh_failure') and len(employees) > 1:
        employees = employees[1:]

    dept_map = {d.id: d.name for d in db.query(Department).all()}

    result = []
    for emp in employees:
        out = EmployeeOut.model_validate(emp)
        out.department_name = dept_map.get(emp.department_id, 'Unknown')
        result.append(out)
    return result


def get_employee_by_id(db: DBSession, employee_id: int) -> EmployeeOut:
    emp = db.get(Employee, employee_id)
    if not emp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Employee {employee_id} not found')
    dept = db.get(Department, emp.department_id)
    out = EmployeeOut.model_validate(emp)
    out.department_name = dept.name if dept else 'Unknown'
    return out


def create_employee(db: DBSession, payload: EmployeeCreate) -> EmployeeOut:
    # Bug toggle check: employee_save_failure
    if is_bug_enabled(db, 'employee_save_failure'):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Save failed: Internal Server Error triggered by active bug toggle (employee_save_failure)',
        )

    # Check department exists
    dept = db.get(Department, payload.department_id)
    if not dept:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Department {payload.department_id} not found')

    # Check duplicate email
    existing = db.query(Employee).filter(Employee.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f'Employee with email {payload.email!r} already exists')

    # Generate employee code
    count = db.query(Employee).count()
    emp_code = f'EMP-{(count + 1):03d}'

    emp = Employee(
        employee_code=emp_code,
        name=payload.name,
        email=payload.email,
        department_id=payload.department_id,
        joining_date=payload.joining_date,
        active=payload.active,
        notes=payload.notes,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(emp)
    db.commit()
    db.refresh(emp)

    out = EmployeeOut.model_validate(emp)
    out.department_name = dept.name
    return out


def update_employee(db: DBSession, employee_id: int, payload: EmployeeUpdate) -> EmployeeOut:
    emp = db.get(Employee, employee_id)
    if not emp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Employee {employee_id} not found')

    if payload.email is not None and payload.email != emp.email:
        existing = db.query(Employee).filter(Employee.email == payload.email, Employee.id != employee_id).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f'Email {payload.email!r} already in use')

    for field, val in payload.model_dump(exclude_unset=True).items():
        setattr(emp, field, val)

    emp.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(emp)

    dept = db.get(Department, emp.department_id)
    out = EmployeeOut.model_validate(emp)
    out.department_name = dept.name if dept else 'Unknown'
    return out
