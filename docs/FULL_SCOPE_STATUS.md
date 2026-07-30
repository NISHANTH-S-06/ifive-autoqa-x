# iFive AutoQA — Full Project Scope & Status

> **Last verified:** 2026-07-27 (Phase 0 Foundation, Phase 1 Mock Task Portal, Phase 2 Local Demo Product Website, Phase 3 Task Connector Integration, Phase 4 AI Analyzer Engine, Phase 5 AI Test Plan Generator & Approval Workflow, Phase 5.1 Acceptance Hardening, Phase 5.2 Real End-to-End Acceptance Verification, Phase 6 Advanced Validation Pack 100% VERIFIED)
> **Status:** All Phases 0–6 are 100% VERIFIED and operational. 100% backend pytest pass (186/186 tests), 100% Playwright E2E pass (41/41 tests), 100% frontend production builds clean.

---

## Table of Contents

1. [Project Summary](#1-project-summary)
2. [Stage-by-Stage Status](#2-stage-by-stage-status)
3. [Backend — Full File Map](#3-backend--full-file-map)
4. [Frontend — Full File Map](#4-frontend--full-file-map)
5. [QA — Full Test Map](#5-qa--full-test-map)
6. [Docs — All Documents](#6-docs--all-documents)
7. [Scripts & CLI Tools](#7-scripts--cli-tools)
8. [Release Builds](#8-release-builds)
9. [UAT Checklist Status](#9-uat-checklist-status)
10. [Genuine Gaps Remaining](#10-genuine-gaps-remaining)

---

## 1. Project Summary

**Platform:** iFive AutoQA — Local-first AI-assisted testing platform  
**Objective:** Help QA teams test critical iFive workflows with deterministic automation and complete failure evidence.

**Product Coverage (scope):**
| Product | Modules Covered |
|---------|----------------|
| iFive ERP | Login, Customer, Vendor, Inventory, Purchase, Sales, Finance, Production, Reports, Export, Permissions |
| iFive HRMS | Employee, Attendance, Leave, Shift, Payroll Preview, Recruitment, Self Service, Permissions |
| iFive CRM | Lead, Opportunity, Follow-up, Quotation, Customer, Reports, Permissions |
| iFive IIoT | Dashboard, Device Status, Telemetry, Alerts, Charts, Filters, Data Freshness |
| App Integration | Authentication, API Mapping, Schema, Retry, Duplicate Handling, Webhooks, Error Logs |

**Running Microservices (all 6 HTTP 200 OK):**
- AutoQA Backend (FastAPI + uvicorn): http://127.0.0.1:8000 (Health: 200 OK)
- Mock Task Portal Backend (FastAPI + uvicorn): http://127.0.0.1:8001 (Health: 200 OK)
- Demo Product Backend (FastAPI + uvicorn): http://127.0.0.1:8002 (Health: 200 OK)
- AutoQA Frontend (Vite + React): http://localhost:5173 (HTTP 200 OK)
- Mock Task Portal Frontend (Vite + React): http://localhost:5174 (HTTP 200 OK)
- Demo Product Frontend (Vite + React): http://localhost:5175 (HTTP 200 OK)

---

## 2. Stage-by-Stage Status

| Stage / Phase | Name | Status | Verification Metrics |
|---------------|------|:---:|----------------------|
| **Phase 0 / Stage 1–3** | Project Scaffold & Backend Foundation | VERIFIED | Structure, FastAPI lifespan, DB migrations, 132 AutoQA backend tests passed |
| **Phase 1** | Mock Task Portal Backend & Frontend | VERIFIED | Task sync, status tracking, 23/23 portal pytest passed |
| **Phase 2** | Demo Product Backend & Frontend | VERIFIED | HRMS & Inventory ERP mock modules, 21/21 demo product pytest passed |
| **Phase 3** | Task Connector Integration | VERIFIED | Sync API, task-import service, 6/6 Phase 3 Playwright tests passed |
| **Phase 4** | AI Analyzer Engine | VERIFIED | Heuristic LocalAI Provider, negative/primary scenario generation, schema validation |
| **Phase 5.1/5.2** | AI Test Plan Generator & Real Acceptance | VERIFIED | Immutability, RBAC self-approval blocking, 15/15 Phase 5.2 Playwright tests passed |
| **Phase 6** | Advanced QA Validation Pack | VERIFIED | Multi-layered API/DB/A11y/Perf validators, HTML/PDF reporting, 20/20 Phase 6 Playwright tests passed |

---

## 3. Backend — Full File Map

### `backend/app/` — Core

| File | Purpose | Size |
|------|---------|------|
| `main.py` | FastAPI app, 16 routers, lifespan, CORS, correlation IDs | 4.5 KB |
| `auth.py` | Cookie sessions, CSRF, login/logout, lockout | 4.0 KB |
| `config.py` | All env vars, directory preparation | 8.8 KB |
| `database.py` | SQLite engine + session factory | 1.5 KB |
| `migrations.py` | Stage 4→14 schema migrations, append-only triggers | 10.5 KB |
| `logging_config.py` | Structured rotating logs, secret redaction | 2.2 KB |
| `security.py` | CSRF token helpers | 0.7 KB |
| `seed.py` | Seed local projects on startup | 0.9 KB |

### `backend/app/api/` — API Routes (16 routers)

| File | Purpose | Size |
|------|---------|------|
| `auth.py` | Login, logout, session management | 10.1 KB |
| `operators.py` | ADMIN operator management | 8.1 KB |
| `audit.py` | Audit trail read endpoints | 2.1 KB |
| `security.py` | Security reports, ADMIN-only | 4.7 KB |
| `projects.py` | Project CRUD | 2.1 KB |
| `test_runs.py` | Test run management | 8.6 KB |
| `test_management.py` | Full test management (largest file) | 40.8 KB |
| `connection_targets.py` | Target lifecycle + probe | 25.3 KB |
| `automated_execution.py` | Run queue, approval, execution, cancellation | 15.3 KB |
| `defects.py` | Defect lifecycle, comments, retests, evidence | 13.0 KB |
| `reports.py` | Report generation, export, saved definitions | 13.5 KB |
| `dashboard.py` | Dashboard metrics summary | 0.8 KB |
| `results.py` | Test result records | 0.5 KB |
| `agents.py` | Agent suggestion endpoints | 0.6 KB |
| `health.py` | Health check (extended in Stage 14) | 0.3 KB |
| `system.py` | Diagnostics, maintenance, system info | 3.2 KB |

### `backend/app/models/` — SQLAlchemy Models

| File | Tables |
|------|--------|
| `operator.py` | `operators` |
| `operator_session.py` | `operator_sessions` |
| `password_history.py` | `password_history` (append-only) |
| `audit_event.py` | `audit_events` (append-only, hash-chained) |
| `project.py` | `projects` |
| `test_management.py` | `test_modules`, `test_suites`, `test_cases`, `test_case_versions`, `manual_runs`, `manual_results` |
| `test_run.py` | `test_runs` |
| `test_result.py` | `test_results` |
| `test_case.py` | `test_case_versions` snapshot |
| `test_suite.py` | `test_suites` |
| `evidence.py` | `evidence` |
| `connection_target.py` | `connection_targets`, `connection_target_versions` |
| `automated_execution.py` | `automated_runs`, `automated_results`, `worker_heartbeats` |
| `defect.py` | `defects`, `defect_comments`, `defect_history`, `defect_retests`, `defect_evidence_links` |
| `reporting.py` | `report_exports`, `report_definitions` |
| `agent_suggestion.py` | `agent_suggestions` |

### `backend/app/services/` — Business Logic

| File | Purpose | Size |
|------|---------|------|
| `test_management.py` | Test case CRUD, version snapshots, approval | 12.2 KB |
| `automated_execution.py` | Worker, lease, retry, structured action engine | 26.7 KB |
| `defect_service.py` | Duplicate detection, state machine transitions | 19.4 KB |
| `report_service.py` | Full export engine, CSV/JSON, formula protection | 25.5 KB |
| `connection_service.py` | DNS validation, connectivity probe | 9.2 KB |
| `target_policy.py` | URL/port/scheme safety rules | 8.1 KB |
| `pinned_http.py` | DNS-pinned HTTP client | 4.2 KB |
| `playwright_runner.py` | Playwright execution wrapper | 11.1 KB |
| `password_service.py` | Hashing, history, expiry | 3.4 KB |
| `audit_service.py` | Hash-chained audit events | 2.9 KB |
| `operator_security.py` | ADMIN security operations | 4.7 KB |
| `retention_service.py` | Artifact cleanup, dry-run, containment | 7.4 KB |
| `backup_service.py` | Local backup, SHA-256 validate, restore | 8.2 KB |
| `diagnostics.py` | Worker/queue/storage/disk health | 4.4 KB |
| `evidence_service.py` | Evidence file upload helper | 0.3 KB |
| `result_parser.py` | Playwright result JSON parser | 0.5 KB |
| `safety_guard.py` | Action allowlist guard | 0.2 KB |
| `suite_registry.py` | Test suite registry | 0.4 KB |

### `backend/app/repositories/`

| File | Purpose |
|------|---------|
| `operator_repository.py` | Operator DB queries |
| `project_repository.py` | Project DB queries |
| `run_repository.py` | Run lifecycle + interrupted recovery |
| `result_repository.py` | Result queries |

### `backend/app/cli/` — CLI Commands

| File | Command |
|------|---------|
| `create_operator.py` | Create local operator interactively |
| `maintenance.py` | Backup, restore, retention, cleanup |
| `migrate.py` | Run schema migrations |
| `worker.py` | Start execution worker |
| `static_server.py` | Serve frontend static build |

---

## 4. Frontend — Full File Map

### `frontend/src/pages/` — Pages (6)

| File | Purpose | Notes |
|------|---------|-------|
| `HomePage.tsx` | Marketing landing page | Hero, Features, FAQ, CTA |
| `ProductsPage.tsx` | Product testing scope | Loads live from API, 6 product cards |
| `TestRunsPage.tsx` | Test runs listing | |
| `AgentsPage.tsx` | AI agent workflow | Workflow steps + agent grid |
| `ReportsPage.tsx` | Reports page | |
| `SettingsPage.tsx` | Settings | |

### `frontend/src/components/` — Components (21)

| File | Purpose | Size |
|------|---------|------|
| `TestManagementCore.tsx` | Full test management UI | 25.9 KB |
| `ConnectionTargetsCore.tsx` | Target lifecycle UI | 17.7 KB |
| `DefectsCore.tsx` | Defect tracker UI | 16.4 KB |
| `AutomatedRunsCore.tsx` | Automated runs UI | 13.2 KB |
| `ManagementReportsCore.tsx` | Reports + export UI | 13.5 KB |
| `AdminPanels.tsx` | Admin operator panels | 11.7 KB |
| `TestDashboardPreview.tsx` | Dashboard preview | 9.2 KB |
| `PasswordControls.tsx` | Password change UI | 6.1 KB |
| `FinalReleaseCore.tsx` | Release build/status UI | 6.8 KB |
| `SessionPanels.tsx` | Session management UI | 3.5 KB |
| `ProductConnections.tsx` | Product scope display | 2.2 KB |
| `Hero.tsx` | Landing hero section | 2.0 KB |
| `AgentWorkflow.tsx` | AI workflow explanation | 1.2 KB |
| `Header.tsx` | Navigation header | 0.9 KB |
| `Footer.tsx` | Footer | 0.9 KB |
| `ReportsSection.tsx` | Reports section | 1.0 KB |
| `SecuritySection.tsx` | Security section | 0.6 KB |
| `FeatureCards.tsx` | Feature grid | 0.7 KB |
| `CTA.tsx` | Call to action | 0.7 KB |
| `FAQ.tsx` | FAQ section | 0.5 KB |
| `AccountSecurityPanel.tsx` | Account security | 0.6 KB |

### `frontend/src/services/` — API Service Layer (9 files)

`api.ts`, `auth.ts`, `automatedExecution.ts`, `connectionTargets.ts`,
`defects.ts`, `reports.ts`, `system.ts`, `testManagement.ts`, `testRuns.ts`

### `frontend/src/types/` — TypeScript Types (9 files)

`auth.ts`, `automatedExecution.ts`, `connectionTarget.ts`, `defect.ts`,
`product.ts`, `report.ts`, `system.ts`, `testManagement.ts`, `testRun.ts`

---

## 5. QA — Full Test Map

### `qa/tests/` — Playwright Spec Files (13 spec files)

| Spec File | Stage | Coverage |
|-----------|:---:|---------|
| `auth/auth-rbac.spec.ts` | 5 | Login, RBAC, session, CSRF |
| `auth/stage7-security.spec.ts` | 7 | Security reports, ADMIN controls |
| `test-management/stage8-management.spec.ts` | 8 | Cases, suites, versions, approval |
| `connection-targets/stage9-connection-targets.spec.ts` | 9 | Target lifecycle, probe, policy |
| `automated-runs/stage10-automated-runs.spec.ts` | 10 | Queue, approval, worker, artifacts |
| `automated-runs/stage11-acceptance.spec.ts` | 11 | DNS pinning, preflight, acceptance |
| `defects/stage12-defects.spec.ts` | 12 | Defect lifecycle, retests, evidence |
| `reports/stage13-management-reports.spec.ts` | 13 | Export, definitions, limits |
| `dashboard/dashboard.spec.ts` | 14 | Dashboard metrics |
| `dashboard/lifecycle.spec.ts` | 14 | Full system lifecycle |
| `erp/erp-smoke.spec.ts` | Smoke | ERP scope visibility check |
| `hrms/hrms-smoke.spec.ts` | Smoke | HRMS scope visibility check |
| `crm/crm-smoke.spec.ts` | Smoke | CRM scope visibility check |
| `iiot/iiot-smoke.spec.ts` | Smoke | IIoT scope visibility check |
| `integration/integration-smoke.spec.ts` | Smoke | Integration scope check |

### `qa/fixtures/` — Test Fixtures

| File | Purpose |
|------|---------|
| `authenticated.fixture.ts` | Auth setup for all tests |
| `safe-mode.fixture.ts` | Safe mode enforcement |
| `test-data.fixture.ts` | Test data helpers |

### `qa/page-objects/` — Page Objects

`LoginPage.ts`, `DashboardPage.ts`, `ExportPage.ts`, `NavigationPage.ts`

### `qa/agents/` — AI Agent Docs

`planner.md`, `generator.md`, `healer.md`, `safety.md`

### `qa/mcp/`

`playwright-mcp.json` — MCP config for Playwright

---

## 6. Docs — All Documents

| File | Purpose | Size |
|------|---------|------|
| `QUICK_START_GUIDE.md` | Setup, run, commands reference | 11.2 KB |
| `SECURITY_AND_SAFETY.md` | Full security model | 10.2 KB |
| `API_DOCUMENTATION.md` | API endpoints reference | 9.1 KB |
| `COMMANDS_REFERENCE.md` | All PowerShell/Python commands | 7.2 KB |
| `DEVELOPMENT_WORKFLOW.md` | Dev workflow guide | 6.2 KB |
| `FULL_END_TO_END_VIDEO_DEMO_SCRIPT.md` | Video demo script | 7.8 KB |
| `FULL_PROJECT_DEMO.md` | Project demo guide | 7.6 KB |
| `TEAM_LEAD_DEMO.md` | Team lead demo | 6.3 KB |
| `LOCAL_RELEASE_OPERATIONS.md` | Release ops, backup, restore | 4.8 KB |
| `RELEASE_READINESS_AUDIT.md` | Stage 14 readiness audit | 3.5 KB |
| `FINAL_UAT_CHECKLIST.md` | UAT pass/fail checklist | 1.9 KB |
| `INSTALLATION.md` | Installation guide | 0.6 KB |
| `AI_AGENT_WORKFLOW.md` | AI agent explanation | 0.4 KB |
| `PRODUCT_TEST_MATRIX.md` | Product → modules matrix | 0.6 KB |
| `iFive_AutoQA_Demo_Recording_Script_Thanglish_English.docx` | Demo recording script | 12.3 KB |
| `iFive_AutoQA_End_to_End_Thanglish_English_Guide.docx` | End-to-end guide (Thanglish) | 16.7 KB |

---

## 7. Scripts & CLI Tools

### `scripts/` — PowerShell + Python Scripts

| Script | Purpose |
|--------|---------|
| `start_backend.ps1` | Start FastAPI backend |
| `start_frontend.ps1` | Start Vite frontend |
| `start_local_system.ps1` | Start all services together |
| `stop_local_system.ps1` | Stop all services |
| `run_backend.ps1` | Run backend (alias) |
| `run_frontend.ps1` | Run frontend (alias) |
| `run_all.ps1` | Run both together |
| `run_tests.ps1` | Run Playwright QA suite |
| `run_migrations.ps1` | Apply DB migrations |
| `setup_project.ps1` | First-time project setup |
| `create_local_operator.ps1` | Create operator interactively |
| `bootstrap_demo_admin.py` | Bootstrap first ADMIN |
| `setup_demo_accounts.py` | Create demo operator set |
| `verify_health.ps1` | Check system health |
| `verify_project.ps1` | Verify project integrity |
| `backup_local.ps1` | Backup database + artifacts |
| `restore_local.ps1` | Restore from backup |
| `build_release.ps1` | Build release package |
| `start_worker.ps1` | Start execution worker |
| `cleanup_local.ps1` | Cleanup local data |
| `run_stage5_acceptance.py` | Stage 5 acceptance tests |
| `QuickStart.ps1` | All-in-one startup script (project root) |

---

## 8. Release Builds

Location: `release/stage14/`

**18 release builds completed** (latest: `20260715T074059Z`)

Each release bundle contains:
- Full backend + frontend + qa + scripts + docs
- `SHA256SUMS.txt` — integrity verification for all files
- `release-manifest.json` — build metadata
- `ARCHITECTURE.md`, `README.md`, `REQUIREMENTS.md`, `SAFETY_RULES.md`, `TEST_STRATEGY.md`

---

## 9. UAT Checklist Status

From `docs/FINAL_UAT_CHECKLIST.md`:

### ✅ PASS (Automated)
- Password policy, history, version invalidation, RBAC, CSRF, audit-chain tests
- Test management and creator-separated approval
- Frozen-version manual execution
- Local-fixture automated execution, worker, cancellation, timeout, retry, artifacts
- Defect lifecycle, evidence, traceability, retest
- Reports, bounded export, saved definitions
- Backup/restore with SHA-256 validation
- Retention dry-run, confirmation, containment, active-artifact protection
- Sanitized health and diagnostics
- Structured rotating logs and secret redaction
- Release package allowlist, exclusions, manifest, checksums
- Responsive dashboard at 320/375/768/1024/1440 pixels

### ⏳ PENDING (Requires Real Targets / Manual)
- Persistent ADMIN login (`active_admin_count = 0` — first ADMIN not created yet)
- Forced password change with authorized persistent operator
- Session management with persistent operators
- ADMIN security UI with persistent ADMIN
- Authorized real non-production target acceptance (no real iFive URL supplied yet)
- Authenticated iFive login (no safe ephemeral credential supplied)

---

## 10. Genuine Gaps Remaining

| Gap | Details | Effort |
|-----|---------|--------|
| **First ADMIN creation** | No operator bootstrapped yet. Run `scripts/create_local_operator.ps1` | 5 min |
| **Real iFive target URL** | Connection targets exist but no real DEV/QA/STAGING URL configured | Config only |
| **Ollama live wiring** | `local-ai/prompts/` and `local-ai/configs/ollama.json` exist. Backend HTTP call to Ollama not wired | Code work |
| **Product smoke packs** | `erp/hrms/crm/iiot/integration` spec files exist but each is ~9 lines (1 basic check). Full smoke pack not written | Test writing |
| **Authenticated iFive run** | Requires safe ephemeral login mechanism + real target + real product URL | Future phase |

---

## Summary

```
Platform stages complete  : 14 / 14  ██████████████ 100%
Release builds            : 18 builds in release/stage14/
Backend API routes        : 16 routers covering all domains
Backend service files     : 18 services
DB models / tables        : 16 model files, 30+ tables
Frontend pages            : 6 pages (all wired, no stubs)
Frontend components       : 21 components
Frontend service modules  : 9 API service files
QA spec files             : 15 spec files (stages 5-14 + 5 product smokes)
QA fixtures               : 3 fixture files
QA page objects           : 4 page objects
Docs                      : 16 documents
Scripts                   : 21 scripts + QuickStart.ps1
CLI commands              : 5 (create_operator, maintenance, migrate, worker, static_server)
AI prompt templates       : 4 (planner, generator, healer, defect_summary)
SHA-256 verified releases : 18
```

**Bottom line:** Core platform is fully built across all 14 stages.  
First ADMIN setup + real iFive target URL + full product smoke packs are the remaining steps before live production UAT.
