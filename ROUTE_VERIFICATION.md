# Route Verification — iFive AutoQA Platform

> **Last updated:** 2026-07-29 | **Backend:** FastAPI on 127.0.0.1:8000 | **Frontend:** Vite on 127.0.0.1:5173

All frontend API calls go through Vite proxy `/api → http://127.0.0.1:8000`.  
Phase 16 routers use `/api/...` prefix hard-coded in the router (not applied by `include_router`).  
All other routers use `prefix='/api'` applied at `include_router` time.

---

## Core Platform Routes

| Router File | API Prefix | HTTP Methods | Frontend Page/Service | Status |
|-------------|-----------|--------------|----------------------|--------|
| `health.py` | `/api/health` | GET | `services/auth.ts` (health check) | ✅ ACTIVE |
| `auth.py` | `/api/auth/*` | GET, POST, PATCH | `services/auth.ts` | ✅ ACTIVE |
| `operators.py` | `/api/operators/*` | GET, POST, PATCH, DELETE | `UsersPage.tsx` | ✅ ACTIVE |
| `audit.py` | `/api/audit/*` | GET | `AuditLogsPage.tsx` | ✅ ACTIVE |
| `projects.py` | `/api/projects/*` | GET, POST, PATCH, DELETE | `ProjectsPage.tsx`, `projectStore` | ✅ ACTIVE |
| `dashboard.py` | `/api/dashboard/*` | GET | `DashboardPage.tsx` | ✅ ACTIVE |
| `results.py` | `/api/results/*` | GET | `EvidencePage.tsx` | ✅ ACTIVE |
| `reports.py` | `/api/reports/*` | GET, POST | `ReportsPage.tsx`, `ManagementReportsCore.tsx` | ✅ ACTIVE |
| `security.py` | `/api/security/*` | GET, POST | `SettingsPage.tsx`, `SecurityCenterPage.tsx` | ✅ ACTIVE |

---

## Test Management Routes

| Router File | API Prefix | HTTP Methods | Frontend Page/Service | Status |
|-------------|-----------|--------------|----------------------|--------|
| `test_management.py` | `/api/test-management/*` | GET, POST, PATCH, DELETE | `TestManagementCore.tsx`, `ApprovalQueuePage.tsx` | ✅ ACTIVE |
| `test_plans.py` | `/api/test-plans/*` | GET, POST, PATCH | `TestPlansPage.tsx`, `TestPlanEditor.tsx` | ✅ ACTIVE |
| `test_runs.py` | `/api/test-runs/*` | GET, POST, PATCH | `AutomatedRunsCore.tsx` | ✅ ACTIVE |
| `task_imports.py` | `/api/task-imports/*` | GET, POST, DELETE | `TaskImportsPage.tsx`, `TaskImportsCore.tsx` | ✅ ACTIVE |
| `company_tasks.py` | `/api/company-tasks/*` | GET, POST, PATCH, DELETE | `CompanyTasksPage.tsx`, `MyTasksPage.tsx` | ✅ ACTIVE |
| `defects.py` | `/api/defects/*` | GET, POST, PATCH, DELETE | `DefectsPage.tsx`, `DefectsCore.tsx` | ✅ ACTIVE |

---

## Automation & Execution Routes

| Router File | API Prefix | HTTP Methods | Frontend Page/Service | Status |
|-------------|-----------|--------------|----------------------|--------|
| `automated_execution.py` | `/api/automated-execution/*` | GET, POST, PATCH | `AutomatedRunsPage.tsx`, `AutomatedRunsCore.tsx` | ✅ ACTIVE |
| `connection_targets.py` | `/api/connection-targets/*` | GET, POST, PATCH, DELETE | `ConnectionTargetsCore.tsx` | ✅ ACTIVE |
| `visual_regression.py` | `/api/visual-regression/*` | GET, POST, PATCH, DELETE | `VisualRegressionPage.tsx` | ✅ ACTIVE |
| `advanced_validation.py` | `/api/advanced-validation/*` | GET, POST, PATCH, DELETE | `AdvancedValidationPage.tsx`, `AdvancedValidationCore.tsx` | ✅ ACTIVE |
| `local_schedules.py` | `/api/local-schedules/*` | GET, POST, PATCH, DELETE | `LocalSchedulesPage.tsx`, `LocalSchedulesCore.tsx` | ✅ ACTIVE |
| `system.py` | `/api/system/*` | GET, POST | `SettingsPage.tsx`, `system.ts` | ✅ ACTIVE |
| `discovery.py` | `/api/discovery/*` | GET, POST | `EnterpriseDiscoveryPage.tsx` | ✅ ACTIVE |

