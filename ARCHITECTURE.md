# Architecture

> **Current Phase:** 16 — Autonomous Enterprise Software Engineering Intelligence Platform  
> **Last updated:** 2026-07-29

## Overview

iFive AutoQA is a **local-first, AI-assisted enterprise QA platform** with six cooperating local services.

## Canonical Port Map

| Service | Technology | Port | Role |
|---------|-----------|------|------|
| AutoQA Backend API | FastAPI + Uvicorn | **8000** | Core platform — auth, all 90 API modules |
| Mock Task Portal API | FastAPI + Uvicorn | **8001** | Simulated Jira-like task management (import target) |
| Demo Product API | FastAPI + Uvicorn | **8002** | Target-under-test product for connectivity/E2E tests |
| AutoQA Frontend | React 18 + Vite | **5173** | Main QA platform UI (all 82 modules) |
| Mock Task Portal UI | React + Vite | **5174** | Mock task portal web UI |
| Demo Product UI | React + Vite | **5175** | Demo product for visual regression and E2E tests |

## Architecture Layers

1. **React/Vite frontend** — 82 active module pages, module-keyed sidebar navigation, `/api` proxy to 8000.
2. **FastAPI backend** — 90 registered routers, RBAC auth, CORS, audit-chain events, SQLite persistence.
3. **Playwright QA workspace** — deterministic browser/API tests, evidence capture, artifact storage.
4. **Local AI workspace** — heuristic-based LocalAI provider, 13 specialized agents, copilot, digital twin.

## Data Flow

1. A QA user selects a product, module, role, and test scope.
2. Planner Agent drafts a test plan.
3. Generator Agent proposes Playwright tests.
4. A human reviews and approves the generated tests.
5. Playwright executes approved tests.
6. The backend records runs, results, evidence, defects, and agent suggestions.
7. The frontend displays dashboard metrics and report detail.

## Safety Boundary

The Safety Agent and backend safety guard block destructive operations before execution. The QA runner also uses safe-mode fixtures so tests can validate restricted behavior without performing restricted actions.

## Persistence

SQLite is the default database for local development. Repository classes isolate database access so PostgreSQL can be introduced later without changing API contracts.
# Stage 5 Security Architecture

React restores an HttpOnly cookie session through `/api/auth/me` and obtains the CSRF browser value through `/api/auth/csrf`. FastAPI hashes session and CSRF values with SHA-256 before database comparison. Passwords use standard-library PBKDF2-HMAC-SHA256 with random salts.

RBAC dependencies guard API routes. Run rows carry nullable creator, approver, executor, and canceller foreign keys. Audit events use deterministic JSON and a SHA-256 previous-hash chain; SQLite triggers reject updates and deletes. The fixed Stage 4 suite registry and runner boundary are unchanged.

# Stage 6 Security Architecture

Operators carry password timestamps, password version, forced-change reason, and credential update timestamps. `password_history` stores only password hashes and is protected by SQLite triggers that reject updates and deletes.

Each session records the password version at login. Authentication rejects revoked, expired, inactive, and password-version-mismatched sessions. Forced password-change sessions may call only `/api/auth/me`, `/api/auth/csrf`, `/api/auth/change-required-password`, logout, and health endpoints until the password is changed.

Security reporting aggregates safe counts only. ADMIN reset and session revocation APIs write audit events with allowlisted metadata and never return passwords, password hashes, session token hashes, or CSRF hashes.

# Stage 8 Test Management Architecture

Stage 8 adds normalized local tables for test projects, modules, managed suites, managed test cases, ordered steps, tags, immutable case versions, manual runs, run cases, step results, and manual evidence. These tables are separate from the existing Stage 4 `/api/test-runs` Playwright execution tables so manual execution management cannot broaden browser automation.

Test-case lifecycle is server-enforced: `DRAFT -> IN_REVIEW -> APPROVED|REJECTED`, with controlled revision and archive paths. Every lifecycle transition creates an audit-chain event. Case-version snapshots are append-only through SQLite triggers and are frozen into manual run cases by version number.

Manual evidence is stored locally under `backend/data/stage8_evidence` with generated filenames, extension/MIME validation, SHA-256 hashing, and path containment checks. API responses expose relative metadata only.

# Stage 9 Connection Target Architecture

Stage 9 adds `connection_targets`, `connection_target_versions`, `connection_checks`, and `target_credential_profiles`. This bounded context is connection management only. It does not call the Playwright runner, submit login forms, mutate iFive data, or execute test suites.

The target-policy service centrally normalizes HTTP/HTTPS origins, validates explicit probe paths, blocks PRODUCTION, rejects embedded credentials, fragments, unsafe schemes, obfuscated IP forms, query-bearing base URLs, metadata/link-local/special address ranges, and cross-origin redirects. DNS is resolved before checks and each resolved address is validated.

