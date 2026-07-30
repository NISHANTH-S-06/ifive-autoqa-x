from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DBSession

from app.auth import AuthContext, get_auth_context
from app.database import get_db
from app.models.test_plan import TestPlan
from app.schemas.test_plan import TestPlanOut, TestPlanUpdate, TestPlanReject, TestPlanVersionOut
from app.services import test_plan_service
from app.services.project_access import ProjectAccessService, ProjectAction

router = APIRouter(prefix='/test-plans', tags=['test-plans'])

def _check_plan_access(db: DBSession, plan_id: int, context: AuthContext, action: ProjectAction = ProjectAction.READ) -> TestPlan:
    plan = db.get(TestPlan, plan_id)
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'TestPlan {plan_id} not found.')
    # Actor identity and RBAC/project-isolation are always derived from the
    # authenticated session. There is no unauthenticated read path here.
    ProjectAccessService(db, context.operator.id).require(plan.project_id, action)
    return plan

@router.get('/{plan_id}', response_model=TestPlanOut)
def get_test_plan(plan_id: int, context: AuthContext = Depends(get_auth_context), db: DBSession = Depends(get_db)):
    plan = _check_plan_access(db, plan_id, context, ProjectAction.READ)
    return TestPlanOut.model_validate(plan)

@router.patch('/{plan_id}', response_model=TestPlanOut)
def update_test_plan(plan_id: int, updates: TestPlanUpdate, context: AuthContext = Depends(get_auth_context), db: DBSession = Depends(get_db)):
    _check_plan_access(db, plan_id, context, ProjectAction.TEST)
    plan = test_plan_service.update_plan(db, plan_id, updates, context.operator.id)
    return TestPlanOut.model_validate(plan)

@router.post('/{plan_id}/submit', response_model=TestPlanOut)
def submit_test_plan(plan_id: int, context: AuthContext = Depends(get_auth_context), db: DBSession = Depends(get_db)):
    _check_plan_access(db, plan_id, context, ProjectAction.TEST)
    plan = test_plan_service.submit_plan(db, plan_id, context.operator.id)
    return TestPlanOut.model_validate(plan)

@router.post('/{plan_id}/approve', response_model=TestPlanOut)
def approve_test_plan(plan_id: int, context: AuthContext = Depends(get_auth_context), db: DBSession = Depends(get_db)):
    _check_plan_access(db, plan_id, context, ProjectAction.APPROVE)
    plan = test_plan_service.approve_plan(db, plan_id, context.operator.id)
    return TestPlanOut.model_validate(plan)

@router.post('/{plan_id}/reject', response_model=TestPlanOut)
def reject_test_plan(plan_id: int, payload: TestPlanReject, context: AuthContext = Depends(get_auth_context), db: DBSession = Depends(get_db)):
    _check_plan_access(db, plan_id, context, ProjectAction.APPROVE)
    plan = test_plan_service.reject_plan(db, plan_id, payload, context.operator.id)
    return TestPlanOut.model_validate(plan)
