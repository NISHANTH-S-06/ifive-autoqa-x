$Script:ProjectRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))

function Update-AutoQaRuntimePaths {
  $configured = [Environment]::GetEnvironmentVariable('AUTOQA_RUNTIME_ROOT', 'Process')
  if ([string]::IsNullOrWhiteSpace($configured)) {
    $Script:RuntimeRoot = Join-Path $Script:ProjectRoot 'runtime'
  } elseif ([System.IO.Path]::IsPathRooted($configured)) {
    $Script:RuntimeRoot = [System.IO.Path]::GetFullPath($configured)
  } else {
    $Script:RuntimeRoot = [System.IO.Path]::GetFullPath((Join-Path (Join-Path $Script:ProjectRoot 'backend') $configured))
  }
  $Script:PidRoot = Join-Path $Script:RuntimeRoot 'pids'
  $Script:LogRoot = Join-Path $Script:RuntimeRoot 'logs'
}

Update-AutoQaRuntimePaths

function Initialize-AutoQaRuntime {
  New-Item -ItemType Directory -Force -Path $Script:RuntimeRoot, $Script:PidRoot, $Script:LogRoot | Out-Null
}

function Import-AutoQaEnvironment {
  param([string]$EnvironmentFile)
  if ([string]::IsNullOrWhiteSpace($EnvironmentFile)) {
    $candidate = Join-Path $Script:ProjectRoot '.env'
    if (-not (Test-Path -LiteralPath $candidate -PathType Leaf)) { return }
    $EnvironmentFile = $candidate
  }
  $resolved = [System.IO.Path]::GetFullPath($EnvironmentFile)
  if (-not (Test-Path -LiteralPath $resolved -PathType Leaf)) { throw 'Environment file does not exist.' }
  foreach ($line in Get-Content -LiteralPath $resolved) {
    $trimmed = $line.Trim()
    if (-not $trimmed -or $trimmed.StartsWith('#')) { continue }
    if ($trimmed -notmatch '^([A-Z][A-Z0-9_]*)=(.*)$') { throw 'Environment file contains an invalid setting line.' }
    $name = $Matches[1]
    $value = $Matches[2]
    if ($name -match '(PASSWORD|TOKEN|SECRET|API_KEY|AUTHORIZATION)' -and $name -ne 'AUTOQA_PASSWORD_MAX_AGE_DAYS') {
      throw "Secret-bearing setting $name is not accepted by release scripts."
    }
    [Environment]::SetEnvironmentVariable($name, $value, 'Process')
  }
  Update-AutoQaRuntimePaths
}

function Get-AutoQaPidPath {
  param([Parameter(Mandatory)][ValidatePattern('^[a-z-]+$')][string]$Service)
  return Join-Path $Script:PidRoot "$Service.json"
}

function Get-AutoQaPidRecord {
  param([Parameter(Mandatory)][string]$Service)
  $path = Get-AutoQaPidPath -Service $Service
  if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { return $null }
  try { return Get-Content -Raw -LiteralPath $path | ConvertFrom-Json } catch { Remove-Item -LiteralPath $path -Force; return $null }
}

function Test-AutoQaOwnedProcess {
  param([Parameter(Mandatory)]$Record)
  $process = Get-Process -Id $Record.pid -ErrorAction SilentlyContinue
  if (-not $process) { return $false }
  try {
    $actualStart = $process.StartTime.ToUniversalTime().ToString('o')
    $actualExecutable = [System.IO.Path]::GetFullPath($process.Path)
    $expectedExecutable = [System.IO.Path]::GetFullPath([string]$Record.executable)
    return $actualStart -eq $Record.start_time_utc -and $actualExecutable -eq $expectedExecutable -and -not [string]::IsNullOrWhiteSpace([string]$Record.expected_marker)
  } catch { return $false }
}

function Remove-AutoQaStalePid {
  param([Parameter(Mandatory)][string]$Service)
  $record = Get-AutoQaPidRecord -Service $Service
  if (-not $record) { return $null }
  if (Test-AutoQaOwnedProcess -Record $record) { return $record }
  Remove-Item -LiteralPath (Get-AutoQaPidPath -Service $Service) -Force -ErrorAction SilentlyContinue
  return $null
}

function Assert-AutoQaPortAvailable {
  param([Parameter(Mandatory)][ValidateRange(1024,65535)][int]$Port, [string]$Service)
  $listener = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
  if (-not $listener) {
    $active = [System.Net.NetworkInformation.IPGlobalProperties]::GetIPGlobalProperties().GetActiveTcpListeners() | Where-Object { $_.Port -eq $Port } | Select-Object -First 1
    if ($active) { throw "Port $Port is already occupied by a process not owned by this AutoQA runtime." }
    return
  }
  $record = if ($Service) { Get-AutoQaPidRecord -Service $Service } else { $null }
  if ($record -and $record.pid -eq $listener.OwningProcess -and (Test-AutoQaOwnedProcess -Record $record)) { return }
  throw "Port $Port is already occupied by a process not owned by this AutoQA runtime."
}

function Start-AutoQaService {
  param(
    [Parameter(Mandatory)][string]$Service,
    [Parameter(Mandatory)][string]$Executable,
    [Parameter(Mandatory)][string[]]$Arguments,
    [Parameter(Mandatory)][string]$WorkingDirectory,
    [Parameter(Mandatory)][string]$ExpectedMarker,
    [int]$Port = 0
  )
  Initialize-AutoQaRuntime
  $existing = Remove-AutoQaStalePid -Service $Service
  if ($existing) { Write-Host "$Service is already running (PID $($existing.pid))."; return }
  if ($Port) { Assert-AutoQaPortAvailable -Port $Port -Service $Service }
  if (-not (Test-Path -LiteralPath $Executable -PathType Leaf)) { throw "$Service executable is unavailable." }
  $stdout = Join-Path $Script:LogRoot "$Service.stdout.log"
  $stderr = Join-Path $Script:LogRoot "$Service.stderr.log"
  $process = Start-Process -FilePath $Executable -ArgumentList $Arguments -WorkingDirectory $WorkingDirectory -WindowStyle Hidden -RedirectStandardOutput $stdout -RedirectStandardError $stderr -PassThru
  Start-Sleep -Milliseconds 500
  if ($process.HasExited) { throw "$Service failed to start. Review its redacted runtime log." }
  $record = [ordered]@{
    service = $Service
    pid = $process.Id
    start_time_utc = $process.StartTime.ToUniversalTime().ToString('o')
    executable = [System.IO.Path]::GetFullPath($Executable)
    expected_marker = $ExpectedMarker
  }
  $record | ConvertTo-Json | Set-Content -LiteralPath (Get-AutoQaPidPath -Service $Service) -Encoding UTF8
  Write-Host "$Service started safely (PID $($process.Id))."
}

function Stop-AutoQaService {
  param([Parameter(Mandatory)][string]$Service)
  $path = Get-AutoQaPidPath -Service $Service
  $record = Get-AutoQaPidRecord -Service $Service
  if (-not $record) { Write-Host "$Service is not running."; return }
  if (-not (Test-AutoQaOwnedProcess -Record $record)) {
    Remove-Item -LiteralPath $path -Force -ErrorAction SilentlyContinue
    Write-Warning "$Service PID record was stale or did not belong to this project; no process was stopped."
    return
  }
  Stop-Process -Id $record.pid -ErrorAction Stop
  Remove-Item -LiteralPath $path -Force
  Write-Host "$Service stopped safely."
}
