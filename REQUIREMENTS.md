# Requirements

## Functional Requirements

- Present the iFive AutoQA platform, supported products, test scope, and safety model.
- Track projects, test suites, test cases, test runs, results, defects, evidence, and agent suggestions.
- Run Playwright tests against approved QA or sandbox environments.
- Capture screenshots, videos, traces, console logs, and network logs for failures.
- Display dashboard metrics including total tests, pass rate, failed tests, open defects, average runtime, and product coverage.
- Generate reviewable test plans and Playwright test suggestions using local AI.
- Require human approval before accepting generated tests or healed test changes.

## Non-Functional Requirements

- Default to SQLite for local development.
- Keep configuration in environment variables.
- Keep secrets out of source control.
- Prefer deterministic checks over AI interpretation.
- Maintain an auditable history of runs and suggestions.

## Out of Scope for Initial Pilot

- Production execution.
- Payment execution.
- Payroll execution.
- Approval execution.
- Record deletion.
- IIoT machine-control actions.
# Stage 5 Security Requirements

- Local operators use `VIEWER`, `TESTER`, `APPROVER`, or `ADMIN`.
- Passwords meet the 12-character complexity policy and are never stored or returned in plaintext.
- Sessions expire after eight hours by default; raw authentication tokens are never stored.
- State changes require CSRF validation.
- TESTER creates runs; APPROVER approves/executes; creators cannot approve their own runs.
- Audit events are append-only and hash-chained.
- No default credentials, real iFive execution, production execution, or AI agents.

# Stage 6 Security Requirements

- ADMIN-created and ADMIN-reset passwords are temporary and require password change before normal access.
- Passwords must satisfy the strong local policy and cannot reuse recent password history.
- Operators can change their own passwords, list safe session metadata, revoke one session, and revoke other sessions.
- ADMIN can reset another operator password without viewing or returning it, and can revoke target operator sessions with a reason.
- Security summary and operator-security reports are ADMIN-only and never expose hashes, raw tokens, CSRF values, cookies, or credential material.
- Password expiry is controlled by `AUTOQA_PASSWORD_MAX_AGE_DAYS`; the default `0` disables expiry for the local pilot.

# Stage 8 Test Management Requirements

- ADMIN manages test-management project, module, and suite structure.
- TESTER or ADMIN creates draft test cases with ordered steps, expected results, priority, type, severity, ownership, and tags.
- APPROVER or ADMIN reviews submitted cases, but creators cannot approve their own cases.
- Approved cases are protected by immutable version snapshots.
- Manual runs use approved active cases only and freeze the selected case version.
- Manual result statuses are `NOT_RUN`, `IN_PROGRESS`, `PASSED`, `FAILED`, `BLOCKED`, and `SKIPPED`; failed or blocked results require notes.
- Evidence upload is local only, allowlisted by file type, hashed, and path-contained.
- CSV and JSON exports respect RBAC, row limits, and spreadsheet formula-injection protection.
- Stage 8 does not execute browser automation, connect to real iFive URLs, install Ollama, or run AI agents.

# Stage 9 Connection Target Requirements

- TESTER or ADMIN can create draft connection target proposals for LOCAL, DEVELOPMENT, QA, or STAGING only.
- APPROVER or ADMIN can review submitted targets, but creators cannot approve their own targets.
- PRODUCTION targets are blocked in Stage 9.
- Target URLs must be normalized server-side and limited to HTTP or HTTPS without embedded credentials, fragments, unsafe schemes, or unapproved ports.
- Probe paths must be explicit read-only paths that begin with `/` and must not contain hosts, traversal, backslashes, query strings, fragments, or control characters.
- Connectivity checks are allowed only for approved and enabled targets and only with `HEAD` or approved-path `GET`.
- DNS/IP validation must block metadata services, link-local, multicast, unspecified, reserved, broadcast, and loopback-for-non-LOCAL targets.
- Redirects must not be followed automatically and cross-origin redirects must be recorded as blocked.
- Results may store sanitized status, headers, TLS summary, latency, and history only; response bodies and sensitive headers must not be stored.
- Credential profiles are metadata only and must not include passwords, tokens, cookies, CSRF values, API keys, or authentication headers.
- Stage 9 does not authenticate to iFive, run Playwright against iFive, mutate business data, install Ollama, run AI agents, or implement Stage 10 execution.

