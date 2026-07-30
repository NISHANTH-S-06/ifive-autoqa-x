import base64
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, Response, UploadFile
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import AuthContext, get_auth_context, require_csrf
from app.config import settings
from app.database import get_db
from app.models.visual_regression import VisualBaseline, VisualBaselineHistory, VisualComparisonRun
from app.services.visual_regression_engine import visual_engine

router = APIRouter(prefix='/visual', tags=['visual-regression'])


class CreateBaselineRequest(BaseModel):
    project_id: int
    name: str = Field(min_length=1, max_length=120)
    module: str = Field(default='GENERAL', max_length=60)
    browser: str = Field(default='chromium', max_length=30)
    viewport_width: int = Field(default=1280, ge=320, le=3840)
    viewport_height: int = Field(default=720, ge=240, le=2160)
    capture_type: str = Field(default='VIEWPORT')
    element_selector: Optional[str] = None
    route_path: str = Field(default='/', max_length=255)
    ignore_rules: Optional[Dict[str, Any]] = None
    image_base64: Optional[str] = None


class CompareRequest(BaseModel):
    project_id: int
    baseline_id: Optional[int] = None
    name: str = Field(default='Visual Regression Check', max_length=120)
    module: str = Field(default='GENERAL', max_length=60)
    browser: str = Field(default='chromium', max_length=30)
    viewport_width: int = Field(default=1280, ge=320, le=3840)
    viewport_height: int = Field(default=720, ge=240, le=2160)
    route_path: str = Field(default='/', max_length=255)
    capture_type: str = Field(default='VIEWPORT')
    run_id: Optional[int] = None
    ignore_rules: Optional[Dict[str, Any]] = None
    image_base64: Optional[str] = None


@router.post('/baseline', status_code=201)
async def create_or_update_baseline(
    project_id: int = Form(...),
    name: str = Form(...),
    module: str = Form('GENERAL'),
    browser: str = Form('chromium'),
    viewport_width: int = Form(1280),
    viewport_height: int = Form(720),
    capture_type: str = Form('VIEWPORT'),
    element_selector: Optional[str] = Form(None),
    route_path: str = Form('/'),
    ignore_rules_json: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    context: AuthContext = Depends(require_csrf),
    db: Session = Depends(get_db),
):
    """Create or update a visual regression baseline."""
    image_bytes = None
    if file:
        image_bytes = await file.read()

    ignore_rules = None
    if ignore_rules_json:
        try:
            ignore_rules = json.loads(ignore_rules_json)
        except Exception:
            raise HTTPException(status_code=422, detail='Invalid ignore_rules_json format.')

    existing = visual_engine.lookup_baseline(
        db,
        project_id=project_id,
        module=module,
        browser=browser,
        viewport_width=viewport_width,
        viewport_height=viewport_height,
        route_path=route_path,
        capture_type=capture_type,
        name=name,
    )

    if existing and image_bytes:
        baseline = visual_engine.update_baseline(
            db,
            baseline_id=existing.id,
            image_bytes=image_bytes,
            ignore_rules=ignore_rules,
            change_summary=f"Updated baseline via API for {name}",
            created_by=context.operator.id,
        )
    else:
        baseline = visual_engine.create_baseline(
            db,
            project_id=project_id,
            name=name,
            module=module,
            browser=browser,
            viewport_width=viewport_width,
            viewport_height=viewport_height,
            capture_type=capture_type,
            element_selector=element_selector,
            route_path=route_path,
            image_bytes=image_bytes,
            ignore_rules=ignore_rules,
            created_by=context.operator.id,
        )

    return baseline


@router.post('/baseline/json', status_code=201)
def create_baseline_json(
    payload: CreateBaselineRequest,
    context: AuthContext = Depends(require_csrf),
    db: Session = Depends(get_db),
):
    """Create baseline using JSON payload with base64 image."""
    image_bytes = None
    if payload.image_base64:
        try:
            image_bytes = base64.b64decode(payload.image_base64.split(',')[-1])
        except Exception:
            raise HTTPException(status_code=422, detail='Invalid base64 image data.')

    baseline = visual_engine.create_baseline(
        db,
        project_id=payload.project_id,
        name=payload.name,
        module=payload.module,
        browser=payload.browser,
        viewport_width=payload.viewport_width,
        viewport_height=payload.viewport_height,
        capture_type=payload.capture_type,
        element_selector=payload.element_selector,
        route_path=payload.route_path,
        image_bytes=image_bytes,
        ignore_rules=payload.ignore_rules,
        created_by=context.operator.id,
    )
    return baseline


@router.post('/compare', status_code=200)
async def compare_images(
    project_id: int = Form(...),
    baseline_id: Optional[int] = Form(None),
    name: str = Form('Visual Regression Check'),
    module: str = Form('GENERAL'),
    browser: str = Form('chromium'),
    viewport_width: int = Form(1280),
    viewport_height: int = Form(720),
    route_path: str = Form('/'),
    capture_type: str = Form('VIEWPORT'),
    run_id: Optional[int] = Form(None),
    ignore_rules_json: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    context: AuthContext = Depends(require_csrf),
    db: Session = Depends(get_db),
):
    """Compare current image against baseline and execute full analysis."""
    image_bytes = None
    if file:
        image_bytes = await file.read()

    if not image_bytes:
        raise HTTPException(status_code=422, detail='Image file is required for comparison.')

    ignore_rules = None
    if ignore_rules_json:
        try:
            ignore_rules = json.loads(ignore_rules_json)
        except Exception:
            pass

    comparison = visual_engine.execute_comparison(
        db=db,
        project_id=project_id,
        current_image_bytes=image_bytes,
        baseline_id=baseline_id,
        name=name,
        module=module,
        browser=browser,
        viewport_width=viewport_width,
        viewport_height=viewport_height,
        route_path=route_path,
        capture_type=capture_type,
        run_id=run_id,
        ignore_rules=ignore_rules,
        created_by=context.operator.id,
    )

    return comparison


