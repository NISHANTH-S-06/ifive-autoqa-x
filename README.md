# iFive AutoQA

iFive AutoQA is a free, local-first AI-assisted quality engineering platform for testing iFive ERP, HRMS, CRM, IIoT, and Application Integration products.

The platform combines deterministic Playwright execution with reviewable local AI assistance. AI may help plan, generate, and repair tests, but pass or fail decisions must come from explicit Playwright assertions and human-approved QA rules.

## Stack

- Frontend: React, Vite, TypeScript
- Backend: FastAPI, Python
- Database: SQLite first, PostgreSQL later if required
- Testing: Playwright Test, TypeScript
- Local AI: design material only; no AI runtime or model is installed or included in the Stage 14 release
- Browser automation: Playwright MCP
- Reports: Playwright HTML reports, traces, screenshots, videos, console logs, and network logs

## Repository Layout

- `frontend/` - React dashboard and marketing experience.
- `backend/` - FastAPI service, repositories, safety guard, and reporting APIs.
- `qa/` - Playwright test packs, page objects, fixtures, reports, and agent prompts.
- `local-ai/` - Ollama setup notes, local model config, and agent prompt templates.
- `scripts/` - Local setup and run scripts.
- `docs/` - Installation, workflow, API, safety, and demo documentation.

## Safety Position

AutoQA is intended for QA and sandbox environments. It must not execute production destructive actions, payments, payroll, approvals, record deletion, or IIoT machine-control operations.

## Current State: Stage 14 Local Release Readiness

Stages 1-14 provide the local FastAPI/React/SQLite platform, test management, approved non-production target registry, controlled local execution, defect traceability, management reports, and hardened local release operations. Production execution remains blocked. Real target execution remains disabled by default and requires separate authorization after target and execution approval.

Use `scripts/run_migrations.ps1`, `scripts/start_local_system.ps1`, `scripts/verify_health.ps1`, and `scripts/stop_local_system.ps1` for the local release lifecycle. Backup, restore, retention, configuration, packaging, security, troubleshooting, final UAT, and demonstration instructions are in `docs/LOCAL_RELEASE_OPERATIONS.md`, `docs/FINAL_UAT_CHECKLIST.md`, and `docs/FULL_PROJECT_DEMO.md`.

No default ADMIN exists. Persistent login, real non-production target, and authenticated iFive acceptance remain pending until explicitly authorized inputs are provided.

## Historical Stage 4 Baseline

Projects and test runs persist in local SQLite. A queued `iFive AutoQA Dashboard` run can execute only after the exact safety confirmation `APPROVE LOCAL TEST EXECUTION`. The backend maps `dashboard-smoke` and `integration-smoke` to fixed local Playwright files; it never accepts a command or file path from the UI.

Lifecycle: `QUEUED -> APPROVED -> RUNNING -> PASSED | FAILED | CANCELLED`. One run may execute at a time, with a default 900-second timeout. Artifacts are isolated under `qa/reports/runs/<RUN_CODE>/` and exposed only through ownership-checked evidence endpoints. Real iFive products and AI agents are not executed in Stage 4.

## Stage 5 Local Security

Stage 5 adds local `VIEWER`, `TESTER`, `APPROVER`, and `ADMIN` operators. There are no default credentials. Create the first operator explicitly with `scripts/create_local_operator.ps1`. Passwords use PBKDF2-HMAC-SHA256; only hashed session tokens are stored. Browser authentication uses an HttpOnly SameSite cookie and CSRF header/cookie validation.

Run creators cannot approve their own runs, including ADMIN creators. Lifecycle identities and a SQLite-protected SHA-256 audit chain record local actions. Real iFive and AI-agent execution remain disabled.

## Stage 6 Operator Security

Stage 6 adds temporary-password enforcement, mandatory first-login password change, self-service password change, ADMIN password reset without password disclosure, append-only password history, password-version session invalidation, own-session listing/revocation, ADMIN session revocation, and ADMIN-only security reports.

