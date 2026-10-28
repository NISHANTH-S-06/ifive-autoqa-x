# API Documentation

The backend exposes a local FastAPI service.

## Initial Endpoints

- `GET /api/health`
- `GET /api/projects`
- `POST /api/projects`
- `GET /api/test-runs`
- `POST /api/test-runs`
- `GET /api/test-runs/{run_id}`
- `POST /api/test-runs/{run_id}/approve` with exact confirmation `APPROVE LOCAL TEST EXECUTION`
- `POST /api/test-runs/{run_id}/execute` with `confirm_local_execution: true`
- `POST /api/test-runs/{run_id}/cancel`
- `GET /api/test-runs/{run_id}/evidence`
- `GET /api/test-runs/{run_id}/evidence/{evidence_id}`
- `GET /api/results`
- `GET /api/reports/summary`
- `GET /api/reports/dashboard`
- `GET /api/agents/suggestions`

Interactive API docs are available at `/docs` when the backend is running.

Stage 4 execution accepts only the internal keys `dashboard-smoke` and `integration-smoke`, only for local `AUTOQA`. Approval moves `QUEUED` to `APPROVED`; execution returns HTTP 202 and progresses asynchronously through `RUNNING` to a terminal state. Only one run executes at once. Evidence responses expose relative metadata, and downloads enforce run ownership and containment.

## Stage 5 APIs

- `POST /api/auth/login`, `POST /api/auth/logout`, `GET /api/auth/me`, `GET /api/auth/csrf`
- `GET/POST /api/operators`
- `PATCH /api/operators/{id}/status`, `PATCH /api/operators/{id}/role`
- `GET /api/audit/events`, `GET /api/audit/verify`

Authenticated mutations require `X-CSRF-Token`. VIEWER reads, TESTER creates projects/runs, APPROVER approves/executes/cancels, and ADMIN manages operators/audit. Safe operator responses never contain hashes, passwords, tokens, or lockout internals.

## Stage 6 APIs

- `POST /api/auth/change-required-password`
- `POST /api/auth/change-password`
- `GET /api/auth/sessions`
- `POST /api/auth/sessions/{session_id}/revoke`
- `POST /api/auth/sessions/revoke-others`
- `POST /api/operators/{operator_id}/reset-password`
- `GET /api/operators/{operator_id}/sessions`
- `POST /api/operators/{operator_id}/sessions/revoke-all`
- `GET /api/security/summary`
- `GET /api/security/operators`

Password-change and session mutation APIs require authentication and CSRF. ADMIN reset requires a reason and never returns the submitted temporary password. Security reports and target-session APIs are ADMIN-only. Forced-change sessions may call only profile, CSRF, required-change, logout, and health endpoints until the password is changed.

## Stage 8 Test Management APIs

- `GET/POST/PATCH /api/test-projects` and `POST /api/test-projects/{id}/archive`
- `GET/POST/PATCH /api/test-modules` and `POST /api/test-modules/{id}/archive`
- `GET/POST/PATCH /api/test-suites` and `POST /api/test-suites/{id}/archive`
- `GET/POST/PATCH /api/test-cases`
- `POST /api/test-cases/{id}/submit`, `/approve`, `/reject`, `/revision`, `/archive`
- `GET /api/test-cases/{id}/versions`
- `GET /api/test-cases/export?format=csv|json`
- `GET/POST /api/manual-test-runs`
- `POST /api/manual-test-runs/{id}/start`, `/complete`, `/cancel`
- `GET/POST /api/manual-test-runs/{id}/cases`
- `PATCH /api/manual-test-runs/{id}/cases/{case_id}`
- `PATCH /api/manual-test-runs/{id}/cases/{case_id}/steps/{step_number}`
- `POST/GET /api/manual-test-runs/{id}/cases/{case_id}/evidence`
- `GET /api/manual-evidence/{id}/download`
- `DELETE /api/manual-evidence/{id}`

Stage 8 APIs require an authenticated active session. Mutations and evidence upload/delete require CSRF. Manual runs are separate from the existing `/api/test-runs` Playwright execution API and do not start browser automation or connect to real iFive URLs. CSV exports escape spreadsheet formula prefixes and apply server-side row limits. Evidence metadata never exposes absolute local paths.

## Stage 9 Connection Target APIs

- `GET/POST /api/connection-targets`
- `GET/PATCH /api/connection-targets/{id}`
- `POST /api/connection-targets/{id}/submit`
- `POST /api/connection-targets/{id}/approve`
- `POST /api/connection-targets/{id}/reject`
- `POST /api/connection-targets/{id}/revision`
- `POST /api/connection-targets/{id}/disable`
- `POST /api/connection-targets/{id}/archive`
- `GET /api/connection-targets/{id}/versions`
- `GET/POST /api/connection-targets/{id}/checks`
- `GET /api/connection-checks/{id}`
- `GET/POST /api/connection-targets/{id}/credential-profiles`
- `PATCH /api/credential-profiles/{id}`

