param([string]$EnvironmentFile, [ValidatePattern('^[A-Za-z0-9_-]{3,80}$')][string]$WorkerKey = 'local-release-worker')
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'lib\AutoQa.Runtime.ps1')
Import-AutoQaEnvironment -EnvironmentFile $EnvironmentFile
$backend = Join-Path $Script:ProjectRoot 'backend'
$python = Join-Path $backend '.venv\Scripts\python.exe'
Start-AutoQaService -Service 'worker' -Executable $python -Arguments @('-m','app.cli.worker','--worker-key',$WorkerKey,'--runtime-marker',$Script:ProjectRoot) -WorkingDirectory $backend -ExpectedMarker $Script:ProjectRoot

