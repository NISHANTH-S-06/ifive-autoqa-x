"""Knowledge Platform Abstract Interfaces for Version 2.0 (Contracts Only)."""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class KnowledgeStore(ABC):
    @abstractmethod
    async def store(self, key: str, value: Dict[str, Any], namespace: str = "default") -> bool:
        pass

    @abstractmethod
    async def query(self, key: str, namespace: str = "default") -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def delete(self, key: str, namespace: str = "default") -> bool:
        pass


class PromptStore(ABC):
    @abstractmethod
    async def get_prompt(self, name: str, version: Optional[str] = None) -> Optional[str]:
        pass

    @abstractmethod
    async def register_prompt(self, name: str, template: str, version: str = "1.0.0") -> bool:
        pass

    @abstractmethod
    async def list_prompts(self) -> List[str]:
        pass


class PatternStore(ABC):
    @abstractmethod
    async def get_pattern(self, pattern_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def register_pattern(self, pattern_id: str, pattern_data: Dict[str, Any]) -> bool:
        pass

    @abstractmethod
    async def search_patterns(self, query: str) -> List[Dict[str, Any]]:
        pass


class MemoryStore(ABC):
    @abstractmethod
    async def save_memory(self, session_id: str, memory_key: str, data: Dict[str, Any]) -> bool:
        pass

    @abstractmethod
    async def recall_memory(self, session_id: str, memory_key: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def clear_memory(self, session_id: str) -> bool:
        pass


class ExecutionHistoryStore(ABC):
    @abstractmethod
    async def record_history(self, run_id: str, payload: Dict[str, Any]) -> bool:
        pass

    @abstractmethod
    async def get_history(self, run_id: str) -> Optional[Dict[str, Any]]:
        pass


class KnowledgeGraph(ABC):
    @abstractmethod
    async def add_node(self, node_id: str, node_type: str, properties: Dict[str, Any]) -> bool:
        pass

    @abstractmethod
    async def add_edge(self, source_id: str, target_id: str, relation: str) -> bool:
        pass

    @abstractmethod
    async def get_topology(self, root_id: Optional[str] = None) -> Dict[str, Any]:
        pass


class VectorStoreInterface(ABC):
    @abstractmethod
    async def upsert_vector(self, vector_id: str, values: List[float], metadata: Dict[str, Any]) -> bool:
        pass

    @abstractmethod
    async def query_similar(self, query_vector: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        pass
