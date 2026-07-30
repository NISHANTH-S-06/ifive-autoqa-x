# PHASE 1 — MOCK TASK PORTAL

**Status:** ✅ Complete  
**Location:** `D:\AUTO_QA_TESTING\mock-task-portal\`  
**Date Completed:** 2026-07-21  
**Security:** Local-only — no real company systems, URLs, credentials, or APIs

---

## Architecture

```
mock-task-portal/
├── backend/                        # FastAPI + SQLite + Alembic
│   ├── alembic/                    # Schema migrations
│   │   └── versions/
│   │       └── 0001_initial_schema.py
│   ├── app/
│   │   ├── api/
│   │   │   ├── auth.py             # POST /auth/login, logout, me
│   │   │   ├── dashboard.py        # GET /dashboard/summary
│   │   │   ├── tasks.py            # Full task CRUD + lifecycle
│   │   │   └── users.py            # GET /users
│   │   ├── models/
│   │   │   ├── task.py             # Task model + transition rules
│   │   │   ├── task_history.py     # Append-only history
│   │   │   └── user.py             # User + UserSession
│   │   ├── schemas/
│   │   │   ├── tasks.py            # TaskCreate, TaskOut, TestingL2TaskOut…
│   │   │   ├── history.py          # HistoryOut
│   │   │   └── users.py            # LoginRequest, UserOut, TokenResponse
│   │   ├── services/
│   │   │   └── task_service.py     # Status transitions + QA results
│   │   ├── auth.py                 # Session tokens + hash
│   │   ├── database.py             # SQLite engine + get_db
│   │   ├── main.py                 # FastAPI app + lifespan
│   │   └── seed.py                 # Demo data
│   ├── tests/
│   │   ├── conftest.py             # Fixtures + multi-user helpers
│   │   └── test_tasks.py           # 23 backend tests
│   ├── alembic.ini
│   ├── pytest.ini
│   └── requirements.txt
└── frontend/                       # React + TypeScript + Vite
    ├── e2e/
    │   └── workflow.spec.ts        # 8 Playwright tests
    ├── src/
    │   ├── pages/
    │   │   ├── LoginPage.tsx
    │   │   ├── DashboardPage.tsx
    │   │   ├── TaskListPage.tsx
    │   │   ├── CreateTaskPage.tsx
    │   │   ├── TaskDetailPage.tsx
    │   │   ├── StatusHistoryPage.tsx
    │   │   └── QueuePages.tsx      # 5 queue pages
    │   ├── App.tsx                 # Router + auth guard
    │   ├── AuthContext.tsx
    │   ├── Sidebar.tsx
    │   ├── api.ts                  # API client
    │   ├── components.tsx          # Shared UI
    │   ├── types.ts                # TypeScript types
    │   └── index.css               # Global styles (dark theme)
    ├── playwright.config.ts
    ├── package.json
    └── vite.config.ts
