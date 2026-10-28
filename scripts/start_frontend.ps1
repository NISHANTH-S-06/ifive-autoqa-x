param([string]$EnvironmentFile, [ValidateRange(1024,65535)][int]$Port = 0)
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'lib\AutoQa.Runtime.ps1')
Import-AutoQaEnvironment -EnvironmentFile $EnvironmentFile
if (-not $Port) { $Port = if ($env:FRONTEND_PORT) { [int]$env:FRONTEND_PORT } else { 3300 } }
$dist = Join-Path $Script:ProjectRoot 'frontend\dist'
$python = Join-Path $Script:ProjectRoot 'backend\.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath (Join-Path $dist 'index.html') -PathType Leaf)) { throw 'Frontend production build is missing. Run npm.cmd run build first.' }
Start-AutoQaService -Service 'frontend' -Executable $python -Arguments @('-m','app.cli.static_server','--port',"$Port",'--root',$dist,'--runtime-marker',$Script:ProjectRoot) -WorkingDirectory (Join-Path $Script:ProjectRoot 'backend') -ExpectedMarker $dist -Port $Port

