# iFive AutoQA X — Handoff Prompt (continue in Antigravity)

## Project Root

`D:\AUTO_QA_TESTING`

Work only inside this directory. Never modify files outside it. Never access real company systems, real credentials, production databases, or real customer/employee data. This is a local proof-of-concept only.

## Role

Act as a senior software architect, QA automation engineer, security reviewer, backend engineer, frontend engineer, and Playwright specialist.

Core rules:

- Audit before changing code. Reuse working modules. Make minimal, safe changes.
- Never claim a test/build/migration passed without pasting the actual command and its actual output.
- Never hardcode PASS, fake evidence, or treat a no-op as success.
- Alembic is the only migration authority — never use `Base.metadata.create_all()` in app startup or anywhere else.
- Every DB query must be project-scoped. DB validation is read-only unless explicitly a disposable local fixture.
- Never add authentication backdoors (magic tokens, optional-auth-skips-RBAC patterns, caller-supplied identity fields treated as trusted actor).
- AI (yourself) may analyze/suggest/draft, but must never execute tests, approve plans, or decide PASS/FAIL/BLOCKED — those are deterministic/human-gated.
- Approved test-plan versions are immutable; editing creates a new DRAFT version.
- Playwright: reuse the existing local QA Playwright install at `D:\AUTO_QA_TESTING\qa`. Do not create a second browser engine. Shared-state suites run serially (`--workers=1`).

## Local Services (verify health before trusting any test result)

| Service | Port | Health check |
| --- | --- | --- |
| AutoQA backend | 8000 | `GET /api/health` |
| Mock Task Portal backend | 8001 | `GET /api/health` |
| Demo Product backend | 8002 | `GET /api/health` |
| Mock Task Portal frontend | 5174 | `GET /` |
| Demo Product frontend | 5175 | `GET /` |

**Known gotcha**: the two Vite frontends (5174, 5175) silently die during long sessions. Always re-check health before running Playwright suites; restart with:

```powershell
Start-Process -FilePath "npm.cmd" -ArgumentList "run dev -- --port 5174 --host 127.0.0.1 --strictPort" -WorkingDirectory "D:\AUTO_QA_TESTING\mock-task-portal\frontend" -WindowStyle Hidden
Start-Process -FilePath "npm.cmd" -ArgumentList "run dev -- --port 5175 --host 127.0.0.1 --strictPort" -WorkingDirectory "D:\AUTO_QA_TESTING\demo-product\frontend" -WindowStyle Hidden
```

Backend (8000):

```powershell
Start-Process -FilePath "D:\AUTO_QA_TESTING\backend\.venv\Scripts\python.exe" -ArgumentList "-m uvicorn app.main:app --host 127.0.0.1 --port 8000" -WorkingDirectory "D:\AUTO_QA_TESTING\backend" -WindowStyle Hidden -RedirectStandardOutput "D:\AUTO_QA_TESTING\backend_8000.log" -RedirectStandardError "D:\AUTO_QA_TESTING\backend_8000.err.log"
```

Mock Task Portal backend (8001) / Demo Product backend (8002): same pattern from `mock-task-portal\backend` and `demo-product\backend`, ports 8001/8002.

**Tool-runner gotcha**: long-running / server-launch commands may report "Command execution timed out" from the shell tool even though the process actually started successfully in the background. Don't treat that error as failure — always re-verify with an actual health check afterward instead of assuming success or failure.

## Canonical Database — READ THIS CAREFULLY

- **Canonical runtime DB**: `D:\AUTO_QA_TESTING\backend\data\autoqa.db`
- `backend/app/config.py`'s `database_path` property resolves the default relative `sqlite:///./data/autoqa.db` against `BACKEND_ROOT`, **not** CWD. So the true DB is always `backend/data/autoqa.db` regardless of what directory you run commands from, unless `DATABASE_URL` env var is explicitly overridden.
- **Do NOT treat `D:\AUTO_QA_TESTING\data\autoqa.db` (project root) as canonical** — it is a separate, stale, unrelated file. Do not migrate or write to it.
- `AUTOQA_ALEMBIC_DATABASE_URL` env var is **not read by the app** (dead/unused name) — don't rely on it. Use `DATABASE_URL` if you ever need an override.
- Alembic head is currently `20260725_05` (corrective migration `backend/alembic/versions/20260725_05_phase6_corrective_fix.py`, which fixed 28 `server_default` metadata-drift columns and restored 4 missing defect-immutability triggers: `defect_comments_no_delete`, `defect_evidence_links_no_delete`, `defect_history_no_delete`, `defect_retests_no_delete`).
- Last verified state: metadata drift 0, 61 tables, 16 triggers, 5 operators, 5 projects (data preserved through all fixes).
- Before any future schema change: back up `backend/data/autoqa.db` (copy + SHA-256 hash) first. Never hand-edit SQLite schema — always go through a new Alembic revision. Always verify clean migration + second-run idempotency + live-DB drift = 0 afterward.