No default credentials are created. If no active ADMIN exists, run `scripts\create_local_operator.ps1` from the extracted project root. Password expiry stays disabled by default with `AUTOQA_PASSWORD_MAX_AGE_DAYS=0`. Stage 6 still does not enable real iFive execution, production execution, or AI agents.

## Stage 7 Local Acceptance Hardening

Stage 7 makes the explicit bootstrap path Stage 6-aware. Bootstrap-created operators must rotate the password on first login, receive password-history and audit-chain records, and duplicate active ADMIN creation is rejected. The UI now clears password fields after failed password actions, blocks mismatched confirmation before submission, and shows recoverable loading, empty, and error states for session and ADMIN security reporting panels.

Persistent ADMIN acceptance is intentionally manual because automation must not create, store, or display a real password. Real iFive execution, production execution, Ollama, and AI agents remain disabled.

## Stage 8 Test Management Core

Stage 8 adds local manual test-management records: test projects, modules, managed suites, test cases, ordered steps, tags, immutable version snapshots, manual runs, run cases, step results, evidence metadata, and CSV/JSON exports.

The lifecycle is `DRAFT -> IN_REVIEW -> APPROVED | REJECTED`, with controlled revisions and archive behavior. Creators cannot approve their own cases. Manual runs can include only approved active cases and freeze the selected case version. Evidence is stored locally under `backend/data/stage8_evidence` with generated filenames, SHA-256 hashes, and no absolute paths in API responses.

Stage 8 is manual execution management only. It does not enable real iFive execution, arbitrary browser targets, production execution, Ollama, or AI agents.

### Stage 9 - Controlled Connection Targets

Stage 9 adds an approved target registry for connection metadata only. Operators can propose LOCAL, DEVELOPMENT, QA, or STAGING targets, submit them for review, approve them through creator-approver separation, and run restricted read-only `HEAD` or approved-path `GET` connectivity checks after approval.

The server normalizes target origins, rejects production, blocks unsafe schemes, embedded credentials, fragments, unapproved probe paths, metadata/link-local/special IP ranges, unsafe redirects, and environment proxy use. Connection checks store sanitized status, headers, TLS summary, latency, and history only; response bodies, cookies, authorization data, CSRF values, passwords, and tokens are not stored.

Credential profiles are metadata only: profile name, optional username hint, and secret source (`NONE` or `PROMPT_AT_USE`). Stage 9 does not authenticate, submit login forms, run Playwright against iFive, mutate business data, or implement the Stage 10 execution engine. Real target acceptance requires a persistent authorized ADMIN and an explicitly approved non-production target.

## Stage 10 Controlled Execution

Stage 10 adds automated run management for structured browser-style actions against execution-approved non-production targets only. Stage 9 target approval is not enough: a target must also pass explicit execution submission and approval, with creator self-approval blocked. Runs freeze the approved target version and approved test-case versions before queueing.

Automated runs support draft, submit, approve, queue, local worker claim, heartbeat, cancellation, timeout, safe retry, progress, step results, failure classification, and sanitized local artifacts. Steps are accepted only as structured JSON actions from the allowlist; arbitrary Playwright, JavaScript, Python, PowerShell, shell commands, uploaded code, full external URLs, browser extensions, authentication headers, cookie/token injection, crawling, port scanning, and production execution remain blocked.

Stage 10 artifacts are stored under generated local paths with SHA-256, size limits, path containment, and authorized download. Response bodies, browser storage state, cookies, tokens, passwords, API keys, CSRF values, authentication headers, executable artifacts, Ollama, AI agents, real iFive execution, and Stage 11 behavior remain out of scope.

## Stage 11 Non-Production Acceptance

Stage 11 hardens the execution boundary for authorized non-production acceptance. Because no real non-production iFive target or persistent active ADMIN is currently present, real-target acceptance remains pending and automated verification uses LOCAL mock targets only.

