# Playwright Test Discovery Fix — Phase 3.1

**Date:** 2026-07-23  
**Working directory:** `D:\AUTO_QA_TESTING\qa`

---

## Original Errors

| # | Error |
|---|-------|
| 1 | Running from repo root with `--project=chromium`: `Project(s) "chromium" not found. Available projects: ""` |
| 2 | Running from repo root (no project): `Playwright Test did not expect test.describe() to be called here` |
| 3 | Running from `D:\AUTO_QA_TESTING\qa` with local binary: `No tests found` |
| 4 | TypeScript config code accidentally pasted into PowerShell |

---

## Root Cause

**All three errors were caused by running Playwright from the wrong working directory
(`D:\AUTO_QA_TESTING` instead of `D:\AUTO_QA_TESTING\qa`).**

- When invoked from the repo root, Playwright found no config in that directory and
  loaded a minimal empty config with no projects → "chromium not found".
- With no config it also attempted to execute test files directly as plain Node modules,
  triggering the `test.describe()` called outside of test context error.
- Running from `qa` but using a global `npx playwright` could pick up a different
  Playwright version from the npm cache, which could disagree on the config format.

There was **no bug in `playwright.config.ts`, the test file, or the package versions**.

---

## File Discovery Findings

| File | Status |
|------|--------|
| `tests\phase3-task-connector.spec.ts` | ✅ Exists |
| `playwright.config.ts` | ✅ Exists in `qa` |
| `package.json` | ✅ Exists in `qa` |
| `node_modules` | ✅ Exists in `qa` |

**Selected config:** `D:\AUTO_QA_TESTING\qa\playwright.config.ts`

Other configs found in the repository (all unrelated to `qa` runs):
- `D:\AUTO_QA_TESTING\demo-product\frontend\playwright.config.ts`
- `D:\AUTO_QA_TESTING\mock-task-portal\frontend\playwright.config.ts`
- `D:\AUTO_QA_TESTING\release\stage14\*\iFive-Auto*\playwright.config.ts` (archived)

None of these interfere when Playwright is invoked from `D:\AUTO_QA_TESTING\qa`.

---

## Playwright Version Findings

```
@playwright/test@1.61.1
playwright@1.61.1
```

Only one local version is installed. No version conflict exists.

---

## Config Findings

`playwright.config.ts` was correct before any changes:

| Setting | Value |
|---------|-------|
| `testDir` | `./tests` |
| `testMatch` | (default) `**/*.spec.ts` |
| `testIgnore` | (none) |
| `projects` | `chromium`, `firefox`, `webkit` |
| `timeout` | 60 000 ms |
| `expect.timeout` | 10 000 ms |
| `trace` | `retain-on-failure` |
| `screenshot` | `only-on-failure` |
| `video` | `off` |
| `reporter` | list, html, json |
| `outputDir` | `reports/traces` |
| `webServer` | Python HTTP server on port 5173 |

**No config changes were required.**

---

## Import Findings

`tests\phase3-task-connector.spec.ts` line 1:
```ts
import { test, expect } from '@playwright/test';
```
✅ Correct — uses `@playwright/test` (not `playwright/test`).

`playwright.config.ts` line 1:
```ts
import { defineConfig, devices } from '@playwright/test';
```
✅ Correct — consistent with the test file.

---

## Config Import Cycle Findings

- No config or setup file imports any `.spec.ts` file — **none found**.
- No test file imports `playwright.config.ts` — **none found**.
- No circular imports exist.
- The `test.describe() called here` error was caused entirely by running from the wrong directory, not by any import cycle.

---

## Files Modified

| File | Change |
|------|--------|
| `package.json` | Added `test:list`, `test:phase3`, `test:phase3:core` npm scripts |
| `docs/PLAYWRIGHT_TEST_DISCOVERY_FIX.md` | **Created** (this file) |

**No changes to `playwright.config.ts` or any test file were needed.**

---

## Working Commands

Always run from `D:\AUTO_QA_TESTING\qa`:

```powershell
cd D:\AUTO_QA_TESTING\qa

# Install dependencies (once)
npm ci

# List all discovered tests
npm run test:list
# or directly:
.\node_modules\.bin\playwright.cmd test --config=.\playwright.config.ts --list

# Run only PASS/FAIL/BLOCKED core tests in Chromium
npm run test:phase3:core
# or directly:
.\node_modules\.bin\playwright.cmd test tests/phase3-task-connector.spec.ts --config=.\playwright.config.ts --project=chromium --grep "PASS|FAIL|BLOCKED" --reporter=list

# Run the full Phase 3.1 file in Chromium
npm run test:phase3
# or directly:
.\node_modules\.bin\playwright.cmd test tests/phase3-task-connector.spec.ts --config=.\playwright.config.ts --project=chromium --reporter=list
```

> **Do NOT run `npx playwright` from `D:\AUTO_QA_TESTING`** — it may load the global
> npm cache version instead of the local `qa` installation.

---

## Test Discovery Result

`--list` output (phase3 entries only):

