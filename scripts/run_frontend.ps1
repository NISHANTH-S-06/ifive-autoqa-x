param([string]$EnvironmentFile)
& (Join-Path $PSScriptRoot 'start_frontend.ps1') -EnvironmentFile $EnvironmentFile

