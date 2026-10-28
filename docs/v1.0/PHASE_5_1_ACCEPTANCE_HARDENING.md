# Phase 5.1 — Test Plan Acceptance Hardening

## Overview

Phase 5.1 focuses on strict acceptance hardening of the AI Test Plan Generator and Human Approval Workflow. This ensures absolute project isolation, execution integrity, safe AI generation, and unbypassable human gates.

## Implemented Hardening Measures

### 1. Database Model & Schema Fixes

- Added `approved_version_number` (Integer, nullable) to `TestPlan` to freeze the exact version that was approved.
- Executed Alembic migration: `027d78334b2d_add_approved_version_number`.
- Fixed Pydantic V2 deprecation warnings in `backend/app/schemas/test_plan.py` (`ConfigDict` over `class Config`).

### 2. Plan Generation & AI Boundaries

- **Unsafe Output Rejection**: Added strict validation in `generate_plan_for_task` to instantly reject AI payloads containing JavaScript, shell execution commands, external URLs, raw passwords/secrets, or raw PASS/FAIL decisions.
- **Local Provider Constraints**: Ensured deterministic mock generates full Primary, Negative, and optional Regression scenarios for `EMPLOYEE_CREATE` and `STOCK_COUNT`.
- **Missing Info Gate**: Strict conditional check implemented. If missing Acceptance Criteria, target route, expected result, or required role, the task enters `NEED_CLARITY` state and blocks execution.

### 3. Approval Hardening

- **Developer Self-Approval Block**: The operator who generated the test plan or owns the source task is strictly blocked from approving it (HTTP 403).
- **Mandatory Rejection Reason**: Rejections must supply a non-empty string reason.
- **Freeze Exact Approved Version**: Once approved, `plan.approved_version_number` is permanently set to `plan.current_version`.

### 4. Exact Version Execution

- `automated_execution.py` strictly fetches the exact `TestPlanVersion` mapped to `approved_version_number`. Even if a user patches a draft and bumps `current_version`, executions will always run the approved snapshot.
- Blocked mutating/destructive operations and enforced full scenario linkage.

## Validation Results

- **Pytest Full Regression**: All backend rules verified comprehensively via `test_test_plan_workflow.py`. Includes unit-level tests for:
  - Missing information blocks.
  - Mandatory scenario checks (HTTP 400).
  - Secrets storage blocks (HTTP 400).
  - Self-approval blocks (HTTP 403).
  - Proper state transitioning (`DRAFT` → `IN_REVIEW` → `REJECTED` / `APPROVED`).
- **Playwright Test Updates**: Updated `qa/tests/phase5-test-plans.spec.ts` to exercise these paths safely.
- **Frontend Validation**: Built cleanly.

## Conclusion

Phase 5.1 is complete. The exact-version execution guarantee prevents drift, and AI safety boundaries prevent runaway deterministic testing.
