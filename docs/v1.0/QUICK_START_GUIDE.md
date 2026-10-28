# Quick Start Guide - Project Setup & Run

Complete guide to set up and start the AutoQA project with ID/password creation and all necessary commands.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Initial Setup](#initial-setup)
3. [Create ID & Password](#create-id--password)
4. [Activate Environments](#activate-environments)
5. [Run Frontend & Backend](#run-frontend--backend)
6. [Complete Startup Script](#complete-startup-script)
7. [Verification](#verification)

---

## Prerequisites

Ensure you have:

- **Python 3.9+** installed
- **Node.js 18+** with npm installed
- **PowerShell 5.1+** or PowerShell Core
- **Git** for version control

Verify installations:

```powershell
python --version
node --version
npm --version
```

---

## Initial Setup

### 1. Clone or Navigate to Project

```powershell
cd d:\AUTO_QA_TESTING
```

### 2. Install Backend Dependencies

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. Install Frontend Dependencies

```powershell
cd ..\frontend
npm install
```

### 4. Run Database Migrations

```powershell
cd ..\backend
python -m app.migrations
```

---

## Create ID & Password

### Option 1: Interactive Setup (Recommended)

Run the operator creation script:

```powershell
.\scripts\create_local_operator.ps1
```

**Follow the prompts:**

- Enter username (e.g., `admin`)
- Enter email address
- Enter role: `VIEWER`, `TESTER`, `APPROVER`, or `ADMIN`
- Password requirements:
  - Minimum 12 characters
  - Mix of uppercase, lowercase, numbers, and special characters
  - Example: `MyProject@2024!`
  - Password will NOT be displayed - secure it immediately
- **IMPORTANT:** First login will require password change

### Option 2: Manual Database Entry (Advanced)

If scripting fails, the database will prompt you to set credentials on first login.

---

## Activate Environments

### 1. Activate Backend Environment (Python)

```powershell
cd d:\AUTO_QA_TESTING\backend
.\.venv\Scripts\Activate.ps1
```

**Expected output:**

```text
(.venv) PS D:\AUTO_QA_TESTING\backend>
```

### 2. Activate Frontend Environment (Node)

```powershell
cd d:\AUTO_QA_TESTING\frontend
npm install  # If not already done
```

---

## Run Frontend & Backend

### Method 1: Separate Terminal Windows (Recommended for Development)

**Terminal 1 - Backend (FastAPI + Uvicorn):**

```powershell
cd d:\AUTO_QA_TESTING\backend
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Expected startup message:

```text
Uvicorn running on http://127.0.0.1:8000
Press CTRL+C to quit
```

**Terminal 2 - Frontend (Vite Dev Server):**

```powershell
cd d:\AUTO_QA_TESTING\frontend
npm run dev
```

Expected startup message:

```text
VITE v6.0.7  ready in 500 ms

➜  Local:   http://localhost:5173/
```

**Terminal 3 - Worker Service (Optional):**

```powershell
cd d:\AUTO_QA_TESTING\backend
.\.venv\Scripts\Activate.ps1
python -m app.cli  # Check available CLI commands
```

### Method 2: Using PowerShell Scripts (Production-like)

**Build frontend first:**

```powershell
cd d:\AUTO_QA_TESTING\frontend
npm run build
```

**Create environment file:**

```powershell
# Copy the example config
Copy-Item config\development.env.example config\development.env
```

**Start all services:**

```powershell
cd d:\AUTO_QA_TESTING
.\scripts\start_local_system.ps1 -EnvironmentFile config\development.env
```

---

## Complete Startup Script

### Create a File: `QuickStart.ps1`

Save this in `d:\AUTO_QA_TESTING\QuickStart.ps1`:

```powershell
# ============================================
# AutoQA Quick Start Script
# ============================================

param(
    [string]$Mode = "dev",  # dev or prod
    [switch]$FirstTime      # First time setup
)

$ErrorActionPreference = 'Stop'
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

function Write-Header {
    param([string]$Message)
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host $Message -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
}

function Test-Command {
    param([string]$Command)
    try {
        $null = & $Command --version 2>&1
        return $true
    } catch {
        return $false
    }
}

# Check prerequisites
Write-Header "Checking Prerequisites"
if (-not (Test-Command "python")) { throw "Python not found. Install Python 3.9+" }
if (-not (Test-Command "node")) { throw "Node.js not found. Install Node.js 18+" }
if (-not (Test-Command "npm")) { throw "npm not found. Install Node.js with npm" }
Write-Host "✓ All prerequisites installed" -ForegroundColor Green

# First time setup
if ($FirstTime) {
    Write-Header "Running First Time Setup"

    # Backend setup
    Write-Host "Installing backend dependencies..." -ForegroundColor Yellow
    $backend = Join-Path $ProjectRoot "backend"
    & python -m venv "$backend\.venv"
    & "$backend\.venv\Scripts\pip.exe" install --upgrade pip
    & "$backend\.venv\Scripts\pip.exe" install -r "$backend\requirements.txt"

    # Frontend setup
    Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
    $frontend = Join-Path $ProjectRoot "frontend"
    Push-Location $frontend
    & npm install
    Pop-Location

    # Database migrations
    Write-Host "Running migrations..." -ForegroundColor Yellow
    $backend = Join-Path $ProjectRoot "backend"
    & "$backend\.venv\Scripts\python.exe" -m app.migrations

    Write-Host "✓ First time setup complete" -ForegroundColor Green
}

# Start services based on mode
if ($Mode -eq "dev") {
    Write-Header "Starting Development Mode"

    Write-Host "Frontend:  http://localhost:5173" -ForegroundColor Cyan
    Write-Host "Backend:   http://127.0.0.1:8000" -ForegroundColor Cyan
    Write-Host "Docs:      http://127.0.0.1:8000/docs" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Opening terminals... (run each in separate window)" -ForegroundColor Yellow

    # Terminal 1: Backend
    $backendCmd = "cd `"$ProjectRoot\backend`" ; .\.venv\Scripts\Activate.ps1 ; python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd -WindowStyle Normal

    Start-Sleep -Seconds 2

    # Terminal 2: Frontend
    $frontendCmd = "cd `"$ProjectRoot\frontend`" ; npm run dev"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCmd -WindowStyle Normal

} else {
    Write-Header "Starting Production Mode"

    Write-Host "Building frontend..." -ForegroundColor Yellow
    $frontend = Join-Path $ProjectRoot "frontend"
    Push-Location $frontend
    & npm run build
    Pop-Location

    Write-Host "Starting services..." -ForegroundColor Yellow
    & "$ProjectRoot\scripts\start_local_system.ps1" -EnvironmentFile "$ProjectRoot\config\development.env"
}

Write-Header "Setup Complete"
Write-Host "✓ Project is ready!" -ForegroundColor Green
```

### Run It:

```powershell
# First time setup with development mode
.\QuickStart.ps1 -FirstTime -Mode dev

# Subsequent times (development)
.\QuickStart.ps1 -Mode dev

# Production mode
.\QuickStart.ps1 -Mode prod
```

---

## Verification

### 1. Check Backend Health

```powershell
curl http://127.0.0.1:8000/health
```

Expected response:

```json
{"status": "healthy"}
```

### 2. Access Frontend

```powershell
# Open in browser
start http://localhost:5173
```

### 3. View API Documentation

```powershell
# Open in browser
start http://127.0.0.1:8000/docs
```

### 4. Check Database

```powershell
cd d:\AUTO_QA_TESTING\backend
.\.venv\Scripts\Activate.ps1
python -c "from app.database import get_db; print('Database connected')"
```

---

## Troubleshooting

### Backend won't start

```powershell
# Activate venv
cd backend
.\.venv\Scripts\Activate.ps1

# Check Python packages
pip list

# Reinstall requirements
pip install --force-reinstall -r requirements.txt
```

### Frontend won't start

```powershell
cd frontend

# Clear node_modules
Remove-Item node_modules -Recurse
Remove-Item package-lock.json

# Reinstall
npm install

# Try dev server
npm run dev
```

### Port already in use

```powershell
# Check process using port 8000
netstat -ano | findstr :8000

# Check process using port 5173
netstat -ano | findstr :5173

# Kill process
taskkill /PID <PID> /F
```

### Permission denied

```powershell
# Allow PowerShell script execution
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

---

## Default Credentials After Setup

After creating an operator with `create_local_operator.ps1`:

| Property | Value |
| ---------- | ------- |
| **Role** | VIEWER, TESTER, APPROVER, or ADMIN |
| **Password** | Set during creation (min 12 characters) |
| **Session Duration** | 8 hours |
| **First Login** | Must change password |

---

## Environment Configuration

### Development Configuration (`config/development.env`)

```env
APP_ENV=development
DATABASE_URL=sqlite:///./data/autoqa-development.db
AUTOQA_DATA_ROOT=./data
AUTOQA_RUNTIME_ROOT=../runtime/development
AUTOQA_SAFE_MODE=true
AUTOQA_DEBUG=true
AUTOQA_ALLOW_PRODUCTION_EXECUTION=false
AUTOQA_FRONTEND_URL=http://127.0.0.1:5173
AUTOQA_COOKIE_SECURE=false
AUTOQA_PASSWORD_MAX_AGE_DAYS=0
```

---

## Quick Reference Commands

```powershell
# Backend commands
cd backend
.\.venv\Scripts\Activate.ps1              # Activate Python environment
python -m uvicorn app.main:app            # Start backend (dev)
python -m app.migrations                  # Run migrations
python -m pytest tests/                   # Run tests

# Frontend commands
cd frontend
npm install                               # Install dependencies
npm run dev                               # Start dev server
npm run build                             # Build for production
npm run preview                           # Preview production build
npm run lint                              # Check TypeScript

# Project commands
.\scripts\create_local_operator.ps1       # Create new user
.\scripts\verify_health.ps1               # Check system health
.\scripts\start_local_system.ps1          # Start all services
```

---

## Next Steps

1. ✅ Complete [Initial Setup](#initial-setup)
2. ✅ [Create ID & Password](#create-id--password)
3. ✅ [Activate Environments](#activate-environments)
4. ✅ [Run Frontend & Backend](#run-frontend--backend)
5. 📖 Read [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
6. 📖 Read [DEVELOPMENT_WORKFLOW.md](DEVELOPMENT_WORKFLOW.md)
7. 🧪 Run tests: `pytest` in backend
8. 🚀 Deploy using [LOCAL_RELEASE_OPERATIONS.md](LOCAL_RELEASE_OPERATIONS.md)

---

**Last Updated:** 2026-07-14  
**Version:** 1.0
