"""Enterprise Structured Logging Framework for Version 2.0."""
import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional


class StructuredLogger:
    def __init__(self, logger_name: str):
        self.logger = logging.getLogger(logger_name)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def _format_entry(
        self,
        level: str,
        message: str,
        correlation_id: Optional[str] = None,
        request_id: Optional[str] = None,
        execution_id: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> str:
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": level,
            "logger": self.logger.name,
            "message": message,
            "correlation_id": correlation_id or str(uuid.uuid4()),
            "request_id": request_id,
            "execution_id": execution_id,
            "extra": extra or {},
        }
        return json.dumps(entry)

    def info(self, message: str, **kwargs) -> None:
        self.logger.info(self._format_entry("INFO", message, **kwargs))

    def warning(self, message: str, **kwargs) -> None:
        self.logger.warning(self._format_entry("WARNING", message, **kwargs))

    def error(self, message: str, **kwargs) -> None:
        self.logger.error(self._format_entry("ERROR", message, **kwargs))


class AuditLogger(StructuredLogger):
    def log_security_event(self, actor: str, action: str, resource: str, success: bool = True) -> None:
        self.info(
            f"AUDIT: {actor} executed {action} on {resource}",
            extra={"actor": actor, "action": action, "resource": resource, "success": success},
        )


class AgentLogger(StructuredLogger):
    def log_agent_step(self, agent_id: str, step_name: str, status: str) -> None:
        self.info(
            f"AGENT [{agent_id}]: {step_name} -> {status}",
            extra={"agent_id": agent_id, "step_name": step_name, "status": status},
        )


class PluginLogger(StructuredLogger):
    def log_plugin_event(self, plugin_id: str, event_name: str, status: str) -> None:
        self.info(
            f"PLUGIN [{plugin_id}]: Event {event_name} -> {status}",
            extra={"plugin_id": plugin_id, "event_name": event_name, "status": status},
        )


class LoggerFactory:
    _loggers: Dict[str, StructuredLogger] = {}

    @classmethod
    def get_logger(cls, name: str) -> StructuredLogger:
        if name not in cls._loggers:
            cls._loggers[name] = StructuredLogger(name)
        return cls._loggers[name]

    @classmethod
    def get_audit_logger(cls) -> AuditLogger:
        return AuditLogger("v2.audit")

    @classmethod
    def get_agent_logger(cls) -> AgentLogger:
        return AgentLogger("v2.agent")

    @classmethod
    def get_plugin_logger(cls) -> PluginLogger:
        return PluginLogger("v2.plugin")
