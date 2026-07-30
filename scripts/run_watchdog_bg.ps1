# Background Watchdog Launcher for iFive AutoQA X Services
$ErrorActionPreference = 'Stop'
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$WatchdogScript = Join-Path $ScriptDir "watchdog_local_services.ps1"

Write-Host "Starting AutoQA Service Watchdog in background..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-File", "$WatchdogScript" -WindowStyle Hidden
Write-Host "[OK] Watchdog actively monitoring ports 8000, 8001, 8002, 5173, 5174, 5175." -ForegroundColor Green
