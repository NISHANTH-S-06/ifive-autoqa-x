<#
.SYNOPSIS
  Local service watchdog for iFive AutoQA X (Phase 6 audit follow-up).
  Monitors all 6 local ports and auto-restarts any service that dies.
  This is a local dev-convenience script only. Not a production supervisor.

.DESCRIPTION
  Ports monitored:
    8000  AutoQA backend        (backend, uvicorn)
    8001  Mock Task Portal API  (mock-task-portal/backend, uvicorn)
    8002  Demo Product API      (demo-product/backend, uvicorn)
    5173  AutoQA frontend       (frontend, vite)
    5174  Mock Task Portal UI   (mock-task-portal/frontend, vite)
    5175  Demo Product UI      (demo-product/frontend, vite)

.USAGE
  Run in its own terminal and leave it open:
    powershell -File scripts\watchdog_local_services.ps1
  Stop with Ctrl+C.
#>

param(
  [int]$IntervalSeconds = 20,
  [string]$RootPath = "D:\AUTO_QA_TESTING"
)

$ErrorActionPreference = 'Continue'
$PythonExe = Join-Path $RootPath "backend\.venv\Scripts\python.exe"
$LogDir = Join-Path $RootPath "runtime\watchdog"
New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
$LogFile = Join-Path $LogDir "watchdog.log"

function Write-Log([string]$message) {
  $line = "[{0}] {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $message
  Write-Host $line
  Add-Content -Path $LogFile -Value $line
}

$Services = @(
  @{ Name = "AutoQA backend";       Port = 8000; HealthPath = "/api/health"; Exe = $PythonExe; Args = "-m uvicorn app.main:app --host 127.0.0.1 --port 8000"; WorkDir = (Join-Path $RootPath "backend") },
  @{ Name = "Mock Task Portal API"; Port = 8001; HealthPath = "/api/health"; Exe = $PythonExe; Args = "-m uvicorn app.main:app --host 127.0.0.1 --port 8001"; WorkDir = (Join-Path $RootPath "mock-task-portal\backend") },
  @{ Name = "Demo Product API";     Port = 8002; HealthPath = "/api/health"; Exe = $PythonExe; Args = "-m uvicorn app.main:app --host 127.0.0.1 --port 8002"; WorkDir = (Join-Path $RootPath "demo-product\backend") },
  @{ Name = "AutoQA frontend";      Port = 5173; HealthPath = "/";           Exe = "npm.cmd";  Args = "run dev -- --port 5173 --host 127.0.0.1 --strictPort"; WorkDir = (Join-Path $RootPath "frontend") },
  @{ Name = "Mock Task Portal UI";  Port = 5174; HealthPath = "/";           Exe = "npm.cmd";  Args = "run dev -- --port 5174 --host 127.0.0.1 --strictPort"; WorkDir = (Join-Path $RootPath "mock-task-portal\frontend") },
  @{ Name = "Demo Product UI";      Port = 5175; HealthPath = "/";           Exe = "npm.cmd";  Args = "run dev -- --port 5175 --host 127.0.0.1 --strictPort"; WorkDir = (Join-Path $RootPath "demo-product\frontend") }
)

function Test-ServiceHealthy($svc) {
  try {
    $uri = "http://127.0.0.1:$($svc.Port)$($svc.HealthPath)"
    $resp = Invoke-WebRequest -Uri $uri -UseBasicParsing -TimeoutSec 5
    return ($resp.StatusCode -eq 200)
  } catch {
    if ($_.Exception.Response -and [int]$_.Exception.Response.StatusCode -eq 404) { return $true }
    return $false
  }
}

function Start-ServiceProcess($svc) {
  Write-Log "RESTARTING $($svc.Name) on port $($svc.Port)"
  Start-Process -FilePath $svc.Exe -ArgumentList $svc.Args -WorkingDirectory $svc.WorkDir -WindowStyle Hidden
}

Write-Log "Watchdog started. Interval=${IntervalSeconds}s. Root=$RootPath"

while ($true) {
  foreach ($svc in $Services) {
    $healthy = Test-ServiceHealthy $svc
    if (-not $healthy) {
      Write-Log "DOWN: $($svc.Name) (port $($svc.Port))"
      Start-ServiceProcess $svc
    }
  }
  Start-Sleep -Seconds $IntervalSeconds
}
