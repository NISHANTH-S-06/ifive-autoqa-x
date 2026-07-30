"""Pydantic schemas for employees and departments."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class DepartmentOut(BaseModel):
    id: int
    name: str

    model_config = {'from_attributes': True}


class EmployeeCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    email: str = Field(..., min_length=3, max_length=128)
    department_id: int
    joining_date: str = Field(..., min_length=1, max_length=32)
    active: bool = True
    notes: Optional[str] = Field(None, max_length=500)

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        if '@' not in v or '.' not in v.split('@')[-1]:
            raise ValueError('Invalid email format')
        return v.lower().strip()


class EmployeeUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=128)
    email: Optional[str] = Field(None, min_length=3, max_length=128)
    department_id: Optional[int] = None
    joining_date: Optional[str] = Field(None, min_length=1, max_length=32)
    active: Optional[bool] = None
    notes: Optional[str] = Field(None, max_length=500)

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if '@' not in v or '.' not in v.split('@')[-1]:
                raise ValueError('Invalid email format')
            return v.lower().strip()
        return v


class EmployeeOut(BaseModel):
    id: int
    employee_code: str
    name: str
    email: str
    department_id: int
    department_name: Optional[str] = None
    joining_date: str
    active: bool
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {'from_attributes': True}
