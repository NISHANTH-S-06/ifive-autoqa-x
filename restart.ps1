# ============================================
# AUTO QA - Restart Script
# ============================================

$ErrorActionPreference = 'Continue'
$ProjectRoot = $PSScriptRoot

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Restarting AUTO QA Services..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

& "$ProjectRoot\stop.ps1"
Start-Sleep -Seconds 2
& "$ProjectRoot\start.ps1"