@router.post('/compare/json', status_code=200)
def compare_images_json(
    payload: CompareRequest,
    context: AuthContext = Depends(require_csrf),
    db: Session = Depends(get_db),
):
    """Compare current image using JSON payload with base64 encoded image."""
    image_bytes = None
    if payload.image_base64:
        try:
            image_bytes = base64.b64decode(payload.image_base64.split(',')[-1])
        except Exception:
            raise HTTPException(status_code=422, detail='Invalid base64 image data.')

    if not image_bytes:
        raise HTTPException(status_code=422, detail='Image base64 content is required for comparison.')

    comparison = visual_engine.execute_comparison(
        db=db,
        project_id=payload.project_id,
        current_image_bytes=image_bytes,
        baseline_id=payload.baseline_id,
        name=payload.name,
        module=payload.module,
        browser=payload.browser,
        viewport_width=payload.viewport_width,
        viewport_height=payload.viewport_height,
        route_path=payload.route_path,
        capture_type=payload.capture_type,
        run_id=payload.run_id,
        ignore_rules=payload.ignore_rules,
        created_by=context.operator.id,
    )
    return comparison


@router.get('/results/{run_id}')
def get_visual_results(
    run_id: int,
    context: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db),
):
    """Retrieve visual regression comparison results for a specific run_id or comparison_run_id."""
    # First search by automated run_id
    stmt = select(VisualComparisonRun).where(VisualComparisonRun.run_id == run_id)
    comparisons = list(db.scalars(stmt).all())

    if not comparisons:
        # Fallback to direct comparison_run_id lookup
        comp = db.get(VisualComparisonRun, run_id)
        if comp:
            comparisons = [comp]

    if not comparisons:
        raise HTTPException(status_code=404, detail=f'No visual regression comparison results found for run_id {run_id}.')

    return comparisons


@router.get('/history')
def get_visual_history(
    project_id: Optional[int] = Query(None),
    module: Optional[str] = Query(None),
    browser: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    ai_classification: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    context: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db),
):
    """Retrieve history of visual comparison runs with filters."""
    stmt = select(VisualComparisonRun).order_by(VisualComparisonRun.created_at.desc())

    if project_id:
        stmt = stmt.where(VisualComparisonRun.project_id == project_id)
    if module:
        stmt = stmt.where(VisualComparisonRun.module == module.upper())
    if browser:
        stmt = stmt.where(VisualComparisonRun.browser == browser.lower())
    if severity:
        stmt = stmt.where(VisualComparisonRun.ai_severity == severity.upper())
    if ai_classification:
        stmt = stmt.where(VisualComparisonRun.ai_classification == ai_classification.upper())
    if status:
        stmt = stmt.where(VisualComparisonRun.status == status.upper())

    stmt = stmt.offset(offset).limit(limit)
    results = list(db.scalars(stmt).all())

    return {
        'total': len(results),
        'offset': offset,
        'limit': limit,
        'comparisons': results,
    }


@router.get('/baselines')
def list_baselines(
    project_id: Optional[int] = Query(None),
    module: Optional[str] = Query(None),
    browser: Optional[str] = Query(None),
    is_active: bool = Query(True),
    context: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db),
):
    """List registered baselines."""
    stmt = select(VisualBaseline).where(VisualBaseline.is_active == is_active).order_by(VisualBaseline.created_at.desc())
    if project_id:
        stmt = stmt.where(VisualBaseline.project_id == project_id)
    if module:
        stmt = stmt.where(VisualBaseline.module == module.upper())
    if browser:
        stmt = stmt.where(VisualBaseline.browser == browser.lower())

    return list(db.scalars(stmt).all())


@router.get('/baselines/{baseline_id}/history')
def get_baseline_history(
    baseline_id: int,
    context: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db),
):
    """Retrieve version history for a specific baseline."""
    baseline = db.get(VisualBaseline, baseline_id)
    if not baseline:
        raise HTTPException(status_code=404, detail='Baseline not found.')

    return visual_engine.get_baseline_history(db, baseline_id)


@router.get('/artifacts/{comparison_id}/{artifact_type}')
def get_artifact_image(
    comparison_id: int,
    artifact_type: str,
    context: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db),
):
    """
    Serve visual diff artifact images (baseline, current, diff, overlay, heatmap, bounding_box).
    """
    comparison = db.get(VisualComparisonRun, comparison_id)
    if not comparison:
        raise HTTPException(status_code=404, detail='Visual comparison run not found.')

    path_map = {
        'baseline': comparison.baseline.image_path if comparison.baseline else None,
        'current': comparison.current_image_path,
        'diff': comparison.diff_image_path,
        'overlay': comparison.overlay_image_path,
        'heatmap': comparison.heatmap_image_path,
        'bounding_box': comparison.bounding_box_image_path,
    }

    rel_path = path_map.get(artifact_type.lower())
    if not rel_path:
        raise HTTPException(status_code=404, detail=f'Artifact type {artifact_type} not available.')

    full_path = settings.data_root / rel_path
    if not full_path.is_file():
        raise HTTPException(status_code=404, detail='Artifact file not found on disk.')

    return Response(content=full_path.read_bytes(), media_type='image/png')
