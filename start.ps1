# ============================================
# AUTO QA - Startup Script
# Backend Port: 8300 | Frontend Port: 3300
# ============================================

$ErrorActionPreference = 'Continue'
$ProjectRoot = $PSScriptRoot

# Load environment variables if .env exists
$EnvFile = Join-Path $ProjectRoot ".env"
if (Test-Path $EnvFile) {
    Get-Content $EnvFile | ForEach-Object {
        $line = $_.Trim()
        if ($line -and -not $line.StartsWith("#") -and $line.Contains("=")) {
            $parts = $line.Split("=", 2)
            [Environment]::SetEnvironmentVariable($parts[0].Trim(), $parts[1].Trim(), 'Process')
        }
    }
}

$BackendPort  = if ($env:BACKEND_PORT)  { [int]$env:BACKEND_PORT }  else { 8300 }
$FrontendPort = if ($env:FRONTEND_PORT) { [int]$env:FRONTEND_PORT } else { 3300 }

$LogDir = Join-Path $ProjectRoot "runtime\logs"
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting AUTO QA Services..." -ForegroundColor Cyan
Write-Host "Backend Port:  $BackendPort" -ForegroundColor Yellow
Write-Host "Frontend Port: $FrontendPort" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan

# Stop any processes currently using target ports
foreach ($port in @($BackendPort, $FrontendPort)) {
    $conns = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($conns) {
        foreach ($conn in $conns) {
            $pidToKill = $conn.OwningProcess
            if ($pidToKill -gt 0) {
                Write-Host "Stopping process PID $pidToKill on port $port..." -ForegroundColor Yellow
                Stop-Process -Id $pidToKill -Force -ErrorAction SilentlyContinue
            }
        }
    }
}

$PythonExe = Join-Path $ProjectRoot "backend\.venv\Scripts\python.exe"
if (-not (Test-Path $PythonExe)) {
    $PythonExe = "python"
}

$BackendLog  = Join-Path $LogDir "backend.out.log"
$FrontendLog = Join-Path $LogDir "frontend.out.log"

$BackendDir = Join-Path $ProjectRoot "backend"
$FrontendDir = Join-Path $ProjectRoot "frontend"

# Launch Backend
Write-Host "Starting Backend API on http://127.0.0.1:$BackendPort..." -ForegroundColor Cyan
$bCmd = "`"$PythonExe`" -m uvicorn app.main:app --host 127.0.0.1 --port $BackendPort --app-dir `"$BackendDir`" --no-access-log"
Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{
    CommandLine = $bCmd
    CurrentDirectory = $BackendDir
} | Out-Null

# Launch Frontend
Write-Host "Starting Frontend UI on http://127.0.0.1:$FrontendPort..." -ForegroundColor Cyan
$ViteBin = Join-Path $FrontendDir "node_modules\vite\bin\vite.js"
$fCmd = "node.exe `"$ViteBin`" --port $FrontendPort --host 127.0.0.1 --strictPort"
Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{
    CommandLine = $fCmd
    CurrentDirectory = $FrontendDir
} | Out-Null


Start-Sleep -Seconds 3

Write-Host ""
Write-Host "[OK] AUTO QA Services Started Successfully!" -ForegroundColor Green
Write-Host "  Backend API:    http://127.0.0.1:$BackendPort" -ForegroundColor Green
Write-Host "  Health Endpoint: http://127.0.0.1:$BackendPort/api/health" -ForegroundColor Green
Write-Host "  Frontend App:   http://127.0.0.1:$FrontendPort" -ForegroundColor Green
Write-Host ""

