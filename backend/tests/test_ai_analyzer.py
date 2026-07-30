import pytest
from app.ai.local_provider import LocalAIProvider
from app.ai.schemas import AIAnalysisResponse
from app.services.task_analysis_service import analyze_imported_task

def test_local_provider_generates_schema():
    provider = LocalAIProvider()
    res = provider.analyze_task(
        task_title="Create Employee",
        task_desc="We need to ensure employee can be created in the HR portal.",
        acceptance_criteria="Employee is created and visible in the table."
    )
    assert isinstance(res, AIAnalysisResponse)
    assert res.risk_classification == "MEDIUM"
    assert len(res.scenarios) > 0
    assert len(res.recommended_steps) > 0
    assert res.template_type == "AI_GENERATED"

    # Test generic ambiguous task returns missing_information
    ambiguous = provider.analyze_task(
        task_title="Process Request",
        task_desc="Do some processing",
        acceptance_criteria="Request processed"
    )
    assert len(ambiguous.missing_information) > 0

def test_task_analysis_service():
    res = analyze_imported_task(
        "Delete obsolete records",
        "Clear out old records from DB",
        "Records deleted"
    )
    assert isinstance(res, AIAnalysisResponse)
    assert res.risk_classification == "HIGH"

