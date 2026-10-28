"""Security Framework Interfaces & Models for Version 2.0 (Contracts Only)."""
from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class AgentPermission(str, Enum):
    EXECUTE_STEP = "EXECUTE_STEP"
    READ_KNOWLEDGE = "READ_KNOWLEDGE"
    WRITE_KNOWLEDGE = "WRITE_KNOWLEDGE"
    HEAL_SELECTOR = "HEAL_SELECTOR"
    EMIT_EVENT = "EMIT_EVENT"


class PluginPermission(str, Enum):
    READ_TASKS = "READ_TASKS"
    WRITE_DEFECTS = "WRITE_DEFECTS"
    NOTIFY_COMMUNICATION = "NOTIFY_COMMUNICATION"
    TRIGGER_PIPELINE = "TRIGGER_PIPELINE"


class SecurityContext(BaseModel):
    operator_id: int = Field(..., description="Active operator/user ID")
    roles: List[str] = Field(default_factory=list, description="Assigned operator roles")
    permissions: List[str] = Field(default_factory=list, description="Granted permissions")
    is_system_call: bool = Field(False, description="Whether triggered by internal system agent")


class ExecutionPolicy(BaseModel):
    allowed_actions: List[str] = Field(default_factory=list)
    blocked_actions: List[str] = Field(default_factory=list)
    rate_limit_per_min: int = Field(100)
    require_dual_approval: bool = Field(False)


class AuditContext(BaseModel):
    actor_id: str = Field(..., description="Actor ID performing action")
    action: str = Field(..., description="Action name")
    resource: str = Field(..., description="Target resource")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PermissionManager(ABC):
    @abstractmethod
    async def has_permission(self, context: SecurityContext, permission: str) -> bool:
        pass

    @abstractmethod
    async def validate_execution(self, context: SecurityContext, policy: ExecutionPolicy) -> bool:
        pass

    @abstractmethod
    async def log_audit(self, audit: AuditContext) -> None:
        pass
