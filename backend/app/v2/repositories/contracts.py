"""Repository Contracts and UnitOfWork Interface for Version 2.0 (Contracts Only, No Table Modifying)."""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, TypeVar, Generic

T = TypeVar("T")


class BaseRepositoryContract(Generic[T], ABC):
    @abstractmethod
    async def get_by_id(self, entity_id: Any) -> Optional[T]:
        pass

    @abstractmethod
    async def list_all(self, limit: int = 100, offset: int = 0) -> List[T]:
        pass

    @abstractmethod
    async def create(self, entity: T) -> T:
        pass

    @abstractmethod
    async def update(self, entity_id: Any, updates: Dict[str, Any]) -> Optional[T]:
        pass

    @abstractmethod
    async def delete(self, entity_id: Any) -> bool:
        pass


class UnitOfWorkInterface(ABC):
    @abstractmethod
    async def commit(self) -> None:
        pass

    @abstractmethod
    async def rollback(self) -> None:
        pass

    @abstractmethod
    async def __aenter__(self):
        pass

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


class AgentRepositoryContract(BaseRepositoryContract[Dict[str, Any]], ABC):
    @abstractmethod
    async def get_by_capability(self, capability: str) -> List[Dict[str, Any]]:
        pass


class PluginRepositoryContract(BaseRepositoryContract[Dict[str, Any]], ABC):
    @abstractmethod
    async def get_by_target(self, target_system: str) -> List[Dict[str, Any]]:
        pass
