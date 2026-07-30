from contextlib import asynccontextmanager
import logging
import time
from uuid import uuid4

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.api import advanced_validation, agents, audit, auth, automated_execution, company_tasks, connection_targets, dashboard, defects, health, local_schedules, operators, projects, reports, results, security, system, task_imports, test_management, test_plans, test_runs, ai, visual_regression, enterprise, discovery, copilot, release_readiness, autonomous_regression, knowledge_graph, digital_qa, digital_twin, continuous_monitoring, predictive_quality, multi_reports, experience_memory, pattern_recognition, test_evolution, root_cause_graph, release_command_center, autonomous_monitoring_v2, onboarding, test_studio, test_lab, data_factory, war_room, plugin_marketplace, integrations
from app.api import (
    distributed_execution, cloud_browser_farm, execution_stream, observability,
    enterprise_analytics, release_governance, compliance_center, api_hub,
    marketplace_ecosystem, enterprise_devops, multi_region_cloud,
    enterprise_security_center, ai_optimizer, executive_command_center,
)
from app.api import (
    enterprise_brain, workflows, business_process, incidents, governance,
    forecast, executive_advisor, knowledge_universe, report_factory, optimization_v2,
)
from app.api import (
    software_graph, change_impact, code_review, coverage, release_intelligence,
    defects_hub, engineering, knowledge_lake, mission_control,
)
from app.api import (
    knowledge_lake_v2, requirements, traceability, architecture, code_quality,
    release_certification, observability_ai, customer_intelligence, policies, sdlc_orchestrator,
)
from app.config import settings
from app.database import SessionLocal, get_db
from app.logging_config import configure_logging, correlation_id_var
from app.migration_safety import assert_database_at_head
from app.seed import seed_local_projects
from app.repositories.run_repository import RunRepository


@asynccontextmanager
async def lifespan(_: FastAPI):
  settings.prepare_directories()
  configure_logging()
  assert_database_at_head(settings.database_url, allow_active=True)
  with SessionLocal() as db:
    seed_local_projects(db)
    recovered = RunRepository(db).recover_interrupted()
    if recovered:
      from app.services.audit_service import append_event
      append_event(db, 'TEST_RUN_INTERRUPTED', 'FAILED', actor_type='SYSTEM', resource_type='TEST_RUN', metadata={'recovered_count': recovered}); db.commit()
  yield

app = FastAPI(
  title='iFive AutoQA API',
  description='Local-first AI-assisted testing platform API.',
  version='1.0.0-local',
  lifespan=lifespan,
)

app.add_middleware(
  CORSMiddleware,
  allow_origins=list({settings.frontend_url, 'http://127.0.0.1:5173', 'http://localhost:5173'}),
  allow_methods=['GET', 'POST', 'PATCH', 'DELETE', 'PUT'],
  allow_headers=['Content-Type', 'X-CSRF-Token'],
  allow_credentials=True,
)


@app.middleware('http')
async def safe_request_logging(request: Request, call_next):
  correlation_id = uuid4().hex
  token = correlation_id_var.set(correlation_id)
  started = time.monotonic()
  logger = logging.getLogger('autoqa.http')
  try:
    response = await call_next(request)
    response.headers['X-Correlation-ID'] = correlation_id
    logger.info(
      'request completed method=%s path=%s status=%s duration_ms=%s',
      request.method,
      request.url.path,
      response.status_code,
      round((time.monotonic() - started) * 1000),
      extra={'category': 'HTTP', 'correlation_id': correlation_id},
    )
    return response
  except Exception as exc:
    logger.error('request failed safely error_category=%s exc=%s', type(exc).__name__, str(exc), exc_info=True, extra={'category': 'HTTP', 'correlation_id': correlation_id})
    response = JSONResponse(status_code=500, content={'detail': 'The request could not be completed safely.'})
    response.headers['X-Correlation-ID'] = correlation_id
    return response
  finally:
    correlation_id_var.reset(token)

