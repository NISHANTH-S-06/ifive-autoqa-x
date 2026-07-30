import base64
import io
import pytest
from PIL import Image, ImageDraw
from sqlalchemy import select

from app.models.project import Project
from app.models.visual_regression import VisualBaseline, VisualBaselineHistory, VisualComparisonRun
from app.services.visual_regression_engine import visual_engine


def create_sample_png(width: int = 400, height: int = 300, color: tuple = (255, 255, 255), add_shape: bool = False) -> bytes:
    """Helper to generate in-memory PNG images for testing."""
    img = Image.new('RGB', (width, height), color=color)
    if add_shape:
        draw = ImageDraw.Draw(img)
        draw.rectangle([50, 50, 200, 150], fill=(255, 0, 0))
        draw.ellipse([220, 160, 350, 250], fill=(0, 0, 255))
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return buf.getvalue()


def get_test_project(db):
    proj = db.scalar(select(Project))
    if not proj:
        proj = Project(name='Test Visual Project', product_code='AUTOQA', environment='local', is_active=True)
        db.add(proj)
        db.commit()
        db.refresh(proj)
    return proj


def test_baseline_creation_and_versioning(db):
    """Test baseline creation, versioning, and history tracking."""
    proj = get_test_project(db)


    # 1. Create baseline
    png_data = create_sample_png(400, 300, color=(240, 240, 240))
    baseline = visual_engine.create_baseline(
        db,
        project_id=proj.id,
        name='ERP Navigation Header',
        module='ERP',
        browser='chromium',
        viewport_width=1280,
        viewport_height=720,
        capture_type='VIEWPORT',
        route_path='/erp/dashboard',
        image_bytes=png_data,
        ignore_rules={'regions': [{'x': 10, 'y': 10, 'width': 50, 'height': 20}]},
        created_by=1,
    )

    assert baseline.id is not None
    assert baseline.version == 1
    assert baseline.module == 'ERP'

    # Check history
    history = visual_engine.get_baseline_history(db, baseline.id)
    assert len(history) == 1
    assert history[0].version == 1

    # 2. Update baseline
    updated_png = create_sample_png(400, 300, color=(250, 250, 250), add_shape=True)
    updated_baseline = visual_engine.update_baseline(
        db,
        baseline_id=baseline.id,
        image_bytes=updated_png,
        change_summary='Updated header redesign',
        created_by=1,
    )

    assert updated_baseline.version == 2
    history_updated = visual_engine.get_baseline_history(db, baseline.id)
    assert len(history_updated) == 2
    assert history_updated[0].version == 2


def test_baseline_lookup(db):
    """Test baseline lookup matching by attributes and resolution."""
    proj = get_test_project(db)
    png_data = create_sample_png(400, 300)

    visual_engine.create_baseline(
        db,
        project_id=proj.id,
        name='HRMS Employee List',
        module='HRMS',
        browser='chromium',
        viewport_width=1280,
        viewport_height=720,
        route_path='/hrms/employees',
        image_bytes=png_data,
    )

    matched = visual_engine.lookup_baseline(
        db,
        project_id=proj.id,
        module='HRMS',
        browser='chromium',
        viewport_width=1280,
        viewport_height=720,
        route_path='/hrms/employees',
    )
    assert matched is not None
    assert matched.name == 'HRMS Employee List'


def test_image_comparison_and_ignore_rules():
    """Test pixel difference detection and ignore rules masking."""
    base_bytes = create_sample_png(400, 300, color=(255, 255, 255))
    curr_bytes = create_sample_png(400, 300, color=(255, 255, 255), add_shape=True)

    # Comparison without ignore rules
    b_img, c_img, metrics_no_ignore = visual_engine.compare_images(base_bytes, curr_bytes)
    assert metrics_no_ignore['diff_percentage'] > 0
    assert metrics_no_ignore['total_pixels_changed'] > 0

    # Comparison with ignore rule masking out the shape area [50,50,350,250]
    ignore_rules = {'regions': [{'x': 40, 'y': 40, 'width': 320, 'height': 220}]}
    _, _, metrics_ignored = visual_engine.compare_images(base_bytes, curr_bytes, ignore_rules)
    assert metrics_ignored['diff_percentage'] < metrics_no_ignore['diff_percentage']


