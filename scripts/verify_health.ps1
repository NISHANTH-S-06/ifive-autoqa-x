param([ValidateRange(1024,65535)][int]$BackendPort = 8000, [ValidateRange(1024,65535)][int]$FrontendPort = 5173)
$ErrorActionPreference = 'Stop'
$health = Invoke-RestMethod -Uri "http://127.0.0.1:$BackendPort/health" -TimeoutSec 5
$frontend = Invoke-WebRequest -UseBasicParsing -Uri "http://127.0.0.1:$FrontendPort" -TimeoutSec 5
if ($health.status -notin @('ok','degraded')) { throw 'Backend health response is invalid.' }
if ($frontend.StatusCode -ne 200) { throw 'Frontend health check failed.' }
Write-Host "Backend: $($health.status); database: $($health.database.ready); migrations: $($health.database.migrations_current); frontend: available"
Write-Host "Worker heartbeat: $($health.worker.heartbeat_ok); queued jobs: $($health.queue.queued); disk warning: $($health.disk.warning); Chromium: $($health.playwright.chromium_available)"

