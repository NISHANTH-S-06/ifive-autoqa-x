# Backend Inventory — iFive AutoQA Platform

> **Last updated:** 2026-07-29 | **Phase:** 16

Complete inventory of all Python files in the backend layer with their status, purpose, and key dependencies.

---

## backend/app/main.py — Application Entry Point

| File | Status | Purpose |
|------|--------|---------|
| `main.py` | ✅ ACTIVE | FastAPI app factory, lifespan, CORS, request logging middleware, all 90 router registrations |

---

## backend/app/ — Core Application Files

| File | Status | Purpose |
|------|--------|---------|
| `auth.py` | ✅ ACTIVE | `AuthContext` dataclass, `get_auth_context` dependency, cookie/CSRF session validation |
| `config.py` | ✅ ACTIVE | Frozen `Settings` dataclass, all env vars, path resolution, validation |
| `database.py` | ✅ ACTIVE | SQLAlchemy engine creation, `SessionLocal`, `get_db` dependency |
| `logging_config.py` | ✅ ACTIVE | Rotating file + console JSON logging setup, `correlation_id_var` context var |
| `migration_config.py` | ✅ ACTIVE | Alembic environment configuration helper |
| `migration_metadata.py` | ✅ ACTIVE | SQLAlchemy metadata for all models (used by Alembic) |
| `migration_safety.py` | ✅ ACTIVE | `assert_database_at_head` — blocks startup if DB schema is not at head |
| `migrations.py` | ✅ ACTIVE | Programmatic migration helpers, upgrade/downgrade logic |
| `security.py` | ✅ ACTIVE | PBKDF2 hash/verify, CSRF token generation |
| `seed.py` | ✅ ACTIVE | Seeds default local projects on startup |

---

## backend/app/api/ — API Routers (90 files)

### Core Platform

| File | Status | Router Prefix | Key Endpoints |
|------|--------|--------------|--------------|
| `health.py` | ✅ ACTIVE | `/api/health` | `GET /health` — DB health snapshot |
| `auth.py` | ✅ ACTIVE | `/api/auth` | login, logout, me, csrf, change-password, change-required-password |
| `operators.py` | ✅ ACTIVE | `/api/operators` | CRUD operators, RBAC admin routes |
| `audit.py` | ✅ ACTIVE | `/api/audit` | Audit event log, chain verification |
| `projects.py` | ✅ ACTIVE | `/api/projects` | Project CRUD, membership |
| `dashboard.py` | ✅ ACTIVE | `/api/dashboard` | Dashboard metrics, health summary |
| `results.py` | ✅ ACTIVE | `/api/results` | Test result evidence |
| `reports.py` | ✅ ACTIVE | `/api/reports` | Management reports (HTML/PDF export) |
| `security.py` | ✅ ACTIVE | `/api/security` | Security reporting, session revocation |
| `system.py` | ✅ ACTIVE | `/api/system` | System info, backup, disk usage, environment |

### Test Management

| File | Status | Router Prefix | Key Endpoints |
|------|--------|--------------|--------------|
| `test_management.py` | ✅ ACTIVE | `/api/test-management` | Suites, cases, steps, runs, evidence, lifecycle |
| `test_plans.py` | ✅ ACTIVE | `/api/test-plans` | Test plan CRUD, version snapshots, approval |
| `test_runs.py` | ✅ ACTIVE | `/api/test-runs` | Playwright run records, status, completion |
| `task_imports.py` | ✅ ACTIVE | `/api/task-imports` | External task import from mock portal, AI analysis |
| `company_tasks.py` | ✅ ACTIVE | `/api/company-tasks` | Task lifecycle, assignments, comments, status |
| `defects.py` | ✅ ACTIVE | `/api/defects` | Defect CRUD, comments, retest, evidence links |

### Automation & Execution

| File | Status | Router Prefix | Key Endpoints |
|------|--------|--------------|--------------|
| `automated_execution.py` | ✅ ACTIVE | `/api/automated-execution` | Job queue, worker, automated run lifecycle |
| `connection_targets.py` | ✅ ACTIVE | `/api/connection-targets` | Target registry, policy checks, connectivity probe |
| `visual_regression.py` | ✅ ACTIVE | `/api/visual-regression` | Baseline capture, diff analysis, visual test runs |
| `advanced_validation.py` | ✅ ACTIVE | `/api/advanced-validation` | API/DB/accessibility/performance validation |
| `local_schedules.py` | ✅ ACTIVE | `/api/local-schedules` | Cron schedule management, trigger history |
| `discovery.py` | ✅ ACTIVE | `/api/discovery` | AI flow discovery, website crawl, sitemap analysis |
| `agents.py` | ✅ ACTIVE | `/api/agents` | 13 specialized AI agents, pipeline orchestration |
| `ai.py` | ✅ ACTIVE | `/api/ai` | AI analysis, pair QA, multi-agent AI operations |

