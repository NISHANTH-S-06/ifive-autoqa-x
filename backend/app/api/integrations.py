from fastapi import APIRouter, Depends, Query, Body, Path
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.auth import AuthContext, get_auth_context
from app.database import get_db
from app.services.enterprise_integrations import EnterpriseIntegrationsService
from app.ai.copilot_v4 import ExecutiveCopilotV4

router = APIRouter(prefix='/integrations', tags=['enterprise-integrations'], dependencies=[Depends(get_auth_context)])


@router.get('/supported', summary='List All Supported Integration Types')
def get_supported(context: AuthContext = Depends(get_auth_context)):
    service = EnterpriseIntegrationsService.__new__(EnterpriseIntegrationsService)
    return {'supported_integrations': service.get_supported_integrations()}


@router.get('/', summary='List Project Integrations')
def list_integrations(
    project_id: int = Query(1),
    context: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db),
):
    service = EnterpriseIntegrationsService(db)
    return service.list_integrations(project_id)


@router.post('/', summary='Add Enterprise Integration')
def add_integration(
    project_id: int = Query(1),
    integration_type: str = Body(..., embed=True),
    integration_name: str = Body(..., embed=True),
    config: Dict[str, Any] = Body({}, embed=True),
    context: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db),
):
    service = EnterpriseIntegrationsService(db)
    cfg = service.add_integration(project_id, integration_type, integration_name, config)
    return {'id': cfg.id, 'integration_type': cfg.integration_type, 'is_active': cfg.is_active}


@router.post('/{integration_id}/test', summary='Test Integration Connectivity')
def test_integration(
    integration_id: int = Path(...),
    context: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db),
):
    service = EnterpriseIntegrationsService(db)
    return service.test_integration(integration_id)


@router.post('/copilot-v4/command', summary='AI Executive Copilot V4 – Natural Language Command')
def copilot_command(
    command: str = Body(..., embed=True),
    context: AuthContext = Depends(get_auth_context),
):
    copilot = ExecutiveCopilotV4()
    return copilot.process_command(command)