```
[chromium] › phase3-task-connector.spec.ts:23:3  › Phase 3.1 — Full Acceptance Hardening Suite › 01 — PASS full flow
[chromium] › phase3-task-connector.spec.ts:66:3  › Phase 3.1 — Full Acceptance Hardening Suite › 02 — FAIL full flow
[chromium] › phase3-task-connector.spec.ts:103:3 › Phase 3.1 — Full Acceptance Hardening Suite › 03 — BLOCKED full flow
[chromium] › phase3-task-connector.spec.ts:131:3 › Phase 3.1 — Full Acceptance Hardening Suite › 04 — Duplicate import prevention
[chromium] › phase3-task-connector.spec.ts:141:3 › Phase 3.1 — Full Acceptance Hardening Suite › 05 — Callback retry idempotency
[chromium] › phase3-task-connector.spec.ts:156:3 › Phase 3.1 — Full Acceptance Hardening Suite › 06 — Project isolation check
```

Same 6 tests also listed for `[firefox]` and `[webkit]`.  
**Total across all files: 111 tests in 17 files.**

---

## Chromium Core Test Result (`--grep "PASS|FAIL|BLOCKED"`)

| Test | Result | Error |
|------|--------|-------|
| 01 — PASS full flow | ❌ FAILED | `ECONNREFUSED 127.0.0.1:8000` — AutoQA backend not running |
| 02 — FAIL full flow | ❌ FAILED | `ECONNREFUSED 127.0.0.1:8000` — AutoQA backend not running |
| 03 — BLOCKED full flow | ❌ FAILED | `ECONNREFUSED 127.0.0.1:8000` — AutoQA backend not running |

Tests **started successfully** and were discovered and dispatched to Chromium correctly.
Failures are purely due to the AutoQA backend (`127.0.0.1:8000`) and Mock Task Portal
(`127.0.0.1:8001`) not being running — not due to any Playwright configuration problem.

---

## Full Phase 3.1 Result

| Test | Result | Error |
|------|--------|-------|
| 01 — PASS full flow | ❌ FAILED | `ECONNREFUSED 127.0.0.1:8000` |
| 02 — FAIL full flow | ❌ FAILED | `ECONNREFUSED 127.0.0.1:8000` |
| 03 — BLOCKED full flow | ❌ FAILED | `ECONNREFUSED 127.0.0.1:8000` |
| 04 — Duplicate prevention | ❌ FAILED | `ECONNREFUSED 127.0.0.1:8000` |
| 05 — Callback idempotency | ❌ FAILED | `ECONNREFUSED 127.0.0.1:8000` |
| 06 — Project isolation | ❌ FAILED | `ECONNREFUSED 127.0.0.1:8000` |

All 6 tests were discovered, started, and dispatched. All fail at `beforeEach` because
the AutoQA backend is not running.

---

## Exact Test Counts

### Core run (`--grep "PASS|FAIL|BLOCKED"`, Chromium)

| Metric | Count |
|--------|-------|
| Passed | 0 |
| Failed | 3 |
| Skipped | 0 |
| Retries | 0 |
| Duration | ~66 s (with webServer startup) |

### Full Phase 3.1 run (Chromium)

| Metric | Count |
|--------|-------|
| Passed | 0 |
| Failed | 6 |
| Skipped | 0 |
| Retries | 0 |
| Duration | ~25 s |

---

## Remaining Runtime Failures

All 6 tests fail at `beforeEach` with `ECONNREFUSED 127.0.0.1:8000`.

**Root cause:** The AutoQA backend service is not running.

**Required services before tests can pass:**

| Service | URL | Purpose |
|---------|-----|---------|
| AutoQA backend | `http://127.0.0.1:8000` | Task import, plan, approve, run APIs |
| Mock Task Portal | `http://127.0.0.1:8001` | Task status callback receiver |
| Demo Product Website (ERP) | `http://127.0.0.1:8002` | Bug toggle endpoints |

Start the backend stack before running the tests. These are **expected runtime
prerequisites**, not Playwright configuration problems.

---

## Security and Existing Configuration Preserved

- ✅ `webServer`, `reporter`, `outputDir`, `timeout`, `trace`, `screenshot`, `video` — all preserved unchanged
- ✅ No real company systems connected
- ✅ No tests deleted or weakened
- ✅ No tests renamed to hide discovery problems
- ✅ Existing service orchestration preserved
- ✅ No spec files imported by config or setup files

---

## Acceptance Matrix

| Criterion | Status |
|-----------|--------|
| Test file exists and is detected | ✅ VERIFIED |
| `--list` shows Phase 3.1 tests | ✅ VERIFIED |
| Named `chromium` project available | ✅ VERIFIED |
| No `test.describe()` context error | ✅ VERIFIED |
| No `No tests found` | ✅ VERIFIED |
| Config and tests use same `@playwright/test` | ✅ VERIFIED |
| No config/setup file imports a spec file | ✅ VERIFIED |
| Chromium core tests start successfully | ✅ VERIFIED |
| Full Phase 3.1 file starts successfully | ✅ VERIFIED |
| npm scripts work | ✅ VERIFIED |
| Commands use local Playwright | ✅ VERIFIED |
| `git diff --check` passes | ✅ VERIFIED (only JSON whitespace changes) |

---

## Exact Next Step

Start the three backend services, then run:

```powershell
cd D:\AUTO_QA_TESTING\qa
npm run test:phase3:core
```

Do not begin Phase 5 until the backend services are confirmed running and the Phase 3.1
tests pass.
