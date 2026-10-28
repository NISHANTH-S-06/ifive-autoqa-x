from fastapi import APIRouter, Depends, Query, Body, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, List

from app.auth import AuthContext, get_auth_context
from app.database import get_db
from app.services.zero_code_test_studio import ZeroCodeTestStudioService

router = APIRouter(prefix='/test-studio', tags=['zero-code-test-studio'], dependencies=[Depends(get_auth_context)])


@router.get('/step-palette', summary='Get Full Zero-Code Step Palette')
def get_step_palette(context: AuthContext = Depends(get_auth_context), db: Session = Depends(get_db)):
    service = ZeroCodeTestStudioService(db)
    return service.get_available_step_types()


@router.post('/flows', summary='Create a Zero-Code Test Flow')
def create_flow(
    project_id: int = Query(1),
    flow_name: str = Body(..., embed=True),
    flow_type: str = Body('SCENARIO', embed=True),
    flow_steps: List[Dict[str, Any]] = Body([], embed=True),
    context: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db),
):
    service = ZeroCodeTestStudioService(db)
    flow = service.create_flow(
        project_id=project_id,
        flow_name=flow_name,
        flow_type=flow_type,
        flow_steps=flow_steps,
        created_by=context.operator.id,
    )
    return {'id': flow.id, 'flow_name': flow.flow_name, 'flow_type': flow.flow_type, 'step_count': len(flow_steps)}


@router.get('/flows', summary='List Zero-Code Test Flows')
def list_flows(
    project_id: int = Query(1),
    context: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db),
):
    service = ZeroCodeTestStudioService(db)
    return service.list_flows(project_id)


@router.get('/flows/{flow_id}', summary='Get Single Test Flow')
def get_flow(
    flow_id: int,
    context: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db),
):
    service = ZeroCodeTestStudioService(db)
    flow = service.get_flow(flow_id)
    if not flow:
        raise HTTPException(status_code=404, detail='Flow not found')
    return flow


@router.post('/flows/{flow_id}/run', summary='Execute Zero-Code Test Flow')
def run_flow(
    flow_id: int,
    context: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db),
):
    service = ZeroCodeTestStudioService(db)
    return service.run_flow(flow_id)


@router.post('/generate-flow', summary='Generate Test Flow from AI Prompt')
def generate_flow(
    prompt: str = Body(..., embed=True),
    flow_type: str = Body('SCENARIO', embed=True),
    context: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db),
):
    if not prompt or not prompt.strip():
        raise HTTPException(status_code=422, detail='Prompt is required')
    service = ZeroCodeTestStudioService(db)
    return service.generate_flow_from_prompt(prompt, flow_type)


@router.post('/flows/run-canvas', summary='Execute Unsaved Canvas Steps')
def run_canvas_steps(
    flow_steps: List[Dict[str, Any]] = Body([], embed=True),
    flow_name: str = Body('Canvas Execution Flow', embed=True),
    context: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db),
):
    service = ZeroCodeTestStudioService(db)
    return service.run_canvas_steps(flow_steps, flow_name)


@router.delete('/flows/{flow_id}', summary='Delete Test Flow')
def delete_flow(
    flow_id: int,
    context: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db),
):
    service = ZeroCodeTestStudioService(db)
    success = service.delete_flow(flow_id)
    if not success:
        raise HTTPException(status_code=404, detail='Flow not found')
    return {'status': 'deleted', 'id': flow_id}

