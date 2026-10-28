"""Task Delegation Engine for Version 2.1 Multi-Agent Ecosystem."""
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from app.v2.ecosystem.registry import AgentDirectory, AgentMetadata, AgentDiscoveryService


class TaskAssignment(BaseModel):
    assignment_id: str = Field(default_factory=lambda: f"asgn-{uuid.uuid4().hex[:6]}")
    task_id: str
    assigned_agent_id: str
    status: str = Field("ASSIGNED", description="ASSIGNED, RUNNING, COMPLETED, FAILED")
    assigned_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CapabilityMatcher:
    def match(self, required_capability: str, available_agents: List[AgentMetadata]) -> List[AgentMetadata]:
        req_upper = required_capability.upper()
        return [
            meta for meta in available_agents
            if any(req_upper in str(c).upper() for c in meta.capabilities)
        ]


class TaskBalancer:
    def select_best_agent(self, candidates: List[AgentMetadata]) -> Optional[AgentMetadata]:
        online = [c for c in candidates if c.status == "ONLINE"]
        return online[0] if online else (candidates[0] if candidates else None)


class TaskDelegator:
    def __init__(self, directory: Optional[AgentDirectory] = None):
        self.directory = directory or AgentDiscoveryService().directory
        self.matcher = CapabilityMatcher()
        self.balancer = TaskBalancer()
        self.assignments: List[TaskAssignment] = []

    def delegate_task(self, task_id: str, required_capability: str) -> Optional[TaskAssignment]:
        candidates = self.matcher.match(required_capability, self.directory.list_all())
        selected = self.balancer.select_best_agent(candidates)
        if not selected:
            return None

        asgn = TaskAssignment(task_id=task_id, assigned_agent_id=selected.agent_id)
        self.assignments.append(asgn)
        return asgn
