# Project Plan

## Objective

Build iFive AutoQA as a free, local-first AI-assisted testing platform that helps QA teams test critical iFive workflows with deterministic automation and complete failure evidence.

## Scope

- Product coverage: ERP, HRMS, CRM, IIoT, and Application Integration.
- Test types: UI, API, workflow, role, permission, export, and regression tests.
- Execution: Playwright Test with Chromium, Firefox, and WebKit.
- Reporting: pass/fail breakdown, defects, evidence, runtime, browser details, and re-run history.
- AI assistance: local planning, generation, failure analysis, and repair suggestions.

## Delivery Phases

1. Scaffold project structure, documentation, and configuration.
2. Implement frontend informational site and dashboard shell.
3. Implement FastAPI health, projects, test runs, results, reports, and agents endpoints.
4. Add Playwright fixtures, page objects, and first smoke pack.
5. Add local AI prompt workflow and human approval guardrails.
6. Add persistence, report ingestion, and dashboard data views.
7. Harden safety controls and audit trail.

## Stage 4 Delivered

- Explicit approval and persisted local execution lifecycle.
- Fixed allowlist: `dashboard-smoke` and `integration-smoke` only.
- Single-run concurrency, cancellation, timeout, and interrupted-run recovery.
- Run-specific JSON, HTML, screenshot, trace, optional video, stdout, and stderr evidence metadata.
- No real ERP, HRMS, CRM, IIoT, authentication, or AI-agent execution.

## Stage 5 Delivered

- Explicit local operator bootstrap with no default credentials.
- Cookie sessions, CSRF protection, lockout, logout, expiry, and revocation.
- Role-based authorization and creator/approver separation.
- Operator identity on run creation, approval, execution, and cancellation.
- Append-only tamper-evident audit events and integrity verification.

## Stage 6 Delivered

- Temporary passwords force first-login password change before protected resources are available.
- Operators can change passwords and manage their own sessions.
- ADMIN can reset another operator password, list target sessions, revoke target sessions, and view security reports.
- Password history is append-only, recent reuse is blocked, and password-version mismatches invalidate older sessions.
- Security audit events remain hash-chained and secret-free.

## Constraints

- Local-first tools only for the pilot.
- No paid AI API dependency for the pilot.
- No production destructive testing.
- Human approval required for generated and healed tests.
