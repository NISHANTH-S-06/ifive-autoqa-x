# 5-service orchestrator script
$ErrorActionPreference = "Stop"

Write-Host "Stopping existing services on ports 8000, 8001, 8002, 5174, 5175..."
foreach ($port in 8000, 8001, 8002, 5174, 5175) {
    $conns = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    foreach ($conn in $conns) {
        if ($conn.State -eq 'Listen') {
            Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue
        }
    }
}

Write-Host "Starting services..."
$procs = @()

$procs += Start-Process -FilePath ".\backend\.venv\Scripts\python.exe" -ArgumentList "-m uvicorn app.main:app --host 127.0.0.1 --port 8000" -WorkingDirectory ".\backend" -PassThru -NoNewWindow
$procs += Start-Process -FilePath ".\backend\.venv\Scripts\python.exe" -ArgumentList "-m uvicorn app.main:app --host 127.0.0.1 --port 8001" -WorkingDirectory ".\mock-task-portal\backend" -PassThru -NoNewWindow
$procs += Start-Process -FilePath ".\backend\.venv\Scripts\python.exe" -ArgumentList "-m uvicorn app.main:app --host 127.0.0.1 --port 8002" -WorkingDirectory ".\demo-product\backend" -PassThru -NoNewWindow

$procs += Start-Process -FilePath "npm.cmd" -ArgumentList "run dev -- --port 5174 --host 127.0.0.1 --strictPort" -WorkingDirectory ".\mock-task-portal\frontend" -PassThru -NoNewWindow
$procs += Start-Process -FilePath "npm.cmd" -ArgumentList "run dev -- --port 5175 --host 127.0.0.1 --strictPort" -WorkingDirectory ".\demo-product\frontend" -PassThru -NoNewWindow

Write-Host "Waiting for health endpoints..."
Start-Sleep -Seconds 10
foreach ($port in 8000, 8001, 8002) {
    $res = Invoke-WebRequest -Uri "http://127.0.0.1:$port/api/health" -UseBasicParsing -ErrorAction SilentlyContinue
    if ($res.StatusCode -ne 200) { Write-Error "Port $port health check failed" }
}
foreach ($port in 5174, 5175) {
    $res = Invoke-WebRequest -Uri "http://127.0.0.1:$port/" -UseBasicParsing -ErrorAction SilentlyContinue
    if ($res.StatusCode -ne 200) { Write-Error "Port $port health check failed" }
}

Write-Host "Running Playwright Tests..."
$testResult = 0
try {
    $env:CI = "true"
    $env:PW_TEST_HTML_REPORT_OPEN = "never"
    Set-Location .\qa
    npx playwright test tests/phase3-task-connector.spec.ts --project=chromium --workers=1
} catch {
    $testResult = 1
} finally {
    Set-Location ..
}

Write-Host "Stopping services..."
foreach ($p in $procs) {
    Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue
}

exit $testResult
