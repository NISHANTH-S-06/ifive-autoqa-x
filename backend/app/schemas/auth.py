from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class OperatorRole(str, Enum):
  VIEWER = 'VIEWER'
  DEVELOPER = 'DEVELOPER'
  TESTER = 'TESTER'
  APPROVER = 'APPROVER'
  PROJECT_MANAGER = 'PROJECT_MANAGER'
  ADMIN = 'ADMIN'


class LoginRequest(BaseModel):
  username: str = Field(min_length=1, max_length=80)
  password: str = Field(min_length=1, max_length=500)


class OperatorRead(BaseModel):
  model_config = ConfigDict(from_attributes=True)
  id: int
  username: str
  display_name: str
  role: OperatorRole
  is_active: bool
  must_change_password: bool = False
  password_changed_at: datetime | None = None
  password_expires_at: datetime | None = None
  failed_login_count: int = 0
  locked_until: datetime | None = None
  last_login_at: datetime | None = None
  created_at: datetime | None = None


class LoginResponse(BaseModel):
  operator: OperatorRead
  csrf_token: str


class OperatorCreate(BaseModel):
  username: str = Field(min_length=1, max_length=80)
  display_name: str = Field(min_length=1, max_length=160)
  role: OperatorRole
  temporary_password: str = Field(min_length=12, max_length=500)


class OperatorStatusUpdate(BaseModel):
  is_active: bool


class OperatorRoleUpdate(BaseModel):
  role: OperatorRole


class PasswordChangeRequest(BaseModel):
  current_password: str = Field(min_length=1, max_length=500)
  new_password: str = Field(min_length=12, max_length=500)
  confirm_password: str = Field(min_length=12, max_length=500)


class AdminPasswordResetRequest(BaseModel):
  temporary_password: str = Field(min_length=12, max_length=500)
  confirm_temporary_password: str = Field(min_length=12, max_length=500)
  reason: str = Field(min_length=1, max_length=200)


class SessionRevokeRequest(BaseModel):
  reason: str | None = Field(default=None, max_length=200)
  confirm_self_revoke: bool = False


class OperatorSessionRead(BaseModel):
  session_id: int
  session_name: str | None = None
  created_at: datetime
  last_seen_at: datetime
  last_activity_at: datetime | None = None
  expires_at: datetime
  revoked_at: datetime | None = None
  user_agent: str | None = None
  ip_address: str | None = None
  is_current: bool
  is_active: bool


class SecuritySummaryRead(BaseModel):
  total_operators: int
  active_operators: int
  inactive_operators: int
  operators_by_role: dict[str, int]
  locked_operators: int
  must_change_password_count: int
  expired_password_count: int
  active_sessions: int
  revoked_sessions_last_24h: int
  failed_logins_last_24h: int
  successful_logins_last_24h: int
  password_changes_last_30d: int
  password_resets_last_30d: int
  audit_chain_valid: bool
  last_audit_verification_at: datetime


class OperatorSecurityRead(BaseModel):
  id: int
  username: str
  display_name: str
  role: OperatorRole
  is_active: bool
  must_change_password: bool
  password_changed_at: datetime | None = None
  password_expires_at: datetime | None = None
  last_login_at: datetime | None = None
  failed_login_count: int
  is_locked: bool
  active_session_count: int