Connectivity uses `httpx` with environment proxy trust disabled, no request body, no cookies, no authorization headers, no CSRF headers, no automatic redirect following, a fixed user agent, bounded timeouts, and sanitized result storage. Check rows reference the approved target version. Target versions are append-only through SQLite triggers. Credential profiles store only metadata and never store passwords, tokens, cookies, or authentication headers.

## Stage 10 Execution Engine

Stage 10 introduces `automated_runs`, `automated_run_cases`, `automated_step_results`, `execution_jobs`, `execution_workers`, `execution_attempts`, `execution_events`, and `execution_artifacts`. Execution is separate from Stage 9 connectivity approval: `connection_targets.execution_enabled`, `execution_approved_by`, and `execution_approved_at` must be set by a separate reviewer before a target can be selected for automation.

The local worker claims one queued job at a time, records heartbeat/lease state, freezes target and case versions, executes only structured allowlisted actions, blocks origin escape and unapproved probe paths, and writes sanitized step results, classifications, events, and artifacts. No database value is treated as a shell command, no `shell=True` is used, and no browser storage state, cookies, tokens, or authentication headers are persisted.

## Stage 11 Acceptance Hardening

Stage 11 adds a pinned HTTP transport for target checks and automated execution. The transport resolves the approved hostname, validates every address through the target policy, selects one validated address, connects only to that address, preserves the approved Host header and TLS SNI, and rechecks the address set before each request. DNS rebinding, address drift, cross-origin redirects, and blocked address ranges stop execution before browser-style actions continue.

Automated runs now carry risk, preflight, DNS pinning, and runtime-secret status. Queueing requires a passing preflight that verifies target approval, separate execution approval, non-production classification, frozen target and case versions, approved structured actions, recent worker heartbeat, bounded timeout/concurrency, and no persisted runtime secret. Only `READ_ONLY` and `SAFE_INTERACTION` actions can proceed; mutating/destructive actions are rejected before queueing.

## Stage 12 Defect and Traceability Architecture

Stage 12 introduces `defects`, `defect_comments`, `defect_history`, `defect_evidence_links`, and `defect_retests`. Defects are linked to Stage 8 manual runs/results/evidence and Stage 10/11 automated runs/results/artifacts without copying secret-bearing content or storing response bodies. Source identifiers, frozen test-case versions, approved target versions, and sanitized failure classifications provide traceability from defect to project, suite, case, run, evidence, and retest.

Comments, history, evidence links, and retest rows are append-only through SQLite triggers. Defect lifecycle transitions are enforced in the service layer with RBAC and separation of duties: creation is TESTER/ADMIN, review/closure is APPROVER/ADMIN, retest is TESTER/ADMIN, and non-ADMIN reporters cannot close their own defects. Stage 12 does not add authenticated iFive workflows, credential persistence, production execution, Ollama, AI agents, or Stage 13 capabilities.

## Phase 4 AI Analyzer Architecture

Phase 4 introduces `LocalAIProvider` heuristics and task-import analysis. The AI analyzer parses title, description, and acceptance criteria from external task imports to produce structured JSON test plan proposals containing `PRIMARY`, `SMOKE`, and `NEGATIVE` scenarios.

## Phase 5 AI Test Plan Architecture

Phase 5 introduces `test_plans`, `test_plan_versions`, `test_scenarios`, and `test_steps`. Plans carry version numbers, cryptographic snapshot hashes (`plan_hash`), creator and approver identities, and lifecycle status (`DRAFT -> IN_REVIEW -> APPROVED | REJECTED`). Creator self-approval and developer task owner self-approval are strictly blocked by service-layer RBAC. Editing an approved plan invalidates approval, resets status to `DRAFT`, and clears execution flags.

## Phase 6 Advanced QA Validation Pack Architecture