app.include_router(health.router, prefix='/api')
app.include_router(auth.router, prefix='/api')
app.include_router(operators.router, prefix='/api')
app.include_router(audit.router, prefix='/api')
app.include_router(projects.router, prefix='/api')
app.include_router(test_runs.router, prefix='/api')
app.include_router(dashboard.router, prefix='/api')
app.include_router(results.router, prefix='/api')
app.include_router(reports.router, prefix='/api')
app.include_router(security.router, prefix='/api')
app.include_router(agents.router, prefix='/api')
app.include_router(test_management.router, prefix='/api')
app.include_router(test_plans.router, prefix='/api')
app.include_router(connection_targets.router, prefix='/api')
app.include_router(automated_execution.router, prefix='/api')
app.include_router(defects.router, prefix='/api')
app.include_router(task_imports.router, prefix='/api')
app.include_router(system.router, prefix='/api')
app.include_router(advanced_validation.router, prefix='/api')
app.include_router(local_schedules.router, prefix='/api')
app.include_router(company_tasks.router, prefix='/api')
app.include_router(ai.router, prefix='/api')
app.include_router(visual_regression.router, prefix='/api')
app.include_router(enterprise.router, prefix='/api')
app.include_router(discovery.router, prefix='/api')
app.include_router(copilot.router, prefix='/api')
app.include_router(release_readiness.router, prefix='/api')
app.include_router(autonomous_regression.router, prefix='/api')
app.include_router(knowledge_graph.router, prefix='/api')
app.include_router(digital_qa.router, prefix='/api')
app.include_router(digital_twin.router, prefix='/api')
app.include_router(continuous_monitoring.router, prefix='/api')
app.include_router(predictive_quality.router, prefix='/api')
app.include_router(multi_reports.router, prefix='/api')
app.include_router(experience_memory.router, prefix='/api')
app.include_router(pattern_recognition.router, prefix='/api')
app.include_router(test_evolution.router, prefix='/api')
app.include_router(root_cause_graph.router, prefix='/api')
app.include_router(release_command_center.router, prefix='/api')
app.include_router(autonomous_monitoring_v2.router, prefix='/api')
app.include_router(onboarding.router, prefix='/api')
app.include_router(test_studio.router, prefix='/api')
app.include_router(test_lab.router, prefix='/api')
app.include_router(data_factory.router, prefix='/api')
app.include_router(war_room.router, prefix='/api')
app.include_router(plugin_marketplace.router, prefix='/api')
app.include_router(integrations.router, prefix='/api')

# ── Phase 13 – Enterprise Cloud Platform ─────────────────────────────────────
app.include_router(distributed_execution.router, prefix='/api')
app.include_router(cloud_browser_farm.router, prefix='/api')
app.include_router(execution_stream.router, prefix='/api')
app.include_router(observability.router, prefix='/api')
app.include_router(enterprise_analytics.router, prefix='/api')
app.include_router(release_governance.router, prefix='/api')
app.include_router(compliance_center.router, prefix='/api')
app.include_router(api_hub.router, prefix='/api')
app.include_router(marketplace_ecosystem.router, prefix='/api')
app.include_router(enterprise_devops.router, prefix='/api')
app.include_router(multi_region_cloud.router, prefix='/api')
app.include_router(enterprise_security_center.router, prefix='/api')
app.include_router(ai_optimizer.router, prefix='/api')
app.include_router(executive_command_center.router, prefix='/api')

# ── Phase 14 – Enterprise Autonomous AI QA Operating System (AI QA OS) ──────
app.include_router(enterprise_brain.router, prefix='/api')
app.include_router(workflows.router, prefix='/api')
app.include_router(business_process.router, prefix='/api')
app.include_router(incidents.router, prefix='/api')
app.include_router(governance.router, prefix='/api')
app.include_router(forecast.router, prefix='/api')
app.include_router(executive_advisor.router, prefix='/api')
app.include_router(knowledge_universe.router, prefix='/api')
app.include_router(report_factory.router, prefix='/api')
app.include_router(optimization_v2.router, prefix='/api')

# ── Phase 15 – Autonomous Enterprise Software Quality Intelligence Platform ──
app.include_router(software_graph.router, prefix='/api')
app.include_router(change_impact.router, prefix='/api')
app.include_router(code_review.router, prefix='/api')
app.include_router(coverage.router, prefix='/api')
app.include_router(release_intelligence.router, prefix='/api')
app.include_router(defects_hub.router, prefix='/api')
app.include_router(engineering.router, prefix='/api')
app.include_router(knowledge_lake.router, prefix='/api')
app.include_router(mission_control.router, prefix='/api')

# ── Phase 16 – Enterprise Autonomous Software Engineering Intelligence Platform ──
app.include_router(knowledge_lake_v2.kl_v2_router)
app.include_router(requirements.req_router)
app.include_router(traceability.trace_router)
app.include_router(architecture.arch_router)
app.include_router(code_quality.code_quality_router)
app.include_router(release_certification.release_cert_router)
app.include_router(observability_ai.observability_router)
app.include_router(customer_intelligence.customer_router)
app.include_router(policies.policy_router)
app.include_router(sdlc_orchestrator.sdlc_router)


@app.get('/')
def root() -> dict[str, str]:
  return {'service': 'iFive AutoQA API', 'status': 'ready'}


@app.get('/health')
def health_alias(db: Session = Depends(get_db)) -> dict:
  return health.health_check(db)
