$ErrorActionPreference = 'Stop'
$root = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$requiredPaths = @(
  'frontend\package.json', 'frontend\dist\index.html', 'backend\requirements.txt',
  'backend\app\config.py', 'backend\app\services\backup_service.py', 'backend\app\services\retention_service.py',
  'qa\playwright.config.ts', 'config\local-release.env.example', 'docs\FINAL_UAT_CHECKLIST.md',
  'scripts\start_local_system.ps1', 'scripts\stop_local_system.ps1', 'scripts\build_release.ps1'
)
foreach ($path in $requiredPaths) {
  if (-not (Test-Path -LiteralPath (Join-Path $root $path))) { throw "Missing required path: $path" }
}
if (Test-Path -LiteralPath (Join-Path $root 'data\autoqa.db')) { throw 'Accidental root data\autoqa.db must remain absent.' }
Write-Host 'iFive AutoQA Stage 14 project verification passed.'

