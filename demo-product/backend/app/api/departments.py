"""Departments API router."""
from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DBSession

from app.auth import AuthContext, get_auth_context
from app.database import get_db
from app.models.department import Department
from app.schemas.employee import DepartmentOut

router = APIRouter(prefix='/api/departments', tags=['departments'])


@router.get('', response_model=List[DepartmentOut])
def list_departments(
    ctx: AuthContext = Depends(get_auth_context),
    db: DBSession = Depends(get_db),
) -> List[DepartmentOut]:
    depts = db.query(Department).order_by(Department.name.asc()).all()
    return [DepartmentOut.model_validate(d) for d in depts]
