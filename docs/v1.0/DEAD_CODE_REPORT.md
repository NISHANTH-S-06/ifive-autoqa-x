# DEAD_CODE_REPORT.md — iFive AutoQA X

Status: DOCUMENTATION ONLY. Nothing listed here has been deleted or modified.
Per project rule ("never remove any feature unless it is proven unused"), this
report exists to let you decide before any removal happens.

Method: cross-referenced every `app.include_router(...)` call in
`backend/app/main.py` (90 total) against every `import ... from './pages/...'`
in `frontend/src/App.tsx` (19 total) and every backend-endpoint reference in
`frontend/src/services/*.ts`. A router is marked ORPHANED only if no live page
or live service references its path — i.e., there is no code path from the
application's entry point that can ever reach it.

## Orphaned backend routers (64) — registered, but unreachable from the live UI

### Unlabeled block (21) — added before the explicit "Phase 13" comment marker

`release_readiness`, `autonomous_regression`, `knowledge_graph`, `digital_qa`,
`digital_twin`, `continuous_monitoring`, `predictive_quality`, `multi_reports`,
`experience_memory`, `pattern_recognition`, `test_evolution`, `root_cause_graph`,
`release_command_center`, `autonomous_monitoring_v2`, `onboarding`, `test_studio`,
`test_lab`, `data_factory`, `war_room`, `plugin_marketplace`, `integrations`

### `# Phase 13 – Enterprise Cloud Platform` (14)

`distributed_execution`, `cloud_browser_farm`, `execution_stream`, `observability`,
`enterprise_analytics`, `release_governance`, `compliance_center`, `api_hub`,
`marketplace_ecosystem`, `enterprise_devops`, `multi_region_cloud`,
`enterprise_security_center`, `ai_optimizer`, `executive_command_center`

### `# Phase 14 – Enterprise Autonomous AI QA Operating System (AI QA OS)` (10)

`enterprise_brain`, `workflows`, `business_process`, `incidents`, `governance`,
`forecast`, `executive_advisor`, `knowledge_universe`, `report_factory`, `optimization_v2`

### `# Phase 15 – Autonomous Enterprise Software Quality Intelligence Platform` (9)

`software_graph`, `change_impact`, `code_review`, `coverage`, `release_intelligence`,
`defects_hub`, `engineering`, `knowledge_lake`, `mission_control`

### `# Phase 16 – Enterprise Autonomous Software Engineering Intelligence Platform` (10)

`knowledge_lake_v2`, `requirements`, `traceability`, `architecture`, `code_quality`,
`release_certification`, `observability_ai`, `customer_intelligence`, `policies`,
`sdlc_orchestrator`

Each of the above has a corresponding `app/services/*.py`, `app/models/*.py` (in most
cases), and `backend/tests/test_*.py` file that is exercised only by its own isolated
test — never by an end-to-end path a real user can take.

## Orphaned frontend pages (~40)

Every page file in `frontend/src/pages/` NOT in this live list:
Dashboard, TaskImports, TestPlans, ApprovalQueue, AutomatedRuns, AdvancedValidation,
VisualRegression, Evidence, Defects, Reports, LocalSchedules, Projects, AuditLogs,
Settings, CompanyTasks, MyTasks, Users, EnterpriseManagement, EnterpriseDiscovery,
EnterpriseCopilot.

Confirmed orphaned (verified present on disk, verified absent from `App.tsx` imports):
`AIAgentsMarketplacePage.tsx`, `AnalyticsCenterPage.tsx`, `ArchitectureIntelligencePage.tsx`,
`BrowserFarmPage.tsx`, `BusinessProcessCenterPage.tsx`, `ChangeImpactCenterPage.tsx`,
`CloudDashboardPage.tsx`, `CodeQualityGovernorPage.tsx`, `CodeReviewCenterPage.tsx`,
`ComplianceCenterPage.tsx`, `CoverageIntelligencePage.tsx`, `CustomerExperiencePage.tsx`,
`DefectIntelligencePage.tsx`, `DevOpsCenterPage.tsx`, `EngineeringAnalyticsPage.tsx`,
`EnterpriseBrainPage.tsx`, `EnterpriseKnowledgeUniversePage.tsx`, `ExecutionCenterPage.tsx`,
`ExecutiveAdvisorPage.tsx`, `ExecutiveCommandCenterPage.tsx`, `ForecastCenterPage.tsx`,
`GovernanceCenterPage.tsx`, `IncidentCommandCenterPage.tsx`, `KnowledgeLakePage.tsx`,
`KnowledgeLakeV2Page.tsx`, `MarketplaceCenterPage.tsx`, `MissionControlPage.tsx`,
`ObservabilityCenterPage.tsx`, `ObservabilityPage.tsx`, `OptimizationCenterV2Page.tsx`,
`PairQAEngineerPage.tsx`, `PolicyCenterPage.tsx`, `ReleaseCertificationPage.tsx`,
`ReleaseGovernancePage.tsx`, `ReleaseIntelligencePage.tsx`, `RequirementCenterPage.tsx`,
`SDLCCenterPage.tsx`, `SecurityCenterPage.tsx`, `SoftwareGraphPage.tsx`,
`TraceabilityMatrixPage.tsx`, `WorkerManagementPage.tsx`, `WorkflowComposerPage.tsx`

## Orphaned frontend services (4)

`phase13Service.ts`, `phase14Service.ts`, `phase15Service.ts`, `phase16Service.ts`
— each exclusively called by the orphaned pages above.

## NOT included in this report (needs a separate, careful pass)

- Corresponding `backend/app/models/*.py` — not yet individually cross-referenced;
  some orphaned routers may share models/tables with live features (would need
  per-model FK/import checking before any removal).

- Corresponding `backend/tests/test_*.py` files for the 64 orphaned routers —
  not yet enumerated by exact filename.

- `release/stage14/` (63 snapshots) and pytest tmp directories — these are disk-space
  debt, not dead *code*, but are safe, zero-risk deletion candidates whenever you want
  them cleaned (they are build outputs / test scratch data, not source).

## Explicitly NOT done

No file has been deleted, moved, or modified as part of this report. No `import`
statement has been removed. No router has been unregistered from `main.py`.
