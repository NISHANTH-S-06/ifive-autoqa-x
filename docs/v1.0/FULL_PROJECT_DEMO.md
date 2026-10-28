# Full Project Demo

This guide demonstrates the completed Stage 1-14 local release without starting another stage, accessing a real iFive system, enabling production execution, or installing AI runtimes.

## 1. Prerequisites

- Windows PowerShell, Python 3.11 or newer, Node.js 20 or newer, and Chromium.
- Backend dependencies installed in `backend\.venv`, frontend and QA dependencies installed with `npm.cmd ci`, and a current frontend production build.
- Ports 8000 and 5173 free, or occupied only by services recorded in `runtime\pids` as belonging to this project.
- The configured database located beneath `AUTOQA_DATA_ROOT`. The local-release default is `backend\data\autoqa.db`.
- No persistent operator is created automatically. Interactive authenticated UAT requires private, authorized operator creation by a human.

## 2. Start Commands

Run from the extracted project root:

```powershell
.\scripts\run_migrations.ps1
cd frontend
npm.cmd run build
cd ..
.\scripts\start_local_system.ps1
.\scripts\verify_health.ps1
```

The official start script launches the backend, production frontend, and one local worker. It rejects unknown port owners and duplicate project services.

## 3. URLs

- Frontend: `http://127.0.0.1:5173`
- Backend health: `http://127.0.0.1:8000/health`
- API documentation: `http://127.0.0.1:8000/docs`

Do not bind these services to a public interface for this local release.

## 4. Test Fixture and Login Approach

Automated acceptance uses temporary operators, isolated SQLite databases, mocked browser API responses, and LOCAL mock targets. The backend and Playwright suites remove or deactivate their temporary identities and do not store plaintext credentials.

For an interactive authenticated demo, an authorized person may run the following command and enter operator details and passwords privately at the prompts:

```powershell
.\scripts\create_local_operator.ps1
```

Create only the roles required for the approved demo. Use different people or disposable local operators for creator and approver actions. Never place passwords, tokens, cookies, CSRF values, or real target credentials in this guide, a command line, a screenshot, or a saved fixture. If no persistent ADMIN is explicitly created, demonstrate authenticated workflows through the automated fixture suites and mark persistent ADMIN UAT as pending.

## 5. Demo Order and Expected Results

1. Authentication and account security: show safe incorrect-login handling, forced password change, session restoration, logout, session revocation, password policy, and security reporting. Normal navigation remains unavailable until a required password change succeeds.
2. Test Management: create a project, module, suite, case, and ordered steps; submit the case; show creator self-approval rejection; approve with a separate role; and open immutable version history.
3. Manual Runs: create a run from an approved frozen case, start it, record step and case outcomes, attach allowlisted evidence, complete it, and show the frozen history.
4. Connection Targets: use only a LOCAL mock target, complete separate approval, run restricted HEAD and approved-path GET checks, and show sanitized history. Response bodies and sensitive headers must not be retained. Target execution remains disabled until separately approved.
5. Automated Runs: separately approve execution eligibility, freeze approved target and case versions, submit and approve with separate roles, queue the run, and show worker heartbeat, progress, sanitized artifacts, cancellation or timeout handling, and policy rejection of dangerous actions.
6. Defects: create from a failed or blocked fixture result, review duplicate warnings, triage, assign, progress, comment, inspect traceability, record a retest, and close or reopen through allowed transitions.
7. Reports: show management metrics, project/date filters, trends, quality measures, and bounded safe CSV or JSON export. Confirm formula-like values are neutralized and no sensitive data is exported.
8. Final Release Readiness: show health, migration state, worker and queue status, Chromium, backup status, cleanup preview, typed destructive confirmations, and VIEWER/ADMIN boundaries.

Expected result: all isolated automated flows pass. Persistent ADMIN, real non-production target, and authenticated iFive login acceptance remain explicitly pending until separately authorized.

## 6. Automated Demonstration Commands

Run the complete verification from the project root when the official runtime is stopped:

```powershell
.\scripts\run_tests.ps1
```

The Playwright configuration starts its own localhost-only static fixture server. If a separately managed QA static server is already running, set `AUTOQA_SKIP_WEBSERVER=1` only for that controlled test process. Do not point `AUTOQA_QA_BASE_URL` at a real iFive host.

## 7. Responsive and Accessibility Checks

Verify the authenticated dashboard at widths 320, 375, 768, 1024, and 1440 pixels. At each width confirm no page-level horizontal overflow, blank page, redirect loop, infinite loader, overlapping controls, unusable form/table/dialog, or unexpected browser-console error. Confirm keyboard reachability, visible focus, understandable errors, wrapping of long values, clear button labels, and status text that does not rely on color alone.

## 8. Stop Commands

Run from the project root:

```powershell
.\scripts\stop_local_system.ps1
```

The stop script terminates only processes whose PID, executable, start time, and project marker match the recorded service ownership.

## 9. Troubleshooting

- Occupied port: identify the owner. Stop it only when it is confirmed as this project's recorded process; otherwise choose another loopback port.
- Backend unavailable: run migrations, inspect the redacted files in `runtime\logs`, and rerun `scripts\verify_health.ps1`.
- Worker heartbeat missing: run `scripts\start_worker.ps1` and wait for the next heartbeat.
- Chromium unavailable: from `qa`, run `npx.cmd playwright install chromium` with approved network access.
- Playwright UI tests show unrelated 401 errors: stop the official runtime before the isolated suite so its own fixture server can own port 5173, or use the explicitly managed localhost-only QA server with `AUTOQA_SKIP_WEBSERVER=1`.
- Restore: stop backend and worker, validate the backup identifier and checksums, and use `scripts\restore_local.ps1 -BackupId <validated-backup-id>`.

## 10. Manual Pending Prerequisites

- Explicit interactive bootstrap and acceptance of a persistent ADMIN.
- Explicit authorization and approval for a real non-production iFive target.
- A safe ephemeral credential-input mechanism and scope for authenticated iFive login validation.
- Confirmed operating-system permissions for runtime storage, backups, browser installation, and the documented recovery location.

## 11. Safety Boundaries

- No default ADMIN, default username, default password, token, or persistent plaintext credential.
- No guessed or unapproved iFive URL and no production target.
- No production execution, payment, payroll, approval, destructive deletion, scan, or IIoT machine-control action.
- No weakening of authentication, RBAC, CSRF, session controls, creator-approver separation, immutable histories, audit integrity, SSRF filtering, DNS pinning, preflight, or dangerous-action blocking.
- No Ollama installation and no AI-agent execution. AI files remain design material only.
- Use LOCAL mock targets and isolated fixtures unless an authorized person separately completes the documented real non-production prerequisites.
