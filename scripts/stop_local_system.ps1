param([string]$EnvironmentFile)
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'lib\AutoQa.Runtime.ps1')
Import-AutoQaEnvironment -EnvironmentFile $EnvironmentFile
Initialize-AutoQaRuntime
Stop-AutoQaService -Service 'worker'
Stop-AutoQaService -Service 'frontend'
Stop-AutoQaService -Service 'backend'
