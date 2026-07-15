# Team Lead Demo

## Demo Flow

1. Open the AutoQA frontend.
2. Explain local-first execution and safety boundaries.
3. Show the product testing scope.
4. Show the dashboard preview.
5. Walk through Planner, Generator, Healer, and Safety agents.
6. Show Playwright evidence types.
7. Explain that Playwright assertions decide pass or fail.

## Stage 4 Safe Demo

1. Queue `dashboard-smoke` for the local AutoQA dashboard.
2. Show that ERP and other product runs have no execution controls.
3. Enter the exact approval confirmation and show `APPROVED`.
4. Execute locally and show `RUNNING`; explain single-run concurrency and the 900-second timeout.
5. Show persisted final counts and ownership-checked report/log/evidence links.
6. Demonstrate cancellation only with a disposable local run if needed.

Do not demo real iFive execution or AI-agent execution in Stage 4.

## Stage 5 Demo

1. Explain that no default credentials exist and show the explicit bootstrap command without entering a password on screen.
2. Login as TESTER and create `dashboard-smoke`.
3. Show that TESTER cannot approve.
4. Login as a different APPROVER, approve, and execute.
5. Show creator/approver/executor identities and audit events.
6. As ADMIN, verify audit integrity and demonstrate safe operator activation/role controls.

Never display passwords, tokens, cookie values, hashes, or real iFive credentials.

## Stage 6 Demo

1. State that no default credentials exist. If needed, show only the bootstrap command path.
2. As ADMIN, create a temporary operator with a manually entered temporary password without displaying it afterward.
3. Login as that operator and show the required password-change screen blocking normal dashboard access.
4. Change the password and show dashboard access.
5. Show My Sessions, current-session marking, and revoke-other-sessions.
6. As ADMIN, show Security Summary, Operator Security, target session view/revoke, and password reset.
7. Verify audit integrity.

Manual acceptance requiring a real ADMIN is pending until the user explicitly bootstraps one. Do not demo real iFive execution, production execution, paid services, or AI agents.

## Stage 7 Demo

1. State that the bootstrap script is now Stage 6-aware: it rejects duplicate active ADMIN creation, forces first-login password change, writes password history, and records a safe audit event.
2. If an ADMIN is not already active, run the bootstrap script only with private human password entry.
3. Show that mismatched password confirmation is blocked in the browser before submission.
4. Show My Sessions loading/empty/error behavior and the safer revoke-other-sessions confirmation.
5. Show ADMIN Security Summary and Operator Security loading, empty, retry, reset, and revoke behavior.
6. Verify audit integrity.

Do not display passwords, tokens, hashes, CSRF values, cookies, raw credential material, real iFive credentials, or AI-agent secrets.

## Stage 8 Demo

1. Show Test Management navigation and explain that it is manual execution management only.
2. As ADMIN, create a project, module, and manual suite.
3. As TESTER or ADMIN, create a draft case with ordered steps, expected results, priority, type, and tags.
4. Submit the case and show that self-approval is blocked.
5. As a separate APPROVER, approve the case and open version history.
6. Create a manual run from approved cases only, start it, record step/case results, attach allowed evidence, and complete the run.
7. Show CSV/JSON export behavior and audit verification.

Do not run browser automation, real iFive products, production targets, Ollama, or AI agents in the Stage 8 demo.

## Stage 9 Demo

1. Show Connection Targets navigation and explain that Stage 9 approves target metadata only.
2. Create a LOCAL mock target draft with explicit probe paths.
3. Submit the target and show that the creator cannot approve it.
4. As a separate APPROVER, approve the target and open version history.
5. Run safe `HEAD` and approved-path `GET` checks.
6. Show sanitized status, HTTP code, duration, safe headers, redirect blocking, and history.
7. Create credential-profile metadata and point out that there is no password or token field.

Do not demo real iFive URLs, login attempts, production targets, business-data mutation, Ollama, AI agents, or Stage 12 execution.

## Stage 10 Demo

1. Show that an approved target still says execution disabled until separate execution approval is completed.
2. Submit execution approval as the target creator, then approve with a separate APPROVER or ADMIN.
3. Create an automated run with an execution-enabled local mock target and approved structured test case.
4. Submit, approve, queue, run the local worker, and show progress, step results, failure classification, worker heartbeat, and sanitized artifacts.
5. State that real iFive URLs, production targets, credentials, browser storage state, arbitrary code, scans, Ollama, AI agents, and Stage 12 execution are not part of this demo.

## Stage 11 Demo

1. Show Stage 11 readiness and explain why persistent ADMIN and real non-production target acceptance remain pending.
2. Use a LOCAL mock target only.
3. Show DNS pinning, preflight, worker heartbeat requirement, approved target/version checks, and runtime-secret safety status.
4. Execute a READ_ONLY or SAFE_INTERACTION controlled acceptance run and show sanitized evidence.
5. State that real authenticated iFive login remains pending until safe ephemeral credential input and explicit authorization are provided.

## Stage 12 Demo

1. Show Defects navigation and explain source traceability.
2. Create a defect from a failed local automated or manual result and review duplicate warning behavior.
3. Open the defect and show source run, frozen case version, target version, evidence/artifact links, history, and traceability.
4. Use separate roles to triage, assign, start, mark fixed, ready for retest, record retest, and close with a resolution.
5. Show that comments/history/retests are append-only and secret-like text is rejected.
6. State that Stage 12 does not create credentials, access real iFive URLs, run AI agents, or begin Stage 13.

## Key Message

iFive AutoQA improves repeatability, visibility, and defect evidence while keeping AI assistance reviewable and safe.
