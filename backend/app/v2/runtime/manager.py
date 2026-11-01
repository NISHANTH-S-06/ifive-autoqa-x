"""Agent Runtime Manager for Version 2.0 (Lifecycle Management & Runtime Control)."""
import asyncio
import time
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from app.v2.agents import BaseAgent, AgentRegistry, PlannerAgent, ExecutionAgent, ReviewAgent, HealingAgent, ReportingAgent, CoordinatorAgent


class RuntimeState(str, Enum):
    STOPPED = "STOPPED"
    STARTING = "STARTING"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    ERROR = "ERROR"


class RuntimeContext(BaseModel):
    runtime_id: str = Field(default_factory=lambda: f"rt-{uuid.uuid4().hex[:6]}")
    state: RuntimeState = RuntimeState.STOPPED
    active_agents: List[str] = Field(default_factory=list)
    active_workflows: List[str] = Field(default_factory=list)
    started_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AgentRuntime:
    def __init__(self, agent: BaseAgent):
        self.agent = agent
        self.state = RuntimeState.STOPPED
        self.last_active_at: Optional[datetime] = None
        self.execution_count: int = 0
        self.error_count: int = 0

    async def startup(self) -> bool:
        self.state = RuntimeState.STARTING
        res = await self.agent.initialize({})
        if res:
            self.state = RuntimeState.RUNNING
            self.last_active_at = datetime.now(timezone.utc)
            return True
        self.state = RuntimeState.ERROR
        return False

    async def shutdown(self) -> bool:
        await self.agent.shutdown()
        self.state = RuntimeState.STOPPED
        return True

    def pause(self) -> None:
        if self.state == RuntimeState.RUNNING:
            self.state = RuntimeState.PAUSED

    def resume(self) -> None:
        if self.state == RuntimeState.PAUSED:
            self.state = RuntimeState.RUNNING

    async def restart(self) -> bool:
        await self.shutdown()
        return await self.startup()


class RuntimeRegistry:
    def __init__(self):
        self._runtimes: Dict[str, AgentRuntime] = {}

    def register(self, agent_id: str, runtime: AgentRuntime) -> None:
        self._runtimes[agent_id] = runtime

    def get(self, agent_id: str) -> Optional[AgentRuntime]:
        return self._runtimes.get(agent_id)

    def list_runtimes(self) -> List[AgentRuntime]:
        return list(self._runtimes.values())


class RuntimeScheduler:
    def __init__(self):
        self.scheduled_jobs: List[Dict[str, Any]] = []

    def schedule_task(self, job_name: str, interval_sec: float) -> str:
        job_id = f"job-{uuid.uuid4().hex[:6]}"
        self.scheduled_jobs.append({"job_id": job_id, "name": job_name, "interval_sec": interval_sec, "status": "ACTIVE"})
        return job_id


class RuntimeManager:
    def __init__(self):
        self.registry = RuntimeRegistry()
        self.scheduler = RuntimeScheduler()
        self.context = RuntimeContext()
        self._initialize_default_runtimes()

    def _initialize_default_runtimes(self) -> None:
        agents = [
            PlannerAgent(),
            ExecutionAgent(),
            ReviewAgent(),
            HealingAgent(),
            ReportingAgent(),
            CoordinatorAgent(),
        ]
        for a in agents:
            rt = AgentRuntime(a)
            self.registry.register(a.agent_id, rt)

    async def start_all(self) -> bool:
        self.context.state = RuntimeState.STARTING
        self.context.started_at = datetime.now(timezone.utc)
        all_success = True

        for rt in self.registry.list_runtimes():
            success = await rt.startup()
            if not success:
                all_success = False
            else:
                self.context.active_agents.append(rt.agent.agent_id)

        self.context.state = RuntimeState.RUNNING if all_success else RuntimeState.ERROR
        return all_success

    async def stop_all(self) -> bool:
        for rt in self.registry.list_runtimes():
            await rt.shutdown()
        self.context.state = RuntimeState.STOPPED
        self.context.active_agents.clear()
        return True

    def pause_all(self) -> None:
        for rt in self.registry.list_runtimes():
            rt.pause()
        self.context.state = RuntimeState.PAUSED

    def resume_all(self) -> None:
        for rt in self.registry.list_runtimes():
            rt.resume()
        self.context.state = RuntimeState.RUNNING

    async def restart_all(self) -> bool:
        await self.stop_all()
        return await self.start_all()

    def get_status(self) -> Dict[str, Any]:
        return {
            "runtime_id": self.context.runtime_id,
            "state": self.context.state.value,
            "active_agents_count": len(self.context.active_agents),
            "started_at": self.context.started_at.isoformat() if self.context.started_at else None,
            "agent_statuses": {rt.agent.agent_id: rt.state.value for rt in self.registry.list_runtimes()},
        }
