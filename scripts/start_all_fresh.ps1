# Start All AutoQA Local Services Fresh
$ErrorActionPreference = 'Continue'
$RootPath = Split-Path -Parent $PSScriptRoot
$PythonExe = Join-Path $RootPath "backend\.venv\Scripts\python.exe"
$LogDir = Join-Path $RootPath "runtime\logs"

if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

Write-Host "Stopping any existing local services..." -ForegroundColor Cyan
& (Join-Path $PSScriptRoot "kill_all_services.ps1")

Write-Host "Running database migrations..." -ForegroundColor Cyan
Push-Location (Join-Path $RootPath "backend")
try {
    & $PythonExe -m app.cli.migrate
} finally {
    Pop-Location
}

Write-Host "Starting AutoQA Backend (8300)..." -ForegroundColor Cyan
Start-Process -FilePath $PythonExe -ArgumentList @('-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', '8300', '--app-dir', "$RootPath\backend", '--no-access-log') -WorkingDirectory "$RootPath\backend" -WindowStyle Hidden -RedirectStandardOutput "$LogDir\backend.out.log" -RedirectStandardError "$LogDir\backend.err.log"

Write-Host "Starting Mock Task Portal API (8001)..." -ForegroundColor Cyan
Start-Process -FilePath $PythonExe -ArgumentList @('-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', '8001', '--app-dir', "$RootPath\mock-task-portal\backend", '--no-access-log') -WorkingDirectory "$RootPath\mock-task-portal\backend" -WindowStyle Hidden -RedirectStandardOutput "$LogDir\mock_api.out.log" -RedirectStandardError "$LogDir\mock_api.err.log"

Write-Host "Starting Demo Product API (8002)..." -ForegroundColor Cyan
Start-Process -FilePath $PythonExe -ArgumentList @('-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', '8002', '--app-dir', "$RootPath\demo-product\backend", '--no-access-log') -WorkingDirectory "$RootPath\demo-product\backend" -WindowStyle Hidden -RedirectStandardOutput "$LogDir\demo_api.out.log" -RedirectStandardError "$LogDir\demo_api.err.log"

Write-Host "Starting AutoQA Frontend (3300)..." -ForegroundColor Cyan
Start-Process -FilePath "npm.cmd" -ArgumentList @('run', 'dev', '--', '--port', '3300', '--host', '127.0.0.1', '--strictPort') -WorkingDirectory "$RootPath\frontend" -WindowStyle Hidden -RedirectStandardOutput "$LogDir\frontend.out.log" -RedirectStandardError "$LogDir\frontend.err.log"


Write-Host "Starting Mock Task Portal UI (5174)..." -ForegroundColor Cyan
Start-Process -FilePath "npm.cmd" -ArgumentList @('run', 'dev', '--', '--port', '5174', '--host', '127.0.0.1', '--strictPort') -WorkingDirectory "$RootPath\mock-task-portal\frontend" -WindowStyle Hidden -RedirectStandardOutput "$LogDir\mock_ui.out.log" -RedirectStandardError "$LogDir\mock_ui.err.log"

Write-Host "Starting Demo Product UI (5175)..." -ForegroundColor Cyan
Start-Process -FilePath "npm.cmd" -ArgumentList @('run', 'dev', '--', '--port', '5175', '--host', '127.0.0.1', '--strictPort') -WorkingDirectory "$RootPath\demo-product\frontend" -WindowStyle Hidden -RedirectStandardOutput "$LogDir\demo_ui.out.log" -RedirectStandardError "$LogDir\demo_ui.err.log"

Write-Host "[OK] All 6 local services started fresh." -ForegroundColor Green
