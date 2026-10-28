"""Core AI Agent Framework Contracts for Version 2.0."""
from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Any, List, Optional, Type
from pydantic import BaseModel, Field


class AgentCapability(str, Enum):
    PLANNING = "PLANNING"
    EXECUTION = "EXECUTION"
    REVIEW = "REVIEW"
    HEALING = "HEALING"
    REPORTING = "REPORTING"


class AgentContext(BaseModel):
    run_id: str = Field(..., description="Unique execution run identifier")
    project_id: int = Field(..., description="Active project ID")
    task_id: Optional[str] = Field(None, description="Optional task ID")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Task execution parameters")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Context metadata")


class AgentResult(BaseModel):
    agent_id: str = Field(..., description="Agent identifier")
    status: str = Field("SUCCESS", description="Result status: SUCCESS, FAILED, SKIPPED")
    output: Dict[str, Any] = Field(default_factory=dict, description="Agent execution output data")
    execution_time_ms: float = Field(0.0, description="Execution duration in milliseconds")
    artifacts: List[str] = Field(default_factory=list, description="Generated artifact URIs")
    error_message: Optional[str] = Field(None, description="Error message if failed")


class BaseAgent(ABC):
    def __init__(self, agent_id: str, name: str, capabilities: List[AgentCapability]):
        self.agent_id = agent_id
        self.name = name
        self.capabilities = capabilities
        self._is_initialized = False

    @abstractmethod
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize agent resources and dependencies asynchronously."""
        pass

    @abstractmethod
    async def execute_task(self, context: AgentContext) -> AgentResult:
        """Execute autonomous task with provided context."""
        pass

    @abstractmethod
    async def evaluate_result(self, result: AgentResult) -> Dict[str, Any]:
        """Evaluate agent result and produce confidence metrics."""
        pass

    @abstractmethod
    async def shutdown(self) -> None:
        """Clean up agent resources."""
        pass


class AgentRegistry:
    def __init__(self):
        self._agents: Dict[str, Type[BaseAgent]] = {}

    def register(self, agent_id: str, agent_cls: Type[BaseAgent]) -> None:
        self._agents[agent_id] = agent_cls

    def get(self, agent_id: str) -> Optional[Type[BaseAgent]]:
        return self._agents.get(agent_id)

    def list_registered(self) -> List[str]:
        return list(self._agents.keys())


class AgentFactory:
    def __init__(self, registry: AgentRegistry):
        self.registry = registry

    def create_agent(self, agent_id: str, *args, **kwargs) -> BaseAgent:
        cls = self.registry.get(agent_id)
        if not cls:
            raise KeyError(f"Agent '{agent_id}' is not registered in AgentRegistry.")
        return cls(agent_id, *args, **kwargs)
