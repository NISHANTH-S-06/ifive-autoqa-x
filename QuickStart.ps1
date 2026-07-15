# ============================================
# AutoQA Quick Start Script
# ============================================
# Usage:
#   .\QuickStart.ps1 -FirstTime -Mode dev
#   .\QuickStart.ps1 -Mode dev
#   .\QuickStart.ps1 -Mode prod

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
Write-Header "🔍 Checking Prerequisites"
$allGood = $true

if (Test-Command "python") {
    python --version
    Write-Host "✓ Python found" -ForegroundColor Green
} else {
    Write-Host "✗ Python not found. Install Python 3.9+" -ForegroundColor Red
    $allGood = $false
}

if (Test-Command "node") {
    node --version
    Write-Host "✓ Node.js found" -ForegroundColor Green
} else {
    Write-Host "✗ Node.js not found. Install Node.js 18+" -ForegroundColor Red
    $allGood = $false
}

if (Test-Command "npm") {
    npm --version
    Write-Host "✓ npm found" -ForegroundColor Green
} else {
    Write-Host "✗ npm not found. Install Node.js with npm" -ForegroundColor Red
    $allGood = $false
}

if (-not $allGood) {
    throw "Prerequisites not met. Please install missing dependencies."
}

# First time setup
if ($FirstTime) {
    Write-Header "📦 Running First Time Setup"
    
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
    & $python -m app.migrations 2>&1 | Select-Object -First 5
    
    Write-Host "✓ First time setup complete!" -ForegroundColor Green
}

# Create environment file if it doesn't exist
if (-not (Test-Path "$ProjectRoot\config\development.env")) {
    Write-Host "Creating development.env from example..." -ForegroundColor Yellow
    Copy-Item "$ProjectRoot\config\development.env.example" "$ProjectRoot\config\development.env"
    Write-Host "✓ Config file created at config\development.env" -ForegroundColor Green
}

# Start services based on mode
if ($Mode -eq "dev") {
    Write-Header "🚀 Starting Development Mode"
    
    Write-Host ""
    Write-Host "Access Points:" -ForegroundColor Cyan
    Write-Host "  Frontend:  http://localhost:5173" -ForegroundColor Green
    Write-Host "  Backend:   http://127.0.0.1:8000" -ForegroundColor Green
    Write-Host "  API Docs:  http://127.0.0.1:8000/docs" -ForegroundColor Green
    Write-Host ""
    Write-Host "⚠ Opening new terminal windows for each service..." -ForegroundColor Yellow
    Write-Host ""
    
    # Terminal 1: Backend
    Write-Host "Terminal 1: Starting Backend (FastAPI)..." -ForegroundColor Cyan
    $backendCmd = @"
`$ErrorActionPreference = 'Stop'
cd `"$ProjectRoot\backend`"
.\.venv\Scripts\Activate.ps1
Write-Host 'Backend starting on http://127.0.0.1:8000' -ForegroundColor Green
Write-Host 'Press Ctrl+C to stop' -ForegroundColor Yellow
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
"@
    
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd -WindowStyle Normal
    Start-Sleep -Seconds 3
    
    # Terminal 2: Frontend
    Write-Host "Terminal 2: Starting Frontend (Vite)..." -ForegroundColor Cyan
    $frontendCmd = @"
`$ErrorActionPreference = 'Stop'
cd `"$ProjectRoot\frontend`"
Write-Host 'Frontend starting on http://localhost:5173' -ForegroundColor Green
Write-Host 'Press Ctrl+C to stop' -ForegroundColor Yellow
npm run dev
"@
    
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCmd -WindowStyle Normal
    
    Write-Host ""
    Write-Host "✓ Services started in new windows" -ForegroundColor Green
    Write-Host "Open browser and navigate to: http://localhost:5173" -ForegroundColor Yellow
    
} elseif ($Mode -eq "prod") {
    Write-Header "🏭 Starting Production Mode"
    
    Write-Host "Building frontend..." -ForegroundColor Yellow
    $frontend = Join-Path $ProjectRoot "frontend"
    Push-Location $frontend
    & npm run build -q
    Pop-Location
    Write-Host "✓ Frontend built" -ForegroundColor Green
    
    Write-Host "Starting services..." -ForegroundColor Yellow
    & "$ProjectRoot\scripts\start_local_system.ps1" -EnvironmentFile "$ProjectRoot\config\development.env"
    
} else {
    Write-Host "Unknown mode: $Mode. Use 'dev' or 'prod'" -ForegroundColor Red
    exit 1
}

Write-Header "✅ Setup Complete!"
Write-Host "Your project is ready to go!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Create a user account: .\scripts\create_local_operator.ps1" -ForegroundColor White
Write-Host "2. Open: http://localhost:5173" -ForegroundColor White
Write-Host "3. Login with your credentials" -ForegroundColor White
Write-Host ""
