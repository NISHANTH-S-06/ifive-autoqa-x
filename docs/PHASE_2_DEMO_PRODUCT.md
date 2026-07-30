# PHASE 2 — DEMO PRODUCT WEBSITE

**Status:** ✅ Complete  
**Location:** `D:\AUTO_QA_TESTING\demo-product\`  
**Date Completed:** 2026-07-21  
**Security:** Local-only target system — no real company systems, URLs, credentials, or APIs  

---

## Architecture

```
demo-product/
├── backend/                        # FastAPI + SQLite + Alembic
│   ├── alembic/                    # Schema migrations
│   │   └── versions/
│   │       └── 0001_initial_schema.py
│   ├── app/
│   │   ├── api/
│   │   │   ├── auth.py             # POST /auth/login, logout, me
│   │   │   ├── demo_settings.py    # GET /demo-settings, PATCH /demo-settings/{key}
│   │   │   ├── departments.py      # GET /departments
│   │   │   ├── employees.py        # CRUD /employees
│   │   │   ├── health.py           # GET /health
│   │   │   ├── products.py         # GET /products
│   │   │   └── stock_counts.py     # GET /stock-counts, POST /stock-counts
│   │   ├── models/
│   │   │   ├── demo_setting.py     # DemoSetting bug toggle model
│   │   │   ├── department.py       # Department model
│   │   │   ├── employee.py         # Employee model
│   │   │   ├── inventory.py        # Product and StockCount models
│   │   │   └── user.py             # User and Session models
│   │   ├── schemas/
│   │   │   ├── demo_setting.py
│   │   │   ├── employee.py
│   │   │   ├── inventory.py
│   │   │   └── user.py
│   │   ├── services/
│   │   │   ├── demo_setting_service.py
│   │   │   ├── employee_service.py
│   │   │   └── inventory_service.py
│   │   ├── auth.py                 # Session tokens + password hash
│   │   ├── database.py             # SQLite engine + get_db
│   │   ├── main.py                 # FastAPI app + lifespan + api_delay middleware
│   │   └── seed.py                 # Idempotent demo data seed
│   ├── tests/                      # Pytest suite (21 tests)
│   │   ├── conftest.py
│   │   ├── test_auth.py
│   │   ├── test_demo_settings.py
│   │   ├── test_employees.py
│   │   ├── test_inventory.py
│   │   └── test_migrations.py
│   ├── alembic.ini
│   ├── pytest.ini
│   └── requirements.txt
├── data/                           # SQLite database storage
│   └── demo_product.db
└── frontend/                       # React + TypeScript + Vite
    ├── e2e/
    │   └── workflow.spec.ts        # 11 Playwright E2E tests
    ├── src/
    │   ├── pages/
    │   │   ├── LoginPage.tsx
    │   │   ├── DashboardPage.tsx
    │   │   ├── EmployeeListPage.tsx
    │   │   ├── CreateEmployeePage.tsx
    │   │   ├── EmployeeDetailPage.tsx
    │   │   ├── ProductListPage.tsx
    │   │   ├── StockCountPage.tsx
    │   │   └── DemoSettingsPage.tsx
    │   ├── App.tsx                 # Router + auth guard + Bug Warning Banner
    │   ├── AuthContext.tsx         # Session context
    │   ├── Sidebar.tsx             # Role-filtered navigation
    │   ├── api.ts                  # API client
    │   ├── types.ts                # TypeScript types
    │   ├── index.css               # Dark theme styles
    │   └── main.tsx
    ├── playwright.config.ts
    ├── package.json
    └── vite.config.ts
```

---

## Ports

- **Demo Product Backend:** `http://localhost:8002`
- **Demo Product Frontend:** `http://localhost:5175`

---

## Demo Authentication & Accounts

Local fixture credentials only — passwords stored as SHA-256 hashes with salt.

| Username | Password | Role | Access Scope |
|---|---|---|---|
| `demo_admin` | `Admin@Demo123` | `DEMO_ADMIN` | Full access + Bug Toggles management |
| `demo_hr_user` | `Hr@Demo123` | `HR_USER` | Dashboard, Employee List, Create Employee, Details |
| `demo_inventory_user` | `Inv@Demo123` | `INVENTORY_USER` | Dashboard, Product List, Stock Count Reconciliation |
| `demo_viewer` | `View@Demo123` | `VIEWER` | Read-only access to Dashboard, Employees, Products |

---

## Required Routes and APIs

