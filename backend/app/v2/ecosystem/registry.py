"""Multi-Agent Registry and Discovery Service for Version 2.1 Ecosystem."""
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from app.v2.agents import BaseAgent, PlannerAgent, ExecutionAgent, ReviewAgent, HealingAgent, ReportingAgent, CoordinatorAgent


class AgentMetadata(BaseModel):
    agent_id: str
    name: str
    version: str = Field("2.1.0")
    capabilities: List[str] = Field(default_factory=list)
    status: str = Field("ONLINE", description="ONLINE, BUSY, OFFLINE")
    health_status: str = Field("HEALTHY", description="HEALTHY, DEGRADED, UNHEALTHY")
    registered_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_heartbeat: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AgentHealthMonitor:
    def check_health(self, metadata: AgentMetadata) -> str:
        delta = (datetime.now(timezone.utc) - metadata.last_heartbeat).total_seconds()
        if delta > 300:
            metadata.health_status = "UNHEALTHY"
            metadata.status = "OFFLINE"
        elif delta > 60:
            metadata.health_status = "DEGRADED"
        else:
            metadata.health_status = "HEALTHY"
        return metadata.health_status


class AgentCapabilityIndex:
    def __init__(self):
        self._index: Dict[str, List[str]] = {}

    def index_agent(self, agent_id: str, capabilities: List[str]) -> None:
        for cap in capabilities:
            cap_key = str(cap).upper()
            if cap_key not in self._index:
                self._index[cap_key] = []
            if agent_id not in self._index[cap_key]:
                self._index[cap_key].append(agent_id)

    def search(self, capability: str) -> List[str]:
        return list(self._index.get(str(capability).upper(), []))


class AgentDirectory:
    def __init__(self):
        self._agents: Dict[str, AgentMetadata] = {}
        self.capability_index = AgentCapabilityIndex()
        self.health_monitor = AgentHealthMonitor()

    def register(self, metadata: AgentMetadata) -> None:
        self._agents[metadata.agent_id] = metadata
        self.capability_index.index_agent(metadata.agent_id, metadata.capabilities)

    def get(self, agent_id: str) -> Optional[AgentMetadata]:
        meta = self._agents.get(agent_id)
        if meta:
            self.health_monitor.check_health(meta)
        return meta

    def list_all(self) -> List[AgentMetadata]:
        for meta in self._agents.values():
            self.health_monitor.check_health(meta)
        return list(self._agents.values())


class AgentDiscoveryService:
    def __init__(self, directory: Optional[AgentDirectory] = None):
        self.directory = directory or AgentDirectory()
        self._auto_discover_default_agents()

    def _auto_discover_default_agents(self) -> None:
        default_agents = [
            AgentMetadata(agent_id="planner", name="Planner Agent", capabilities=["PLANNING", "WORKFLOW"]),
            AgentMetadata(agent_id="knowledge", name="Knowledge Agent", capabilities=["KNOWLEDGE", "SEARCH"]),
            AgentMetadata(agent_id="reasoning", name="Reasoning Agent", capabilities=["REASONING", "LOGIC"]),
            AgentMetadata(agent_id="decision", name="Decision Agent", capabilities=["DECISION", "EVALUATION"]),
            AgentMetadata(agent_id="executor", name="Execution Agent", capabilities=["EXECUTION", "RUNNER"]),
            AgentMetadata(agent_id="reviewer", name="Review Agent", capabilities=["REVIEW", "VERIFICATION"]),
            AgentMetadata(agent_id="healer", name="Healing Agent", capabilities=["HEALING", "AUTO_REPAIR"]),
            AgentMetadata(agent_id="reporter", name="Reporting Agent", capabilities=["REPORTING", "JSON_EXPORT"]),
            AgentMetadata(agent_id="coordinator", name="Coordinator Agent", capabilities=["COORDINATION", "ORCHESTRATION"]),
            AgentMetadata(agent_id="audit", name="Audit Agent", capabilities=["AUDIT", "SECURITY"]),
        ]
        for meta in default_agents:
            self.directory.register(meta)

    def discover_by_capability(self, capability: str) -> List[AgentMetadata]:
        ids = self.directory.capability_index.search(capability)
        return [self.directory.get(aid) for aid in ids if self.directory.get(aid)]