---

## AI & Intelligence Routes

| Router File | API Prefix | HTTP Methods | Frontend Page/Service | Status |
|-------------|-----------|--------------|----------------------|--------|
| `ai.py` | `/api/ai/*` | GET, POST | `phase13Service.ts`, AI pages | ✅ ACTIVE |
| `agents.py` | `/api/agents/*` | GET, POST | `AIAgentsMarketplacePage.tsx` | ✅ ACTIVE |
| `copilot.py` | `/api/copilot/*` | POST | `EnterpriseCopilotPage.tsx` | ✅ ACTIVE |
| `knowledge_graph.py` | `/api/knowledge-graph/*` | GET | `KnowledgeGraphViewerPage.tsx` | ✅ ACTIVE |
| `digital_twin.py` | `/api/digital-twin/*` | GET | `DigitalQAEngineerPage.tsx` | ✅ ACTIVE |
| `continuous_monitoring.py` | `/api/monitoring/*` | GET | `ContinuousMonitoringPage.tsx` | ✅ ACTIVE |
| `predictive_quality.py` | `/api/predictive/*` | GET | `PredictionCenterPage.tsx` | ✅ ACTIVE |
| `autonomous_regression.py` | `/api/autonomous-regression/*` | GET, POST | `AutonomousRegressionPage.tsx` | ✅ ACTIVE |
| `autonomous_monitoring_v2.py` | `/api/autonomous-monitoring/*` | GET | `ContinuousMonitoringPage.tsx` | ✅ ACTIVE |
| `digital_qa.py` | `/api/digital-qa/*` | GET, POST | `DigitalQAEngineerPage.tsx` | ✅ ACTIVE |
| `experience_memory.py` | `/api/experience-memory/*` | GET | `AIMemoryCenterPage.tsx` | ✅ ACTIVE |
| `pattern_recognition.py` | `/api/pattern-recognition/*` | GET | `PatternRecognitionPage.tsx` | ✅ ACTIVE |
| `test_evolution.py` | `/api/test-evolution/*` | GET | `SelfEvolutionDashboardPage.tsx` | ✅ ACTIVE |
| `root_cause_graph.py` | `/api/root-cause/*` | GET | Backend internal | ✅ ACTIVE |

---

## Enterprise Platform Routes (Phase 13)

| Router File | API Prefix | HTTP Methods | Frontend Page | Status |
|-------------|-----------|--------------|--------------|--------|
| `distributed_execution.py` | `/api/distributed-execution/*` | GET, POST | `ExecutionCenterPage.tsx` | ✅ ACTIVE |
| `cloud_browser_farm.py` | `/api/browser-farm/*` | GET, POST | `BrowserFarmPage.tsx` | ✅ ACTIVE |
| `execution_stream.py` | `/api/execution-stream/*` | GET | `ExecutionCenterPage.tsx` | ✅ ACTIVE |
| `observability.py` | `/api/observability/*` | GET | `ObservabilityPage.tsx` | ✅ ACTIVE |
| `enterprise_analytics.py` | `/api/enterprise-analytics/*` | GET | `AnalyticsCenterPage.tsx` | ✅ ACTIVE |
| `release_governance.py` | `/api/release-governance/*` | GET, POST | `ReleaseGovernancePage.tsx` | ✅ ACTIVE |
| `compliance_center.py` | `/api/compliance/*` | GET | `ComplianceCenterPage.tsx` | ✅ ACTIVE |
| `api_hub.py` | `/api/api-hub/*` | GET | `MarketplaceCenterPage.tsx` | ✅ ACTIVE |
| `marketplace_ecosystem.py` | `/api/marketplace/*` | GET | `MarketplaceCenterPage.tsx` | ✅ ACTIVE |
| `enterprise_devops.py` | `/api/enterprise-devops/*` | GET | `DevOpsCenterPage.tsx` | ✅ ACTIVE |
| `multi_region_cloud.py` | `/api/multi-region/*` | GET | `CloudDashboardPage.tsx` | ✅ ACTIVE |
| `enterprise_security_center.py` | `/api/enterprise-security/*` | GET | `SecurityCenterPage.tsx` | ✅ ACTIVE |
| `ai_optimizer.py` | `/api/ai-optimizer/*` | GET, POST | `WorkerManagementPage.tsx` | ✅ ACTIVE |
| `executive_command_center.py` | `/api/executive-command/*` | GET | `ExecutiveCommandCenterPage.tsx` | ✅ ACTIVE |

