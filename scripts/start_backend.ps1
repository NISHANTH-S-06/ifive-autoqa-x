param([string]$EnvironmentFile, [ValidateRange(1024,65535)][int]$Port = 0)
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'lib\AutoQa.Runtime.ps1')
Import-AutoQaEnvironment -EnvironmentFile $EnvironmentFile
if (-not $Port) { $Port = if ($env:BACKEND_PORT) { [int]$env:BACKEND_PORT } else { 8300 } }
$backend = Join-Path $Script:ProjectRoot 'backend'
$python = Join-Path $backend '.venv\Scripts\python.exe'
Start-AutoQaService -Service 'backend' -Executable $python -Arguments @('-m','uvicorn','app.main:app','--host','127.0.0.1','--port',"$Port",'--app-dir',$backend,'--no-access-log') -WorkingDirectory $backend -ExpectedMarker $backend -Port $Port

