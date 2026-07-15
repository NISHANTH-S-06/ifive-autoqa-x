# Final UAT Checklist

Status values are PASS, FAIL, or PENDING. Manual prerequisites must not be inferred from automated tests.

## Identity And Security

- [ ] PENDING - Persistent ADMIN login (`active_admin_count=0`).
- [ ] PENDING - Forced password change with an authorized persistent operator.
- [ ] PENDING - Session management with persistent operators.
- [ ] PENDING - ADMIN security UI with a persistent ADMIN.
- [x] PASS - Automated password policy, history, version invalidation, RBAC, CSRF, and audit-chain tests.

## Management Workflows

- [x] PASS - Test management and creator-separated approval.
- [x] PASS - Frozen-version manual execution.
- [ ] PENDING - Authorized real non-production target acceptance.
- [ ] PENDING - Authenticated iFive login; no safe ephemeral credential was supplied.
- [x] PASS - Local-fixture automated execution, worker, cancellation, timeout, retry, and artifacts.
- [x] PASS - Defect lifecycle, evidence, traceability, and retest.
- [x] PASS - Reports, bounded export, and saved definitions.

## Release Operations

- [x] PASS - Isolated backup and SHA-256 validation.
- [x] PASS - Isolated restore, pre-restore backup, and rollback safety.
- [x] PASS - Retention dry-run, confirmation, containment, and active-artifact protection.
- [x] PASS - Sanitized health and diagnostics.
- [x] PASS - Structured rotating logs and secret redaction.
- [x] PASS - Release package allowlist, exclusions, manifest, and checksums.
- [x] PASS - Responsive final dashboard at 320, 375, 768, 1024, and 1440 pixels.

## Final Manual Acceptance

- [ ] PENDING - Authorized person creates the first ADMIN interactively.
- [ ] PENDING - Authorized person supplies and approves a real non-production iFive target.
- [ ] PENDING - Authorized person supplies a safe ephemeral login mechanism and scope.
- [ ] PENDING - Release owner records operating-system backup permissions and recovery location.

