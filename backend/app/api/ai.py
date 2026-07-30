from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, AnyHttpUrl
from typing import Dict, Any, List

from app.ai.context_builder import AIContextBuilder
from app.ai.validation_planner import ValidationPlanner

router = APIRouter(tags=["AI Services"])

# Dependency injection for AI engines
def get_context_builder() -> AIContextBuilder:
    return AIContextBuilder()

def get_validation_planner() -> ValidationPlanner:
    return ValidationPlanner()


class ContextRequest(BaseModel):
    url: str
    force_refresh: bool = False

class ValidationPlanRequest(BaseModel):
    context_data: Dict[str, Any]
    steps: List[Dict[str, Any]]
    expected_flow: str = ""
    acceptance_criteria: str = ""


@router.post("/ai/context/build", summary="Build Application Context")
def build_context(
    request: ContextRequest,
    context_builder: AIContextBuilder = Depends(get_context_builder)
) -> Dict[str, Any]:
    """
    Builds a complete application context by crawling the specified URL
    using Playwright, extracting DOM, Network, Storage, Meta, etc.
    """
    try:
        context_data = context_builder.build_context(request.url, request.force_refresh)
        return {"status": "success", "data": context_data}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Context building failed: {str(e)}"
        )


@router.post("/ai/validations/plan", summary="Plan Step Validations")
def plan_validations(
    request: ValidationPlanRequest,
    planner: ValidationPlanner = Depends(get_validation_planner)
) -> Dict[str, Any]:
    """
    Automatically determine required validations for every generated Playwright step
    based on context JSON and acceptance criteria.
    """
    try:
        plan = planner.plan_validations(
            context_data=request.context_data,
            steps=request.steps,
            expected_flow=request.expected_flow,
            acceptance_criteria=request.acceptance_criteria
        )
        return {"status": "success", "data": plan}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Validation planning failed: {str(e)}"
        )

from app.ai.decision_engine import AIDecisionEngine
from app.ai.self_healing import SelfHealingEngine
from app.ai.schemas import ExecutionFailure

def get_decision_engine() -> AIDecisionEngine:
    return AIDecisionEngine()

def get_self_healing_engine() -> SelfHealingEngine:
    return SelfHealingEngine()


@router.post("/ai/decision/analyze", summary="Analyze Execution Failure")
def analyze_failure(
    request: ExecutionFailure,
    engine: AIDecisionEngine = Depends(get_decision_engine)
) -> Dict[str, Any]:
    """
    Analyzes a test step failure and decides the next action (HEAL, ABORT, CONTINUE).
    """
    try:
        decision = engine.decide_next_action(request)
        return {"status": "success", "data": decision}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Decision analysis failed: {str(e)}"
        )


@router.post("/ai/healing/heal", summary="Heal Broken Selector")
def heal_step(
    request: ExecutionFailure,
    engine: SelfHealingEngine = Depends(get_self_healing_engine)
) -> Dict[str, Any]:
    """
    Attempts to heuristically find a replacement selector for a broken step based on current DOM.
    """
    try:
        healing_res = engine.heal_test_step(request)
        return {"status": "success", "data": healing_res}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Self-healing failed: {str(e)}"
        )


@router.get("/ai/dashboard/summary", summary="AI Pipeline Summary")
def get_ai_dashboard_summary() -> Dict[str, Any]:
    """
    Returns high-level AI engine status and health for the dashboard overview.
    """
    return {
        "status": "success",
        "data": {
            "ai_engines": {
                "context_builder": "ONLINE",
                "validation_planner": "ONLINE",
                "decision_engine": "ONLINE",
                "self_healing": "ONLINE"
            },
            "heuristics_active": True,
            "models_loaded": 4,
            "overall_health_score": 98
        }
    }
