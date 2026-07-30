from app.ai.local_provider import LocalAIProvider
from app.ai.schemas import AIAnalysisResponse

def get_ai_provider():
    return LocalAIProvider()

def analyze_imported_task(title: str, description: str, acceptance_criteria: str) -> AIAnalysisResponse:
    provider = get_ai_provider()
    return provider.analyze_task(title, description, acceptance_criteria)