### AI & Intelligence

| File | Status | Router Prefix | Key Endpoints |
|------|--------|--------------|--------------|
| `copilot.py` | ✅ ACTIVE | `/api/copilot` | AI copilot query endpoint |
| `knowledge_graph.py` | ✅ ACTIVE | `/api/knowledge-graph` | Application topology graph |
| `digital_twin.py` | ✅ ACTIVE | `/api/digital-twin` | Digital twin application mirror |
| `digital_qa.py` | ✅ ACTIVE | `/api/digital-qa` | Digital QA engineer actions |
| `continuous_monitoring.py` | ✅ ACTIVE | `/api/monitoring` | Autonomous monitoring alerts |
| `autonomous_monitoring_v2.py` | ✅ ACTIVE | `/api/autonomous-monitoring` | V2 monitoring status |
| `predictive_quality.py` | ✅ ACTIVE | `/api/predictive` | Quality failure density forecast |
| `autonomous_regression.py` | ✅ ACTIVE | `/api/autonomous-regression` | Autonomous regression trigger |
| `experience_memory.py` | ✅ ACTIVE | `/api/experience-memory` | AI memory and learned patterns |
| `pattern_recognition.py` | ✅ ACTIVE | `/api/pattern-recognition` | Pattern detection results |
| `test_evolution.py` | ✅ ACTIVE | `/api/test-evolution` | Self-evolution dashboard data |
| `root_cause_graph.py` | ✅ ACTIVE | `/api/root-cause` | Root cause graph analysis |

### Phase 13 — Enterprise Cloud Platform

| File | Status | Router Prefix | Key Endpoints |
|------|--------|--------------|--------------|
| `distributed_execution.py` | ✅ ACTIVE | `/api/distributed-execution` | Distributed job dispatch, execution jobs |
| `cloud_browser_farm.py` | ✅ ACTIVE | `/api/browser-farm` | Browser farm sessions, node status |
| `execution_stream.py` | ✅ ACTIVE | `/api/execution-stream` | Real-time execution event stream |
| `observability.py` | ✅ ACTIVE | `/api/observability` | Platform observability metrics |
| `enterprise_analytics.py` | ✅ ACTIVE | `/api/enterprise-analytics` | Enterprise-level analytics |
| `release_governance.py` | ✅ ACTIVE | `/api/release-governance` | Release gates, governance policies |
| `compliance_center.py` | ✅ ACTIVE | `/api/compliance` | Compliance reports, audit readiness |
| `api_hub.py` | ✅ ACTIVE | `/api/api-hub` | API catalog, integration hub |
| `marketplace_ecosystem.py` | ✅ ACTIVE | `/api/marketplace` | Plugin and extension marketplace |
| `enterprise_devops.py` | ✅ ACTIVE | `/api/enterprise-devops` | CI/CD pipeline integration data |
| `multi_region_cloud.py` | ✅ ACTIVE | `/api/multi-region` | Multi-region cloud dashboard |
| `enterprise_security_center.py` | ✅ ACTIVE | `/api/enterprise-security` | Enterprise security posture |
| `ai_optimizer.py` | ✅ ACTIVE | `/api/ai-optimizer` | AI optimizer, worker status |
| `executive_command_center.py` | ✅ ACTIVE | `/api/executive-command` | Global command center overview |

### Phase 14 — AI QA Operating System

