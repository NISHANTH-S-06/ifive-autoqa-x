$ErrorActionPreference = 'Stop'
$root = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$stamp = (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssZ')
$destination = Join-Path $root "release\stage14\$stamp\iFive-AutoQA"
New-Item -ItemType Directory -Force -Path $destination | Out-Null

function Copy-ReleaseItem {
  param([Parameter(Mandatory)][string]$RelativePath)
  $source = Join-Path $root $RelativePath
  if (-not (Test-Path -LiteralPath $source)) { throw "Required release item is missing: $RelativePath" }
  $target = Join-Path $destination $RelativePath
  $parent = Split-Path -Parent $target
  New-Item -ItemType Directory -Force -Path $parent | Out-Null
  if (Test-Path -LiteralPath $source -PathType Container) {
    Copy-Item -LiteralPath $source -Destination $target -Recurse
  } else {
    Copy-Item -LiteralPath $source -Destination $target
  }
}

$items = @(
  'backend\app', 'backend\requirements.txt', 'backend\pytest.ini',
  'frontend\dist', 'frontend\package.json', 'frontend\package-lock.json',
  'qa\fixtures', 'qa\page-objects', 'qa\specs', 'qa\test-data', 'qa\tests', 'qa\package.json', 'qa\package-lock.json', 'qa\playwright.config.ts', 'qa\tsconfig.json', 'qa\static-server.mjs',
  'scripts\lib', 'scripts\backup_local.ps1', 'scripts\build_release.ps1', 'scripts\cleanup_local.ps1', 'scripts\create_local_operator.ps1', 'scripts\restore_local.ps1', 'scripts\run_all.ps1', 'scripts\run_backend.ps1', 'scripts\run_frontend.ps1', 'scripts\run_migrations.ps1', 'scripts\run_tests.ps1', 'scripts\start_backend.ps1', 'scripts\start_frontend.ps1', 'scripts\start_local_system.ps1', 'scripts\start_worker.ps1', 'scripts\stop_local_system.ps1', 'scripts\verify_health.ps1', 'scripts\verify_project.ps1',
  'config', 'docs\API_DOCUMENTATION.md', 'docs\DEVELOPMENT_WORKFLOW.md', 'docs\FINAL_UAT_CHECKLIST.md', 'docs\FULL_PROJECT_DEMO.md', 'docs\INSTALLATION.md', 'docs\LOCAL_RELEASE_OPERATIONS.md', 'docs\PRODUCT_TEST_MATRIX.md', 'docs\RELEASE_READINESS_AUDIT.md', 'docs\SECURITY_AND_SAFETY.md', 'docs\TEAM_LEAD_DEMO.md', '.env.example', 'README.md', 'ARCHITECTURE.md', 'REQUIREMENTS.md', 'SAFETY_RULES.md', 'TEST_STRATEGY.md'
)
foreach ($item in $items) { Copy-ReleaseItem -RelativePath $item }

Get-ChildItem -LiteralPath $destination -Recurse -Directory -Filter '__pycache__' | Remove-Item -Recurse -Force
Get-ChildItem -LiteralPath $destination -Recurse -File | Where-Object { $_.Extension -in @('.pyc','.pyo') } | Remove-Item -Force
$forbidden = @('.venv','node_modules','test-results','playwright-report','runtime','backups','logs','pids')
foreach ($name in $forbidden) {
  if (Get-ChildItem -LiteralPath $destination -Recurse -Force | Where-Object { $_.Name -eq $name }) { throw "Release contains forbidden item: $name" }
}
if (Get-ChildItem -LiteralPath $destination -Recurse -File | Where-Object { $_.Extension -in @('.db','.sqlite','.sqlite3','.log') -or $_.Name -eq '.env' }) { throw 'Release contains runtime data, logs, or environment secrets.' }
$secretHits = Get-ChildItem -LiteralPath $destination -Recurse -File | Select-String -Pattern '-----BEGIN [A-Z ]*PRIVATE KEY-----','\bsk-[A-Za-z0-9_-]{20,}','(?i)\bBearer\s+[A-Za-z0-9._~+/-]{16,}'
if ($secretHits) { throw 'Release secret scan detected credential-like material.' }

$manifest = [ordered]@{
  product = 'iFive AutoQA'
  release = 'Stage 14 local release'
  created_at = (Get-Date).ToUniversalTime().ToString('o')
  production_execution = 'disabled'
  real_target_execution = 'disabled-by-default'
  default_admin = $false
  package_root = 'iFive-AutoQA'
}
$manifest | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $destination 'release-manifest.json') -Encoding UTF8
$checksumPath = Join-Path $destination 'SHA256SUMS.txt'
$checksums = Get-ChildItem -LiteralPath $destination -Recurse -File | Where-Object { $_.FullName -ne $checksumPath } | Sort-Object FullName | ForEach-Object {
  $relative = $_.FullName.Substring($destination.Length + 1).Replace('\','/')
  "$((Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLower())  $relative"
}
$checksums | Set-Content -LiteralPath $checksumPath -Encoding ASCII
Write-Host "Release package prepared: $destination"
Write-Host "Checksum entries: $($checksums.Count)"
