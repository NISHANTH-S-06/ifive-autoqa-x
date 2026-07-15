param([string]$EnvironmentFile)
& (Join-Path $PSScriptRoot 'start_local_system.ps1') -EnvironmentFile $EnvironmentFile