Connection checks and automated execution now pin requests to one validated resolved address, preserve the approved Host header and TLS server name, revalidate DNS before use, and block DNS rebinding/address changes, unsafe redirects, and blocked address ranges. Automated queueing performs Stage 11 preflight checks for approved/enabled targets, separate execution approval, frozen target and case versions, worker availability, structured actions, DNS pinning, timeout/concurrency limits, and runtime-secret safety.

Execution risk levels are limited to `READ_ONLY` and `SAFE_INTERACTION`. `MUTATING`, `DESTRUCTIVE`, dangerous action wording, runtime credential persistence, traces/storage state for secrets, production access, real iFive access without explicit authorization, Ollama, AI agents, and Stage 13 behavior remain blocked.

## Stage 12 Defect Management

Stage 12 adds controlled defect management and end-to-end traceability. Defects can be created directly or from failed/blocked manual results and failed/timed-out/blocked automated results, with duplicate warning/confirmation and immutable links to source runs, run cases, step results, frozen test-case versions, approved target versions, evidence, and execution artifacts.

The defect lifecycle is `NEW -> TRIAGED -> ASSIGNED -> IN_PROGRESS -> FIXED -> READY_FOR_RETEST -> RETEST_PASSED -> CLOSED`, with reject, duplicate, and reopen controls. TESTER or ADMIN can create and retest defects; APPROVER or ADMIN can triage, assign, mark fixed/ready, reject, duplicate, and close, with reporter self-closure blocked unless ADMIN. Comments, history, evidence links, and retest records are append-only and sanitized.

Stage 12 does not create credentials, bootstrap an ADMIN, access real iFive targets, broaden production execution, store secrets, install Ollama, run AI agents, or begin Stage 13.

## Phase 4 Completion

Phase 4 repository cleanup, full system audit, evidence-based project health scoring, and Local AI Task Analyzer foundation is now complete. The repository has been pruned of unneeded caches and artifacts. The AI Analyzer allows for deterministic local evaluation of imported tasks to generate structured, JSON-based test plan recommendations strictly for human review, without executing arbitrary commands or sending data externally.

## Phase 5 & Phase 5.1 Completion

Phase 5 and Phase 5.1 implement deterministic AI test plan generation, versioned test plan models (`TestPlan`, `TestPlanVersion`, `TestScenario`, `TestStep`), human review and approval workflows, developer self-approval blocking, unsafe AI output rejection, canonical `NEED_CLARITY` missing information gates, exact approved-version execution linkage, and React plan editing UI.

## Phase 5.2 Completion — Real End-to-End Acceptance Verification

Phase 5.2 proves the complete real local end-to-end acceptance flow without main-flow API mocks. Test plans are generated via local AI analysis, reviewed, edited, approved by independent approvers, and executed against the real Demo Product (`http://127.0.0.1:5175`). All 15 E2E Playwright tests and 162 total backend pytest tests pass green with 100% verification.

## Phase 6 Completion — Advanced QA Validation Pack

Phase 6 implements the complete Advanced QA Validation Pack, extending test plans with multi-layered validation profiles:
- **API Validation Engine:** Enforces HTTP status codes, JSON schema structures, header templates, and origin policy rules.
- **Read-Only Database Validation Engine:** Safely executes read-only SQL queries (`SELECT`, `WITH`) with AST/token safety parsers, row limit checks, and data column assertion assertions.
- **Accessibility Validation Engine:** Evaluates DOM scan violations against WCAG 2.1 AA standards and thresholds.
- **Performance Validation Engine:** Assesses timing metrics (navigation duration, TTI, TTFB) against warning and failure thresholds (`PASS`, `PASS_WITH_WARNINGS`, `FAIL`).
- **Unified Result Aggregation & Defect Grouping:** Aggregates multi-layered outcomes, computes SHA-256 result hashes, and generates deduplicated defect records.
- **Management Reporting & Schedules:** Produces standalone HTML and PDF validation reports with SHA-256 cryptographic signatures, and supports cron-scheduled automated validation runs.

All 20 E2E Playwright tests in Phase 6 (`qa/tests/phase6-advanced-validation.spec.ts`) and all 186 total backend pytest unit tests pass green with 100% verification.
