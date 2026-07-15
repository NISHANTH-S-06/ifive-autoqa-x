# Security and Safety

- Use QA or sandbox environments only.
- Do not run destructive tests against production.
- Do not execute payments, payroll, approvals, deletion, or IIoT control actions.
- Store secrets in environment variables.
- Require human approval for generated and healed tests.
- Preserve evidence and audit history.

## Execution Boundary

The server owns the suite registry and fixed Playwright command. Requests cannot provide files, paths, URLs, shell commands, or arguments. Execution is limited to local AutoQA, requires explicit approval, uses `shell=False`, and permits one tracked process. Cancellation and timeout affect only that process. Startup recovery marks orphaned `RUNNING` records failed with `Execution interrupted before completion.`

Evidence downloads require matching run ownership and a resolved path inside `qa/reports/runs/<RUN_CODE>`. Stored paths are relative; stdout/stderr are truncated and secret-like assignments are redacted. Video is optional because FFmpeg is unavailable, while failure screenshots and traces remain enabled.

## Authentication and Audit

PBKDF2 password hashes and SHA-256 session/CSRF hashes are stored locally. Authentication cookies are HttpOnly, SameSite=Lax, and optionally Secure. State changes require the matching CSRF value. Lockout, expiry, revocation, inactive accounts, and generic login errors are enforced.

Audit rows are deterministic SHA-256 chain entries. SQLite triggers reject UPDATE and DELETE, while `/api/audit/verify` recomputes the complete chain without repair. Creator/approver separation applies even to ADMIN.

## Stage 6 Credential and Session Safety

Temporary passwords and reset passwords are never returned, logged, emailed, or stored in plaintext. Password policy enforces length, character classes, username/display-name exclusion, placeholder rejection, repeated/sequential rejection, and recent-history reuse prevention.

Password history is append-only and stores hashes only. Password changes increment `password_version`; sessions created with older versions are revoked or rejected. Session APIs expose only safe metadata: masked IP, summarized user agent, timestamps, active/current flags, and revocation state.

Forced password-change operators cannot access dashboard, projects, runs, evidence, operator management, audit, execution controls, or security reports until the password is changed. Security reports are ADMIN-only aggregate views and do not expose hashes, token material, CSRF values, cookies, raw IP lists, or credential values.

## Stage 7 Bootstrap and UI Acceptance Safety

The local bootstrap script is an explicit administrative action only. It prompts interactively, does not print passwords, does not create default credentials, and rejects creation of a second active ADMIN. A bootstrap-created operator is active but must change the password before normal dashboard access; the initial hash is recorded in password history and the audit chain records only safe metadata.

Stage 7 UI acceptance keeps forced-password-change operators inside the password-change flow, clears password fields after failed password actions, blocks mismatched confirmation before network submission, and exposes loading, empty, error, and retry states for session and ADMIN security reporting panels.

Real iFive execution, production execution, Ollama installation, and AI-agent execution remain disabled unless a later stage explicitly changes those boundaries.

## Stage 8 Test Management Safety

Stage 8 manual test management is authenticated and CSRF-protected. VIEWER can read approved active content, TESTER can author and execute assigned manual work, APPROVER can review, and ADMIN can manage structure. Creator-approver separation still applies to ADMIN-created cases.

Case versions are append-only and manual run cases freeze the selected version number. Evidence upload accepts only local allowlisted document/image/archive types, stores generated filenames under `backend/data/stage8_evidence`, records SHA-256, and never returns absolute paths. CSV exports escape spreadsheet formula prefixes and omit credential/session/audit-chain internals.

Manual runs do not execute Playwright, do not open browsers against real iFive products, and do not install or invoke AI agents.

## Stage 9 Connection Target Safety

Stage 9 is a connection-management boundary only. It allows registry metadata, review/approval, and restricted read-only connectivity checks. It does not authenticate, submit login forms, crawl, scan ports, run Playwright against iFive, upload files, mutate business data, or execute test suites.

Target policy accepts only HTTP/HTTPS, normalizes origins, rejects credentials, fragments, unsafe schemes, obfuscated IPs, query-bearing base URLs, unsafe probe paths, and PRODUCTION. DNS is resolved before checks; metadata, link-local, multicast, unspecified, reserved, broadcast, and non-LOCAL loopback addresses are blocked. Redirects are not automatically followed and cross-origin redirects are recorded as blocked.

