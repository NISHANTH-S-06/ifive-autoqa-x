# Architecture

## Overview

iFive AutoQA has four local layers:

1. React/Vite frontend for product pages, dashboard views, settings, and reports.
2. FastAPI backend for project metadata, test run orchestration, results, reports, and agent suggestions.
3. Playwright QA workspace for deterministic browser/API tests and evidence capture.
4. Local AI workspace for Ollama-backed planning, generation, and healing prompts.

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
