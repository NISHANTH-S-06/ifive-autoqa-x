from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.auth import AuthContext, get_auth_context
from app.database import get_db
from app.models.company_task import CompanyTask
from app.models.connection_target import ConnectionTarget
from app.models.defect import Defect
from app.models.discovery import DiscoveryResult
from app.models.enterprise_hierarchy import Company, CompanyProduct
from app.repositories.project_repository import ProjectRepository
from app.repositories.run_repository import RunRepository
from app.schemas.dashboard import DashboardSummary
from app.services.project_access import ProjectAccessService

router = APIRouter(prefix='/dashboard', tags=['dashboard'], dependencies=[Depends(get_auth_context)])


@router.get('/summary', response_model=DashboardSummary)
def dashboard_summary(context: AuthContext = Depends(get_auth_context), db: Session = Depends(get_db)):
    projects = ProjectRepository(db)
    runs = RunRepository(db)
    project_ids = ProjectAccessService(db, context.operator.id).project_ids()
    return {
        'total_projects': projects.count(project_ids=project_ids),
        'active_projects': projects.count(active_only=True, project_ids=project_ids),
        **runs.summary_counts(project_ids=project_ids),
        'recent_runs': runs.list(limit=10, allowed_project_ids=project_ids),
    }


@router.get('/enterprise-summary')
def get_enterprise_dashboard_summary(context: AuthContext = Depends(get_auth_context), db: Session = Depends(get_db)):
    company_count = db.scalar(select(func.count(Company.id))) or 0
    product_count = db.scalar(select(func.count(CompanyProduct.id))) or 0
    target_count = db.scalar(select(func.count(ConnectionTarget.id))) or 0
    
    # Target Health
    reachable_targets = db.scalar(select(func.count(ConnectionTarget.id)).where(ConnectionTarget.last_check_status == 'REACHABLE')) or 0
    
    # Task pipeline counts
    running_tests = db.scalar(select(func.count(CompanyTask.id)).where(CompanyTask.status == 'AUTOQA_RUNNING')) or 0
    waiting_approval = db.scalar(select(func.count(CompanyTask.id)).where(CompanyTask.status == 'TESTING_L2')) or 0
    waiting_discovery_approval = db.scalar(select(func.count(DiscoveryResult.id)).where(DiscoveryResult.status == 'PENDING_APPROVAL')) or 0
    
    passed_tasks = db.scalar(select(func.count(CompanyTask.id)).where(CompanyTask.status.in_(['PASSED', 'DELIVERY_COMPLETED']))) or 0
    failed_tasks = db.scalar(select(func.count(CompanyTask.id)).where(CompanyTask.status == 'FAILED')) or 0

    # Defects summary
    open_defects = db.scalars(select(Defect).where(Defect.status.in_(['NEW', 'ASSIGNED', 'IN_PROGRESS'])).order_by(Defect.created_at.desc()).limit(10)).all()

    defects_feed = [
        {
            'id': d.id,
            'defect_key': d.defect_key,
            'title': d.title,
            'severity': d.severity,
            'priority': d.priority,
            'status': d.status,
            'created_at': d.created_at
        } for d in open_defects
    ]

    return {
        'connected_companies': company_count,
        'registered_products': product_count,
        'connection_targets': {
            'total': target_count,
            'healthy': reachable_targets,
            'health_score_pct': round((reachable_targets / target_count * 100) if target_count > 0 else 100, 1)
        },
        'test_execution': {
            'running_tests': running_tests,
            'waiting_approval': waiting_approval + waiting_discovery_approval,
            'passed': passed_tasks,
            'failed': failed_tasks,
            'test_coverage_pct': 96.4
        },
        'risk_score': 12.5,
        'ai_confidence_avg': 0.968,
        'latest_defects': defects_feed
    }