Mutations require CSRF. TESTER or ADMIN can create and submit target proposals. APPROVER or ADMIN can approve/reject submitted targets, with creator self-approval blocked. ADMIN can disable and archive targets. APPROVER or ADMIN can run restricted checks only against approved enabled targets.

Connection checks accept only `HEAD` or `GET` for approved probe paths. The API stores sanitized metadata only: status, HTTP status, safe headers, TLS summary, latency, redirect outcome, and safe error category. It does not store response bodies, cookies, `Set-Cookie`, authorization headers, CSRF values, raw certificates, or secrets. Credential-profile APIs store metadata only and reject extra secret fields.

## Stage 10 Automated Execution

- `POST /api/connection-targets/{id}/execution-submit`
- `POST /api/connection-targets/{id}/execution-approve`
- `POST /api/connection-targets/{id}/execution-disable`
- `GET /api/automated-runs`, `POST /api/automated-runs`, `GET /api/automated-runs/{id}`
- `POST /api/automated-runs/{id}/submit`, `/approve`, `/queue`, `/cancel`, `/retry`
- `GET /api/automated-runs/{id}/cases`, `/steps`, `/events`, `/artifacts`
- `GET /api/execution-workers`, `POST /api/execution-workers/heartbeat`, `POST /api/execution-workers/run-next`
- `GET /api/execution-artifacts/{artifact_id}/download`

All mutations require CSRF. TESTER/ADMIN can create and submit runs; APPROVER/ADMIN approve, queue, retry, and operate the local worker. Creator self-approval is blocked. Automated runs require execution-enabled non-production targets and approved frozen test-case versions. The worker stores sanitized events, results, and artifacts only.

## Stage 11 Acceptance APIs

- `GET /api/automated-runs/readiness`
- `GET /api/automated-runs/{id}/preflight`

Readiness reports the active ADMIN prerequisite, real-target authorization state, DNS pinning state, runtime-secret warning, and allowed/blocked risk levels. It never supplies a real target URL or credential.

Preflight verifies target approval, separate execution approval, non-production classification, frozen target and case versions, structured actions, worker heartbeat, timeout/concurrency limits, DNS pinning, and runtime-secret safety before queueing. Queueing fails unless Stage 11 preflight passes. Only `READ_ONLY` and `SAFE_INTERACTION` risk levels are accepted.

## Stage 12 Defect APIs

- `GET/POST /api/defects`
- `GET/PATCH /api/defects/{id}`
- `POST /api/defects/from-run`
- `POST /api/defects/{id}/triage`, `/assign`, `/start`, `/fix`, `/ready-for-retest`, `/reopen`, `/close`, `/reject`, `/duplicate`
- `GET/POST /api/defects/{id}/comments`
- `GET /api/defects/{id}/history`
- `GET /api/defects/{id}/evidence`
- `POST /api/defects/{id}/retest`
- `GET /api/defects/{id}/traceability`
- `GET /api/traceability/test-cases/{case_id}`
- `GET /api/traceability/runs/{run_id}?run_type=manual|automated`

All mutations require CSRF. TESTER/ADMIN can create defects and record retests. APPROVER/ADMIN can triage, assign, mark fixed/ready, reject, duplicate, and close defects. Source creation supports failed/blocked manual results and failed/timed-out/blocked automated results with duplicate warning before confirmed creation. Responses expose sanitized metadata only and never include passwords, tokens, cookies, CSRF values, authorization headers, response bodies, or absolute local paths.

## Stage 13 Report APIs

- `GET /api/reports/dashboard`, `/executions`, `/defects`, `/trends`, `/quality`, `/traceability`, `/targets`, `/workers`
- `POST /api/reports/export`, `GET /api/reports/exports`, `GET /api/reports/exports/{id}/download`
- `GET/POST /api/report-definitions`, `PATCH /api/report-definitions/{id}`, `POST /api/report-definitions/{id}/run`, `/disable`

Report reads require authentication. Export and saved-definition mutations are ADMIN-only and CSRF-protected. Exports are local, bounded, formula-safe, checksummed, and path-contained.

## Stage 14 System APIs

- `GET /health` and `GET /api/health` provide sanitized public process readiness.
- `GET /api/system/health` provides authenticated database, migration, storage, worker, queue, frontend, disk, and Chromium state.
- `GET/POST /api/system/backups` lists validated backups or creates one after ADMIN CSRF and exact confirmation.
- `GET /api/system/cleanup-preview` performs an ADMIN-only dry-run.
- `POST /api/system/cleanup` requires ADMIN CSRF and exact confirmation.

System responses expose booleans, counts, safe categories, generated backup IDs, and checksums only. They do not expose environment values, credentials, hashes, cookies, request headers, stack traces, or absolute paths. Restore is intentionally offline and interactive through `scripts/restore_local.ps1`.
