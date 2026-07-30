"""Phase 13 – Enterprise Analytics API router."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth import get_auth_context, AuthContext
from app.database import get_db
from app.services.enterprise_analytics_engine import EnterpriseAnalyticsEngine

router = APIRouter(prefix='/analytics', tags=['Phase13-Analytics'])


@router.get('/quality-trends')
def quality_trends(project_id: int | None = None, db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return EnterpriseAnalyticsEngine(db).get_quality_trends(project_id=project_id)


@router.get('/release-trends')
def release_trends(project_id: int | None = None, db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return EnterpriseAnalyticsEngine(db).get_release_trends(project_id=project_id)


@router.get('/developer-quality')
def developer_quality(project_id: int | None = None, db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return EnterpriseAnalyticsEngine(db).get_developer_quality(project_id=project_id)


@router.get('/failure-heatmap')
def failure_heatmap(project_id: int | None = None, db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return EnterpriseAnalyticsEngine(db).get_failure_heatmap(project_id=project_id)


@router.get('/flaky-tests')
def flaky_tests(project_id: int | None = None, db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return EnterpriseAnalyticsEngine(db).get_flaky_tests(project_id=project_id)


@router.get('/browser-stats')
def browser_stats(db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return EnterpriseAnalyticsEngine(db).get_browser_stats()


@router.get('/cost')
def cost_analytics(project_id: int | None = None, db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return EnterpriseAnalyticsEngine(db).get_cost_analytics(project_id=project_id)


@router.get('/kpis')
def all_kpis(db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    return EnterpriseAnalyticsEngine(db).get_all_kpis()


@router.post('/snapshots/{snapshot_type}', status_code=201)
def generate_snapshot(snapshot_type: str, project_id: int | None = None, db: Session = Depends(get_db), _: AuthContext = Depends(get_auth_context)):
    snap = EnterpriseAnalyticsEngine(db).generate_snapshot(snapshot_type, project_id)
    return {'id': snap.id, 'snapshot_type': snap.snapshot_type, 'quality_score': snap.quality_score}
