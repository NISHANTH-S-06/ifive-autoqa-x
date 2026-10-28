# System Technical Baseline Specifications (Version 1.0)

**Platform**: iFive AutoQA X Enterprise Platform  
**Target Baseline**: Version 1.0 GA  
**Date**: 2026-08-03  

---

## 1. Directory Structure Baseline

```text
d:\AUTO_QA_TESTING
├── backend/                  # FastAPI 0.139 Core Service
│   ├── app/                  # 93 App Submodules
│   │   ├── ai/               # 40 AI Agent & Copilot Modules
│   │   ├── api/              # 47 REST Router Modules
│   │   ├── models/           # 34 SQLAlchemy ORM Model Files
│   │   ├── schemas/          # 14 Pydantic DTO Schema Files
│   │   └── services/         # 87 Business & Execution Services
│   ├── alembic/              # 21 Migration Scripts
│   └── tests/                # 38 Integration & Unit Test Files (192 Tests)
├── frontend/                 # React 18 + Vite Web Portal
│   └── src/
│       ├── pages/            # 40 Module Page Components
│       ├── components/       # 59 UI Components
│       ├── services/         # 16 API & Auth Services
│       └── styles/           # index.css Vanilla Design Tokens
├── qa/                       # Playwright Browser Automation Suite (11 .mjs scripts)
├── demo-product/             # Isolated Sample Enterprise ERP (Backend 8002, UI 5175)
├── mock-task-portal/         # Isolated Mock Task Portal (Backend 8001, UI 5174)
└── docs/
    ├── v1.0/                 # Frozen Version 1.0 Archive (60 Specifications)
    └── v2/                   # Version 2.0 AI Engineering Platform Architecture
```

---

## 2. Database Schema & ORM Model Inventory

- **Total Database Tables**: 147 Tables
- **Key Tables**:
  - `operators`, `operator_sessions`, `password_history` (Authentication & Security)
  - `projects`, `project_members` (Multi-tenant Project Isolation)
  - `company_tasks`, `external_task_imports` (Enterprise Delivery & ERP Tasks)
  - `automated_runs`, `automated_run_cases`, `automated_step_results` (Playwright Execution Engine)
  - `connection_targets`, `target_policy_versions` (Connection Targets & Approval Queue)
  - `defects`, `defect_ai_analyses` (Defect Tracking & AI Copilot Analysis)
  - `visual_baselines`, `visual_comparisons` (Phase 6 Visual Regression Engine)
  - `knowledge_nodes`, `knowledge_edges` (AI Knowledge Graph)

---

## 3. Security & Access Control Baseline

- **Password Cryptography**: PBKDF2 with SHA-256 password hashing.
- **Session Tokens**: Cryptographic session tokens stored in `autoqa_session` HTTP-only cookies.
- **CSRF Guards**: `X-CSRF-Token` header verification on all mutating endpoints (`POST`, `PATCH`, `DELETE`).
- **RBAC Roles**: 6 Granular roles (`ADMIN`, `DEVELOPER`, `TESTER`, `APPROVER`, `PROJECT_MANAGER`, `VIEWER`).
- **SSRF Defense**: `PinnedTargetSession` with metadata IP blocking (`169.254.169.254`) and DNS pinning.

---

## 4. Verification Verdict

**System Baseline Verdict**: 🟢 **VERIFIED & STORED** — Technical specifications recorded cleanly in `SYSTEM_BASELINE.md`.