| File | Status | Router Prefix | Key Endpoints |
|------|--------|--------------|--------------|
| `enterprise_brain.py` | ✅ ACTIVE | `/api/enterprise-brain` | AI brain inference, recommendations |
| `workflows.py` | ✅ ACTIVE | `/api/workflows` | Workflow definitions, composer |
| `business_process.py` | ✅ ACTIVE | `/api/business-process` | Business process mapping |
| `incidents.py` | ✅ ACTIVE | `/api/incidents` | Incident lifecycle management |
| `governance.py` | ✅ ACTIVE | `/api/governance` | Governance rules and assessments |
| `forecast.py` | ✅ ACTIVE | `/api/forecast` | AI quality forecast center |
| `executive_advisor.py` | ✅ ACTIVE | `/api/executive-advisor` | Executive-level AI advisory |
| `knowledge_universe.py` | ✅ ACTIVE | `/api/knowledge-universe` | Knowledge universe catalog |
| `report_factory.py` | ✅ ACTIVE | `/api/report-factory` | Report factory, executive analytics |
| `optimization_v2.py` | ✅ ACTIVE | `/api/optimization-v2` | Optimization engine V2 |

### Phase 15 — Software Quality Intelligence

| File | Status | Router Prefix | Key Endpoints |
|------|--------|--------------|--------------|
| `software_graph.py` | ✅ ACTIVE | `/api/software-graph` | Software dependency/call graph |
| `change_impact.py` | ✅ ACTIVE | `/api/change-impact` | Change impact analysis |
| `code_review.py` | ✅ ACTIVE | `/api/code-review` | AI code review analysis |
| `coverage.py` | ✅ ACTIVE | `/api/coverage` | Test coverage intelligence |
| `release_intelligence.py` | ✅ ACTIVE | `/api/release-intelligence` | Release readiness intelligence |
| `defects_hub.py` | ✅ ACTIVE | `/api/defects-hub` | Defect pattern intelligence |
| `engineering.py` | ✅ ACTIVE | `/api/engineering` | Engineering analytics |
| `knowledge_lake.py` | ✅ ACTIVE | `/api/knowledge-lake` | Knowledge lake catalog |
| `mission_control.py` | ✅ ACTIVE | `/api/mission-control` | Executive mission control |

### Phase 16 — Engineering Intelligence Platform

| File | Status | Router Prefix | Key Endpoints |
|------|--------|--------------|--------------|
| `knowledge_lake_v2.py` | ✅ ACTIVE | `/api/knowledge-lake-v2` | V2 knowledge lake with semantic search |
| `requirements.py` | ✅ ACTIVE | `/api/requirements` | Requirement traceability center |
| `traceability.py` | ✅ ACTIVE | `/api/traceability` | Traceability matrix generation |
| `architecture.py` | ✅ ACTIVE | `/api/architecture` | Architecture intelligence graph |
| `code_quality.py` | ✅ ACTIVE | `/api/code-quality` | Code quality governor analysis |
| `release_certification.py` | ✅ ACTIVE | `/api/release-certification` | Release certification workflow |
| `observability_ai.py` | ✅ ACTIVE | `/api/observability-ai` | AI-powered observability center |
| `customer_intelligence.py` | ✅ ACTIVE | `/api/customer-intelligence` | Customer experience intelligence |
| `policies.py` | ✅ ACTIVE | `/api/policies` | Policy engine management |
| `sdlc_orchestrator.py` | ✅ ACTIVE | `/api/sdlc` | SDLC orchestration, executive decisions |

### Additional Enterprise

| File | Status | Router Prefix | Key Endpoints |
|------|--------|--------------|--------------|
| `enterprise.py` | ✅ ACTIVE | `/api/enterprise` | Company hierarchy, enterprise setup |
| `onboarding.py` | ✅ ACTIVE | `/api/onboarding` | Zero-code onboarding wizard |
| `test_studio.py` | ✅ ACTIVE | `/api/test-studio` | Zero-code test studio |
| `test_lab.py` | ✅ ACTIVE | `/api/test-lab` | Autonomous test lab |
| `data_factory.py` | ✅ ACTIVE | `/api/data-factory` | Test data factory |
| `war_room.py` | ✅ ACTIVE | `/api/war-room` | Release war room status |
| `plugin_marketplace.py` | ✅ ACTIVE | `/api/plugins` | Plugin marketplace |
| `integrations.py` | ✅ ACTIVE | `/api/integrations` | Enterprise integrations catalog |
| `release_readiness.py` | ✅ ACTIVE | `/api/release-readiness` | Release readiness assessment |
| `release_command_center.py` | ✅ ACTIVE | `/api/release-command` | Release command center |
| `multi_reports.py` | ✅ ACTIVE | `/api/multi-reports` | Multi-format report generation |

---

## backend/app/services/ — Business Logic (86 files)

