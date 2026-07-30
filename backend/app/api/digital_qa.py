from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any

from app.auth import AuthContext, get_auth_context
from app.ai.reasoning_engine import AIDigitalQAReasoningEngine
from app.ai.autonomous_exploration import AutonomousExplorationEngine
from app.ai.strategy_generator import AITestStrategyGenerator

router = APIRouter(prefix='/digital-qa', tags=['digital-qa'], dependencies=[Depends(get_auth_context)])


class ReasoningRequest(BaseModel):
    page_url: str
    module_name: Optional[str] = 'General'

class ExplorationRequest(BaseModel):
    target_url: str

class StrategyRequest(BaseModel):
    project_name: str
    target_url: str


@router.post('/reason', summary='Generate Senior QA AI Reasoning Tree')
def generate_reasoning(payload: ReasoningRequest):
    engine = AIDigitalQAReasoningEngine()
    return engine.generate_page_reasoning(payload.page_url, payload.module_name)


@router.post('/explore', summary='Trigger Autonomous Application Exploration')
def explore_application(payload: ExplorationRequest):
    engine = AutonomousExplorationEngine()
    return engine.explore_application_graph(payload.target_url)


@router.post('/strategy', summary='Generate 16 Enterprise Testing Strategies')
def generate_strategies(payload: StrategyRequest):
    engine = AITestStrategyGenerator()
    return engine.generate_all_strategies(payload.project_name, payload.target_url)
