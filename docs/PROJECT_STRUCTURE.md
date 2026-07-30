# PROJECT_STRUCTURE.md — iFive AutoQA X

Generated from direct repository inspection. Every figure below was obtained by
reading actual files (`main.py`, `App.tsx`, `frontend/src/pages`, `frontend/src/services`),
not inferred or assumed.

## 1. Top-level layout

```
D:\AUTO_QA_TESTING\
  backend/         FastAPI application (298 .py files under app/, 36 test files under tests/)
  frontend/        Main operator dashboard (React + TS + Vite, no react-router)
  mock-task-portal/  Standalone FastAPI + React app (port 8001 / 5174) - Testing L2 task source
  demo-product/      Standalone FastAPI + React app (port 8002 / 5175) - safe Playwright target
  qa/              Playwright test suite for the main dashboard (31+ specs)
  docs/            Project documentation
  scripts/         PowerShell lifecycle scripts (start/stop/backup/verify/migrate)
  release/stage14/ 63 accumulated release-package snapshots (2026-07-13 .. 2026-07-28)
  runtime/         PID files, logs, backups, and ~42+ leftover pytest tmp_path directories
  local-ai/        AI provider configs/prompts (deterministic rule-based, no Ollama/LLM installed)
```

## 2. Backend module inventory (`backend/app/main.py`)

`main.py` registers **90 routers**, added in four visible generations. The file's own
comments mark exactly where scope expanded beyond the original product:

| Block | Router count | Comment in source | Status |
|---|---|---|---|
| Original product (health, auth, operators, audit, projects, test_runs, dashboard, results, reports, security, agents, test_management, test_plans, connection_targets, automated_execution, defects, task_imports, system, advanced_validation, local_schedules, company_tasks, ai, visual_regression, enterprise, discovery, copilot) | 26 | none (foundational) | **LIVE** — every one of these has a corresponding page imported in `App.tsx` |
| Unlabeled pre-Phase-13 additions (release_readiness, autonomous_regression, knowledge_graph, digital_qa, digital_twin, continuous_monitoring, predictive_quality, multi_reports, experience_memory, pattern_recognition, test_evolution, root_cause_graph, release_command_center, autonomous_monitoring_v2, onboarding, test_studio, test_lab, data_factory, war_room, plugin_marketplace, integrations) | 21 | none | **ORPHANED** — none matched an `App.tsx` import |
| `# Phase 13 – Enterprise Cloud Platform` | 14 | explicit in source | **ORPHANED** |
| `# Phase 14 – Enterprise Autonomous AI QA Operating System (AI QA OS)` | 10 | explicit in source | **ORPHANED** |
| `# Phase 15 – Autonomous Enterprise Software Quality Intelligence Platform` | 9 | explicit in source | **ORPHANED** |
| `# Phase 16 – Enterprise Autonomous Software Engineering Intelligence Platform` | 10 | explicit in source | **ORPHANED** (has real frontend pages + `phase16Service.ts`, but zero import from `App.tsx`) |
| **Total** | **90** | | **26 live / 64 orphaned** |

## 3. Frontend module inventory

`frontend/src/App.tsx` is the sole router (no `react-router` package installed; a
hand-rolled `ModuleKey` switch). It imports **exactly 19 pages**:

Dashboard, Task Imports, Test Plans, Approval Queue, Automated Runs, Advanced
Validation, Visual Regression, Evidence, Defects, Reports, Local Schedules,
Projects, Audit Logs, Settings, Company Tasks, My Tasks, Users, Enterprise
Management, Enterprise Discovery, Enterprise Copilot.

`frontend/src/pages/` on disk contains **~59 page files**. The ~40 not in the list
above (`EnterpriseBrainPage.tsx`, `MissionControlPage.tsx`, `WorkflowComposerPage.tsx`,
`CustomerExperiencePage.tsx`, `MarketplaceCenterPage.tsx`, `BrowserFarmPage.tsx`,
`SDLCCenterPage.tsx`, `SoftwareGraphPage.tsx`, `TraceabilityMatrixPage.tsx`, etc.)
are fully coded, call real backend endpoints via `phase13Service.ts`..`phase16Service.ts`,
but have **zero import reference anywhere in `App.tsx`**. They cannot be reached by
any user of the running application.

`frontend/src/components/` (Core module components actually rendered by the 19 live
pages) contains 26 files matching the live Sidebar exactly. `frontend/src/services/`
has 16 files; 4 of them (`phase13Service.ts`-`phase16Service.ts`) exclusively serve
the orphaned pages above.

## 4. Disk-space / operational debt (not code, but real findings)

- `release/stage14/` — **63 separate full release-package snapshots** accumulated between
  2026-07-13 and 2026-07-28, none pruned.
- `runtime/pytest-*`, `runtime/pytest_temp`, `backend/all_tmp`, `backend/p14_tmp`,
  `backend/p15_tmp`, `backend/p15_tmp2`, `backend/p15_tmp3` — dozens of leftover
  pytest `--basetemp` directories (`tmp_path` never cleaned between CI/manual runs),
  many containing the same orphaned-feature test scratch DBs (`ai_agents_marketplace`,
  `enterprise_brain`, `mission_control`, etc.) referenced above.

## 5. Recommendation

Treat the **26-router / 19-page set as the actual product** for the remainder of the
Enterprise Stabilization Sprint (Steps 3+: refactor, standardize, optimize). Treat the
other 64 routers / 40 pages as documented in `DEAD_CODE_REPORT.md` — flagged, not
deleted, pending your decision.