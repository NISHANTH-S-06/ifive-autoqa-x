# ============================================
# AutoQA Quick Start Script
# ============================================
# Usage:
#   .\QuickStart.ps1 -FirstTime -Mode dev
#   .\QuickStart.ps1 -Mode dev
#   .\QuickStart.ps1 -Mode prod

param(
    [string]$Mode = "dev",
    [switch]$FirstTime
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
$allGood = $true

if (Test-Command "python") {
    python --version
    Write-Host "[OK] Python found" -ForegroundColor Green
} else {
    Write-Host "[FAIL] Python not found. Install Python 3.9+" -ForegroundColor Red
    $allGood = $false
}

if (Test-Command "node") {
    node --version
    Write-Host "[OK] Node.js found" -ForegroundColor Green
} else {
    Write-Host "[FAIL] Node.js not found. Install Node.js 18+" -ForegroundColor Red
    $allGood = $false
}

if (Test-Command "npm") {
    npm --version
    Write-Host "[OK] npm found" -ForegroundColor Green
} else {
    Write-Host "[FAIL] npm not found. Install Node.js with npm" -ForegroundColor Red
    $allGood = $false
}

if (-not $allGood) {
    throw "Prerequisites not met. Please install missing dependencies."
}

# First time setup
if ($FirstTime) {
    Write-Header "Running First Time Setup"
    
    # Backend setup
    Write-Host "Installing backend dependencies..." -ForegroundColor Yellow
    $backend = Join-Path $ProjectRoot "backend"
    
    if (-not (Test-Path "$backend\.venv")) {
        Write-Host "Creating Python virtual environment..." -ForegroundColor Yellow
        & python -m venv "$backend\.venv"
    }
    
    Write-Host "Upgrading pip..." -ForegroundColor Yellow
    & "$backend\.venv\Scripts\pip.exe" install --upgrade pip -q
    
    Write-Host "Installing Python packages..." -ForegroundColor Yellow
    & "$backend\.venv\Scripts\pip.exe" install -r "$backend\requirements.txt" -q
    
    # Frontend setup
    Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
    $frontend = Join-Path $ProjectRoot "frontend"
    Push-Location $frontend
    & npm install -q
    Pop-Location
    
    # Database migrations
    Write-Host "Running database migrations..." -ForegroundColor Yellow
    $python = Join-Path $backend ".venv\Scripts\python.exe"
    Push-Location $backend
    try {
        $env:AUTOQA_ALEMBIC_DATABASE_URL = "sqlite:///$($ProjectRoot.Replace('\','/'))/backend/data/autoqa.db"
        $env:AUTOQA_ALEMBIC_ALLOW_ACTIVE_DATABASE = "true"
        & $python -m app.cli.migrate 2>&1 | Select-Object -First 5
        if ($LASTEXITCODE) { throw "Database migration failed." }
    } finally {
        Remove-Item Env:\AUTOQA_ALEMBIC_DATABASE_URL -ErrorAction SilentlyContinue
        Remove-Item Env:\AUTOQA_ALEMBIC_ALLOW_ACTIVE_DATABASE -ErrorAction SilentlyContinue
        Pop-Location
    }
    
    Write-Host "[OK] First time setup complete!" -ForegroundColor Green
}

# Create environment file if it doesn't exist
if (-not (Test-Path "$ProjectRoot\config\development.env")) {
    Write-Host "Creating development.env from example..." -ForegroundColor Yellow
    Copy-Item "$ProjectRoot\config\development.env.example" "$ProjectRoot\config\development.env"
    Write-Host "[OK] Config file created at config\development.env" -ForegroundColor Green
}

# Start services based on mode
if ($Mode -eq "dev") {
    Write-Header "Starting Development Mode"
    
    Write-Host ""
    Write-Host "Access Points:" -ForegroundColor Cyan
    Write-Host "  Frontend:  http://localhost:5173" -ForegroundColor Green
    Write-Host "  Backend:   http://127.0.0.1:8000" -ForegroundColor Green
    Write-Host "  API Docs:  http://127.0.0.1:8000/docs" -ForegroundColor Green
    Write-Host ""
    Write-Host "Starting services using start_all_fresh.ps1..." -ForegroundColor Yellow
    Write-Host ""
    
    & "$ProjectRoot\scripts\start_all_fresh.ps1"
    
    Write-Host ""
    Write-Host "[OK] All services started!" -ForegroundColor Green
    Write-Host "Open browser and navigate to: http://localhost:5173" -ForegroundColor Yellow
    
} elseif ($Mode -eq "prod") {
    Write-Header "Starting Production Mode"
    
    Write-Host "Building frontend..." -ForegroundColor Yellow
    $frontend = Join-Path $ProjectRoot "frontend"
    Push-Location $frontend
    & npm run build -q
    Pop-Location
    Write-Host "[OK] Frontend built" -ForegroundColor Green
    
    Write-Host "Starting services..." -ForegroundColor Yellow
    & "$ProjectRoot\scripts\start_local_system.ps1" -EnvironmentFile "$ProjectRoot\config\development.env"
    
} else {
    Write-Host "Unknown mode: $Mode. Use 'dev' or 'prod'" -ForegroundColor Red
    exit 1
}

Write-Header "Setup Complete!"
Write-Host "Your project is ready to go!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Create a user account: .\scripts\create_local_operator.ps1" -ForegroundColor White
Write-Host "2. Open: http://localhost:5173" -ForegroundColor White
Write-Host "3. Login with your credentials" -ForegroundColor White
Write-Host ""