```

---

## Database

**Engine:** SQLite (`mock-task-portal/data/portal.db`)  
**Migrations:** Alembic (revision `0001_initial_schema`)  

### Tables

| Table | Purpose |
|---|---|
| `users` | Demo user accounts (username, role, password_hash) |
| `user_sessions` | Bearer token sessions (TTL=8h) |
| `tasks` | Task records with all required fields |
| `task_history` | Append-only status audit trail |

### Task Fields

All 24 required fields are implemented:

`id`, `task_code`, `project_name`, `module_name`, `title`, `description`,
`assigned_developer`, `assigned_tester`, `task_given_by`, `target_date`,
`priority`, `application_url`, `page_path`, `environment`, `expected_result`,
`acceptance_criteria`, `test_data`, `developer_notes`, `rework_remarks`,
`revision`, `status`, `created_at`, `updated_at`, `testing_l2_at`, `completed_at`

---

## Roles

| Role | Username | Password |
|---|---|---|
| SUPERADMIN | admin | Admin@Demo123 |
| DEVELOPER | dev1 | Dev@Demo123 |
| TESTER | tester1 | Test@Demo123 |
| DELIVERY | delivery1 | Del@Demo123 |
| VIEWER | viewer1 | View@Demo123 |

### Permission Rules

| Action | SUPERADMIN | DEVELOPER | TESTER | DELIVERY | VIEWER |
|---|---|---|---|---|---|
| Create task | ✅ | ❌ | ❌ | ❌ | ❌ |
| View all tasks | ✅ | own only | L2+ only | DELIVERY only | ✅ |
| Assign task | ✅ | ❌ | ❌ | ❌ | ❌ |
| Move ASSIGNED → IN_PROGRESS | ✅ | ✅ | ❌ | ❌ | ❌ |
| Move to TESTING_L2 | ✅ | ✅ | ❌ | ❌ | ❌ |
| Add developer notes | ✅ | own task | ❌ | ❌ | ❌ |
| Record QA result | ✅ | ❌ | ✅ | ❌ | ❌ |
| Add rework remarks | ✅ | ❌ | ✅ | ❌ | ❌ |
| Move QA_PASSED → DELIVERY_READY | ✅ | ❌ | ❌ | ❌ | ❌ |
| Move DELIVERY_READY → COMPLETED | ✅ | ❌ | ❌ | ✅ | ❌ |

---

## Status Lifecycle

```
CREATED
  └─ ASSIGNED                         (SUPERADMIN)
       └─ IN_PROGRESS                 (DEVELOPER)
            ├─ TESTING_L1             (DEVELOPER)
            │    └─ TESTING_L2        (DEVELOPER, SUPERADMIN)
            │         └─ QA_RUNNING   (TESTER) [auto on qa-result]
            │              ├─ QA_PASSED → DELIVERY_READY → DELIVERY_COMPLETED
            │              └─ QA_FAILED → REWORK → IN_PROGRESS → TESTING_L2
            └─ NEED_CLARITY / HOLD / CANCELLED (various roles)
```

**Terminal states:** `DELIVERY_COMPLETED`, `CANCELLED`  
**Blocked states:** `NEED_CLARITY`, `HOLD`

---

## APIs Implemented

| Method | Path | Role | Description |
|---|---|---|---|
| POST | `/api/auth/login` | public | Login |
| POST | `/api/auth/logout` | any | Logout |
| GET | `/api/auth/me` | any | Current user |
| GET | `/api/users` | any | User list (for dropdowns) |
| POST | `/api/tasks` | SUPERADMIN | Create task |
| GET | `/api/tasks` | role-filtered | List tasks + filters |
| GET | `/api/tasks?status=TESTING_L2` | any | **Connector contract** |
| GET | `/api/tasks/{id}` | role-filtered | Get task |
| PATCH | `/api/tasks/{id}` | SUPERADMIN | Update task metadata |
| PATCH | `/api/tasks/{id}/status` | role-validated | Change status |
| POST | `/api/tasks/{id}/developer-notes` | DEVELOPER/SUPERADMIN | Add notes |
| POST | `/api/tasks/{id}/rework-remarks` | TESTER/SUPERADMIN | Add remarks |
| GET | `/api/tasks/{id}/history` | any | Status history |
| POST | `/api/tasks/{id}/qa-result` | TESTER/SUPERADMIN | Record QA result |
| GET | `/api/dashboard/summary` | any | Dashboard counts |
| GET | `/api/health` | public | Health check |

### Testing L2 Connector Contract

`GET /api/tasks?status=TESTING_L2` returns structured JSON:

```json
{
  "source_system": "MOCK_TASK_PORTAL",
  "source_task_id": 2,
  "source_revision": 1,
  "project_name": "Demo ERP",
  "module_name": "Inventory Module",
  "title": "Stock Count Reconciliation",
  "description": "...",
  "application_url": "http://localhost:3000",
  "page_path": "/inventory/stock-count",
  "environment": "local",
  "expected_result": "...",
  "acceptance_criteria": "...",
  "test_data": "...",
  "assigned_developer": "dev1",
  "assigned_tester": "tester1",
  "priority": "CRITICAL",
  "developer_notes": "...",
  "status": "TESTING_L2",
  "testing_l2_at": "2026-07-21T..."
}
```

---

## UI Pages

| # | Page | Route | Description |
|---|---|---|---|
| 1 | Login | `/login` | Auth with demo credentials panel |
| 2 | Dashboard | `/` | Stats grid by status, clickable filters |
| 3 | Create Task | `/tasks/create` | Full task creation form |
| 4 | Task List | `/tasks` | Filterable table by status/priority/project/dev |
| 5 | Task Details | `/tasks/:id` | Full detail + action modals |
| 6 | Developer View | `/developer-view` | Developer's own tasks |
| 7 | Testing L2 Queue | `/testing-l2-queue` | TESTING_L2 filtered list |
| 8 | Rework Queue | `/rework-queue` | REWORK filtered list |
| 9 | Delivery Ready | `/delivery-ready` | DELIVERY_READY filtered list |
| 10 | Delivery Completed | `/delivery-completed` | DELIVERY_COMPLETED list |
| 11 | Status History | `/tasks/:id/history` | Append-only history trail |

---

## Commands

### Backend

```powershell
# Install deps
pip install -r mock-task-portal/backend/requirements.txt

