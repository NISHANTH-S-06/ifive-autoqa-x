from abc import ABC, abstractmethod
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger('autoqa.ai.agents')

class BaseAgent(ABC):
    """
    Abstract base class for all 13 specialized Phase 9 AI agents.
    Every agent is completely modular and exposes its own execution service.
    """

    def __init__(self, agent_name: str):
        self.agent_name = agent_name

    @abstractmethod
    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute agent task and return structured output dictionary.
        """
        pass

    def get_status(self) -> Dict[str, Any]:
        return {
            'agent_name': self.agent_name,
            'status': 'ONLINE',
            'health_score': 99.8
        }