| File | Status | Used By |
|------|--------|---------|
| `audit_service.py` | ✅ ACTIVE | All write operations for audit chain |
| `automated_execution.py` | ✅ ACTIVE | `api/automated_execution.py` |
| `ai_agents_marketplace.py` | ✅ ACTIVE | `api/agents.py` |
| `ai_code_reviewer.py` | ✅ ACTIVE | `api/code_review.py` |
| `ai_execution_optimizer.py` | ✅ ACTIVE | `api/ai_optimizer.py` |
| `api_hub.py` | ✅ ACTIVE | `api/api_hub.py` |
| `architecture_intelligence.py` | ✅ ACTIVE | `api/architecture.py` |
| `autonomous_monitoring_v2.py` | ✅ ACTIVE | `api/autonomous_monitoring_v2.py` |
| `autonomous_optimization.py` | ✅ ACTIVE | `api/optimization_v2.py` |
| `autonomous_regression.py` | ✅ ACTIVE | `api/autonomous_regression.py` |
| `autonomous_release_validator.py` | ✅ ACTIVE | Release certification pipeline |
| `autonomous_test_lab.py` | ✅ ACTIVE | `api/test_lab.py` |
| `backup_service.py` | ✅ ACTIVE | `api/system.py` |
| `business_process_center.py` | ✅ ACTIVE | `api/business_process.py` |
| `change_impact_intelligence.py` | ✅ ACTIVE | `api/change_impact.py` |
| `cloud_browser_farm.py` | ✅ ACTIVE | `api/cloud_browser_farm.py` |
| `code_quality_governor.py` | ✅ ACTIVE | `api/code_quality.py` |
| `company_task_autoqa.py` | ✅ ACTIVE | `api/company_tasks.py` |
| `compliance_center.py` | ✅ ACTIVE | `api/compliance_center.py` |
| `connection_service.py` | ✅ ACTIVE | `api/connection_targets.py` |
| `continuous_monitoring.py` | ✅ ACTIVE | `api/continuous_monitoring.py` |
| `coverage_intelligence.py` | ✅ ACTIVE | `api/coverage.py` |
| `customer_experience_intelligence.py` | ✅ ACTIVE | `api/customer_intelligence.py` |
| `defect_intelligence_hub.py` | ✅ ACTIVE | `api/defects_hub.py` |
| `defect_service.py` | ✅ ACTIVE | `api/defects.py` |
| `diagnostics.py` | ✅ ACTIVE | `api/health.py`, `api/system.py` |
| `digital_twin_v2.py` | ✅ ACTIVE | `api/digital_twin.py` |
| `distributed_execution.py` | ✅ ACTIVE | `api/distributed_execution.py` |
| `engineering_analytics.py` | ✅ ACTIVE | `api/engineering.py` |
| `enterprise_analytics_engine.py` | ✅ ACTIVE | `api/enterprise_analytics.py` |
| `enterprise_devops.py` | ✅ ACTIVE | `api/enterprise_devops.py` |
| `enterprise_integrations.py` | ✅ ACTIVE | `api/integrations.py` |
| `enterprise_policy_engine.py` | ✅ ACTIVE | `api/policies.py` |
| `enterprise_security_center.py` | ✅ ACTIVE | `api/enterprise_security_center.py` |
| `evidence_service.py` | ✅ ACTIVE | `api/results.py` |
| `execution_stream.py` | ✅ ACTIVE | `api/execution_stream.py` |
| `executive_advisor.py` | ✅ ACTIVE | `api/executive_advisor.py` |
| `executive_command_center.py` | ✅ ACTIVE | `api/executive_command_center.py` |
| `executive_mission_control.py` | ✅ ACTIVE | `api/mission_control.py` |
| `forecast_center.py` | ✅ ACTIVE | `api/forecast.py` |
| `governance_center.py` | ✅ ACTIVE | `api/governance.py` |
| `incident_commander.py` | ✅ ACTIVE | `api/incidents.py` |
| `knowledge_lake_v2.py` | ✅ ACTIVE | `api/knowledge_lake_v2.py` |
| `knowledge_universe.py` | ✅ ACTIVE | `api/knowledge_universe.py` |
| `marketplace_ecosystem.py` | ✅ ACTIVE | `api/marketplace_ecosystem.py` |
| `multi_cloud_platform.py` | ✅ ACTIVE | `api/multi_region_cloud.py` |
| `multi_format_reports.py` | ✅ ACTIVE | `api/multi_reports.py` |
| `multi_region_cloud.py` | ✅ ACTIVE | `api/multi_region_cloud.py` |
| `notification_service.py` | ✅ ACTIVE | Internal event notifications |
| `observability_platform.py` | ✅ ACTIVE | `api/observability.py` |
| `operator_security.py` | ✅ ACTIVE | `api/operators.py`, `api/auth.py` |
| `optimization_engine_v2.py` | ✅ ACTIVE | `api/optimization_v2.py` |
| `pair_qa_engineer.py` | ✅ ACTIVE | `api/ai.py` |
| `password_service.py` | ✅ ACTIVE | `api/auth.py`, `api/operators.py` |
| `pinned_http.py` | ✅ ACTIVE | `connection_service.py` — DNS-pinned HTTP transport |
| `playwright_runner.py` | ✅ ACTIVE | `api/test_runs.py` |
| `plugin_marketplace.py` | ✅ ACTIVE | `api/plugin_marketplace.py` |
| `production_observability_ai.py` | ✅ ACTIVE | `api/observability_ai.py` |
| `project_access.py` | ✅ ACTIVE | All project-scoped endpoints |
| `release_certification_service.py` | ✅ ACTIVE | `api/release_certification.py` |
| `release_governance.py` | ✅ ACTIVE | `api/release_governance.py` |
| `release_intelligence.py` | ✅ ACTIVE | `api/release_intelligence.py` |
| `release_readiness.py` | ✅ ACTIVE | `api/release_readiness.py` |
| `release_simulation.py` | ✅ ACTIVE | `api/release_command_center.py` |
| `release_war_room.py` | ✅ ACTIVE | `api/war_room.py` |
| `report_factory_v2.py` | ✅ ACTIVE | `api/report_factory.py` |
| `report_service.py` | ✅ ACTIVE | `api/reports.py` |
| `requirement_intelligence.py` | ✅ ACTIVE | `api/requirements.py` |
| `result_parser.py` | ✅ ACTIVE | `api/results.py` |
| `retention_service.py` | ✅ ACTIVE | `api/system.py` |
| `safety_guard.py` | ✅ ACTIVE | Execution pipeline safety check |
| `sdlc_orchestrator.py` | ✅ ACTIVE | `api/sdlc_orchestrator.py` |
| `self_optimization.py` | ✅ ACTIVE | `api/test_evolution.py` |
| `software_graph.py` | ✅ ACTIVE | `api/software_graph.py` |
| `suite_registry.py` | ✅ ACTIVE | Test suite registration |
| `target_policy.py` | ✅ ACTIVE | Connection target URL/address policy |
| `task_analysis_service.py` | ✅ ACTIVE | Task import AI analysis |
| `task_import_service.py` | ✅ ACTIVE | `api/task_imports.py` |
| `test_management.py` | ✅ ACTIVE | `api/test_management.py` |
| `test_plan_service.py` | ✅ ACTIVE | `api/test_plans.py` |
| `traceability_matrix_service.py` | ✅ ACTIVE | `api/traceability.py` |
| `visual_regression_engine.py` | ✅ ACTIVE | `api/visual_regression.py` |
| `website_discovery.py` | ✅ ACTIVE | `api/discovery.py` |
| `workflow_composer.py` | ✅ ACTIVE | `api/workflows.py` |
| `zero_code_onboarding.py` | ✅ ACTIVE | `api/onboarding.py` |
| `zero_code_test_studio.py` | ✅ ACTIVE | `api/test_studio.py` |

