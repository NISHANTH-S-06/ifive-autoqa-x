param([string]$EnvironmentFile)
& (Join-Path $PSScriptRoot 'start_backend.ps1') -EnvironmentFile $EnvironmentFile