Phase 6 introduces `advanced_validation_profiles`, `api_validation_definitions`, `database_validation_definitions`, `accessibility_validation_definitions`, `performance_validation_definitions`, `advanced_validation_runs`, and `advanced_validation_results`.
- **API Validation:** Evaluates endpoint status codes, JSON schema compliance, and HTTP headers against target origin policies.
- **Read-Only Database Validation:** Executes SQL queries against approved connection profiles (`backend/data/autoqa.db`, `demo_product`, `mock_task_portal`) using strict read-only AST safety validation (`SELECT`, `WITH`) that rejects mutating statements (`INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `CREATE`, `ATTACH`, `PRAGMA`).
- **Accessibility Validation:** Scans DOM violation trees against WCAG 2.1 AA thresholds.
- **Performance Validation:** Compares timing metrics against warning and failure thresholds.
- **Result Aggregation & Defects:** Combines validator DTOs using strict precedence (`BLOCKED > FAIL > PASS_WITH_WARNINGS > PASS`), computes SHA-256 result hashes, and generates deduplicated defect records.
- **Schedules & Reports:** Manages `local_schedules` cron execution and outputs cryptographic HTML and PDF validation reports.

## Phase 7 Visual Regression Architecture

Phase 7 introduces `visual_baselines`, `visual_test_runs`, and `visual_test_results`. Baseline images are captured at approved connection targets using Playwright. Diff analysis uses pixel-level comparison with configurable thresholds. Visual test runs are linked to connection target versions and test case versions. Artifacts are stored under `backend/data/visual_runs` with SHA-256 hashes and path containment checks.

## Phase 8 Enterprise Management & AI Discovery Architecture

Phase 8 introduces the enterprise hierarchy (`companies`, `departments`, `teams`, `enterprise_members`) and AI Flow Discovery. Discovery uses authenticated Playwright sessions to crawl approved connection targets, extract navigation flows, form interactions, and API call patterns. All discovery sessions are scoped to approved non-production targets.

## Phase 9 AI Copilot & Agent Architecture

Phase 9 introduces `AICopilotEngine` for contextual QA advice, `AgentRegistry` with 13 specialized agents (Planner, Generator, Healer, Analyzer, Reviewer, Optimizer, Documenter, Explorer, Validator, Monitor, Reporter, Predictor, Orchestrator), and `AgentOrchestrator` for multi-agent pipeline execution. All AI inference uses local heuristics — no external AI calls.

## Phase 10 Zero-Code Ecosystem Architecture

Phase 10 introduces the zero-code test studio (GUI test builder), autonomous test lab (AI-driven test generation), test data factory (structured data generation), and project onboarding wizard. Zero-code test definitions are stored as structured JSON with strictly allowlisted action types. No shell commands or dynamic code execution are used.

## Phase 11 Release Command Center Architecture

Phase 11 introduces the release war room (cross-project release health), release command center (coordinated release workflows), and autonomous regression (AI-triggered regression suite selection). Release readiness evaluates test coverage, defect density, approval status, and validation pass rates against configurable thresholds.

## Phase 12 Defect Intelligence Hub Architecture

Phase 12 introduces defect pattern analytics, defect intelligence scoring, and knowledge lake v1. Defect patterns are derived from existing defect records using heuristic classification. Intelligence scores aggregate severity, recurrence, and traceability coverage.

## Phase 13 Enterprise Cloud Platform Architecture

Phase 13 introduces distributed execution (multi-worker job dispatch), cloud browser farm (Playwright node pool), real-time execution streaming (SSE event bus), enterprise observability (metrics aggregation), enterprise analytics (KPI rollups), release governance (gate policies), compliance center (audit readiness), enterprise DevOps (CI/CD pipeline integration), multi-region cloud dashboard, enterprise security center (RBAC audit), and the executive command center. All execution remains local; "cloud" terminology refers to enterprise-scale orchestration patterns.

## Phase 14 AI QA Operating System Architecture

Phase 14 introduces the enterprise AI brain (cross-platform AI recommendations), workflow composer (visual workflow builder), business process hub (process mapping), incident commander (incident lifecycle management), AI forecast center (quality trend prediction), governance center (policy enforcement), knowledge universe (enterprise knowledge catalog), AI executive advisor (C-suite QA intelligence), AI agents marketplace (agent composition), and optimization engine V2 (automated test suite optimization).

## Phase 15 Autonomous Software Quality Intelligence Architecture

Phase 15 introduces the software intelligence graph (codebase dependency mapping), change impact center (PR-to-test impact analysis), AI code reviewer (static analysis integration), coverage intelligence (multi-dimensional coverage metrics), release intelligence (release risk scoring), defect intelligence hub (pattern-driven defect prediction), engineering analytics (developer productivity KPIs), knowledge lake v1 (QA asset catalog), and executive mission control (real-time C-suite QA dashboard).

## Phase 16 Autonomous Engineering Intelligence Platform Architecture

Phase 16 is the current and final local phase. It introduces:
- **Knowledge Lake V2** — semantic search over all QA artifacts with vector similarity scoring
- **Requirement Intelligence Center** — requirement traceability, gap analysis, and test coverage mapping
- **Traceability Matrix** — end-to-end traceability from requirements through test cases to defects
- **Architecture Intelligence** — system dependency graph seeding and architecture risk scoring
- **Code Quality Governor** — code quality gate enforcement with configurable thresholds
- **Release Certification** — formal release certification workflow with cryptographic sign-off
- **Observability Center (AI)** — AI-powered anomaly detection over observability metrics
- **Customer Experience Intelligence** — customer journey QA impact scoring
- **Policy Engine** — enterprise policy definition, enforcement, and audit integration
- **Autonomous SDLC Orchestrator** — full-cycle SDLC automation with executive decision support

Phase 16 routers use `/api/<path>` prefixes embedded in the router definition (not applied via `main.py` `include_router` prefix) to maintain independence from prior phase prefix conventions.
