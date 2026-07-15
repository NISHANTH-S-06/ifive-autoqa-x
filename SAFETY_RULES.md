# Safety Rules

## Allowed Environments

- QA
- Sandbox
- Local development

## Blocked Environments

- Production
- Live payment systems
- Live payroll systems
- Live IIoT machine-control systems

## Blocked Actions

- Payment execution
- Payroll execution
- Record deletion
- Approval execution
- Production destructive testing
- IIoT machine-control commands
- Unauthorized access attempts beyond approved permission tests

## AI Guardrails

- AI may suggest plans, tests, and repairs.
- AI must not decide pass or fail.
- Playwright assertions determine test outcomes.
- Humans must approve generated and healed tests.
- All agent suggestions must be auditable.

## Secret Handling

- Use environment variables.
- Never commit secrets.
- Keep `.env` files ignored by Git.

## Stage 4 Local Execution

- Only the `AUTOQA` project in `local` may be approved and executed.
- Approval requires the exact phrase `APPROVE LOCAL TEST EXECUTION`.
- Only `dashboard-smoke` and `integration-smoke` are allowlisted; API-supplied paths, globs, arguments, and commands are rejected.
- Playwright runs with `shell=False`, one process at a time, and a configurable timeout (`AUTOQA_RUN_TIMEOUT_SECONDS`, default 900).
- Cancellation targets only the tracked process for that run. Interrupted runs become `FAILED` and are never silently passed or retried.
- Evidence paths are relative and must remain inside their run folder. Logs are size-limited and common secret values are redacted.

## Stage 5 Identity Rules

- No default credentials or plaintext passwords.
- HttpOnly session cookies, hashed stored tokens, eight-hour expiry, revocation, and CSRF validation are mandatory.
- Five failed attempts lock an account for 15 minutes.
- TESTER creates; APPROVER or ADMIN approves/executes; a creator can never approve the same run.
- ADMIN cannot bypass execution safety or remove the final active ADMIN.
- Audit metadata excludes passwords, hashes, tokens, cookies, CSRF values, Authorization headers, and secrets.

## Stage 6 Operator Security Rules

- No default ADMIN or default password may be created.
- Temporary and reset passwords must be entered manually, never generated for display, logged, emailed, returned, or stored in plaintext.
- Password changes and ADMIN resets increment password version and invalidate older sessions.
- Password-history rows are append-only and store hashes only.
- A forced-change operator is blocked from dashboard, projects, runs, evidence, operator management, audit log, execution controls, and security reports until the password changes.
- Real iFive execution, production enablement, paid APIs, local AI installation, and Planner/Generator/Healer agents remain out of scope.

## Stage 9 Connection Target Rules

- Stage 9 is registry and connectivity management only; it is not a test execution engine.
- Only LOCAL, DEVELOPMENT, QA, and STAGING targets may be proposed. PRODUCTION is blocked.
- Target URLs must be HTTP/HTTPS and must not include credentials, fragments, unsafe schemes, or unapproved ports.
- Probe paths must be explicit read-only paths and must not include hosts, traversal, backslashes, query strings, or fragments.
- Only approved enabled targets may be checked.
- Only `HEAD` and approved-path `GET` are allowed.
- DNS/IP validation must block metadata, link-local, multicast, unspecified, reserved, broadcast, and non-LOCAL loopback targets.
- Redirects must not be followed automatically; cross-origin redirects are blocked.
- Checks must not send cookies, authorization, proxy authorization, CSRF headers, request bodies, or credential material.
- Stored results must not contain response bodies, cookies, `Set-Cookie`, authorization data, tokens, passwords, or raw certificates.
- Credential profiles are metadata only and must not contain passwords, tokens, cookies, or API keys.
- Stage 9 must not submit login forms, crawl targets, scan ports, run Playwright against iFive, mutate business data, install Ollama, run AI agents, or implement Stage 10.

## Stage 10 Rules

- Stage 9 approval alone must not enable automated execution.
- Execution requires separate approval on a non-production approved target, with creator self-approval blocked.
- Automated steps must be structured allowlisted actions only; arbitrary code, shell commands, full URLs, uploaded code, browser extensions, local files, cookie/token injection, and authentication-header injection are blocked.
- The worker must enforce approved origin and approved relative paths during navigation, redirects, history movement, and artifact capture.
- Queue leases, heartbeat, cancellation, timeout, retry, and progress must be auditable.
- Artifacts must be generated, path-contained, non-executable, size-limited, hashed, and free of credential-like content.
- Stage 10 must not run real iFive, production targets, Ollama, AI agents, vulnerability scans, port scans, crawling, or Stage 11 behavior.

## Stage 11 Rules

- Real target acceptance requires an active ADMIN, exact authorized non-production URL, approved target registry state, `execution_enabled=true`, separate execution approver, and written non-production authorization.
- Without those prerequisites, only LOCAL mock targets may be used and real acceptance remains pending.
- DNS pinning must validate all resolved addresses, connect only to one validated address, preserve approved Host/TLS SNI, and block DNS rebinding, address changes, unsafe redirects, and blocked IP ranges.
- Queueing requires Stage 11 preflight and recent worker heartbeat.
- Runtime secrets must be ephemeral only; if safe ephemeral input is unavailable, authenticated login testing remains pending.
- Only `READ_ONLY` and `SAFE_INTERACTION` are allowed. `MUTATING`, `DESTRUCTIVE`, dangerous action wording, production access, business-data mutation, uploads, arbitrary JavaScript, shell commands, external origins, popups, crawling, scanning, brute force, Ollama, AI agents, and Stage 13 behavior are blocked.

## Stage 12 Rules

- Defects may be created only by TESTER or ADMIN and only from direct local metadata or failed/blocked manual/automated source results already stored in AutoQA.
- Defect source links must preserve frozen test-case version and target-version metadata where available; they must not copy response bodies, browser storage state, cookies, tokens, passwords, authorization headers, CSRF values, or absolute paths.
- Comments, history, evidence links, and retest records are append-only and must reject credential-like content.
- Retesting requires TESTER or ADMIN and can be recorded only after the defect is ready for retest.
- Closure requires APPROVER or ADMIN, a safe resolution, and reporter self-closure is blocked unless the operator is ADMIN.
- Stage 12 must not bootstrap ADMIN, create credentials, authenticate to iFive, open real iFive URLs, broaden production execution, install Ollama, run AI agents, or begin Stage 13.