# Start backend (port 8001)
cd mock-task-portal/backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001

# Run backend tests
python -m pytest tests/ -v --tb=short

# Run Alembic migration only
cd mock-task-portal/backend
alembic upgrade head
```

### Frontend

```powershell
# Install deps
cd mock-task-portal/frontend
npm install

# Start dev server (port 5174)
npm run dev

# Build production
npm run build

# Run Playwright tests (requires backend + frontend running)
npx playwright test
```

---

## Test Results

### Backend Tests — pytest

**Result: 23 passed, 0 failed**

| # | Test | Status |
|---|---|---|
| 1 | test_create_task_success | ✅ PASSED |
| 2 | test_create_task_duplicate_code_rejected | ✅ PASSED |
| 3 | test_create_task_only_superadmin | ✅ PASSED |
| 4 | test_assignment_created_to_assigned | ✅ PASSED |
| 5 | test_developer_can_only_see_own_tasks | ✅ PASSED |
| 6 | test_developer_cannot_access_unassigned_task | ✅ PASSED |
| 7 | test_invalid_transition_rejected | ✅ PASSED |
| 8 | test_full_happy_path_transitions | ✅ PASSED |
| 9 | test_testing_l2_filter_returns_connector_contract | ✅ PASSED |
| 10 | test_developer_can_add_notes | ✅ PASSED |
| 11 | test_developer_cannot_add_notes_to_others_task | ✅ PASSED |
| 12 | test_tester_can_add_rework_remarks | ✅ PASSED |
| 13 | test_qa_pass_moves_to_qa_passed | ✅ PASSED |
| 14 | test_qa_fail_moves_to_qa_failed | ✅ PASSED |
| 15 | test_qa_blocked_moves_to_need_clarity | ✅ PASSED |
| 16 | test_delivery_workflow | ✅ PASSED |
| 17 | test_viewer_cannot_change_status | ✅ PASSED |
| 18 | test_delivery_cannot_change_status_to_non_delivery | ✅ PASSED |
| 19 | test_status_history_is_append_only | ✅ PASSED |
| 20 | test_history_records_correct_fields | ✅ PASSED |
| 21 | test_revision_increments_on_rework_cycle | ✅ PASSED |
| 22 | test_dashboard_summary | ✅ PASSED |
| 23 | test_login_with_invalid_credentials | ✅ PASSED |

### Frontend Build

**Result: ✅ Build successful — 35 modules, 0 TypeScript errors**  
Output: `dist/index.html`, `dist/assets/index.css`, `dist/assets/index.js`

### Playwright E2E Tests

**Result: 8 passed, 0 failed**

| # | Test | Status |
|---|---|---|
| 1 | Login page renders and login succeeds | ✅ PASSED |
| 2 | Login with wrong password shows error | ✅ PASSED |
| 3 | Create task via UI | ✅ PASSED |
| 4 | Developer moves task to TESTING_L2 | ✅ PASSED |
| 5 | Tester sees task in Testing L2 queue | ✅ PASSED |
| 6 | Tester records PASS — task moves to QA_PASSED | ✅ PASSED |
| 7 | FAIL task moves to REWORK | ✅ PASSED |
| 8 | Delivery user completes task | ✅ PASSED |

---

## Security Controls

- ✅ No real company URLs (all use `localhost:3000` placeholders)
- ✅ No real credentials (demo-only SHA-256 hashed passwords)
- ✅ No production environment access
- ✅ No secrets in repository (no `.env` with real values)
- ✅ Bearer token sessions with 8h TTL
- ✅ Role-based access enforcement on every endpoint
- ✅ Status transition validation (unauthorized transitions → 403/422)
- ✅ Developer access restricted to own tasks
- ✅ Tester access restricted to L2+ tasks
- ✅ Delivery access restricted to DELIVERY_READY tasks
- ✅ Alembic-only schema migrations
- ✅ Append-only task history (no DELETE/PUT endpoints)
- ✅ Input validation via Pydantic schemas
- ✅ Duplicate task code rejected (409)
- ✅ `source_system = "MOCK_TASK_PORTAL"` labels all connector output

---

## Phase 1 Acceptance Matrix

| Criterion | Status |
|---|---|
| Mock Task Portal starts locally | ✅ VERIFIED |
| Clean Alembic migration succeeds | ✅ VERIFIED |
| Task can be created and assigned | ✅ VERIFIED |
| Developer can move task to TESTING_L2 | ✅ VERIFIED |
| Testing L2 API returns correct task | ✅ VERIFIED |
| Tester can record PASS, FAIL, or BLOCKED | ✅ VERIFIED |
| PASS moves to QA_PASSED | ✅ VERIFIED |
| FAIL moves to REWORK | ✅ VERIFIED |
| Delivery workflow works | ✅ VERIFIED |
| Status history is append-only | ✅ VERIFIED |
| Backend tests pass (23/23) | ✅ VERIFIED |
| Frontend build passes | ✅ VERIFIED |
| Playwright workflow passes (8/8) | ✅ VERIFIED |
| No real company system accessed | ✅ VERIFIED |

---

## Demo Seed Data

Seeded automatically on first startup:

| Entity | Details |
|---|---|
| admin (SUPERADMIN) | Admin@Demo123 |
| dev1 (DEVELOPER) | Dev@Demo123 |
| tester1 (TESTER) | Test@Demo123 |
| delivery1 (DELIVERY) | Del@Demo123 |
| viewer1 (VIEWER) | View@Demo123 |
| DEMO-001 | "Employee Form Save Button" — in ASSIGNED state |
| DEMO-002 | "Stock Count Reconciliation" — in TESTING_L2 state |

---

## Known Limitations

1. **Password security**: Uses SHA-256 + static salt (not bcrypt). Acceptable for demo — not for production.
2. **No pagination**: Task list fetches all tasks. Add pagination in Phase 2 if needed.
3. **No real file attachments**: `test_data` is plain text.
4. **Single worker Playwright tests**: Tests run sequentially to avoid DB conflicts.
5. **No JWT**: Uses simple DB-stored session tokens.
6. **Seed idempotency**: Seed only checks if `admin` user exists; re-seeding requires deleting `portal.db`.

---

## Exact Phase 2 Task

Phase 2 will integrate the Mock Task Portal with the AutoQA execution engine:

1. **AutoQA Connector** (`backend/app/connectors/mock_portal.py`):
   - Poll `GET /api/tasks?status=TESTING_L2` from Mock Task Portal
   - Map `TestingL2TaskOut` fields to AutoQA `ExecutionTask` schema
   - Use `source_system`, `source_task_id`, `source_revision` for deduplication

2. **Stage 10 Extension** (`backend/app/stages/stage_10_portal_connector.py`):
   - Fetch TESTING_L2 tasks from portal
   - Submit to AutoQA execution queue
   - Report results back via `POST /api/tasks/{id}/qa-result`

3. **Result Callback**:
   - Map AutoQA `TestResult` → QA result (`PASS`/`FAIL`/`BLOCKED`)
   - Include execution evidence URL in `reason` field

4. **Environment Safety**:
   - Use `MOCK_PORTAL_BASE_URL` env var (default: `http://localhost:8001`)
   - Only connect to local portal — not any real company API

**Stop signal**: Do not begin Phase 2 until explicitly instructed.
