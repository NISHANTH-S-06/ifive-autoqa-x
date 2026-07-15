# Test Strategy

## Test Layers

- UI tests for pages, buttons, forms, menus, and workflows.
- API tests for authentication, requests, responses, and schemas.
- Role and permission tests for authorized and unauthorized access.
- Cross-browser tests on Chromium, Firefox, and WebKit.
- Export tests for reports and downloadable files.
- Regression tests for critical business workflows.

## Evidence

Each failed test should preserve:

- Screenshot
- Trace
- Video
- Console logs
- Network logs
- Error summary

## Product Test Packs

- ERP: login, customer, vendor, inventory, purchase, sales, finance, production, reports, export, permissions.
- HRMS: employee, attendance, leave, shift, payroll preview, recruitment, self service, permissions.
- CRM: lead, opportunity, follow-up, quotation, customer, reports, permissions.
- IIoT: dashboard, device status, telemetry, alerts, charts, filters, data freshness.
- Application Integration: authentication, API mapping, schema, retry, duplicate handling, webhooks, error logs.

## Decision Rule

AI assists the testing process. Final pass or fail is always decided by deterministic Playwright assertions.
# Stage 5 Test Strategy

Backend tests use isolated temporary SQLite databases and cover login, generic failures, lockout, session expiry/revocation, CSRF, RBAC, separation of duty, operator management, audit triggers, hash verification, and Stage 3/4 regressions. Playwright uses deterministic API mocking for role UI states. The controlled real acceptance flow uses explicitly created temporary local TESTER and APPROVER accounts and only `dashboard-smoke`.

# Stage 6 Test Strategy

Backend tests cover password policy rules, required first-login change, self-service change, ADMIN reset, password-history triggers, session listing/revocation, password-version invalidation, security reporting, sensitive-field exclusion, and audit-chain validity. Frontend and Playwright tests use API mocking for password/session/security UI states and continue to run only local AutoQA allowlisted suites. Real ADMIN acceptance is pending until an ADMIN is explicitly bootstrapped.

# Stage 7 Test Strategy

Backend tests cover the interactive bootstrap boundary with isolated temporary SQLite databases: mandatory password rotation, password-history insertion, safe audit metadata, password non-disclosure in output, duplicate active ADMIN rejection, and non-ADMIN bootstrap behavior when an ADMIN already exists.

Playwright tests cover forced password-change routing, client-side confirmation mismatch blocking, post-change dashboard access, My Sessions empty state, ADMIN security empty state, and security-report retry recovery. Persistent ADMIN acceptance remains manual because no password may be generated, stored, or displayed by automation.

# Stage 8 Test Strategy

Backend tests cover project/module/suite validation, cross-project rejection, lifecycle transitions, self-approval blocking, rejection reasons, immutable version triggers, tag search, pagination/sort allow-listing, manual run creation/execution/completion, frozen case versions, evidence validation/download/delete, export formula escaping, mandatory-password-change blocking, disabled-operator blocking, CSRF, RBAC, and audit-chain validity.

Playwright tests use mocked local API data to create test-management structure, create and submit a case, verify self-approval blocking, approve through a separate mocked role, create a manual run, record manual results, verify version history/search, and exercise evidence upload failure handling. No Playwright test connects to a real iFive URL for Stage 8.

# Stage 9 Test Strategy

Backend tests cover target creation, duplicate keys, invalid URL schemes, embedded credentials, production blocking, probe-path validation, lifecycle transitions, creator self-approval blocking, immutable target-version triggers, approved local HEAD/GET checks, unsafe redirect blocking, response-size limiting, sensitive-header stripping, credential metadata secret-field rejection, CSRF/RBAC, forced-password-change blocking, inactive operators, password-version mismatch, and audit-chain validity.

Playwright tests use a local mock target URL and mocked AutoQA APIs to create a target draft, submit it, verify the creator cannot approve, approve with a separate role, run safe HEAD and GET checks, verify sanitized results, verify unsafe redirect display, confirm no unsupported method or arbitrary URL check control, create credential metadata without password fields, verify responsive behavior, and confirm Stage 8 and local Playwright restrictions remain visible. No browser test connects to a real iFive URL.

## Stage 10

Backend tests cover execution target approval, Stage 9 approval not implying execution approval, creator self-approval blocking, production/draft/disabled target blocking, approved-case and frozen-version enforcement, structured-action validation, arbitrary code and external URL rejection, queueing, worker heartbeat, job lease, cancellation, timeout, safe retry, concurrency limit behavior, origin/redirect escape blocking, artifact path safety, secret redaction, CSRF/RBAC, audit-chain validity, and Stage 1-9 regression.

Playwright tests use a local mock target URL in mocked AutoQA API data, create and approve an execution target, create an automated run, submit/approve/queue it, run the local worker control, verify pass results and sanitized evidence, and confirm browser storage does not contain password, token, or cookie strings. No Playwright test connects to a real iFive URL for Stage 10.

## Stage 11

Backend tests cover missing persistent ADMIN readiness, missing real-target authorization, worker-required preflight, approved READ_ONLY execution, validated address pinning, DNS rebinding blocking, runtime-secret refusal when safe ephemeral input is unavailable, dangerous/mutating/destructive action blocking, artifact redaction, and audit-chain validity.

Playwright tests use a local mock target and mocked AutoQA APIs to display the Stage 11 readiness checklist, show ADMIN and real-target acceptance pending, create an approved run, execute the controlled acceptance path, view preflight/results/evidence, and confirm browser storage does not contain password, token, or cookie strings. No Playwright test connects to a real iFive URL for Stage 11.

## Stage 12

Backend tests cover direct and source-based defect creation, manual and automated failed-result linking, duplicate warning/confirmation, RBAC, CSRF, cross-project rejection, secret-like content rejection, lifecycle transitions, assignment, closure requirements, retest state control, append-only defect comments/history/retests, evidence/artifact links, traceability endpoints, and audit-chain validity.

Playwright tests use mocked local AutoQA API data to create a defect from a failed automated run, confirm source evidence and traceability, add comments, move through triage/assignment/fix/ready/retest/closure with separate roles, verify viewer restrictions, check responsive layouts at 320, 375, 768, 1024, and 1440 pixels, and confirm browser storage does not contain password, token, or cookie strings. No Playwright test connects to a real iFive URL for Stage 12.
