# Architecture Inventory — iFive AutoQA Platform

> **Last updated:** 2026-07-29 | **Phase:** 16 (Autonomous Enterprise Software Engineering Intelligence Platform)

---

## 1. System Overview

iFive AutoQA is a **local-first, AI-assisted enterprise QA platform** composed of six cooperating local services.

```
┌─────────────────────────────────────────────────────────────────┐
│                     iFive AutoQA — Local Stack                   │
│                                                                   │
│  ┌──────────────────────┐    ┌──────────────────────────────┐   │
│  │  AutoQA Frontend     │    │  Mock Task Portal Frontend    │   │
│  │  React/Vite          │    │  (Test Harness / Dev Tasks)  │   │
│  │  127.0.0.1:5173      │    │  127.0.0.1:5174              │   │
│  └────────┬─────────────┘    └──────────────┬───────────────┘   │
│           │ /api proxy                        │ /api proxy        │
│           ▼                                   ▼                   │
│  ┌──────────────────────┐    ┌──────────────────────────────┐   │
│  │  AutoQA Backend      │    │  Mock Task Portal API         │   │
│  │  FastAPI/Uvicorn     │    │  FastAPI/Uvicorn              │   │
│  │  127.0.0.1:8000      │    │  127.0.0.1:8001              │   │
│  └────────┬─────────────┘    └──────────────────────────────┘   │
│           │                                                        │
│           ▼                   ┌──────────────────────────────┐   │
│  ┌──────────────────────┐    │  Demo Product Frontend        │   │
│  │  SQLite DB           │    │  (Target Under Test)          │   │
│  │  backend/data/       │    │  127.0.0.1:5175              │   │
│  │  autoqa.db           │    └──────────────┬───────────────┘   │
│  └──────────────────────┘                   │ /api proxy        │
│                              ┌──────────────▼───────────────┐   │
│                              │  Demo Product API             │   │
│                              │  FastAPI/Uvicorn              │   │
│                              │  127.0.0.1:8002              │   │
│                              └──────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Canonical Port Map

| # | Service | Technology | Port | Role |
|---|---------|-----------|------|------|
| 1 | **AutoQA Backend API** | FastAPI + Uvicorn | **8000** | Core platform — auth, projects, test runs, AI agents, all feature APIs |
| 2 | **Mock Task Portal API** | FastAPI + Uvicorn | **8001** | Simulated external task management system (Jira-like) for import testing |
| 3 | **Demo Product API** | FastAPI + Uvicorn | **8002** | Target-under-test product used for connectivity, execution, and visual regression tests |
| 4 | **AutoQA Frontend** | React 18 + Vite + TypeScript | **5173** | Main QA platform UI — all modules, dashboard, reports |
| 5 | **Mock Task Portal UI** | React + Vite | **5174** | Task portal web UI for end-to-end import flow tests |
| 6 | **Demo Product UI** | React + Vite | **5175** | Demo product web UI for visual regression and E2E testing |

---

## 3. Architecture Layers

### Layer 1 — Frontend (React/Vite)
- **Entry:** `frontend/src/main.tsx` → `App.tsx`
- **Routing:** Module-based single-page switching via `ModuleKey` enum in `Sidebar.tsx`
- **State:** `AuthContext`, `ProjectProvider` (Zustand-style stores)
- **API:** All calls through `frontend/src/services/api.ts` using `/api` prefix (proxied to 8000 in dev)
- **Phases covered:** UI modules for Phases 4–16 (90 API-backed modules)

### Layer 2 — Backend API (FastAPI)
- **Entry:** `backend/app/main.py` (lifespan, CORS, middleware, router registration)
- **Routers:** `backend/app/api/` — 90 router files, all registered in `main.py`
- **Auth:** HttpOnly cookie sessions + CSRF double-submit. PBKDF2-HMAC-SHA256 password hashing
- **RBAC:** `AuthContext` dependency guards all non-health endpoints
- **Database:** SQLAlchemy ORM → SQLite (`backend/data/autoqa.db`)

### Layer 3 — Business Logic (Services)
- **Location:** `backend/app/services/` — 86 service files
- **Pattern:** Services are instantiated per-request, receive an SQLAlchemy `Session`
- **Core services:** `automated_execution`, `defect_service`, `visual_regression_engine`, `report_service`, `task_import_service`, `test_plan_service`, `test_management`

### Layer 4 — Data (Models + Repositories)
- **Models:** `backend/app/models/` — 33 files including phase-specific model files (`phase9_models.py` → `phase16_models.py`)
- **Repositories:** `backend/app/repositories/` — isolated database-access classes
- **Migrations:** Alembic (`backend/alembic/`) + `backend/app/migrations.py` + `migration_safety.py`

### Layer 5 — AI Engine
- **Location:** `backend/app/ai/`
- **Components:** `LocalAIProvider`, `AgentRegistry`, `AgentOrchestrator`, `AICopilotEngine`, `KnowledgeGraphService`, `DigitalTwinService`, `PredictiveQualityEngine`
- **No external AI dependencies** — all heuristic/local inference

### Layer 6 — QA Workspace
- **Location:** `qa/` — Playwright test suites
- **Runner:** `scripts/playwright_runner.py` via Chromium
- **Evidence:** Written to `backend/data/stage8_evidence/`
- **Artifacts:** Written to `backend/data/stage10_artifacts/`

---

## 4. Backend Directory Structure

```
backend/
├── app/
│   ├── main.py              ← FastAPI app, all routers registered
│   ├── config.py            ← Settings (frozen dataclass, env-driven)
│   ├── database.py          ← SQLAlchemy engine + session factory
│   ├── auth.py              ← AuthContext dependency, session/CSRF
│   ├── security.py          ← PBKDF2, CSRF helpers
│   ├── logging_config.py    ← Rotating file + console JSON logging
│   ├── seed.py              ← Auto-seeds local projects on startup
│   ├── migration_safety.py  ← Alembic head assertion guard
│   ├── migrations.py        ← Schema migration helpers
│   ├── api/                 ← 90 FastAPI routers (one per feature domain)
│   ├── services/            ← 86 service modules (business logic)
│   ├── models/              ← 33 SQLAlchemy model files
│   ├── repositories/        ← Database access objects
│   ├── schemas/             ← Pydantic request/response schemas
│   ├── ai/                  ← AI engine, agents, heuristics
│   ├── cli/                 ← CLI tools (static server, etc.)
│   ├── connectors/          ← External connectivity (pinned HTTP)
│   ├── reporting/           ← Report generation (HTML/PDF)
│   ├── scheduling/          ← Local cron scheduler
│   └── validation/          ← Advanced validation engine
├── alembic/                 ← Database migration scripts
├── data/                    ← SQLite DB + evidence + artifacts
├── tests/                   ← Backend pytest test suite
├── requirements.txt         ← Python dependencies
├── pytest.ini               ← Pytest config
└── alembic.ini              ← Alembic config
```

---

## 5. Frontend Directory Structure

```
frontend/src/
├── App.tsx                  ← Root: login, session restore, module router switch
├── main.tsx                 ← React 18 createRoot entry
├── authContext.ts           ← AuthContext type + hook
├── pages/                   ← 82 page components (one per sidebar module)
├── components/              ← Shared UI components
│   ├── layout/              ← Sidebar, TopHeader, CommandPalette
│   ├── ui/                  ← Design system: ToastSystem, Badge, etc.
│   ├── common/              ← Shared table, form, card wrappers
│   ├── dashboard/           ← Dashboard-specific widgets
│   └── *.tsx                ← Feature-specific core components
├── layouts/
│   └── AppShell.tsx         ← Main shell: sidebar + top header + page area
├── services/                ← API clients (auth, api, phase*Service files)
├── stores/                  ← Zustand-style state (projectStore, etc.)
├── types/                   ← TypeScript type definitions
└── styles/                  ← Global CSS design tokens
```

---

## 6. Phase Architecture Timeline

| Phase | Name | Key Capabilities |
|-------|------|-----------------|
| Stages 1–4 | Core QA Platform | Test runs, Playwright execution, evidence capture |
| Stage 5 | Security | RBAC, CSRF, session hardening, audit chain |
| Stage 6 | Operator Security | Password history, version, forced-change flow |
| Stage 8 | Test Management | Managed suites, manual runs, lifecycle DRAFT→APPROVED |
| Stage 9 | Connection Targets | Secure target registry, policy-validated connectivity |
| Stage 10 | Execution Engine | Automated runs, structured safe actions, worker system |
| Stage 11 | Acceptance Hardening | Pinned HTTP transport, DNS rebinding protection |
| Stage 12 | Defect Traceability | Defect lifecycle, retest, audit-chain evidence links |
| Phase 4 | AI Analyzer | LocalAI task analysis, test plan proposals |
| Phase 5 | AI Test Plans | Versioned plans, DRAFT→APPROVED lifecycle, crypto hashes |
| Phase 6 | Advanced Validation | API/DB/accessibility/performance validation engine |
| Phase 7 | Visual Regression | Baseline capture, pixel diff, visual test runs |
| Phase 8 | Enterprise & Discovery | Company hierarchy, AI flow discovery |
| Phase 9 | AI Copilot & Agents | AI copilot chat, 13 specialized agents, orchestrator |
| Phase 10 | Zero-Code Ecosystem | Onboarding wizard, zero-code studio, test lab, data factory |
| Phase 11 | Release Command Center | War room, release readiness, autonomous regression |
| Phase 12 | Defect Intelligence Hub | Defect pattern analysis, defect intelligence reports |
| Phase 13 | Enterprise Cloud Platform | Distributed execution, browser farm, observability, DevOps |
| Phase 14 | AI QA Operating System | Enterprise brain, workflow composer, incident commander |
| Phase 15 | Software Quality Intelligence | Software graph, change impact, coverage, engineering analytics |
| Phase 16 | Engineering Intelligence | Knowledge lake V2, requirement center, architecture intel, release cert |

---

## 7. Key Configuration Files

| File | Purpose |
|------|---------|
| `backend/.env.example` | Backend env var template (DATABASE_URL, ports, safety flags) |
| `frontend/.env.example` | Frontend env var template (VITE_API_BASE_URL) |
| `backend/app/config.py` | Frozen `Settings` dataclass — all env vars with validation |
| `frontend/vite.config.ts` | Vite dev server config — port 5173, /api proxy to 8000 |
| `backend/pytest.ini` | Pytest config for backend test suite |
| `backend/alembic.ini` | Alembic DB migration config |
| `SAFETY_RULES.md` | Immutable safety constraints for the platform |

---

## 8. Runtime Directories (Not Source-Controlled)

| Directory | Purpose |
|-----------|---------|
| `backend/data/autoqa.db` | SQLite database |
| `backend/data/stage8_evidence/` | Manual test evidence files |
| `backend/data/stage10_artifacts/` | Automated run artifacts (screenshots, HAR) |
| `backend/data/visual_baselines/` | Visual regression baseline images |
| `backend/data/visual_runs/` | Visual regression run diffs |
| `backend/data/stage13_exports/` | Report exports (HTML/PDF) |
| `runtime/logs/` | Application logs (rotating) |
| `runtime/pids/` | Service PID files |
| `runtime/backups/` | Database backups |
| `qa/reports/runs/` | Playwright QA run reports |
