from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProductCode(str, Enum):
  ERP = 'ERP'
  HRMS = 'HRMS'
  CRM = 'CRM'
  IIOT = 'IIOT'
  INTEGRATION = 'INTEGRATION'
  AUTOQA = 'AUTOQA'


class ProjectCreate(BaseModel):
  name: str = Field(min_length=1, max_length=160)
  product_code: str = Field(min_length=1, max_length=80)
  description: str | None = Field(default=None, max_length=500)
  base_url: str | None = Field(default=None, max_length=500)
  environment: str = 'local'

  @field_validator('name', 'environment')
  @classmethod
  def strip_required(cls, value: str) -> str:
    if not value.strip():
      raise ValueError('must not be blank')
    return value.strip()


class ProjectRead(ProjectCreate):
  model_config = ConfigDict(from_attributes=True)

  id: int
  is_active: bool
  created_at: datetime
  updated_at: datetime


class ProjectMemberCreate(BaseModel):
  operator_id: int = Field(gt=0)
  role: str = Field(pattern='^(OWNER|ADMIN|APPROVER|TESTER|VIEWER)$')


class ProjectMemberUpdate(BaseModel):
  role: str | None = Field(default=None, pattern='^(OWNER|ADMIN|APPROVER|TESTER|VIEWER)$')
  status: str | None = Field(default=None, pattern='^(ACTIVE|INACTIVE)$')


class ProjectMemberRead(BaseModel):
  model_config = ConfigDict(from_attributes=True)

  id: int
  project_id: int
  operator_id: int
  role: str
  status: str
  joined_at: datetime
  created_at: datetime
  updated_at: datetime
  deactivated_at: datetime | None
