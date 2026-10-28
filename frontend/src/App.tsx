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

          {/* Demo Credentials */}
          <div style={{
            marginTop: '1.25rem',
            padding: '0.85rem 1rem',
            borderRadius: 'var(--radius-md)',
            background: 'rgba(37,99,235,0.08)',
            border: '1px solid rgba(37,99,235,0.2)',
            fontSize: '0.78rem',
          }}>
            <div style={{ fontWeight: 700, color: 'var(--text-muted)', marginBottom: '0.5rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Demo Credentials
            </div>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr>
                  <th style={{ textAlign: 'left', color: 'var(--text-muted)', fontWeight: 600, paddingBottom: '0.25rem' }}>Username</th>
                  <th style={{ textAlign: 'left', color: 'var(--text-muted)', fontWeight: 600, paddingBottom: '0.25rem' }}>Role</th>
                </tr>
              </thead>
              <tbody>
                {[
                  { u: 'admin', r: 'Admin' },
                  { u: 'approver', r: 'Admin' },
                  { u: 'dev1', r: 'Developer' },
                  { u: 'viewer', r: 'Viewer' },
                ].map(({ u, r }) => (
                  <tr key={u} style={{ cursor: 'pointer' }} onClick={() => { setUsername(u); setPassword('Admin@1234'); }}>
                    <td style={{ padding: '2px 0', color: '#60a5fa', fontFamily: 'monospace', fontWeight: 600 }}>{u}</td>
                    <td style={{ padding: '2px 0', color: 'var(--text-muted)' }}>{r}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            <div style={{ marginTop: '0.5rem', color: 'var(--text-muted)' }}>
              Password: <span style={{ fontFamily: 'monospace', color: '#34d399', fontWeight: 700 }}>Admin@1234</span>
              <span style={{ marginLeft: '0.5rem', fontSize: '0.72rem', opacity: 0.7 }}>(click row to auto-fill)</span>
            </div>
          </div>
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
      case 'digital-qa': return <DigitalQAEngineerPage />;
      case 'executive-intelligence': return <ExecutiveIntelligenceDashboardPage />;
      case 'continuous-monitoring': return <ContinuousMonitoringPage />;
      case 'ai-copilot': return <EnterpriseCopilotPage />;
      case 'release-readiness': return <ReleaseReadinessPage />;
      case 'autonomous-regression': return <AutonomousRegressionPage />;
      case 'enterprise-mgmt': return <EnterpriseManagementPage />;
      case 'enterprise-discovery': return <EnterpriseDiscoveryPage />;
      case 'company-tasks': return <CompanyTasksPage onNavigate={setActiveModule} />;
      case 'my-tasks': return <MyTasksPage onNavigate={setActiveModule} />;
      case 'task-imports': return <TaskImportsPage />;
      case 'test-plans': return <TestPlansPage />;
      case 'approval-queue': return <ApprovalQueuePage onNavigate={setActiveModule} />;
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
