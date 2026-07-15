param([Parameter(Mandatory)][ValidatePattern('^AUTOQA-[0-9]{8}T[0-9]{6}-[0-9]{6}Z$')][string]$BackupId, [string]$EnvironmentFile)
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'lib\AutoQa.Runtime.ps1')
Import-AutoQaEnvironment -EnvironmentFile $EnvironmentFile
foreach ($service in 'backend','worker') {
  if (Remove-AutoQaStalePid -Service $service) { throw 'Stop the local AutoQA system before restore.' }
}
$backend = Join-Path $Script:ProjectRoot 'backend'
Push-Location $backend
try {
  & (Join-Path $backend '.venv\Scripts\python.exe') -m app.cli.maintenance restore $BackupId
  if ($LASTEXITCODE) { throw 'Restore command failed.' }
} finally { Pop-Location }
