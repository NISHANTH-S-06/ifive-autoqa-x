"""Agent Communication Bus Models and Context Manager for Version 2.0."""
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class MessageType(str, Enum):
    REQUEST = "REQUEST"
    RESPONSE = "RESPONSE"
    BROADCAST = "BROADCAST"
    NOTIFICATION = "NOTIFICATION"
    ERROR = "ERROR"


class AgentMessage(BaseModel):
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sender_id: str = Field(..., description="ID of sending agent")
    receiver_id: Optional[str] = Field(None, description="ID of receiving agent; None for broadcast")
    message_type: MessageType = Field(MessageType.NOTIFICATION)
    payload: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    correlation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))


class AgentRequest(BaseModel):
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sender_id: str = Field(...)
    action: str = Field(..., description="Requested agent action")
    parameters: Dict[str, Any] = Field(default_factory=dict)


class AgentResponse(BaseModel):
    request_id: str = Field(...)
    responder_id: str = Field(...)
    status: str = Field("SUCCESS", description="Response status: SUCCESS, FAILED")
    data: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = Field(None)


class AgentContextManager:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self._messages: List[AgentMessage] = []
        self._variables: Dict[str, Any] = {}

    def log_message(self, message: AgentMessage) -> None:
        self._messages.append(message)

    def get_messages(self, receiver_id: Optional[str] = None) -> List[AgentMessage]:
        if receiver_id:
            return [m for m in self._messages if m.receiver_id == receiver_id or m.message_type == MessageType.BROADCAST]
        return list(self._messages)

    def set_variable(self, key: str, value: Any) -> None:
        self._variables[key] = value

    def get_variable(self, key: str, default: Any = None) -> Any:
        return self._variables.get(key, default)

    def clear(self) -> None:
        self._messages.clear()
        self._variables.clear()