def test_ai_visual_analyzer_classification():
    """Test AI Visual Analyzer severity and classification output."""
    base_b = visual_engine.lookup_baseline  # dummy
    # Case 1: Cosmetic
    metrics_cosmetic = {'diff_percentage': 0.01, 'total_pixels_changed': 20, 'missing_elements_count': 0, 'layout_shifts': 0}
    res_c = visual_engine.analyze_visual_difference(metrics_cosmetic, base_b)
    assert res_c['ai_classification'] == 'COSMETIC'

    # Case 2: Critical
    metrics_critical = {'diff_percentage': 12.5, 'total_pixels_changed': 15000, 'missing_elements_count': 4, 'layout_shifts': 3}
    res_crit = visual_engine.analyze_visual_difference(metrics_critical, base_b)
    assert res_crit['ai_classification'] == 'CRITICAL'
    assert 'CRITICAL' in res_crit['ai_recommendation']


def test_full_pipeline_execution(db):
    """Test full Visual Regression pipeline execution."""
    proj = get_test_project(db)
    curr_bytes = create_sample_png(400, 300, color=(255, 255, 255), add_shape=True)

    comp = visual_engine.execute_comparison(
        db=db,
        project_id=proj.id,
        current_image_bytes=curr_bytes,
        name='Full Pipeline Verification',
        module='DASHBOARD',
        browser='chromium',
        viewport_width=1280,
        viewport_height=720,
        route_path='/dashboard',
    )

    assert comp.id is not None
    assert comp.baseline_id is not None
    assert comp.current_image_path is not None
    assert comp.diff_image_path is not None
    assert comp.overlay_image_path is not None
    assert comp.heatmap_image_path is not None
    assert comp.bounding_box_image_path is not None


def test_visual_api_endpoints(client, db):
    """Test Visual Regression API endpoints."""
    proj = get_test_project(db)
    png_data = create_sample_png(400, 300, color=(240, 240, 240))
    b64_image = base64.b64encode(png_data).decode('utf-8')

    # 1. Create baseline endpoint
    resp_b = client.post(
        '/api/visual/baseline/json',
        json={
            'project_id': proj.id,
            'name': 'API Test Baseline',
            'module': 'AUTHENTICATION',
            'browser': 'chromium',
            'viewport_width': 1280,
            'viewport_height': 720,
            'route_path': '/login',
            'image_base64': b64_image,
        },
    )
    assert resp_b.status_code == 201
    baseline_id = resp_b.json()['id']

    # 2. Compare endpoint
    curr_png = create_sample_png(400, 300, color=(255, 255, 255), add_shape=True)
    b64_curr = base64.b64encode(curr_png).decode('utf-8')
    resp_c = client.post(
        '/api/visual/compare/json',
        json={
            'project_id': proj.id,
            'baseline_id': baseline_id,
            'name': 'API Test Comparison',
            'module': 'AUTHENTICATION',
            'browser': 'chromium',
            'viewport_width': 1280,
            'viewport_height': 720,
            'route_path': '/login',
            'image_base64': b64_curr,
        },
    )
    assert resp_c.status_code == 200
    comp_data = resp_c.json()
    comp_id = comp_data['id']
    assert comp_data['status'] in {'DIFF_DETECTED', 'FAILED', 'PASSED'}

    # 3. History endpoint
    resp_h = client.get('/api/visual/history?module=AUTHENTICATION')
    assert resp_h.status_code == 200
    assert resp_h.json()['total'] >= 1

    # 4. Baselines list endpoint
    resp_list = client.get(f'/api/visual/baselines?project_id={proj.id}')
    assert resp_list.status_code == 200
    assert len(resp_list.json()) >= 1

    # 5. Artifact streaming endpoint
    resp_art = client.get(f'/api/visual/artifacts/{comp_id}/diff')
    assert resp_art.status_code == 200
    assert resp_art.headers['content-type'] == 'image/png'