## Security Fixes Already Applied This Session (do not reintroduce these)

1. **Removed a hardcoded auth backdoor** from `backend/app/auth.py`: a magic `token == 'admin_token'` cookie that bypassed all real session/password validation when `app_env` was `local`/`test`. Confirmed it was live and reachable. Removed entirely; `get_optional_auth_context` (the legitimate optional-auth helper) was left intact.
2. **Converted `backend/app/api/task_imports.py` to mandatory authentication** for: `list_task_imports`, `get_task_import`, `prepare_plan`, `analyze_task_import`, `get_plans_for_import`, `approve_plan`, `run_task_import`, `retry_callback`, `get_task_import_status`. All now use `get_auth_context` (mandatory), `_check_import_access` always enforces RBAC via `ProjectAccessService.require(...)` (no more `if context is not None` skip). `reset-for-testing` now requires mandatory ADMIN auth (still app_env-gated to local/test). `approve_plan`'s spoofable `operator_username` query param was **removed entirely** — actor identity is derived only from `context.operator.username`.
3. **Left `sync_task_imports` as-is** (already had `Depends(require_csrf)` mandatory auth+CSRF when inspected — turned out to already be correctly protected, this was a false alarm from an earlier stale read).
4. Updated `qa/tests/phase3-task-connector.spec.ts` to use the file's existing real `beforeEach` login (`autoqaCsrfToken` via real `/api/auth/login`) for all the now-mandatory-auth calls (`prepare-plan`, `approve`, `run` x3, `callback/retry`). Updated `qa/tests/phase5-real-acceptance.spec.ts` similarly for its Test 11 (now uses the already-real `adminContext.request` instead of a fake cookie).
5. **Fixed a real, unrelated pre-existing bug** in `backend/app/services/task_import_service.py`: `first_operator_id` was only assigned inside the `if test_plan:` branch but also used in the `else:` (legacy Phase 3, no-TestPlan) branch — guaranteed `UnboundLocalError` whenever a task has no Phase 5 TestPlan. Fixed by hoisting the assignment above the branch.

## Known Remaining Issues / Flagged-but-not-fixed (need your decision or continued work)

1. **Weak/no-op tests in `qa/tests/phase5-real-acceptance.spec.ts`** (not yet rewritten):
   - Test 11 previously soft-checked `if (runsRes.ok())` (now uses real auth but still needs the assertions strengthened to check exact `test_plan_id`, `approved_version_number`, `test_plan_version_id`, `source_revision`, `project_id`, `plan_hash`, `immutable_snapshot_hash`, and that draft edits don't mutate an existing run's frozen metadata).
   - Test 12 is a literal `expect(true).toBe(true)` no-op — needs real negative-input tests against the AI/plan-generation boundary (malformed JSON, external URL, `<script>`, `javascript:`, `eval(`, shell/Python injection strings, raw secrets, prompt-injection attempts, AI-instructed PASS/FAIL — all must be rejected with 4xx, no plan/version/run created, audit event recorded without storing the secret).
2. **Phase 3.1 Test 02 ("FAIL full flow")** hit `Test timeout of 60000ms exceeded` on last run. Not yet root-caused — could be a legitimately-too-tight timeout for cold Playwright-subprocess launches in this environment, or a real perf regression. Check `qa/playwright.config.ts` timeout settings before changing anything.
3. **Tracked-file audit incomplete** — still need line-by-line review of: `backend/app/services/automated_execution.py` (539-line diff, not yet reviewed), `backend/app/api/system.py` (partially reviewed), `backend/app/models/project.py` (reviewed, fine), `backend/app/services/target_policy.py` (reviewed, fine), `qa/playwright.config.ts`, `frontend/src/App.tsx`, `QuickStart.ps1` (only starts main backend/frontend/worker — does NOT start Mock Task Portal or Demo Product; start those separately).
4. **`playwright` Python package is not installed and not in `backend/requirements.txt`** — harmless/unused because real execution goes through a Node.js runner (`qa/automated-execution-runner.mjs`) via subprocess, using the already-installed `qa/node_modules` Playwright. Not a bug. There IS a second, older/legacy runner (`backend/app/services/playwright_runner.py`, used by `backend/app/api/test_runs.py`) that also shells out to the npm Playwright CLI — clarify which one Phase 6 should build on; don't create a third.

