"""In-memory Event Framework for Version 2.0 (Local, Zero-External-Dependency)."""
import inspect
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Callable, Awaitable, Optional, Type
from pydantic import BaseModel, Field


class BaseEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str = Field(..., description="Event type identifier")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    correlation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    payload: Dict[str, Any] = Field(default_factory=dict)


# Specialized Event Models
class AgentStarted(BaseEvent):
    event_type: str = "AgentStarted"

class AgentCompleted(BaseEvent):
    event_type: str = "AgentCompleted"

class AgentFailed(BaseEvent):
    event_type: str = "AgentFailed"

class WorkflowStarted(BaseEvent):
    event_type: str = "WorkflowStarted"

class WorkflowCompleted(BaseEvent):
    event_type: str = "WorkflowCompleted"

class TaskCreated(BaseEvent):
    event_type: str = "TaskCreated"

class TaskCompleted(BaseEvent):
    event_type: str = "TaskCompleted"

class TaskFailed(BaseEvent):
    event_type: str = "TaskFailed"


EventHandler = Callable[[BaseEvent], Awaitable[None]]


class EventStore:
    def __init__(self):
        self._events: List[BaseEvent] = []

    def append(self, event: BaseEvent) -> None:
        self._events.append(event)

    def get_all(self) -> List[BaseEvent]:
        return list(self._events)

    def get_by_type(self, event_type: str) -> List[BaseEvent]:
        return [e for e in self._events if e.event_type == event_type]

    def clear(self) -> None:
        self._events.clear()


class EventBus:
    def __init__(self, store: Optional[EventStore] = None):
        self._subscribers: Dict[str, List[EventHandler]] = {}
        self.store = store or EventStore()

    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)

    async def publish(self, event: BaseEvent) -> None:
        self.store.append(event)
        handlers = self._subscribers.get(event.event_type, [])
        for handler in handlers:
            if inspect.iscoroutinefunction(handler):
                await handler(event)
    async def publish_platform_event(self, source_engine: str, event_type: str, payload: Dict[str, Any]) -> BaseEvent:
        event = BaseEvent(event_type=event_type, payload={"source_engine": source_engine, **payload})
        await self.publish(event)
        return event

    def clear_subscribers(self) -> None:
        self._subscribers.clear()


class EventPublisher:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus

    async def publish(self, event: BaseEvent) -> None:
        await self.event_bus.publish(event)