---

## backend/app/models/ — SQLAlchemy Models (33 files)

| File | Status | Tables / Entities |
|------|--------|------------------|
| `__init__.py` | ✅ ACTIVE | Imports all models for Alembic metadata |
| `operator.py` | ✅ ACTIVE | `operators` |
| `operator_session.py` | ✅ ACTIVE | `operator_sessions` |
| `password_history.py` | ✅ ACTIVE | `password_history` (append-only) |
| `project.py` | ✅ ACTIVE | `projects` |
| `project_membership.py` | ✅ ACTIVE | `project_memberships` |
| `test_case.py` | ✅ ACTIVE | `test_cases` |
| `test_suite.py` | ✅ ACTIVE | `test_suites` |
| `test_plan.py` | ✅ ACTIVE | `test_plans`, `test_plan_versions` |
| `test_run.py` | ✅ ACTIVE | `test_runs` (Playwright run records) |
| `test_result.py` | ✅ ACTIVE | `test_results`, `test_evidence` |
| `test_management.py` | ✅ ACTIVE | Stage 8 managed tables: suites, cases, steps, runs, evidence |
| `connection_target.py` | ✅ ACTIVE | `connection_targets`, `connection_target_versions`, `connection_checks`, `credential_profiles` |
| `automated_execution.py` | ✅ ACTIVE | Stage 10/11 execution tables: runs, cases, step results, jobs, workers, attempts, events, artifacts |
| `defect.py` | ✅ ACTIVE | `defects`, `defect_comments`, `defect_history`, `defect_evidence_links`, `defect_retests` |
| `advanced_validation.py` | ✅ ACTIVE | Stage 12 validation tables: profiles, definitions, runs, results |
| `discovery.py` | ✅ ACTIVE | `discovery_sessions`, `discovered_flows` |
| `evidence.py` | ✅ ACTIVE | Evidence file metadata |
| `external_task_import.py` | ✅ ACTIVE | `external_task_imports` |
| `company_task.py` | ✅ ACTIVE | `company_tasks`, task assignments, comments |
| `agent_suggestion.py` | ✅ ACTIVE | `agent_suggestions` |
| `audit_event.py` | ✅ ACTIVE | `audit_events` (append-only, hash chain) |
| `reporting.py` | ✅ ACTIVE | `report_records` |
| `visual_regression.py` | ✅ ACTIVE | `visual_baselines`, `visual_test_runs`, `visual_test_results` |
| `enterprise_hierarchy.py` | ✅ ACTIVE | `companies`, `departments`, `teams`, `enterprise_members` |
| `phase9_models.py` | ✅ ACTIVE | AI Copilot sessions, agent execution records |
| `phase10_models.py` | ✅ ACTIVE | Zero-code studio definitions, onboarding sessions |
| `phase11_models.py` | ✅ ACTIVE | Release command, autonomous regression records |
| `phase12_models.py` | ✅ ACTIVE | Defect intelligence, knowledge lake entries |
| `phase13_models.py` | ✅ ACTIVE | Enterprise cloud: browser farm, distributed jobs, compliance, observability |
| `phase14_models.py` | ✅ ACTIVE | AI OS: workflows, incidents, governance, forecasts |
| `phase15_models.py` | ✅ ACTIVE | Software graph, change impact, coverage, engineering analytics |
| `phase16_models.py` | ✅ ACTIVE | Knowledge lake V2, requirements, traceability, architecture, release cert |

