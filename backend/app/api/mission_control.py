"""Phase 15 – Executive Mission Control & Pair QA & Release Validator API router."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth import get_auth_context, AuthContext
from app.database import get_db
from app.services.autonomous_release_validator import AutonomousReleaseValidator
from app.services.executive_mission_control import ExecutiveMissionControlService, SelfEvolvingIntelligenceService
from app.services.pair_qa_engineer import PairQAEngineerService

router = APIRouter(prefix='/mission-control', tags=['Phase15-MissionControl'])


class PairQAAssistRequest(BaseModel):
    intent: str
    context: dict[str, Any] = {}


class ValidateReleaseRequest(BaseModel):
    release_version: str


@router.get('/dashboard')
def get_mission_control(db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return ExecutiveMissionControlService(db).get_mission_control()


@router.post('/pair-qa/assist')
def pair_qa_assist(body: PairQAAssistRequest, db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return PairQAEngineerService(db).assist(body.intent, body.context)


@router.post('/release-validator/validate')
def validate_release(body: ValidateReleaseRequest, db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return AutonomousReleaseValidator(db).validate_release(body.release_version)


@router.post('/self-evolving/evolve')
def evolve_model(db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return SelfEvolvingIntelligenceService(db).evolve_model()
