# Start All AutoQA Local Services Fresh
$ErrorActionPreference = 'Continue'
$RootPath = "D:\AUTO_QA_TESTING"
$PythonExe = Join-Path $RootPath "backend\.venv\Scripts\python.exe"

Write-Host "Running database migrations..." -ForegroundColor Cyan
Push-Location (Join-Path $RootPath "backend")
try {
    & $PythonExe -m app.cli.migrate
} finally {
    Pop-Location
}

Write-Host "Starting AutoQA Backend (8000)..." -ForegroundColor Cyan
Start-Process -FilePath $PythonExe -ArgumentList "-m uvicorn app.main:app --app-dir `"$RootPath\backend`" --host 127.0.0.1 --port 8000" -WorkingDirectory (Join-Path $RootPath "backend") -WindowStyle Hidden

Write-Host "Starting Mock Task Portal API (8001)..." -ForegroundColor Cyan
Start-Process -FilePath $PythonExe -ArgumentList "-m uvicorn app.main:app --app-dir `"$RootPath\mock-task-portal\backend`" --host 127.0.0.1 --port 8001" -WorkingDirectory (Join-Path $RootPath "mock-task-portal\backend") -WindowStyle Hidden

Write-Host "Starting Demo Product API (8002)..." -ForegroundColor Cyan
Start-Process -FilePath $PythonExe -ArgumentList "-m uvicorn app.main:app --app-dir `"$RootPath\demo-product\backend`" --host 127.0.0.1 --port 8002" -WorkingDirectory (Join-Path $RootPath "demo-product\backend") -WindowStyle Hidden

Write-Host "Starting AutoQA Frontend (5173)..." -ForegroundColor Cyan
Start-Process -FilePath "npm.cmd" -ArgumentList "run dev -- --port 5173 --host 127.0.0.1 --strictPort" -WorkingDirectory (Join-Path $RootPath "frontend") -WindowStyle Hidden

Write-Host "Starting Mock Task Portal UI (5174)..." -ForegroundColor Cyan
Start-Process -FilePath "npm.cmd" -ArgumentList "run dev -- --port 5174 --host 127.0.0.1 --strictPort" -WorkingDirectory (Join-Path $RootPath "mock-task-portal\frontend") -WindowStyle Hidden

Write-Host "Starting Demo Product UI (5175)..." -ForegroundColor Cyan
Start-Process -FilePath "npm.cmd" -ArgumentList "run dev -- --port 5175 --host 127.0.0.1 --strictPort" -WorkingDirectory (Join-Path $RootPath "demo-product\frontend") -WindowStyle Hidden

Write-Host "[OK] All 6 local services started fresh." -ForegroundColor Green
