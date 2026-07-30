from abc import ABC, abstractmethod
from app.ai.schemas import AIAnalysisResponse

class BaseAIProvider(ABC):
    @abstractmethod
    def analyze_task(self, task_title: str, task_desc: str, acceptance_criteria: str) -> AIAnalysisResponse:
        pass