---

## AI QA Operating System Routes (Phase 14)

| Router File | API Prefix | HTTP Methods | Frontend Page | Status |
|-------------|-----------|--------------|--------------|--------|
| `enterprise_brain.py` | `/api/enterprise-brain/*` | GET, POST | `EnterpriseBrainPage.tsx` | ✅ ACTIVE |
| `workflows.py` | `/api/workflows/*` | GET, POST | `WorkflowComposerPage.tsx` | ✅ ACTIVE |
| `business_process.py` | `/api/business-process/*` | GET | `BusinessProcessCenterPage.tsx` | ✅ ACTIVE |
| `incidents.py` | `/api/incidents/*` | GET, POST | `IncidentCommandCenterPage.tsx` | ✅ ACTIVE |
| `governance.py` | `/api/governance/*` | GET | `GovernanceCenterPage.tsx` | ✅ ACTIVE |
| `forecast.py` | `/api/forecast/*` | GET | `ForecastCenterPage.tsx` | ✅ ACTIVE |
| `executive_advisor.py` | `/api/executive-advisor/*` | GET, POST | `ExecutiveAdvisorPage.tsx` | ✅ ACTIVE |
| `knowledge_universe.py` | `/api/knowledge-universe/*` | GET | `EnterpriseKnowledgeUniversePage.tsx` | ✅ ACTIVE |
| `report_factory.py` | `/api/report-factory/*` | GET, POST | `ExecutiveAnalyticsPage.tsx` | ✅ ACTIVE |
| `optimization_v2.py` | `/api/optimization-v2/*` | GET, POST | `OptimizationCenterV2Page.tsx` | ✅ ACTIVE |

---

## Software Quality Intelligence Routes (Phase 15)

| Router File | API Prefix | HTTP Methods | Frontend Page | Status |
|-------------|-----------|--------------|--------------|--------|
| `software_graph.py` | `/api/software-graph/*` | GET | `SoftwareGraphPage.tsx` | ✅ ACTIVE |
| `change_impact.py` | `/api/change-impact/*` | GET, POST | `ChangeImpactCenterPage.tsx` | ✅ ACTIVE |
| `code_review.py` | `/api/code-review/*` | GET, POST | `CodeReviewCenterPage.tsx` | ✅ ACTIVE |
| `coverage.py` | `/api/coverage/*` | GET | `CoverageIntelligencePage.tsx` | ✅ ACTIVE |
| `release_intelligence.py` | `/api/release-intelligence/*` | GET | `ReleaseIntelligencePage.tsx` | ✅ ACTIVE |
| `defects_hub.py` | `/api/defects-hub/*` | GET | `DefectIntelligencePage.tsx` | ✅ ACTIVE |
| `engineering.py` | `/api/engineering/*` | GET | `EngineeringAnalyticsPage.tsx` | ✅ ACTIVE |
| `knowledge_lake.py` | `/api/knowledge-lake/*` | GET | `KnowledgeLakePage.tsx` | ✅ ACTIVE |
| `mission_control.py` | `/api/mission-control/*` | GET | `MissionControlPage.tsx` | ✅ ACTIVE |

---

## Engineering Intelligence Routes (Phase 16)

> **Note:** Phase 16 routers use a custom prefix built into the router (e.g., `APIRouter(prefix="/api/knowledge-lake-v2")`). They are registered via `app.include_router(router)` without an additional prefix in `main.py`.

| Router File | API Prefix | HTTP Methods | Frontend Page | Status |
|-------------|-----------|--------------|--------------|--------|
| `knowledge_lake_v2.py` | `/api/knowledge-lake-v2/*` | GET, POST | `KnowledgeLakeV2Page.tsx` | ✅ ACTIVE |
| `requirements.py` | `/api/requirements/*` | GET, POST | `RequirementCenterPage.tsx` | ✅ ACTIVE |
| `traceability.py` | `/api/traceability/*` | GET, POST | `TraceabilityMatrixPage.tsx` | ✅ ACTIVE |
| `architecture.py` | `/api/architecture/*` | GET, POST | `ArchitectureIntelligencePage.tsx` | ✅ ACTIVE |
| `code_quality.py` | `/api/code-quality/*` | GET, POST | `CodeQualityGovernorPage.tsx` | ✅ ACTIVE |
| `release_certification.py` | `/api/release-certification/*` | GET, POST | `ReleaseCertificationPage.tsx` | ✅ ACTIVE |
| `observability_ai.py` | `/api/observability-ai/*` | GET | `ObservabilityCenterPage.tsx` | ✅ ACTIVE |
| `customer_intelligence.py` | `/api/customer-intelligence/*` | GET | `CustomerExperiencePage.tsx` | ✅ ACTIVE |
| `policies.py` | `/api/policies/*` | GET, POST | `PolicyCenterPage.tsx` | ✅ ACTIVE |
| `sdlc_orchestrator.py` | `/api/sdlc/*` | GET, POST | `SDLCCenterPage.tsx`, `ExecutiveDecisionCenterPage.tsx` | ✅ ACTIVE |

