from contextlib import asynccontextmanager
import logging
import time
from uuid import uuid4

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.api import agents, audit, auth, automated_execution, connection_targets, dashboard, defects, health, operators, projects, reports, results, security, system, test_management, test_runs
from app.config import settings
from app.database import Base, SessionLocal, engine, get_db
from app.logging_config import configure_logging, correlation_id_var
from app.migrations import install_audit_protection, migrate_stage4_schema, migrate_stage6_schema, migrate_stage8_schema, migrate_stage9_schema, migrate_stage10_schema, migrate_stage11_schema, migrate_stage12_schema, migrate_stage13_schema
from app.models import agent_suggestion, audit_event, automated_execution as automated_execution_models, connection_target, defect, evidence, operator, operator_session, password_history, project, reporting, test_case, test_management as test_management_models, test_result, test_run, test_suite
from app.seed import seed_local_projects
from app.repositories.run_repository import RunRepository


@asynccontextmanager
async def lifespan(_: FastAPI):
  settings.prepare_directories()
  configure_logging()
  migrate_stage4_schema(engine)
  migrate_stage6_schema(engine)
  migrate_stage8_schema(engine)
  migrate_stage9_schema(engine)
  migrate_stage10_schema(engine)
  migrate_stage11_schema(engine)
  migrate_stage12_schema(engine)
  migrate_stage13_schema(engine)
  Base.metadata.create_all(bind=engine)
  install_audit_protection(engine)
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
  allow_methods=['GET', 'POST', 'PATCH', 'DELETE'],
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
    logger.error('request failed safely error_category=%s', type(exc).__name__, extra={'category': 'HTTP', 'correlation_id': correlation_id})
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
app.include_router(connection_targets.router, prefix='/api')
app.include_router(automated_execution.router, prefix='/api')
app.include_router(defects.router, prefix='/api')
app.include_router(system.router, prefix='/api')


@app.get('/')
def root() -> dict[str, str]:
  return {'service': 'iFive AutoQA API', 'status': 'ready'}


@app.get('/health')
def health_alias(db: Session = Depends(get_db)) -> dict:
  return health.health_check(db)
