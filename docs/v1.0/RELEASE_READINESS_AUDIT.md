# Stage 14 Release Readiness Audit

Audit date: 2026-07-13

## Confirmed Ready

- Stages 1-13 APIs, RBAC, CSRF, session security, audit-chain protection, immutable histories, URL policy, DNS pinning, execution preflight, dangerous-action blocking, artifact limits, report limits, and formula-safe exports are present.
- SQLite is the only supported local release database and all migrations are repeatable at startup or through `scripts/run_migrations.ps1`.
- Frontend and QA dependency manifests are locked; backend Python dependencies are version-pinned.
- Evidence, execution artifacts, Playwright runs, and report exports use generated or validated relative paths and size limits.
- No default ADMIN or credentials exist. Production execution is blocked in code.

## Gaps Found And Resolved

- Environment settings lacked release-profile validation and configurable storage roots.
- Startup and shutdown scripts did not manage ports, ownership, duplicate processes, PID files, or complete-system lifecycle.
- No explicit database backup, checksum validation, rollback-safe restore, retention preview, or cleanup command existed.
- Health exposed only basic process state; worker, queue, migration, storage, disk, frontend, and Chromium checks were missing.
- Application logging was not structured, rotated, bounded, or centrally redacted.
- There was no allowlisted local release package or final UAT checklist.
- Existing environment examples referenced AI settings and a placeholder test password; these were removed.

## Security Risks

- Local HTTP means `AUTOQA_COOKIE_SECURE=false`; bind only to loopback. HTTPS remains a future prerequisite before non-loopback access.
- `AUTOQA_ALLOW_REAL_TARGET_EXECUTION` is false by default. Enabling it requires separate authorization and does not bypass target approval, execution approval, DNS pinning, or production blocking.
- SQLite backups contain password hashes and application metadata. Treat backup directories as sensitive local files even though plaintext credentials are prohibited.
- A machine administrator can alter local files or process state. Operating-system account and disk protections remain external controls.

## Deployment And Data-Loss Risks

- Restore requires all backend and worker processes to be stopped. An existing-database safety backup is created before replacement.
- Disk exhaustion can interrupt database or artifact writes. Diagnostics warn at the configured free-space threshold.
- SQLite supports concurrent reads but serializes writes. One execution-worker concurrency remains the supported local-release topology.
- Artifact cleanup is irreversible after confirmation; dry-run is the default and metadata/history records are preserved.

## Manual Prerequisites

- Persistent ADMIN login acceptance: pending because `active_admin_count=0`.
- Real non-production target acceptance: pending because no authorized target has been supplied.
- Authenticated iFive workflow acceptance: pending because no safe ephemeral login credential has been supplied.
- The local operator must install pinned dependencies and Playwright Chromium, choose a reviewed environment profile, and protect runtime/backup folders.

## Files Requiring Change

Changes are limited to configuration, startup, diagnostics, safe logging, maintenance services, release scripts, release documentation, the final readiness UI, and Stage 14 tests. No Stage 1-13 immutable-history schema is replaced.