---

## backend/app/repositories/ — Database Access Objects

| File | Status | Purpose |
|------|--------|---------|
| `run_repository.py` | ✅ ACTIVE | Test run CRUD + `recover_interrupted` (called on startup) |
| *(others)* | ✅ ACTIVE | Isolated DB access per domain |

---

## backend/ Root Scripts

| File | Status | Purpose |
|------|--------|---------|
| `requirements.txt` | ✅ ACTIVE | Python dependencies for `pip install` |
| `pytest.ini` | ✅ ACTIVE | Pytest configuration |
| `alembic.ini` | ✅ ACTIVE | Alembic migration config |
| `seed_db.py` | ✅ ACTIVE | Standalone DB seed script (dev use) |
| `.env.example` | ✅ ACTIVE | Environment variable template |
| `.venv/` | ✅ ACTIVE | Python virtual environment |
| `alembic/` | ✅ ACTIVE | Alembic migration scripts |
| `data/` | ✅ ACTIVE | SQLite DB + runtime data |
| `tests/` | ✅ ACTIVE | pytest test suite |

---

## Summary Counts

| Category | Count | Status |
|----------|-------|--------|
| Backend API router files | 90 | All ACTIVE |
| Backend service files | 86 | All ACTIVE |
| Backend model files | 33 | All ACTIVE |
| Frontend page files | 82 | All ACTIVE (4 dead pages removed) |
| Frontend service files | 16 | All ACTIVE |
| Root-level dead files removed | 45 | DELETED ✓ |
| Backend temp directories removed | 13 | DELETED ✓ |
| Backend debug scripts removed | 3 | DELETED ✓ |
| Frontend dead pages removed | 4 | DELETED ✓ |
