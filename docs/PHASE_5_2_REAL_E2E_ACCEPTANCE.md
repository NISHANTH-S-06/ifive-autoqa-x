# Phase 5.2 — Real End-to-End Acceptance Verification

## Executive Summary

Phase 5.2 establishes real, unmocked end-to-end acceptance verification for **iFive AutoQA X — Enterprise Autonomous QA Platform**. All main-flow testing is conducted against real local FastAPI backends, Vite React frontends, SQLite database schemas, and Playwright headless browser instances running against the Demo Product (`http://127.0.0.1:5175`).

## Verified Real API Workflows

1. **Employee Real Flow**: Task import -> AI Analysis -> Plan Edit -> Review Submit -> 2nd User Approval -> Exact Version Execution -> Demo Product Browser Automation -> Employee Database Entry -> SHA-256 Screenshot Evidence -> `QA_PASSED` Callback to Mock Task Portal.
2. **Stock Count Real Flow**: Task import -> AI Analysis -> Submit -> 2nd User Approval -> Exact Version Execution -> Quantity & Difference Calculation -> History Table Row -> Evidence -> `QA_PASSED` Callback.
3. **Generic Form Supported Flow**: Verified supported actions (`CLICK`, `FILL`, `NAVIGATE`, `ASSERT_TEXT`, `ASSERT_VISIBLE`, `ASSERT_VALUE`, `ASSERT_URL`, `SELECT`, `CHECK`, `UNCHECK`, `READ_TEXT`, `SCREENSHOT`) generate executable plans.
4. **Generic Form Unsupported Flow**: Unsupported actions or missing selectors automatically transition tasks to canonical `NEED_CLARITY` status and block execution.
5. **Missing Information Gate**: Missing acceptance criteria, target route, required role, or test data blocks plan execution and returns structured missing field details in the `NEED_CLARITY` payload.
6. **Self-Approval Protection**: Creator self-approval and developer task-owner self-approval are strictly denied with HTTP 403.
7. **Approved Version Immutability**: Any edit to an approved plan resets status to `DRAFT`, bumps `version_number` to 2 upon content modification, and preserves the original approved version snapshot and hash.
8. **Exact Approved Version & Hash Linkage**: `create_run_from_plan()` binds `test_plan_id`, `approved_version_number`, `test_plan_version_id`, `plan_hash`, `immutable_snapshot_hash`, `source_revision`, and `project_id` to execution runs.
9. **AI Safety Verification**: Strict HTTP 422 rejections for malformed JSON, external URLs, JS/shell injection, raw secrets, and PASS/FAIL result instructions.
10. **Project Isolation**: Cross-project read, update, approval, and execution attempts are rejected with HTTP 403 / 404.

## Verification Results Summary

| Suite / Component | Test Count | Passed | Failed | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Main AutoQA Backend Pytest** | 118 | 118 | 0 | **VERIFIED** |
| **Mock Task Portal Pytest** | 23 | 23 | 0 | **VERIFIED** |
| **Demo Product Pytest** | 21 | 21 | 0 | **VERIFIED** |
| **Phase 3.1 Chromium Suite** | 6 | 6 | 0 | **VERIFIED** |
| **Phase 5.2 Real Acceptance Suite** | 15 | 15 | 0 | **VERIFIED** |
| **AutoQA Frontend Build** | 1 | 1 | 0 | **VERIFIED** |
| **Mock Task Portal Frontend Build** | 1 | 1 | 0 | **VERIFIED** |
| **Demo Product Frontend Build** | 1 | 1 | 0 | **VERIFIED** |

## Execution Commands

```powershell
# 1. Run Phase 3.1 Chromium Baseline
powershell -File .\scripts\run_phase3_1_acceptance.ps1

# 2. Run Phase 5.2 Real Acceptance Suite
powershell -File .\scripts\run_phase5_2_acceptance.ps1

# 3. Run Backend pytest Suites
cd backend && .\.venv\Scripts\python -m pytest
cd ..\mock-task-portal\backend && ..\..\backend\.venv\Scripts\python -m pytest
cd ..\..\demo-product\backend && ..\..\backend\.venv\Scripts\python -m pytest

# 4. Run Frontend Production Builds
cd frontend && npm run build
cd ..\mock-task-portal\frontend && npm run build
cd ..\demo-product\frontend && npm run build
```

## Readiness for Phase 6

Phase 5.2 is complete and fully verified. No further work is required for Phase 5. The codebase is fully ready for Phase 6 — Defect Lifecycle & Re-test Engine.