| Route | Method | Endpoint | Role Access | Purpose |
|---|---|---|---|---|
| `/login` | POST | `/api/auth/login` | Public | Demo user login |
| `/login` | POST | `/api/auth/logout` | Authenticated | Revoke session |
| — | GET | `/api/auth/me` | Authenticated | Current user profile |
| `/dashboard` | GET | `/api/dashboard` | All | Dashboard summary |
| `/hr/employees` | GET | `/api/employees` | All | List employees |
| `/hr/employees/new` | POST | `/api/employees` | ADMIN, HR | Create employee |
| `/hr/employees/:id` | GET | `/api/employees/{id}` | All | View employee details |
| `/inventory/products` | GET | `/api/products` | All | Product catalog |
| `/inventory/stock-count` | GET/POST | `/api/stock-counts` | ADMIN, INVENTORY | Submit stock count audit |
| `/demo-settings` | GET/PATCH | `/api/demo-settings` | ADMIN | Manage intentional bug toggles |
| — | GET | `/api/health` | Public | System health check |

---

## Intentional Bug Toggles

Managed via `/demo-settings` by `demo_admin`:

1. `employee_save_failure`: Save returns HTTP 500 Internal Server Error; record is not created.
2. `employee_success_message_missing`: Employee record created in DB, but UI success banner is hidden.
3. `employee_table_refresh_failure`: Record created in DB, but `GET /api/employees` omits newly created record.
4. `stock_difference_error`: Calculates an intentionally incorrect difference formula (`(counted - prev) + 10`).
5. `api_delay`: Adds a safe 3-second delay to non-health API requests.
6. `login_failure_mode`: Returns HTTP 503 Service Unavailable on login attempts.

---

## Test Results

### 1. Backend Pytest Suite

**Result: 21 passed, 0 failed**

- `test_auth.py`: 4 passed (login success, invalid pass, login_failure_mode 503, auth me)
- `test_employees.py`: 6 passed (create success, invalid email, duplicate email 409, role restriction 403, save failure 500, table refresh failure)
- `test_inventory.py`: 5 passed (product list, stock count success, negative qty rejection, stock difference error, role restriction 403)
- `test_demo_settings.py`: 4 passed (list settings, admin update, non-admin 403, unknown setting 404)
- `test_migrations.py`: 2 passed (Alembic clean migration, seed idempotency)

### 2. Frontend Build (Vite + TypeScript)

**Result: ✅ Build succeeded — 35 modules transformed, 0 TypeScript errors.**

### 3. Playwright E2E Browser Suite

**Result: 11 passed, 0 failed**

1. Login and dashboard — ✅ PASSED
2. Create employee PASS flow — ✅ PASSED
3. Employee required-field validation — ✅ PASSED
4. Duplicate email rejection — ✅ PASSED
5. Employee details values — ✅ PASSED
6. Inventory stock count calculation — ✅ PASSED
7. Employee Save failure toggle — ✅ PASSED
8. Missing success-message toggle — ✅ PASSED
9. Login failure BLOCKED-style scenario — ✅ PASSED
10. Role-based menu visibility — ✅ PASSED
11. Responsive layout at 1366x768 and 375x812 — ✅ PASSED

---

## Commands

### Backend

```powershell
# Install backend dependencies
pip install -r demo-product/backend/requirements.txt

# Run backend server (port 8002)
cd demo-product/backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8002

# Run backend tests
python -m pytest tests/ -v --tb=short
```

### Frontend

```powershell
# Install dependencies
cd demo-product/frontend
npm install

# Run dev server (port 5175)
npm run dev

# Build production bundle
npm run build

# Run Playwright E2E tests
npx playwright test
```

---

## Phase 2 Acceptance Matrix

| Criterion | Status |
|---|---|
| Demo Product starts locally | **VERIFIED** |
| Alembic clean migration succeeds | **VERIFIED** |
| Seed data loads safely & idempotently | **VERIFIED** |
| Login works with demo users | **VERIFIED** |
| Employee PASS workflow works | **VERIFIED** |
| Inventory stock-count workflow works | **VERIFIED** |
| All 6 intentional bug toggles work | **VERIFIED** |
| PASS, FAIL, and BLOCKED demonstrations are repeatable | **VERIFIED** |
| API data persists after refresh | **VERIFIED** |
| Backend tests pass (21/21) | **VERIFIED** |
| Frontend build passes | **VERIFIED** |
| Real Playwright E2E tests pass (11/11) | **VERIFIED** |
| No company system accessed | **VERIFIED** |
| AutoQA is not connected yet | **VERIFIED** |

---

## Exact Phase 3 Task

Phase 3 will integrate the AutoQA execution engine with the Mock Task Portal and Demo Product Website:

1. **Task Polling Connector** (`backend/app/connectors/mock_portal.py`):
   - Poll `GET http://localhost:8001/api/tasks?status=TESTING_L2` from Mock Task Portal.
   - Parse tasks into AutoQA execution queue items.

2. **AutoQA Automated Playwright Runner**:
   - Drive target URLs (`http://localhost:5175`) on Demo Product Website using Playwright.
   - Execute task actions (e.g. Employee Create, Stock Count Audit).
   - Capture video, screenshots, trace, and console logs.

3. **Result Callback**:
   - Report execution result (`PASS` / `FAIL` / `BLOCKED`) back to Mock Task Portal (`POST /api/tasks/{id}/qa-result`).