## Verified-Good State (as of last check this session)

- `git diff --check` -> exit 0 (clean, no whitespace errors)
- Full backend pytest: **128 passed, 0 failed**, 3257 warnings, ~169s (`cd backend && python -m pytest -q`) — this was BEFORE the `task_import_service.py` UnboundLocalError fix and the task_imports.py auth conversion; must be re-run and reconfirmed before trusting it
- `python -m compileall -q app tests` -> exit 0
- `alembic current` / `alembic heads` -> single head, `20260725_05`
- Clean migration + second-run idempotency -> both exit 0, live DB drift 0, fresh DB drift 0
- Phase 3.1 Test 01 ("PASS full flow") -> genuinely passed for real (real Chromium, real Node Playwright runner, real employee creation) after the frontend-restart + UnboundLocalError fixes
- Phase 3.1 Tests 02-06 -> not yet completed (blocked by Test 02 timeout, serial mode)
- Phase 5.2, Mock Task Portal suite, Demo Product suite, frontend builds, Phase 6 A-J functional audit, Phase 6 Playwright acceptance, documentation updates -> not yet done this session

## Exact Next Steps, In Order

1. Verify all 5 services healthy (restart frontends if dead — see gotcha above).
2. Re-run full backend pytest (background + log-poll pattern — direct synchronous calls can exceed the tool's response window on this ~3min suite; write to a log file and poll it).
3. Root-cause the Phase 3.1 Test 02 timeout; fix minimally; re-run Phase 3.1 fully (`cd qa && npx playwright test tests/phase3-task-connector.spec.ts --project=chromium --workers=1`) until all 6 tests genuinely pass.
4. Run Phase 5.2 (`qa/tests/phase5-real-acceptance.spec.ts`) — first rewrite Test 11 and Test 12 as described above (no soft-pass, no no-op), then run for real.
5. Finish the tracked-file audit on the 5 remaining files listed above; classify each as VERIFIED_REQUIRED / VERIFIED_FIX / PARTIAL / SUSPICIOUS / UNRELATED / NEEDS_REPAIR.
6. Run remaining baseline suites: main frontend TypeScript check + production build; Mock Task Portal backend pytest + frontend build + Playwright E2E; Demo Product backend pytest + frontend build + Playwright E2E; `git diff --check`.
7. Only after 1-6 are all genuinely green: continue the Phase 6 functional audit (API validation, read-only DB validation, accessibility, performance, console/network, evidence completeness, unified result aggregator, defect grouping, HTML/PDF reporting, local scheduling) against the existing (already-scaffolded, untracked) `backend/app/validation/`, `backend/app/reporting/`, `backend/app/scheduling/` modules — reuse/repair, do not rebuild from scratch.
8. Run `backend/tests/test_phase6_advanced_validation.py`, `qa/tests/phase6-advanced-validation.spec.ts`, `scripts/run_phase6_acceptance.ps1`.
9. Update documentation: `docs/PHASE_6_ADVANCED_QA_VALIDATION_PACK.md`, `docs/PHASE_6A_API_DB_VALIDATION.md`, `docs/PHASE_6B_ACCESSIBILITY_PERFORMANCE.md`, `docs/PHASE_6C_REPORTING_SCHEDULING.md`, `docs/PHASE_6_ACCEPTANCE_REPORT.md`, `docs/FULL_SCOPE_STATUS.md`, `README.md`, `ARCHITECTURE.md`, `TEST_STRATEGY.md`, `SAFETY_RULES.md` — document the canonical-DB clarification, the security fixes, the corrective migration, and exact test counts/commands. Use status labels: VERIFIED_COMPLETE / IMPLEMENTED_PARTIAL / SCAFFOLDED_ONLY / NOT_IMPLEMENTED / BLOCKED_BY_ENVIRONMENT / BLOCKED_BY_AUTHORIZATION. Never describe this local PoC as production-deployment-ready.

## Response Format to Follow

For every substantive response: Audit Findings -> Root Cause -> Existing Modules Reused -> Files Created -> Files Modified -> Architecture/Flow -> APIs Added/Changed -> Database/Migration Changes -> Security Controls Preserved -> Tests Added -> Commands Executed -> Exact Test Results (passed/failed/skipped/retries/warnings/duration) -> Acceptance Matrix (VERIFIED/PARTIAL/NOT VERIFIED/BLOCKED BY ENVIRONMENT/BLOCKED BY AUTHORIZATION) -> Remaining Limitations -> Exact Next Step.

Do not begin work beyond what's explicitly requested in a given turn. Every completion claim must be backed by an actual file path, function name, API route, test name, command, hash, or artifact — never assert something passed without pasting real output.
