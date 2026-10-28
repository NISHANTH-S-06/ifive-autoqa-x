"""Pytest Test Suite for Phase 17.5 Enterprise AI Copilot & Self-Learning Platform."""
import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI

from app.v2.copilot import EnterpriseCopilot, CopilotSession
from app.v2.context import ContextEngine
from app.v2.recommendation import RecommendationEngine
from app.v2.learning import LearningEngine, FeedbackEngine
from app.v2.knowledge import KnowledgeEvolutionEngine
from app.v2.prompts import PromptLibrary
from app.v2.advisors import BusinessAdvisor
from app.v2.api.v2_router import router as v2_router


@pytest.mark.anyio
async def test_enterprise_copilot_chat():
    copilot = EnterpriseCopilot()
    res_plan = copilot.chat("user-1", "/plan Purchase Order Flow", project_id=1)
    assert res_plan["response"]["confidence_score"] == 95.0
    assert "Plan" in res_plan["response"]["content"]

    res_rec = copilot.chat("user-1", "/recommend locators", project_id=1)
    assert "Recommendation" in res_rec["response"]["content"]


@pytest.mark.anyio
async def test_context_intelligence_engine():
    engine = ContextEngine()
    ctx = engine.get_context(project_id=1)
    assert ctx["project_id"] == 1
    assert "Authentication" in ctx["knowledge_modules"]


@pytest.mark.anyio
async def test_recommendation_engine_generation():
    engine = RecommendationEngine()
    recs = engine.generate_recommendations()
    assert len(recs) >= 5
    types = [r.type for r in recs]
    assert "AUTOMATION" in types
    assert "SECURITY" in types


@pytest.mark.anyio
async def test_learning_engine_and_feedback_loop():
    learn_engine = LearningEngine()
    rec = learn_engine.process_execution_learning({"status": "SUCCESS"})
    assert rec.learning_type == "PATTERN"

    fb_engine = FeedbackEngine()
    fb = fb_engine.submit_feedback(rating=5, comments="Excellent guidance", correction="Add explicit wait")
    assert fb.rating == 5
    assert len(fb_engine.correction_memory.list_corrections()) == 1


@pytest.mark.anyio
async def test_knowledge_evolution_engine():
    evo_engine = KnowledgeEvolutionEngine()
    item = evo_engine.evolve_pattern("pat-auth")
    assert item.usage_count >= 16
    assert item.lifecycle_state == "EVOLVED"


@pytest.mark.anyio
async def test_prompt_intelligence_framework():
    library = PromptLibrary()
    rendered = library.render_prompt("task_breakdown", {"requirement": "Create Sales Order", "project_id": 1})
    assert "Create Sales Order" in rendered
    assert "1" in rendered


@pytest.mark.anyio
async def test_business_and_workflow_advisors():
    advisor = BusinessAdvisor()
    advisories = advisor.get_all_advisories(project_id=1)
    assert len(advisories) >= 4
    categories = [a.category for a in advisories]
    assert "WORKFLOW" in categories
    assert "RISK" in categories
    assert "QUALITY" in categories


@pytest.mark.anyio
async def test_fastapi_v2_copilot_router_endpoints():
    app = FastAPI()
    app.include_router(v2_router)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        # Copilot status
        res = await client.get("/api/v2/copilot/status")
        assert res.status_code == 200
        assert res.json()["status"] == "ONLINE"

        # Copilot chat
        res = await client.post("/api/v2/copilot/chat", json={"user_id": "test-user", "message": "/recommend", "project_id": 1})
        assert res.status_code == 200
        assert "response" in res.json()

        # Copilot context
        res = await client.get("/api/v2/copilot/context?project_id=1")
        assert res.status_code == 200

        # Copilot recommendations
        res = await client.get("/api/v2/copilot/recommend")
        assert res.status_code == 200
        assert res.json()["total_recommendations"] >= 5

        # Copilot advisor
        res = await client.get("/api/v2/copilot/advisor")
        assert res.status_code == 200
        assert len(res.json()["advisories"]) >= 4

        # Copilot learning
        res = await client.get("/api/v2/copilot/learning")
        assert res.status_code == 200

        # Copilot feedback
        res = await client.post("/api/v2/copilot/feedback", json={"rating": 5, "comments": "Great recommendation"})
        assert res.status_code == 200
        assert res.json()["status"] == "success"

        # Copilot knowledge evolution
        res = await client.get("/api/v2/copilot/knowledge")
        assert res.status_code == 200
        assert "evolved_knowledge" in res.json()
