param([switch]$Apply, [string]$EnvironmentFile)
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'lib\AutoQa.Runtime.ps1')
Import-AutoQaEnvironment -EnvironmentFile $EnvironmentFile
$backend = Join-Path $Script:ProjectRoot 'backend'
$arguments = @('-m','app.cli.maintenance','cleanup')
if ($Apply) { $arguments += '--apply' }
Push-Location $backend
try {
  & (Join-Path $backend '.venv\Scripts\python.exe') @arguments
  if ($LASTEXITCODE) { throw 'Cleanup command failed.' }
} finally { Pop-Location }
