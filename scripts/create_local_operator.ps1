$ErrorActionPreference = "Stop"
$python = Join-Path $PSScriptRoot "..\backend\.venv\Scripts\python.exe"
if (-not (Test-Path $python)) { throw "Backend virtual environment is missing." }
Push-Location (Join-Path $PSScriptRoot "..\backend")
try { & $python -m app.cli.create_operator } finally { Pop-Location }