## Stage 10 Controlled Execution

- Automated execution requires an approved, enabled, non-production Stage 9 target plus separate execution approval.
- Target creators and execution submitters cannot approve execution for their own targets.
- Automated runs may include only approved active test cases and frozen approved test-case versions.
- Steps must be structured allowlisted actions: relative navigation, click, fill, select, check/uncheck, key press, wait, assertions, screenshot, read text, reload, and back/forward within the approved origin.
- The engine must reject arbitrary code, full external URLs, unapproved redirects, unapproved origins, shell commands, browser extensions, local files, authentication headers, cookie/token injection, crawling, port scanning, vulnerability scanning, and production execution.
- Queueing requires approval and records worker heartbeat, lease, cancellation, timeout, retry, progress, step results, failure classification, and artifacts.
- Artifacts must use generated safe filenames, relative paths, SHA-256, size limits, path containment, authorized download, and no executable or credential-bearing content.
- Stage 10 must not connect to real iFive without separate explicit authorization and must not implement Stage 11.

## Stage 11 Non-Production Acceptance Requirements

- Real target acceptance requires an active ADMIN, exact non-production target URL, DEVELOPMENT/QA/STAGING confirmation, written authorization, approved target registry state, `execution_enabled=true`, separate execution approver, and non-production classification.
- If those prerequisites are missing, Stage 11 must not access a real target and must verify behavior with LOCAL mock targets only.
- DNS pinning must resolve the approved hostname, validate all resolved IPs, connect to one validated address, preserve Host and TLS SNI, revalidate redirects, and block rebinding/address changes and unsafe address ranges.
- Execution preflight must verify target approval, separate execution approval, production blocking, frozen target/case versions, approved structured actions, worker availability, bounded timeout/concurrency, and runtime-secret safety before queueing.
- Runtime secrets must not be stored in the database, environment, browser storage state, logs, screenshots, traces, artifacts, audit metadata, or reports. If safe ephemeral input is unavailable, authenticated login acceptance remains pending.
- Stage 11 may execute only `READ_ONLY` and `SAFE_INTERACTION`; `MUTATING`, `DESTRUCTIVE`, dangerous action wording, production access, business-data mutation, uploads, arbitrary JavaScript, shell commands, external origins, popups, scanning, crawling, and brute force remain blocked.

## Stage 12 Defect Management Requirements

- TESTER or ADMIN can create defects directly or from failed/blocked manual results and failed/timed-out/blocked automated results.
- Defects must link to project/module/suite/case scope, frozen test-case version, manual or automated source run data, approved target version where applicable, and sanitized evidence/artifact metadata.
- Possible duplicate source defects must be reported before creation and require explicit confirmation.
- Lifecycle transitions must enforce `NEW`, `TRIAGED`, `ASSIGNED`, `IN_PROGRESS`, `FIXED`, `READY_FOR_RETEST`, `RETEST_PASSED`, `REOPENED`, `CLOSED`, `REJECTED`, and `DUPLICATE` rules.
- APPROVER or ADMIN controls triage, assignment, fix/ready marking, rejection, duplicate marking, and closure. TESTER or ADMIN controls retest recording. Non-ADMIN reporters cannot close their own defects.
- Closure requires a resolution; rejection/reopen require a reason; duplicate marking requires a same-project original defect.
- Comments, history, evidence links, and retest records must be append-only and sanitized against credential-like content.
- Stage 12 must not create credentials, bootstrap ADMIN, access real iFive targets, persist runtime secrets, enable production execution, install Ollama, run AI agents, or implement Stage 13.