---

## Additional Enterprise Routes

| Router File | API Prefix | HTTP Methods | Frontend Page | Status |
|-------------|-----------|--------------|--------------|--------|
| `enterprise.py` | `/api/enterprise/*` | GET, POST | `EnterpriseManagementPage.tsx` | ✅ ACTIVE |
| `onboarding.py` | `/api/onboarding/*` | GET, POST | `ProjectOnboardingWizardPage.tsx` | ✅ ACTIVE |
| `test_studio.py` | `/api/test-studio/*` | GET, POST | `ZeroCodeTestStudioPage.tsx` | ✅ ACTIVE |
| `test_lab.py` | `/api/test-lab/*` | GET, POST | `AutonomousTestLabPage.tsx` | ✅ ACTIVE |
| `data_factory.py` | `/api/data-factory/*` | GET, POST | `TestDataFactoryPage.tsx` | ✅ ACTIVE |
| `war_room.py` | `/api/war-room/*` | GET | `ReleaseWarRoomPage.tsx` | ✅ ACTIVE |
| `plugin_marketplace.py` | `/api/plugins/*` | GET | `PluginMarketplacePage.tsx` | ✅ ACTIVE |
| `integrations.py` | `/api/integrations/*` | GET | `EnterpriseIntegrationsPage.tsx` | ✅ ACTIVE |
| `release_readiness.py` | `/api/release-readiness/*` | GET | `ReleaseReadinessPage.tsx` | ✅ ACTIVE |
| `release_command_center.py` | `/api/release-command/*` | GET | `ReleaseCommandCenterPage.tsx` | ✅ ACTIVE |
| `multi_reports.py` | `/api/multi-reports/*` | GET, POST | `ReportsPage.tsx` | ✅ ACTIVE |

---

## Route Summary

| Category | Count |
|----------|-------|
| Core platform routes | 9 |
| Test management routes | 6 |
| Automation & execution routes | 7 |
| AI & intelligence routes | 14 |
| Phase 13 enterprise cloud routes | 14 |
| Phase 14 AI OS routes | 10 |
| Phase 15 quality intelligence routes | 9 |
| Phase 16 engineering intelligence routes | 10 |
| Additional enterprise routes | 11 |
| **Total API router files** | **90** |

---

## Frontend Module ↔ Sidebar Key ↔ Backend Route Mapping

