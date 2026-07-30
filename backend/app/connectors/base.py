"""Base Connector Abstraction for External Task Portals."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseTaskConnector(ABC):
    """Abstract interface for task management connectors."""

    @abstractmethod
    def health_check(self) -> bool:
        """Check if the external portal is reachable."""

    @abstractmethod
    def fetch_testing_l2_tasks(self) -> List[Dict[str, Any]]:
        """Fetch tasks in TESTING_L2 status ready for automated QA."""

    @abstractmethod
    def fetch_task(self, source_task_id: str | int) -> Optional[Dict[str, Any]]:
        """Fetch details of a single task by source ID."""

    @abstractmethod
    def send_qa_result(
        self,
        source_task_id: str | int,
        source_revision: int,
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Send automated QA execution result back to external portal."""
