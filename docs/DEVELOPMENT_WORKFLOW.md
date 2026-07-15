# Development Workflow

1. Confirm the target environment is local, QA, or sandbox.
2. Update requirements, test plans, or product matrix before writing tests.
3. Generate or edit Playwright tests.
4. Run tests locally.
5. Review evidence and defects.
6. Approve or reject AI-generated suggestions.
7. Commit only reviewed code and configuration.

## Approved Local Run Workflow

1. Queue `dashboard-smoke` or `integration-smoke` for `iFive AutoQA Dashboard` in `local`.
2. Review the suite and type `APPROVE LOCAL TEST EXECUTION`.
3. Execute locally. A second run remains approved until the active run completes.
4. Poll every 2.5 seconds until `PASSED`, `FAILED`, or `CANCELLED`.
5. Review counts, safe error summary, HTML/JSON reports, logs, screenshots, and traces.

Runs time out after 900 seconds by default. Stage 4 does not run real iFive products or AI agents.

## Stage 5 Operator Workflow

1. Bootstrap the first ADMIN explicitly.
2. ADMIN creates separate TESTER and APPROVER operators.
3. TESTER signs in and creates the queued run.
4. A different APPROVER enters the exact approval phrase and executes it.
5. Review operator identity fields and the audit chain.
6. Logout revokes the session; no raw token is kept in localStorage.

## Stage 6 Operator Security Workflow

1. Confirm whether an active ADMIN exists; if not, bootstrap one explicitly.
2. ADMIN creates operators with a manually entered temporary password.
3. The operator logs in and can access only the required password-change screen, CSRF, profile, logout, and health endpoints.
4. After password change, the operator can use normal authorized resources.
5. Operators can change passwords and revoke their own sessions.
6. ADMIN can reset another operator password and revoke target sessions with a safe reason.
7. Verify `/api/audit/verify` after password and session workflows.

## Stage 7 Persistent ADMIN Acceptance Workflow

1. If local acceptance requires an ADMIN and none exists, run `scripts\create_local_operator.ps1` from the project root and enter the username, display name, role, and password interactively.
2. Do not save, echo, paste into logs, or commit the bootstrap password.
3. Sign in with the bootstrap account and complete the mandatory password change before using dashboard or ADMIN features.
4. Verify My Sessions, Revoke Other Sessions, Security Summary, Operator Security, password reset, and audit integrity from the UI.
5. Keep real iFive execution, production execution, Ollama, and AI agents disabled for Stage 7.

## Stage 8 Test Management Workflow

1. ADMIN creates a test project, module, and managed manual suite.
2. TESTER or ADMIN creates a draft test case with ordered steps and expected results.
3. The creator submits the case for review.
4. A separate APPROVER or ADMIN approves or rejects the case; creators cannot self-approve.
5. Approved case snapshots become immutable versions.
6. TESTER or ADMIN creates a manual run from approved active cases only.
7. The assigned tester starts the manual run, records step/case results, attaches allowed local evidence, and completes or cancels the run.
8. Exports may be CSV or JSON only and must avoid sensitive fields.

Manual Stage 8 runs do not trigger Playwright execution and do not connect to real iFive product URLs.

## Stage 9 Connection Target Workflow

1. TESTER or ADMIN creates a target draft with LOCAL, DEVELOPMENT, QA, or STAGING environment metadata.
2. The server normalizes the origin and validates URL, host, port, TLS policy, and explicit probe paths.
3. The creator submits the target for review.
4. A separate APPROVER or ADMIN approves or rejects it; creators cannot self-approve.
5. APPROVER or ADMIN runs restricted `HEAD` or approved-path `GET` checks against approved enabled targets only.
6. Review sanitized health, headers, TLS summary, redirect outcome, latency, and history.
7. Add credential-profile metadata only when needed; never enter a password or token.

## Stage 10 Workflow

1. Submit an approved non-production target for execution approval.
2. Have a separate APPROVER or ADMIN approve execution; the target creator cannot approve it.
3. Create approved test cases with structured JSON automation actions only.
4. Create an automated run from an execution-enabled target and approved cases.
5. Submit, approve, queue, and process the run with the local worker control.
6. Review step results, failure classification, worker heartbeat, and sanitized artifacts.
7. Do not use real iFive URLs, production targets, arbitrary code, shell commands, credentials, cookies, tokens, Ollama, AI agents, or Stage 12 behavior.

Stage 9 does not submit login forms, authenticate to iFive, run Playwright against target URLs, mutate business data, or enable production execution. Real target acceptance requires an explicitly approved non-production target and a persistent authorized ADMIN.

## Stage 11 Acceptance Workflow

1. Confirm whether a persistent active ADMIN and explicitly authorized non-production target exist.
2. If either prerequisite is missing, use LOCAL mock targets only.
3. Verify readiness and preflight before queueing any automated run.
4. Execute only `READ_ONLY` or `SAFE_INTERACTION` approved actions.
5. Review pinned-DNS status, safe artifacts, and audit-chain validity.
6. Keep authenticated real iFive login validation pending until safe ephemeral credential input is explicitly authorized.

## Stage 12 Defect Workflow

1. TESTER or ADMIN creates a defect directly or from an existing failed/blocked manual or automated result.
2. Review duplicate warnings before confirming source-based creation.
3. APPROVER or ADMIN triages, assigns, rejects, marks duplicate, marks fixed/ready, and closes defects.
4. TESTER or ADMIN records retest results only after the defect is ready for retest.
5. Review traceability from defect to project, suite, case version, source run, evidence/artifact links, retests, and history.
6. Do not enter secrets in defect text, comments, resolutions, or retest notes.
7. Do not bootstrap ADMIN, open real iFive URLs, enable production execution, install Ollama, run AI agents, or start Stage 13.
