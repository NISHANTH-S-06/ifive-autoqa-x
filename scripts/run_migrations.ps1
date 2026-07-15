param([string]$EnvironmentFile)
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'lib\AutoQa.Runtime.ps1')
Import-AutoQaEnvironment -EnvironmentFile $EnvironmentFile
$backend = Join-Path $Script:ProjectRoot 'backend'
$python = Join-Path $backend '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $python -PathType Leaf)) { throw 'Backend virtual environment is missing.' }
Push-Location $backend
try { & $python -m app.cli.migrate; if ($LASTEXITCODE) { throw 'Migration command failed.' } } finally { Pop-Location }

