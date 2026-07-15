# Command Reference - All Terminal Commands

Quick copy-paste commands for setting up and running the project.

---

## 🔑 Create User Account (ID & Password)

Run this first after database setup:

```powershell
.\scripts\create_local_operator.ps1
```

**What it does:**
- Prompts for username
- Prompts for email
- Prompts for role: `VIEWER`, `TESTER`, `APPROVER`, or `ADMIN`
- Prompts for password (12+ chars, mixed case, numbers, special chars)
- Creates user in database
- Forces password change on first login

**Password Requirements:**
- ✓ Minimum 12 characters
- ✓ At least one uppercase letter (A-Z)
- ✓ At least one lowercase letter (a-z)
- ✓ At least one number (0-9)
- ✓ At least one special character (!@#$%^&*)
- ✓ Example: `MyProject@2024!Admin`

---

## 🐍 Backend Setup & Run

### One-time Setup (First Time)

```powershell
cd d:\AUTO_QA_TESTING\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Activate Python Environment (Every Time)

```powershell
cd d:\AUTO_QA_TESTING\backend
.\.venv\Scripts\Activate.ps1
```

Expected output:
```
(.venv) PS D:\AUTO_QA_TESTING\backend>
```

### Run Backend Server (Development)

```powershell
cd d:\AUTO_QA_TESTING\backend
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Expected output:
```
Uvicorn running on http://127.0.0.1:8000
Press CTRL+C to quit
```

### Run Migrations

```powershell
cd d:\AUTO_QA_TESTING\backend
.\.venv\Scripts\Activate.ps1
python -m app.migrations
```

### Test Backend Health

```powershell
curl http://127.0.0.1:8000/health
# Or in PowerShell:
Invoke-WebRequest -Uri http://127.0.0.1:8000/health
```

---

## 🎨 Frontend Setup & Run

### One-time Setup (First Time)

```powershell
cd d:\AUTO_QA_TESTING\frontend
npm install
```

### Run Frontend Dev Server

```powershell
cd d:\AUTO_QA_TESTING\frontend
npm run dev
```

Expected output:
```
VITE v6.0.7  ready in 500 ms
➜  Local:   http://localhost:5173/
```

### Build Frontend for Production

```powershell
cd d:\AUTO_QA_TESTING\frontend
npm run build
```

### Preview Production Build

```powershell
cd d:\AUTO_QA_TESTING\frontend
npm run preview
```

### Check TypeScript Errors

```powershell
cd d:\AUTO_QA_TESTING\frontend
npm run lint
```

---

## 🚀 Automated Startup Scripts

### Option 1: Quick Start (Recommended for Development)

```powershell
cd d:\AUTO_QA_TESTING

# First time with full setup
.\QuickStart.ps1 -FirstTime -Mode dev

# Subsequent times
.\QuickStart.ps1 -Mode dev
```

This opens **two separate terminal windows**:
- Terminal 1: Backend on port 8000
- Terminal 2: Frontend on port 5173

### Option 2: Complete System Start (All Services)

```powershell
cd d:\AUTO_QA_TESTING
.\scripts\start_local_system.ps1 -EnvironmentFile config\development.env
```

Starts:
- Backend (FastAPI)
- Frontend (Static Server)
- Worker Service
- Health verification

### Option 3: Start Individual Services

**Backend only:**
```powershell
.\scripts\start_backend.ps1 -EnvironmentFile config\development.env -Port 8000
```

**Frontend only (requires production build first):**
```powershell
cd frontend && npm run build
.\scripts\start_frontend.ps1 -EnvironmentFile config\development.env -Port 5173
```

---

## 🧪 Testing

### Run All Tests

```powershell
cd d:\AUTO_QA_TESTING\backend
.\.venv\Scripts\Activate.ps1
pytest tests/ -v
```

### Run Specific Test File

```powershell
pytest tests/test_health.py -v
```

### Run Tests Matching Pattern

```powershell
pytest tests/ -k "security" -v
```

### Run with Coverage

```powershell
pytest tests/ --cov=app --cov-report=html
```

---

## 📋 Project Management

### Create Configuration File

```powershell
cd d:\AUTO_QA_TESTING
Copy-Item config\development.env.example config\development.env
```

Edit `config\development.env` with your settings.

### Verify Project Health

```powershell
.\scripts\verify_health.ps1
```

### View Project Structure

```powershell
tree /F /A
```

### Check Python Environment

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
pip list
```

### Check Node Environment

```powershell
cd frontend
npm list
npm outdated
```

---

## 🔧 Troubleshooting Commands

### Port Already in Use

```powershell
# Find process using port 8000 (Backend)
netstat -ano | findstr :8000

# Find process using port 5173 (Frontend)
netstat -ano | findstr :5173

# Kill process by PID (replace XXXX with actual PID)
taskkill /PID XXXX /F
```

### Clear Python Cache

```powershell
cd d:\AUTO_QA_TESTING\backend
.\.venv\Scripts\Activate.ps1
python -m pip cache purge
pip install --force-reinstall -r requirements.txt
```

### Clear Node Modules

```powershell
cd d:\AUTO_QA_TESTING\frontend
Remove-Item node_modules -Recurse -Force
Remove-Item package-lock.json
npm install
```

### Check Database Connection

```powershell
cd d:\AUTO_QA_TESTING\backend
.\.venv\Scripts\Activate.ps1
python -c "from app.database import SessionLocal; db = SessionLocal(); print('✓ Database connected')"
```

### Reset Database (⚠️ Deletes all data)

```powershell
cd d:\AUTO_QA_TESTING\backend
rm -Path data\autoqa-development.db
.\.venv\Scripts\Activate.ps1
python -m app.migrations
```

### Allow PowerShell Scripts to Run

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

---

## 📍 Access Points After Startup

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://localhost:5173 | Web application |
| Backend | http://127.0.0.1:8000 | API server |
| API Docs | http://127.0.0.1:8000/docs | Swagger UI (interactive docs) |
| ReDoc | http://127.0.0.1:8000/redoc | Alternative API docs |
| Health | http://127.0.0.1:8000/health | Backend health status |

---

## 🎯 Complete Startup Sequence (Manual)

If you want to manually do everything step by step:

**Terminal 1 - Setup:**
```powershell
cd d:\AUTO_QA_TESTING
.\scripts\create_local_operator.ps1  # Create user account
```

**Terminal 2 - Backend:**
```powershell
cd d:\AUTO_QA_TESTING\backend
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

**Terminal 3 - Frontend:**
```powershell
cd d:\AUTO_QA_TESTING\frontend
npm run dev
```

**Then:**
1. Open browser: http://localhost:5173
2. Login with credentials from step 1
3. Change password on first login
4. Start testing!

---

## 🔗 Useful Documentation

- [QUICK_START_GUIDE.md](QUICK_START_GUIDE.md) - Full setup guide
- [API_DOCUMENTATION.md](API_DOCUMENTATION.md) - API endpoints
- [DEVELOPMENT_WORKFLOW.md](DEVELOPMENT_WORKFLOW.md) - Development practices
- [LOCAL_RELEASE_OPERATIONS.md](LOCAL_RELEASE_OPERATIONS.md) - Production deployment
- [SECURITY_AND_SAFETY.md](SECURITY_AND_SAFETY.md) - Security guidelines

---

**Last Updated:** 2026-07-14  
**Quick Copy-Paste Cheat Sheet**
