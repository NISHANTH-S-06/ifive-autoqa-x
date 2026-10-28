# Phase 6 — Advanced QA Validation Pack

> **Status:** `VERIFIED_COMPLETE`  
> **Last Verified:** 2026-07-27  
> **Backend Pytest:** 10 / 10 Passed (`backend/tests/test_phase6_advanced_validation.py`)  
> **Playwright E2E:** 20 / 20 Passed (`qa/tests/phase6-advanced-validation.spec.ts`)  

---

## Executive Overview

The Phase 6 Advanced QA Validation Pack equips iFive AutoQA with multi-layered, production-grade validation capabilities beyond basic Playwright DOM automation. It enables QA engineers to attach multi-tier validation profiles (`AdvancedValidationProfile`) to test plans and automated runs.

### Key Validation Engines

1. **API Validation Engine**: Performs HTTP GET/POST checks against approved target origins, verifying status codes, expected JSON schemas, header templates, and JSONPath assertions.
2. **Read-Only Database Validation Engine**: Executes read-only SQL queries (`SELECT`, `WITH`) against approved local SQLite database connection profiles (`backend/data/autoqa.db`, `demo_product`, `mock_task_portal`) with strict read-only AST safety validation.
3. **Accessibility Validation Engine**: Scans DOM trees against WCAG 2.1 AA rules and severity thresholds (`critical`, `serious`, `moderate`).
4. **Performance Validation Engine**: Compares navigation and timing metrics against warning and failure thresholds.
5. **Unified Result Aggregations & Defect Grouping**: Computes unified status with strict precedence (`BLOCKED > FAIL > PASS_WITH_WARNINGS > PASS`), SHA-256 cryptographic result hashes, and deduplicated defect grouping.
6. **Schedules & Reporting**: Cron-scheduled validation execution and HTML/PDF report generation with SHA-256 signatures.

---

## Canonical Database Clarification

- **Canonical SQLite DB Location**: `backend/data/autoqa.db`
- **Correction**: Resolved connection profile map pointing to `data/autoqa.db` by explicitly mapping `autoqa` to `backend/data/autoqa.db`.

---

## Verification Commands & Proofs

```powershell
# Backend Pytest Verification
cd d:\AUTO_QA_TESTING\backend
.\.venv\Scripts\pytest tests/test_phase6_advanced_validation.py -v

# Playwright E2E Suite Verification
cd d:\AUTO_QA_TESTING\qa
npx playwright test tests/phase6-advanced-validation.spec.ts --project=chromium --workers=1
```
