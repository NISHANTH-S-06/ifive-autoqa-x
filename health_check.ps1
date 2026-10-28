# ============================================
# AUTO QA - Health Check Script
# Backend Port: 8300 | Frontend Port: 3300
# Health Endpoint: /api/health
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

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Checking AUTO QA Services Health..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$backendHealthy = $false
$frontendHealthy = $false

# 1. Backend /api/health check
$backendUrl = "http://127.0.0.1:$BackendPort/api/health"
Write-Host "Checking Backend API Health at $backendUrl..." -NoNewline
try {
    $backendRes = Invoke-WebRequest -Uri $backendUrl -Method Get -TimeoutSec 5 -UseBasicParsing
    if ($backendRes.StatusCode -eq 200) {
        $backendHealthy = $true
        Write-Host " [OK] (HTTP 200)" -ForegroundColor Green
    } else {
        Write-Host " [FAIL] (HTTP $($backendRes.StatusCode))" -ForegroundColor Red
    }
} catch {
    Write-Host " [FAIL] ($_)" -ForegroundColor Red
}

# 2. Frontend web app check
$frontendUrl = "http://127.0.0.1:$FrontendPort"
Write-Host "Checking Frontend App at $frontendUrl..." -NoNewline
try {
    $frontendRes = Invoke-WebRequest -Uri $frontendUrl -Method Get -TimeoutSec 5 -UseBasicParsing
    if ($frontendRes.StatusCode -eq 200) {
        $frontendHealthy = $true
        Write-Host " [OK] (HTTP 200)" -ForegroundColor Green
    } else {
        Write-Host " [FAIL] (HTTP $($frontendRes.StatusCode))" -ForegroundColor Red
    }
} catch {
    Write-Host " [FAIL] ($_)" -ForegroundColor Red
}

Write-Host ""
if ($backendHealthy -and $frontendHealthy) {
    Write-Host "[SUCCESS] All AUTO QA services are HEALTHY and accessible!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "[ERROR] One or more AUTO QA services failed health check." -ForegroundColor Red
    exit 1
}