Connection checks send no request body, cookies, authorization, proxy-authorization, CSRF values, or credential headers. Environment proxy trust is disabled. Stored check history contains sanitized status, selected safe headers, TLS summary, latency, and error category only. Response bodies, raw certificates, `Set-Cookie`, authorization values, cookies, tokens, and passwords are not stored or displayed. Credential profiles are metadata only.

## Stage 10 Execution Safety

Stage 10 execution is gated by both Stage 9 target approval and separate execution approval. Production targets, disabled targets, draft targets, stale target versions, unapproved cases, and non-structured steps are rejected. The worker accepts only allowlisted relative-path browser actions and blocks full URLs, code-like payloads, credential-like payloads, unapproved paths, unsafe redirects, and origin escape.

Artifacts are local, path-contained, generated-name files with SHA-256 and size limits. No browser storage state, cookies, tokens, passwords, API keys, CSRF values, authentication headers, raw credential material, executable files, shell commands, Ollama, AI agents, or real iFive execution are introduced.

## Stage 11 Acceptance Safety

Stage 11 keeps real iFive acceptance pending until a persistent active ADMIN and an explicitly authorized non-production target are supplied. Without that authorization, validation uses LOCAL mock targets only and does not open, search, remember, or test any real iFive URL.

DNS socket pinning is enforced for connection checks and automated execution: the approved host is resolved, every address is validated, one address is pinned for the request, Host and TLS SNI remain the approved host, and DNS rebinding or address-set changes are blocked. Redirects remain locked to the approved origin and are not followed during execution.

Queueing requires Stage 11 preflight. Runtime credential input is not persisted; when safe ephemeral input is unavailable, authenticated login validation remains pending. Only `READ_ONLY` and `SAFE_INTERACTION` actions are allowed. Dangerous wording and `MUTATING` or `DESTRUCTIVE` risk levels produce policy-blocked results and audit events rather than execution.

## Stage 12 Defect Safety

Stage 12 defect management is metadata and traceability only. It can link to existing failed manual or automated source records, approved target versions, frozen case versions, local evidence metadata, and sanitized execution artifacts, but it does not authenticate to iFive or open any real target.

Defect comments, history, evidence links, and retests are append-only. Service validation rejects credential-like content in defect fields, comments, and retest notes. API responses expose IDs, status, classifications, SHA-256/evidence metadata, and relative linkage only; they do not expose response bodies, cookies, tokens, passwords, authorization headers, CSRF values, browser storage state, runtime secrets, or absolute local paths.

Lifecycle controls preserve separation of duties. TESTER/ADMIN can create and retest; APPROVER/ADMIN can review and close; non-ADMIN reporters cannot close their own defects. Stage 12 does not create credentials, bootstrap an ADMIN, enable production execution, install Ollama, run AI agents, or begin Stage 13.

## Stage 13 Reporting Safety

Stage 13 reports use database-authoritative aggregates, validated bounded filters, pagination, a 500-row export cap, spreadsheet-formula escaping, generated filenames, path containment, and role-protected export/saved-report actions. Reports do not expose passwords, sessions, cookies, authorization data, secret values, or absolute storage paths.

## Stage 14 Local Release Safety

Stage 14 validates environment settings before startup. Safe mode and TLS verification must remain enabled; production execution cannot be enabled; debug is disabled for local release; real non-production target execution remains disabled by default. Configured SQLite and storage paths are constrained to approved roots.

Project lifecycle scripts bind only to loopback, reject occupied ports, prevent duplicate service starts, store PID records only under `runtime/pids`, and stop a process only after its PID, start time, and project command marker match. No lifecycle script creates operators or targets, accepts password arguments, or installs AI software.

Backups are explicit, timestamped, checksum-manifested, and stored outside source/data directories. Restore validates all paths, hashes, and SQLite integrity, creates a pre-restore backup, and rolls back failed replacement. Retention defaults to dry-run, requires typed confirmation, protects active artifacts and all append-only/immutable histories, and records a safe audit summary.

Application logs are structured, rotated, size-bounded, and redact password, token, cookie, CSRF, authorization, API-key, secret, and browser-storage patterns. Request logs omit queries, headers, bodies, evidence, response bodies, and stack-trace text. Health output contains safe state, counts, and booleans only.
