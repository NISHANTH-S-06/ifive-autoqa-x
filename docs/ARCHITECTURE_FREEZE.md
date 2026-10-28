# ARCHITECTURE_FREEZE.md — iFive AutoQA X

Status: **ACTIVE BASELINE** as of this document's creation. This is the reference
all subsequent Enterprise Stabilization Sprint work (Steps 3-15) must operate against.

## Why this exists

`PROJECT_STRUCTURE.md` (Inventory) and `DEAD_CODE_REPORT.md` (Classification) proved,
with direct code evidence, that `backend/app/main.py` registers 90 routers but only 26
are reachable from the live application, and `frontend/src/pages/` contains ~59 page
files but only 19 are ever imported by `App.tsx`. Without freezing this boundary
explicitly, every subsequent cleanup/refactor step risks either (a) silently treating
orphaned scaffolding as product surface worth preserving/refactoring, or (b) scope
creeping back into "make it more enterprise" additions mid-sprint — the exact pattern
that produced the 64-router split in the first place.

## Frozen scope: what counts as "the product" for this sprint

### In scope (26 backend routers / 19 frontend pages) — Version 1.0.0 Release Candidate surface

| Frontend page | Backend router(s) |
| --- | --- |
| DashboardPage | dashboard, results |
| TaskImportsPage | task_imports, company_tasks |
| TestPlansPage | test_plans, test_management |
| ApprovalQueuePage | test_plans, test_management |
| AutomatedRunsPage | automated_execution |
| AdvancedValidationPage | advanced_validation |
| VisualRegressionPage | visual_regression |
| EvidencePage | automated_execution, results |
| DefectsPage | defects |
| ReportsPage | reports |
| LocalSchedulesPage | local_schedules |
| ProjectsPage | projects, connection_targets |
| AuditLogsPage | audit |
| SettingsPage | operators, security, system |
| CompanyTasksPage | company_tasks |
| MyTasksPage | company_tasks |
| UsersPage | operators |
| EnterpriseManagementPage | enterprise |
| EnterpriseDiscoveryPage | discovery |
| EnterpriseCopilotPage | copilot |
| (cross-cutting) | health, auth, agents, ai, test_runs |

These 26 routers, their models, services, repositories, schemas, and the 19 live pages
plus their 26 supporting components and 12 live service files (`api.ts`, `auth.ts`,
`automatedExecution.ts`, `companyTasks.ts`, `connectionTargets.ts`, `defects.ts`,
`reports.ts`, `system.ts`, `testManagement.ts`, `testPlans.ts`, `testRuns.ts`,
`visualRegressionService.ts`) are the **only** surface Steps 3-15 (structure refactor,
backend/frontend cleanup, API/DB/security/performance audits, dependency cleanup,
test cleanup, code quality) will touch.

### Frozen out of scope (64 backend routers / ~40 frontend pages / 4 frontend services)

Everything enumerated by name in `DEAD_CODE_REPORT.md`. **No refactor, standardization,
security hardening, performance optimization, or dependency change will be applied to
this code during this sprint.** It is not deleted. It is not modified. It is not
audited further until you make an explicit decision on it (wire in, or remove).

## Rules for the remainder of this sprint

1. Every Step 3-15 report must state which of the two scopes above it covers.
2. If a Step 3-15 task would naturally touch orphaned code (e.g., a dependency used by
   both live and orphaned routers), that dependency is documented but not changed until
   the orphaned-code decision is made separately.

3. No new "enterprise/AI/autonomous/intelligence"-style modules are added during this
   sprint. This sprint is stabilization only, per the original instruction ("Do NOT
   implement Phase 17", "Do NOT begin Phase 7" in earlier authorized turns).

4. This freeze does not expire automatically. It stays in force until you explicitly
   revise it.

## Sign-off

Proposed by: Claude (this session), based on direct code evidence in
`PROJECT_STRUCTURE.md` and `DEAD_CODE_REPORT.md`.
Adopted: per your instruction to proceed with Inventory → Classification → Freeze → Cleanup.
