# Local Release Operations

## Install

Use Python 3.11+ and Node.js 20+ on Windows PowerShell. Install only from pinned local manifests:

```powershell
Set-Location <extracted-project-root>
cd backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
cd ..\frontend
npm.cmd ci
cd ..\qa
npm.cmd ci
npx.cmd playwright install chromium
```

No script creates an ADMIN, registers a target, installs Ollama, or runs an AI agent.

## Configure

Review one template under `config/`. Runtime scripts optionally read a root `.env`; secret-bearing variables are rejected. Local-release defaults keep debug, production execution, and real-target execution disabled while TLS verification remains enabled.

Configured SQLite and data paths must remain within `AUTOQA_DATA_ROOT`. Runtime PID/log/temp paths and backups must remain outside source and data directories.

## Migrate And Start

```powershell
.\scripts\run_migrations.ps1
cd frontend
npm.cmd run build
cd ..
.\scripts\start_local_system.ps1
.\scripts\verify_health.ps1
```

Individual commands are `start_backend.ps1`, `start_frontend.ps1`, and `start_worker.ps1`. Duplicate processes and occupied ports are rejected. Stop all project-owned services with `scripts/stop_local_system.ps1`. When an explicit environment file was used for startup, pass the same `-EnvironmentFile` value during shutdown.

## ADMIN Bootstrap

An authorized person must explicitly run `scripts/create_local_operator.ps1` and enter the password interactively. There are no default credentials. A bootstrap-created operator must change the password at first login.

## Backup And Restore

Run `scripts/backup_local.ps1` and type the requested confirmation. Backups are stored under the configured backup root, outside source/data directories. Each contains a SQLite online backup, evidence, execution artifacts, report exports, local Playwright run evidence, configuration templates, and a SHA-256 manifest. Plaintext credentials and active `.env` files are excluded.

Stop backend and worker before restoring, then run:

```powershell
.\scripts\restore_local.ps1 -BackupId AUTOQA-YYYYMMDDTHHMMSS-ffffffZ
```

Restore verifies identity, containment, every checksum, and SQLite integrity. It creates a backup of the active system first and rolls replacements back if an operation fails.

## Retention Cleanup

`scripts/cleanup_local.ps1` performs a dry-run. `scripts/cleanup_local.ps1 -Apply` requires typed confirmation. Confirmed cleanup can remove expired physical artifacts/evidence/exports, old connection checks, expired sessions, completed jobs, and old temporary runtime files.

Active-run artifacts, audit events, password history, test-case/target versions, defect history, and append-only records are never selected.

## Workflows

- Test management: author, review with a different operator, approve, then create frozen-version manual runs.
- Target management: register non-production metadata, submit, approve with a different operator, and perform approved-path checks.
- Automated execution: separately approve target execution, use approved frozen test versions, pass preflight, then queue to the single local worker.
- Defects: create from manual/automated failures, follow controlled lifecycle and retest, and preserve traceability.
- Reports: use database-authoritative filters; ADMIN may create bounded exports and saved report definitions.

## Troubleshooting

- Occupied port: stop the owning application or select another loopback port. Scripts never kill an unknown owner.
- Stale PID: rerun start/stop. Stale records are removed after ownership validation.
- Degraded health: inspect safe diagnostics for database, migrations, storage, disk, frontend, worker, and Chromium.
- Worker unavailable: run `start_worker.ps1` and verify its heartbeat.
- Chromium unavailable: run `npx.cmd playwright install chromium` from `qa`.
- Migration failure: stop services, create a backup, inspect redacted runtime logs, and rerun migrations.

## Known Limitations

- Local release is loopback-only and SQLite-only.
- One execution worker and one claimed job at a time are supported.
- Persistent ADMIN, real target, and authenticated iFive acceptance remain pending.
- Production execution remains blocked and cannot be enabled by environment configuration.
- No Ollama or AI-agent runtime is included in the release package.

## Release Package

Run `scripts/build_release.ps1` after frontend build and verification. The timestamped output under `release/stage14` includes an allowlisted file set, `release-manifest.json`, and `SHA256SUMS.txt`. It excludes dependencies, browser caches, test output, databases, backups, credentials, logs, user evidence, generated exports, and PID files.
