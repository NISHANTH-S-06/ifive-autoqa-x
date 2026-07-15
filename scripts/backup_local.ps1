param([string]$EnvironmentFile)
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'lib\AutoQa.Runtime.ps1')
Import-AutoQaEnvironment -EnvironmentFile $EnvironmentFile
$backend = Join-Path $Script:ProjectRoot 'backend'
Push-Location $backend
try {
  & (Join-Path $backend '.venv\Scripts\python.exe') -m app.cli.maintenance backup
  if ($LASTEXITCODE) { throw 'Backup command failed.' }
} finally { Pop-Location }
