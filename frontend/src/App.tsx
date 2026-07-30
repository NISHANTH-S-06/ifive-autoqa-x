import React, { type FormEvent, useEffect, useRef, useState } from 'react';
import { AuthContext } from './authContext';
import { AppShell } from './layouts/AppShell';
import type { ModuleKey } from './components/layout/Sidebar';
import { ProjectProvider } from './stores/projectStore';
import { RequiredPasswordChange } from './components/PasswordControls';
import { login, logout, restoreSession } from './services/auth';
import type { Operator } from './types/auth';

import { DashboardPage } from './pages/DashboardPage';
import { TaskImportsPage } from './pages/TaskImportsPage';
import { TestPlansPage } from './pages/TestPlansPage';
import { ApprovalQueuePage } from './pages/ApprovalQueuePage';
import { AutomatedRunsPage } from './pages/AutomatedRunsPage';
import { AdvancedValidationPage } from './pages/AdvancedValidationPage';
import { VisualRegressionPage } from './pages/VisualRegressionPage';
import { EvidencePage } from './pages/EvidencePage';
import { DefectsPage } from './pages/DefectsPage';
import { ReportsPage } from './pages/ReportsPage';
import { LocalSchedulesPage } from './pages/LocalSchedulesPage';
import { ProjectsPage } from './pages/ProjectsPage';
import { AuditLogsPage } from './pages/AuditLogsPage';
import { SettingsPage } from './pages/SettingsPage';
import { CompanyTasksPage } from './pages/CompanyTasksPage';
import { MyTasksPage } from './pages/MyTasksPage';
import { UsersPage } from './pages/UsersPage';
import { EnterpriseManagementPage } from './pages/EnterpriseManagementPage';
import { EnterpriseDiscoveryPage } from './pages/EnterpriseDiscoveryPage';
import { EnterpriseCopilotPage } from './pages/EnterpriseCopilotPage';
import { ReleaseReadinessPage } from './pages/ReleaseReadinessPage';
import { AutonomousRegressionPage } from './pages/AutonomousRegressionPage';
import { DigitalQAEngineerPage } from './pages/DigitalQAEngineerPage';
import { ExecutiveIntelligenceDashboardPage } from './pages/ExecutiveIntelligenceDashboardPage';
import { ContinuousMonitoringPage } from './pages/ContinuousMonitoringPage';
import { AIMemoryCenterPage } from './pages/AIMemoryCenterPage';
import { PatternRecognitionPage } from './pages/PatternRecognitionPage';
import { PredictionCenterPage } from './pages/PredictionCenterPage';
import { ReleaseCommandCenterPage } from './pages/ReleaseCommandCenterPage';
import { KnowledgeGraphViewerPage } from './pages/KnowledgeGraphViewerPage';
import { OptimizationCenterPage } from './pages/OptimizationCenterPage';
import { ExecutiveAnalyticsPage } from './pages/ExecutiveAnalyticsPage';
import { SelfEvolutionDashboardPage } from './pages/SelfEvolutionDashboardPage';
import { ProjectOnboardingWizardPage } from './pages/ProjectOnboardingWizardPage';
import { ZeroCodeTestStudioPage } from './pages/ZeroCodeTestStudioPage';
import { AutonomousTestLabPage } from './pages/AutonomousTestLabPage';
import { TestDataFactoryPage } from './pages/TestDataFactoryPage';
import { ReleaseWarRoomPage } from './pages/ReleaseWarRoomPage';
import { PluginMarketplacePage } from './pages/PluginMarketplacePage';
import { EnterpriseIntegrationsPage } from './pages/EnterpriseIntegrationsPage';
import { ExecutionCenterPage } from './pages/ExecutionCenterPage';
import { BrowserFarmPage } from './pages/BrowserFarmPage';
import { WorkerManagementPage } from './pages/WorkerManagementPage';
import { CloudDashboardPage } from './pages/CloudDashboardPage';
import { AnalyticsCenterPage } from './pages/AnalyticsCenterPage';
import { ComplianceCenterPage } from './pages/ComplianceCenterPage';
import { ReleaseGovernancePage } from './pages/ReleaseGovernancePage';
import { SecurityCenterPage } from './pages/SecurityCenterPage';
import { MarketplaceCenterPage } from './pages/MarketplaceCenterPage';
import { DevOpsCenterPage } from './pages/DevOpsCenterPage';
import { ObservabilityPage } from './pages/ObservabilityPage';
import { ExecutiveCommandCenterPage } from './pages/ExecutiveCommandCenterPage';
import { EnterpriseBrainPage } from './pages/EnterpriseBrainPage';
import { WorkflowComposerPage } from './pages/WorkflowComposerPage';
import { BusinessProcessCenterPage } from './pages/BusinessProcessCenterPage';
import { IncidentCommandCenterPage } from './pages/IncidentCommandCenterPage';
import { ForecastCenterPage } from './pages/ForecastCenterPage';
import { GovernanceCenterPage } from './pages/GovernanceCenterPage';
import { EnterpriseKnowledgeUniversePage } from './pages/EnterpriseKnowledgeUniversePage';
import { ExecutiveAdvisorPage } from './pages/ExecutiveAdvisorPage';
import { AIAgentsMarketplacePage } from './pages/AIAgentsMarketplacePage';
import { OptimizationCenterV2Page } from './pages/OptimizationCenterV2Page';
import { SoftwareGraphPage } from './pages/SoftwareGraphPage';
import { ChangeImpactCenterPage } from './pages/ChangeImpactCenterPage';
import { CodeReviewCenterPage } from './pages/CodeReviewCenterPage';
import { CoverageIntelligencePage } from './pages/CoverageIntelligencePage';
import { ReleaseIntelligencePage } from './pages/ReleaseIntelligencePage';
import { DefectIntelligencePage } from './pages/DefectIntelligencePage';
import { EngineeringAnalyticsPage } from './pages/EngineeringAnalyticsPage';
import { KnowledgeLakePage } from './pages/KnowledgeLakePage';
import { MissionControlPage } from './pages/MissionControlPage';
import { PairQAEngineerPage } from './pages/PairQAEngineerPage';
import { KnowledgeLakeV2Page } from './pages/KnowledgeLakeV2Page';
import { RequirementCenterPage } from './pages/RequirementCenterPage';
import { TraceabilityMatrixPage } from './pages/TraceabilityMatrixPage';
import { ArchitectureIntelligencePage } from './pages/ArchitectureIntelligencePage';
import { CodeQualityGovernorPage } from './pages/CodeQualityGovernorPage';
import { ReleaseCertificationPage } from './pages/ReleaseCertificationPage';
import { ObservabilityCenterPage } from './pages/ObservabilityCenterPage';
import { CustomerExperiencePage } from './pages/CustomerExperiencePage';
import { PolicyCenterPage } from './pages/PolicyCenterPage';
import { SDLCCenterPage, ExecutiveDecisionCenterPage } from './pages/SDLCCenterPage';

