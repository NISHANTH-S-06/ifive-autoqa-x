"""Error Framework and Custom Exception Definitions for Version 2.0."""
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class BaseException(Exception):
    def __init__(self, message: str, error_code: str = "V2_ERROR", details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}


class AgentException(BaseException):
    def __init__(self, message: str, agent_id: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code="AGENT_ERROR", details=details or {})
        self.agent_id = agent_id


class PluginException(BaseException):
    def __init__(self, message: str, plugin_id: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code="PLUGIN_ERROR", details=details or {})
        self.plugin_id = plugin_id


class WorkflowException(BaseException):
    def __init__(self, message: str, workflow_id: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code="WORKFLOW_ERROR", details=details or {})
        self.workflow_id = workflow_id


class ValidationException(BaseException):
    def __init__(self, message: str, field_errors: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code="VALIDATION_ERROR", details=field_errors or {})


class ExecutionException(BaseException):
    def __init__(self, message: str, run_id: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code="EXECUTION_ERROR", details=details or {})
        self.run_id = run_id


class ErrorResponse(BaseModel):
    status: str = Field("error", description="Response status")
    error_code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error message")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional error context")
