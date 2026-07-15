from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.test_management import Page


class EnvironmentType(str, Enum):
  LOCAL = 'LOCAL'
  DEVELOPMENT = 'DEVELOPMENT'
  QA = 'QA'
  STAGING = 'STAGING'
  PRODUCTION = 'PRODUCTION'


class TargetLifecycle(str, Enum):
  DRAFT = 'DRAFT'
  IN_REVIEW = 'IN_REVIEW'
  APPROVED = 'APPROVED'
  REJECTED = 'REJECTED'
  DISABLED = 'DISABLED'
  ARCHIVED = 'ARCHIVED'


class CheckStatus(str, Enum):
  PENDING = 'PENDING'
  RUNNING = 'RUNNING'
  REACHABLE = 'REACHABLE'
  UNREACHABLE = 'UNREACHABLE'
  POLICY_BLOCKED = 'POLICY_BLOCKED'
  DNS_ERROR = 'DNS_ERROR'
  TCP_ERROR = 'TCP_ERROR'
  TLS_ERROR = 'TLS_ERROR'
  TIMEOUT = 'TIMEOUT'
  HTTP_ERROR = 'HTTP_ERROR'
  REDIRECT_BLOCKED = 'REDIRECT_BLOCKED'
  CANCELLED = 'CANCELLED'


class CheckMethod(str, Enum):
  HEAD = 'HEAD'
  GET = 'GET'


class SecretSource(str, Enum):
  PROMPT_AT_USE = 'PROMPT_AT_USE'
  NONE = 'NONE'


def _strip_required(value: str) -> str:
  value = value.strip()
  if not value:
    raise ValueError('must not be blank')
  if any(ord(ch) < 32 for ch in value):
    raise ValueError('control characters are not allowed')
  return value


class ConnectionTargetCreate(BaseModel):
  project_id: int | None = Field(default=None, gt=0)
  target_key: str = Field(min_length=2, max_length=60)
  name: str = Field(min_length=1, max_length=180)
  description: str | None = Field(default=None, max_length=2000)
  environment_type: EnvironmentType
  base_url: str = Field(min_length=8, max_length=1000)
  allowed_probe_paths: list[str] = Field(default_factory=lambda: ['/'], min_length=1, max_length=10)
  tls_required: bool = True
  tls_verify: bool = True
  connection_timeout_seconds: int = Field(default=5, ge=1, le=15)
  owner_operator_id: int | None = None

  @field_validator('target_key', 'name', 'base_url')
  @classmethod
  def strip_required(cls, value: str) -> str:
    return _strip_required(value)


class ConnectionTargetUpdate(BaseModel):
  name: str | None = Field(default=None, min_length=1, max_length=180)
  description: str | None = Field(default=None, max_length=2000)
  environment_type: EnvironmentType | None = None
  base_url: str | None = Field(default=None, min_length=8, max_length=1000)
  allowed_probe_paths: list[str] | None = Field(default=None, min_length=1, max_length=10)
  tls_required: bool | None = None
  tls_verify: bool | None = None
  connection_timeout_seconds: int | None = Field(default=None, ge=1, le=15)
  owner_operator_id: int | None = None
  version: int | None = Field(default=None, ge=1)


class LifecycleReason(BaseModel):
  reason: str | None = Field(default=None, max_length=500)


class ConnectionCheckCreate(BaseModel):
  method: CheckMethod = CheckMethod.HEAD
  probe_path: str = Field(default='/', min_length=1, max_length=500)


class CredentialProfileCreate(BaseModel):
  model_config = ConfigDict(extra='forbid')
  profile_name: str = Field(min_length=1, max_length=120)
  username_hint: str | None = Field(default=None, max_length=160)
  secret_source: SecretSource = SecretSource.NONE
  enabled: bool = True

  @field_validator('profile_name')
  @classmethod
  def strip_profile(cls, value: str) -> str:
    return _strip_required(value)


class CredentialProfileUpdate(BaseModel):
  model_config = ConfigDict(extra='forbid')
  profile_name: str | None = Field(default=None, min_length=1, max_length=120)
  username_hint: str | None = Field(default=None, max_length=160)
  secret_source: SecretSource | None = None
  enabled: bool | None = None


class ConnectionTargetRead(BaseModel):
  model_config = ConfigDict(from_attributes=True)
  id: int
  project_id: int
  target_key: str
  name: str
  description: str | None
  environment_type: str
  base_url: str
  normalized_scheme: str
  normalized_host: str
  normalized_port: int
  normalized_origin: str
  allowed_probe_paths: list[str] = []
  tls_required: bool
  tls_verify: bool
  connection_timeout_seconds: int
  lifecycle_state: str
  enabled: bool
  owner_operator_id: int | None
  created_by: int
  reviewed_by: int | None
  approved_by: int | None
  created_at: datetime
  updated_at: datetime
  submitted_at: datetime | None
  approved_at: datetime | None
  rejected_at: datetime | None
  disabled_at: datetime | None
  archived_at: datetime | None
  rejection_reason: str | None
  last_check_at: datetime | None
  last_check_status: str | None
  execution_enabled: bool = False
  execution_submitted_by: int | None = None
  execution_submitted_at: datetime | None = None
  execution_approved_by: int | None = None
  execution_approved_at: datetime | None = None
  version: int


class ConnectionTargetList(BaseModel):
  items: list[ConnectionTargetRead]
  page: Page


class ConnectionTargetVersionRead(BaseModel):
  model_config = ConfigDict(from_attributes=True)
  id: int
  target_id: int
  version_number: int
  snapshot_json: str
  change_summary: str | None
  created_by: int
  created_at: datetime
  source_state: str


class ConnectionCheckRead(BaseModel):
  model_config = ConfigDict(from_attributes=True)
  id: int
  check_key: str
  target_id: int
  target_version: int
  probe_path: str
  method: str
  requested_origin: str
  resolved_addresses: list[str] = []
  started_at: datetime
  completed_at: datetime | None
  duration_ms: int | None
  status: str
  http_status: int | None
  final_origin: str | None
  redirect_count: int
  tls_protocol: str | None
  tls_certificate_summary: dict | None = None
  response_headers: dict[str, str] = {}
  response_size_bytes: int
  error_category: str | None
  safe_error_message: str | None
  initiated_by: int
  created_at: datetime


class CredentialProfileRead(BaseModel):
  model_config = ConfigDict(from_attributes=True)
  id: int
  target_id: int
  profile_name: str
  username_hint: str | None
  secret_source: str
  enabled: bool
  created_by: int
  created_at: datetime
  updated_at: datetime
  last_used_at: datetime | None