export default function App() {
  const [operator, setOperator] = useState<Operator | null>(null);
  const [checking, setChecking] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [activeModule, setActiveModule] = useState<ModuleKey>('dashboard');
  const [showPasswordChangeModal, setShowPasswordChangeModal] = useState(false);
  const passwordRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    void restoreSession()
      .then(setOperator)
      .catch(() => undefined)
      .finally(() => setChecking(false));
  }, []);

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    if (submitting) return;
    setSubmitting(true);
    setError('');
    try {
      setOperator(await login(username, password));
      setPassword('');
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Backend unavailable.');
      setPassword('');
      passwordRef.current?.focus();
    } finally {
      setSubmitting(false);
    }
  };

  const signOut = async () => {
    try {
      await logout();
    } finally {
      setOperator(null);
      setUsername('');
      setPassword('');
    }
  };

  const refreshOperator = async () => {
    setOperator(await restoreSession());
  };

  if (checking) {
    return (
      <main className="login-shell" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100vh', backgroundColor: 'var(--bg-app)' }}>
        <div className="card" style={{ padding: '2rem', textAlign: 'center' }} role="status">
          <div className="skeleton" style={{ height: '2rem', width: '200px', margin: '0 auto 1rem' }}></div>
          <p style={{ color: 'var(--text-muted)' }}>Loading AutoQA Dashboard...</p>
        </div>
      </main>
    );
  }

  if (!operator) {
    return (
      <main className="login-shell" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100vh', backgroundColor: 'var(--bg-app)', padding: '1rem' }}>
        <div className="card" style={{ maxWidth: '420px', width: '100%', padding: '2rem', boxShadow: 'var(--shadow-xl)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
            <div style={{ width: '40px', height: '40px', borderRadius: 'var(--radius-md)', background: 'linear-gradient(135deg, #2563eb, #0ea5e9)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', fontWeight: 700, fontSize: '1.1rem' }}>
              i5
            </div>
            <div>
              <h2 style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--text-main)', lineHeight: 1.2 }}>iFive AutoQA</h2>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Enterprise Testing & Verification</span>
            </div>
          </div>

          <h3 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: '0.25rem' }}>Operator Sign In</h3>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '1.25rem' }}>
            Sign in with a locally created operator account to access project suites.
          </p>

          {error && (
            <div style={{ padding: '0.75rem', borderRadius: 'var(--radius-md)', backgroundColor: 'var(--status-fail-bg)', color: 'var(--status-fail-text)', border: '1px solid var(--status-fail-border)', fontSize: '0.8rem', marginBottom: '1rem' }} role="alert">
              {error}
            </div>
          )}

          <form onSubmit={submit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, marginBottom: '0.35rem' }}>Username</label>
              <input
                data-testid="login-username"
                className="input"
                required
                autoComplete="username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Enter operator username"
              />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, marginBottom: '0.35rem' }}>Password</label>
              <input
                data-testid="login-password"
                ref={passwordRef}
                className="input"
                required
                type="password"
                autoComplete="current-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
              />
            </div>

            <button
              data-testid="login-submit"
              className="btn btn-primary"
              disabled={submitting}
              style={{ width: '100%', marginTop: '0.5rem', height: '42px', fontSize: '0.9rem' }}
            >
              {submitting ? 'Signing in...' : 'Sign In to AutoQA'}
            </button>
          </form>
        </div>
      </main>
    );
  }

  if (operator.must_change_password) {
    return (
      <RequiredPasswordChange
        username={operator.username}
        displayName={operator.display_name}
        onChanged={refreshOperator}
        onLogout={signOut}
      />
    );
  }

  const renderModulePage = () => {
    switch (activeModule) {
      case 'dashboard': return <DashboardPage />;
      case 'release-command-center': return <ReleaseCommandCenterPage />;
      case 'self-evolution-dashboard': return <SelfEvolutionDashboardPage />;
      case 'ai-memory-center': return <AIMemoryCenterPage />;
      case 'pattern-recognition': return <PatternRecognitionPage />;
      case 'prediction-center': return <PredictionCenterPage />;
      case 'knowledge-graph-viewer': return <KnowledgeGraphViewerPage />;
      case 'optimization-center': return <OptimizationCenterPage />;
      case 'executive-analytics': return <ExecutiveAnalyticsPage />;
      case 'release-war-room': return <ReleaseWarRoomPage />;
      case 'project-onboarding': return <ProjectOnboardingWizardPage />;
      case 'zero-code-studio': return <ZeroCodeTestStudioPage />;
      case 'autonomous-test-lab': return <AutonomousTestLabPage />;
      case 'data-factory': return <TestDataFactoryPage />;
      case 'plugin-marketplace': return <PluginMarketplacePage />;
      case 'enterprise-integrations': return <EnterpriseIntegrationsPage />;
      case 'execution-center': return <ExecutionCenterPage />;
      case 'browser-farm': return <BrowserFarmPage />;
      case 'worker-management': return <WorkerManagementPage />;
      case 'cloud-dashboard': return <CloudDashboardPage />;
      case 'analytics-center': return <AnalyticsCenterPage />;
      case 'compliance-center': return <ComplianceCenterPage />;
      case 'release-governance': return <ReleaseGovernancePage />;
      case 'security-center': return <SecurityCenterPage />;
      case 'marketplace-center': return <MarketplaceCenterPage />;
      case 'devops-center': return <DevOpsCenterPage />;
      case 'observability': return <ObservabilityPage />;
      case 'executive-command-center': return <ExecutiveCommandCenterPage />;
      case 'enterprise-brain': return <EnterpriseBrainPage />;
      case 'workflow-composer': return <WorkflowComposerPage />;
      case 'business-process-center': return <BusinessProcessCenterPage />;
      case 'incident-command-center': return <IncidentCommandCenterPage />;
      case 'forecast-center': return <ForecastCenterPage />;
      case 'governance-center': return <GovernanceCenterPage />;
      case 'knowledge-universe': return <EnterpriseKnowledgeUniversePage />;
      case 'executive-advisor': return <ExecutiveAdvisorPage />;
      case 'ai-agents-marketplace': return <AIAgentsMarketplacePage />;
      case 'optimization-center-v2': return <OptimizationCenterV2Page />;
      case 'software-graph': return <SoftwareGraphPage />;
      case 'change-impact-center': return <ChangeImpactCenterPage />;
      case 'code-review-center': return <CodeReviewCenterPage />;
      case 'coverage-intelligence': return <CoverageIntelligencePage />;
      case 'release-intelligence': return <ReleaseIntelligencePage />;
      case 'defect-intelligence': return <DefectIntelligencePage />;
      case 'engineering-analytics': return <EngineeringAnalyticsPage />;
      case 'knowledge-lake': return <KnowledgeLakePage />;
      case 'mission-control': return <MissionControlPage />;
      case 'pair-qa-engineer': return <PairQAEngineerPage />;
      case 'knowledge-lake-v2': return <KnowledgeLakeV2Page />;
      case 'requirement-center': return <RequirementCenterPage />;
      case 'traceability-matrix': return <TraceabilityMatrixPage />;
      case 'architecture-intelligence': return <ArchitectureIntelligencePage />;
      case 'code-quality-governor': return <CodeQualityGovernorPage />;
      case 'release-certification': return <ReleaseCertificationPage />;
      case 'observability-center': return <ObservabilityCenterPage />;
      case 'customer-experience': return <CustomerExperiencePage />;
      case 'policy-center': return <PolicyCenterPage />;
      case 'sdlc-center': return <SDLCCenterPage />;
      case 'executive-decision-center': return <ExecutiveDecisionCenterPage />;
      case 'digital-qa': return <DigitalQAEngineerPage />;
      case 'executive-intelligence': return <ExecutiveIntelligenceDashboardPage />;
      case 'continuous-monitoring': return <ContinuousMonitoringPage />;
      case 'ai-copilot': return <EnterpriseCopilotPage />;
      case 'release-readiness': return <ReleaseReadinessPage />;
      case 'autonomous-regression': return <AutonomousRegressionPage />;
      case 'enterprise-mgmt': return <EnterpriseManagementPage />;
      case 'enterprise-discovery': return <EnterpriseDiscoveryPage />;
      case 'company-tasks': return <CompanyTasksPage />;
      case 'my-tasks': return <MyTasksPage />;
      case 'task-imports': return <TaskImportsPage />;
      case 'test-plans': return <TestPlansPage />;
      case 'approval-queue': return <ApprovalQueuePage />;
      case 'automated-runs': return <AutomatedRunsPage />;
      case 'visual-regression': return <VisualRegressionPage />;
      case 'advanced-validation': return <AdvancedValidationPage />;

      case 'evidence': return <EvidencePage />;
      case 'defects': return <DefectsPage />;
      case 'reports': return <ReportsPage />;
      case 'schedules': return <LocalSchedulesPage />;
      case 'projects': return <ProjectsPage />;
      case 'audit-logs': return <AuditLogsPage />;
      case 'users': return <UsersPage />;
      case 'settings': return <SettingsPage />;
      default: return <DashboardPage />;
    }
  };

  return (
    <AuthContext.Provider value={{ operator, logout: signOut }}>
      <ProjectProvider>
        <AppShell
          operator={operator}
          onLogout={signOut}
          onChangePassword={() => setActiveModule('settings')}
          activeModule={activeModule}
          onSelectModule={setActiveModule}
        >
          {renderModulePage()}
        </AppShell>
      </ProjectProvider>
    </AuthContext.Provider>
  );
}
