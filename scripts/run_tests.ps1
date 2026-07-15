param([switch]$SkipPlaywrightExecution)
$ErrorActionPreference = 'Stop'
$root = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$python = Join-Path $root 'backend\.venv\Scripts\python.exe'
Push-Location (Join-Path $root 'backend')
try {
  & $python -m compileall app tests
  if ($LASTEXITCODE) { throw 'Backend compileall failed.' }
  & $python -m pytest
  if ($LASTEXITCODE) { throw 'Backend tests failed.' }
} finally { Pop-Location }
Push-Location (Join-Path $root 'frontend')
try {
  npm.cmd run lint
  if ($LASTEXITCODE) { throw 'Frontend lint failed.' }
  npm.cmd run build
  if ($LASTEXITCODE) { throw 'Frontend build failed.' }
} finally { Pop-Location }
Push-Location (Join-Path $root 'qa')
try {
  npx.cmd tsc --noEmit
  if ($LASTEXITCODE) { throw 'QA TypeScript check failed.' }
  npx.cmd playwright test --project=chromium --list
  if ($LASTEXITCODE) { throw 'Playwright discovery failed.' }
  if (-not $SkipPlaywrightExecution) {
    npx.cmd playwright test --project=chromium --workers=1 --reporter=list
    if ($LASTEXITCODE) { throw 'Playwright execution failed.' }
  }
} finally { Pop-Location }
& (Join-Path $PSScriptRoot 'verify_project.ps1')

