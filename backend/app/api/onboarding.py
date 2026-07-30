from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.auth import AuthContext, get_auth_context
from app.database import get_db
from app.services.zero_code_onboarding import ZeroCodeOnboardingService

router = APIRouter(prefix='/onboarding', tags=['zero-code-onboarding'], dependencies=[Depends(get_auth_context)])


@router.post('/start', summary='Start Zero-Code Guided Onboarding Wizard Session')
def start_onboarding(
    company_name: str = Body(..., embed=True),
    product_name: str = Body(..., embed=True),
    application_url: str = Body(..., embed=True),
    auth_type: str = Body('USERNAME_PASSWORD', embed=True),
    auth_config: Dict[str, Any] = Body({}, embed=True),
    browser_selection: str = Body('CHROMIUM', embed=True),
    environment: str = Body('QA', embed=True),
    context: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db),
):
    service = ZeroCodeOnboardingService(db)
    session = service.start_session(
        company_name=company_name,
        product_name=product_name,
        application_url=application_url,
        auth_type=auth_type,
        auth_config=auth_config,
        browser_selection=browser_selection,
        environment=environment,
        created_by=context.operator.id,
    )
    return {
        'session_id': session.id,
        'company_name': session.company_name,
        'product_name': session.product_name,
        'application_url': session.application_url,
        'auth_type': session.auth_type,
        'browser_selection': session.browser_selection,
        'environment': session.environment,
        'current_step': session.current_step,
        'validation_status': session.validation_status,
    }


@router.post('/validate/{session_id}', summary='Step 7 – AI Connection Validation')
def validate_connection(
    session_id: int,
    context: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db),
):
    service = ZeroCodeOnboardingService(db)
    return service.validate_connection(session_id)


@router.get('/session/{session_id}', summary='Get Onboarding Session Details')
def get_session(
    session_id: int,
    context: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db),
):
    service = ZeroCodeOnboardingService(db)
    session = service.get_session(session_id)
    if not session:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail='Onboarding session not found')
    return {
        'session_id': session.id,
        'company_name': session.company_name,
        'product_name': session.product_name,
        'application_url': session.application_url,
        'auth_type': session.auth_type,
        'browser_selection': session.browser_selection,
        'environment': session.environment,
        'validation_status': session.validation_status,
        'current_step': session.current_step,
    }