| `ModuleKey` | Sidebar Label | Primary Backend Prefix |
|-------------|--------------|----------------------|
| `dashboard` | Dashboard | `/api/dashboard` |
| `release-war-room` | Release War Room | `/api/war-room` |
| `release-command-center` | Release Command Center | `/api/release-command` |
| `self-evolution-dashboard` | Self Evolution Dashboard | `/api/test-evolution` |
| `ai-memory-center` | AI Memory Center | `/api/experience-memory` |
| `pattern-recognition` | Pattern Recognition | `/api/pattern-recognition` |
| `prediction-center` | Prediction Center | `/api/predictive` |
| `knowledge-graph-viewer` | Knowledge Graph Viewer | `/api/knowledge-graph` |
| `optimization-center` | Optimization Center | `/api/ai-optimizer` |
| `executive-analytics` | Executive Analytics | `/api/report-factory` |
| `project-onboarding` | Onboarding Wizard | `/api/onboarding` |
| `zero-code-studio` | Zero-Code Test Studio | `/api/test-studio` |
| `autonomous-test-lab` | Autonomous Test Lab | `/api/test-lab` |
| `data-factory` | Test Data Factory | `/api/data-factory` |
| `plugin-marketplace` | Plugin Marketplace | `/api/plugins` |
| `enterprise-integrations` | Enterprise Integrations | `/api/integrations` |
| `execution-center` | Execution Center | `/api/distributed-execution` |
| `browser-farm` | Cloud Browser Farm | `/api/browser-farm` |
| `worker-management` | AI Optimizer & Workers | `/api/ai-optimizer` |
| `cloud-dashboard` | Cloud Dashboard | `/api/multi-region` |
| `analytics-center` | Analytics Center | `/api/enterprise-analytics` |
| `release-governance` | Release Governance | `/api/release-governance` |
| `compliance-center` | Compliance Center | `/api/compliance` |
| `security-center` | Security Center | `/api/enterprise-security` |
| `marketplace-center` | Enterprise Marketplace | `/api/marketplace` |
| `devops-center` | DevOps Center | `/api/enterprise-devops` |
| `observability` | Observability Platform | `/api/observability` |
| `executive-command-center` | Global Command Center | `/api/executive-command` |
| `enterprise-brain` | AI Enterprise Brain | `/api/enterprise-brain` |
| `workflow-composer` | Workflow Composer | `/api/workflows` |
| `business-process-center` | Business Process Hub | `/api/business-process` |
| `incident-command-center` | Incident Commander | `/api/incidents` |
| `forecast-center` | AI Forecast Center | `/api/forecast` |
| `governance-center` | Governance Center | `/api/governance` |
| `knowledge-universe` | Knowledge Universe | `/api/knowledge-universe` |
| `executive-advisor` | AI Executive Advisor | `/api/executive-advisor` |
| `ai-agents-marketplace` | AI Agents Marketplace | `/api/agents` |
| `optimization-center-v2` | Optimization Engine V2 | `/api/optimization-v2` |
| `software-graph` | Software Intel Graph | `/api/software-graph` |
| `change-impact-center` | Change Impact Center | `/api/change-impact` |
| `code-review-center` | AI Code Reviewer | `/api/code-review` |
| `coverage-intelligence` | Coverage Intelligence | `/api/coverage` |
| `release-intelligence` | Release Intelligence | `/api/release-intelligence` |
| `defect-intelligence` | Defect Intelligence | `/api/defects-hub` |
| `engineering-analytics` | Engineering Analytics | `/api/engineering` |
| `knowledge-lake` | Knowledge Lake | `/api/knowledge-lake` |
| `mission-control` | Executive Mission Control | `/api/mission-control` |
| `pair-qa-engineer` | AI Pair QA Engineer | `/api/ai` |
| `knowledge-lake-v2` | Knowledge Lake V2 | `/api/knowledge-lake-v2` |
| `requirement-center` | Requirement Intelligence | `/api/requirements` |
| `traceability-matrix` | Traceability Matrix | `/api/traceability` |
| `architecture-intelligence` | Architecture Intelligence | `/api/architecture` |
| `code-quality-governor` | Code Quality Governor | `/api/code-quality` |
| `release-certification` | Release Certification | `/api/release-certification` |
| `observability-center` | Observability Center | `/api/observability-ai` |
| `customer-experience` | Customer Experience | `/api/customer-intelligence` |
| `policy-center` | Policy Engine | `/api/policies` |
| `sdlc-center` | Autonomous SDLC | `/api/sdlc` |
| `executive-decision-center` | Executive Decisions | `/api/sdlc` |
| `digital-qa` | AI Digital QA Engineer | `/api/digital-qa` |
| `executive-intelligence` | Executive Intelligence | `/api/enterprise-analytics` |
| `continuous-monitoring` | Autonomous Monitoring | `/api/monitoring` |
| `ai-copilot` | AI Copilot | `/api/copilot` |
| `release-readiness` | Release Readiness | `/api/release-readiness` |
| `autonomous-regression` | Autonomous Regression | `/api/autonomous-regression` |
| `enterprise-discovery` | AI Flow Discovery | `/api/discovery` |
| `enterprise-mgmt` | Enterprise Setup | `/api/enterprise` |
| `company-tasks` | Company Tasks | `/api/company-tasks` |
| `my-tasks` | My Tasks | `/api/company-tasks` |
| `task-imports` | Task Imports | `/api/task-imports` |
| `test-plans` | Test Plans | `/api/test-plans` |
| `approval-queue` | Approval Queue | `/api/test-management` |
| `automated-runs` | Automated Runs | `/api/automated-execution` |
| `visual-regression` | Visual Regression | `/api/visual-regression` |
| `advanced-validation` | Advanced Validation | `/api/advanced-validation` |
| `evidence` | Evidence | `/api/results` |
| `defects` | Defects | `/api/defects` |
| `reports` | Reports | `/api/reports` |
| `schedules` | Local Schedules | `/api/local-schedules` |
| `projects` | Projects | `/api/projects` |
| `audit-logs` | Audit Logs | `/api/audit` |
| `users` | Users | `/api/operators` |
| `settings` | Settings | `/api/system`, `/api/security` |
