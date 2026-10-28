# ============================================
# AUTO QA - Shutdown Script
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

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Stopping AUTO QA Services..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$stopped = 0
foreach ($port in @($BackendPort, $FrontendPort)) {
    $conns = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($conns) {
        foreach ($conn in $conns) {
            $pidToKill = $conn.OwningProcess
            if ($pidToKill -gt 0) {
                try {
                    $proc = Get-Process -Id $pidToKill -ErrorAction SilentlyContinue
                    $procName = if ($proc) { $proc.ProcessName } else { "PID $pidToKill" }
                    Write-Host "Stopping $procName (PID $pidToKill) on port $port..." -ForegroundColor Yellow
                    Stop-Process -Id $pidToKill -Force -ErrorAction SilentlyContinue
                    $stopped++
                } catch {
                    # Ignore
                }
            }
        }
    } else {
        Write-Host "No process listening on port $port." -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "[OK] Stopped $stopped process(es). All AUTO QA ports released." -ForegroundColor Green
Write-Host ""
