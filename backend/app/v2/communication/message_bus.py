"""Agent Communication Framework & Priority Message Bus for Version 2.1 Ecosystem."""
import asyncio
import inspect
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Any, List, Callable, Awaitable, Optional
from pydantic import BaseModel, Field


class MessageType(str, Enum):
    DIRECT = "DIRECT"
    BROADCAST = "BROADCAST"
    EVENT = "EVENT"
    REQUEST = "REQUEST"
    RESPONSE = "RESPONSE"


class AgentMessage(BaseModel):
    message_id: str = Field(default_factory=lambda: f"msg-{uuid.uuid4().hex[:6]}")
    sender_id: str
    receiver_id: Optional[str] = Field(None)
    message_type: MessageType = MessageType.DIRECT
    payload: Dict[str, Any] = Field(default_factory=dict)
    priority: int = Field(1, description="1=Highest priority, 10=Lowest")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class BroadcastMessage(AgentMessage):
    message_type: MessageType = MessageType.BROADCAST
    receiver_id: Optional[str] = None


class DirectMessage(AgentMessage):
    message_type: MessageType = MessageType.DIRECT
    receiver_id: str


class EventMessage(AgentMessage):
    message_type: MessageType = MessageType.EVENT


MessageHandler = Callable[[AgentMessage], Awaitable[None]]


class PriorityQueue:
    def __init__(self):
        self._queue: List[AgentMessage] = []

    def push(self, message: AgentMessage) -> None:
        self._queue.append(message)
        self._queue.sort(key=lambda m: m.priority)

    def pop(self) -> Optional[AgentMessage]:
        return self._queue.pop(0) if self._queue else None

    def list_all(self) -> List[AgentMessage]:
        return list(self._queue)


class MessageRouter:
    def __init__(self):
        self._listeners: Dict[str, List[MessageHandler]] = {}

    def register_listener(self, agent_id: str, handler: MessageHandler) -> None:
        if agent_id not in self._listeners:
            self._listeners[agent_id] = []
        self._listeners[agent_id].append(handler)

    async def route(self, message: AgentMessage) -> int:
        delivered = 0
        if message.message_type == MessageType.BROADCAST or not message.receiver_id:
            for agent_id, handlers in self._listeners.items():
                if agent_id != message.sender_id:
                    for h in handlers:
                        if inspect.iscoroutinefunction(h):
                            await h(message)
                        else:
                            h(message)
                        delivered += 1
        else:
            handlers = self._listeners.get(message.receiver_id, [])
            for h in handlers:
                if inspect.iscoroutinefunction(h):
                    await h(message)
                else:
                    h(message)
                delivered += 1
        return delivered


class MessageBus:
    def __init__(self):
        self.router = MessageRouter()
        self.queue = PriorityQueue()
        self._history: List[AgentMessage] = []

    def subscribe(self, agent_id: str, handler: MessageHandler) -> None:
        self.router.register_listener(agent_id, handler)

    async def publish(self, message: AgentMessage) -> int:
        self.queue.push(message)
        self._history.append(message)
        return await self.router.route(message)

    async def send_direct(self, sender_id: str, receiver_id: str, payload: Dict[str, Any], priority: int = 1) -> AgentMessage:
        msg = DirectMessage(sender_id=sender_id, receiver_id=receiver_id, payload=payload, priority=priority)
        await self.publish(msg)
        return msg

    async def broadcast(self, sender_id: str, payload: Dict[str, Any], priority: int = 1) -> AgentMessage:
        msg = BroadcastMessage(sender_id=sender_id, payload=payload, priority=priority)
        await self.publish(msg)
        return msg

    def get_history(self) -> List[AgentMessage]:
        return list(self._history)
