param([string]$EnvironmentFile)
$ErrorActionPreference = 'Stop'
& (Join-Path $PSScriptRoot 'start_backend.ps1') -EnvironmentFile $EnvironmentFile
& (Join-Path $PSScriptRoot 'start_frontend.ps1') -EnvironmentFile $EnvironmentFile
& (Join-Path $PSScriptRoot 'start_worker.ps1') -EnvironmentFile $EnvironmentFile
Start-Sleep -Seconds 1
& (Join-Path $PSScriptRoot 'verify_health.ps1')

