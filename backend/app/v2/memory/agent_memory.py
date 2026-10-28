"""In-memory Agent Memory System for Version 2.0 (Zero External DB Dependencies)."""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class MemoryEntry(BaseModel):
    key: str
    value: Any
    category: str = "general"
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AgentMemory:
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self._store: Dict[str, MemoryEntry] = {}

    def set(self, key: str, value: Any, category: str = "general", metadata: Optional[Dict[str, Any]] = None) -> None:
        self._store[key] = MemoryEntry(key=key, value=value, category=category, metadata=metadata or {})

    def get(self, key: str, default: Any = None) -> Any:
        entry = self._store.get(key)
        return entry.value if entry else default

    def delete(self, key: str) -> bool:
        return self._store.pop(key, None) is not None

    def list_entries(self, category: Optional[str] = None) -> List[MemoryEntry]:
        if category:
            return [e for e in self._store.values() if e.category == category]
        return list(self._store.values())

    def clear(self) -> None:
        self._store.clear()


class SessionMemory:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self._data: Dict[str, Any] = {}

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def clear(self) -> None:
        self._data.clear()


class WorkflowMemory:
    def __init__(self, workflow_id: str):
        self.workflow_id = workflow_id
        self.plan: Optional[Dict[str, Any]] = None
        self.step_results: List[Dict[str, Any]] = []
        self.status: str = "PENDING"

    def record_step(self, step_id: str, result: Dict[str, Any]) -> None:
        self.step_results.append({"step_id": step_id, "result": result})

    def get_step_results(self) -> List[Dict[str, Any]]:
        return list(self.step_results)

    def clear(self) -> None:
        self.plan = None
        self.step_results.clear()
        self.status = "PENDING"


class ExecutionMemory:
    def __init__(self):
        self._runs: Dict[str, Dict[str, Any]] = {}

    def record_run(self, run_id: str, run_data: Dict[str, Any]) -> None:
        self._runs[run_id] = run_data

    def get_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        return self._runs.get(run_id)

    def list_runs(self) -> List[Dict[str, Any]]:
        return list(self._runs.values())

    def clear(self) -> None:
        self._runs.clear()
