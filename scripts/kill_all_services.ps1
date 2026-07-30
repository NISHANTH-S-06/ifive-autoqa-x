# Kill All AutoQA Local Services (Ports 8000, 8001, 8002, 5173, 5174, 5175)
$ErrorActionPreference = 'Continue'

$ports = @(8000, 8001, 8002, 5173, 5174, 5175)

foreach ($port in $ports) {
    $connections = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($connections) {
        foreach ($conn in $connections) {
            $pidToKill = $conn.OwningProcess
            if ($pidToKill -gt 0) {
                try {
                    $proc = Get-Process -Id $pidToKill -ErrorAction SilentlyContinue
                    if ($proc) {
                        Write-Host "Stopping process $($proc.ProcessName) (PID $pidToKill) on port $port" -ForegroundColor Yellow
                        Stop-Process -Id $pidToKill -Force -ErrorAction SilentlyContinue
                    }
                } catch {
                    # Ignore
                }
            }
        }
    }
}

Write-Host "[OK] All local port processes stopped." -ForegroundColor Green
