"""Employees API router."""
from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session as DBSession

from app.auth import AuthContext, get_auth_context
from app.database import get_db
from app.schemas.employee import EmployeeCreate, EmployeeOut, EmployeeUpdate
from app.services import employee_service

router = APIRouter(prefix='/api/employees', tags=['employees'])


@router.get('', response_model=List[EmployeeOut])
def list_employees(
    ctx: AuthContext = Depends(get_auth_context),
    db: DBSession = Depends(get_db),
) -> List[EmployeeOut]:
    return employee_service.list_employees(db)


@router.post('', response_model=EmployeeOut, status_code=status.HTTP_201_CREATED)
def create_employee(
    payload: EmployeeCreate,
    ctx: AuthContext = Depends(get_auth_context),
    db: DBSession = Depends(get_db),
) -> EmployeeOut:
    ctx.require_role('DEMO_ADMIN', 'HR_USER')
    return employee_service.create_employee(db, payload)


@router.get('/{employee_id}', response_model=EmployeeOut)
def get_employee(
    employee_id: int,
    ctx: AuthContext = Depends(get_auth_context),
    db: DBSession = Depends(get_db),
) -> EmployeeOut:
    return employee_service.get_employee_by_id(db, employee_id)


@router.patch('/{employee_id}', response_model=EmployeeOut)
def update_employee(
    employee_id: int,
    payload: EmployeeUpdate,
    ctx: AuthContext = Depends(get_auth_context),
    db: DBSession = Depends(get_db),
) -> EmployeeOut:
    ctx.require_role('DEMO_ADMIN', 'HR_USER')
    return employee_service.update_employee(db, employee_id, payload)
