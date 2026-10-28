import React from 'react';
import { motion } from 'framer-motion';
import {
  LayoutDashboard, FileInput, FileCode, CheckSquare, PlayCircle,
  ShieldCheck, Image, Bug, BarChart3, CalendarClock, FolderGit2,
  FileCheck2, Settings, ChevronLeft, ChevronRight, Sparkles,
  ClipboardList, ListTodo, Users, Building2, Globe, Bot, GitBranch, Brain, Activity,
  Layers2, Monitor, Database, Package, Globe2
} from 'lucide-react';
import type { OperatorRole } from '../../types/auth';

export type ModuleKey =
  | 'dashboard'
  | 'release-command-center'
  | 'self-evolution-dashboard'
  | 'ai-memory-center'
  | 'pattern-recognition'
  | 'prediction-center'
  | 'knowledge-graph-viewer'
  | 'optimization-center'
  | 'executive-analytics'
  | 'project-onboarding'
  | 'zero-code-studio'
  | 'autonomous-test-lab'
  | 'data-factory'
  | 'release-war-room'
  | 'plugin-marketplace'
  | 'enterprise-integrations'
  | 'execution-center'
  | 'browser-farm'
  | 'worker-management'
  | 'cloud-dashboard'
  | 'analytics-center'
  | 'compliance-center'
  | 'release-governance'
  | 'security-center'
  | 'marketplace-center'
  | 'devops-center'
  | 'observability'
  | 'executive-command-center'
  | 'enterprise-brain'
  | 'workflow-composer'
  | 'business-process-center'
  | 'incident-command-center'
  | 'forecast-center'
  | 'governance-center'
  | 'knowledge-universe'
  | 'executive-advisor'
  | 'ai-agents-marketplace'
  | 'optimization-center-v2'
  | 'software-graph'
  | 'change-impact-center'
  | 'code-review-center'
  | 'coverage-intelligence'
  | 'release-intelligence'
  | 'defect-intelligence'
  | 'engineering-analytics'
  | 'knowledge-lake'
  | 'mission-control'
  | 'pair-qa-engineer'
  | 'knowledge-lake-v2'
  | 'requirement-center'
  | 'traceability-matrix'
  | 'architecture-intelligence'
  | 'code-quality-governor'
  | 'release-certification'
  | 'observability-center'
  | 'customer-experience'
  | 'policy-center'
  | 'sdlc-center'
  | 'executive-decision-center'
  | 'digital-qa'
  | 'executive-intelligence'
  | 'continuous-monitoring'
  | 'ai-copilot'
  | 'release-readiness'
  | 'autonomous-regression'
  | 'enterprise-mgmt'
  | 'enterprise-discovery'
  | 'company-tasks'      // PM / Admin: all tasks
  | 'my-tasks'           // Developer: assigned tasks
  | 'task-imports'
  | 'test-plans'
  | 'approval-queue'
  | 'automated-runs'
  | 'visual-regression'
  | 'advanced-validation'
  | 'evidence'
  | 'defects'
  | 'reports'
  | 'schedules'
  | 'projects'
  | 'audit-logs'
  | 'users'              // Admin only
  | 'settings';


interface NavItem {
  key: ModuleKey;
  label: string;
  icon: React.ElementType;
  section?: string;
  badge?: number;
  roles?: OperatorRole[];
}

interface SidebarProps {
  activeModule: ModuleKey;
  onSelectModule: (module: ModuleKey) => void;
  collapsed: boolean;
  onToggleCollapse: () => void;
  pendingApprovalsCount?: number;
  operatorRole?: OperatorRole;
}

/** Role display config */
const ROLE_LABELS: Record<OperatorRole, { label: string; color: string }> = {
  ADMIN: { label: 'Super Admin', color: '#ef4444' },
  PROJECT_MANAGER: { label: 'Project Manager', color: '#f59e0b' },
  DEVELOPER: { label: 'Developer', color: '#3b82f6' },
  TESTER: { label: 'Tester', color: '#8b5cf6' },
  APPROVER: { label: 'Approver', color: '#06b6d4' },
  VIEWER: { label: 'Viewer', color: '#64748b' },
};

const ALL_NAV_ITEMS: NavItem[] = [
  // ── Overview & Delivery ────────────────────────────────────────────────────
  { key: 'dashboard', label: 'Dashboard', icon: LayoutDashboard, section: 'Overview & Delivery' },
  { key: 'company-tasks', label: 'Delivery Tasks', icon: ClipboardList, section: 'Overview & Delivery', roles: ['ADMIN', 'PROJECT_MANAGER'] },
  { key: 'projects', label: 'Projects', icon: FolderGit2, section: 'Overview & Delivery', roles: ['ADMIN', 'PROJECT_MANAGER'] },
  { key: 'my-tasks', label: 'Developer Tasks', icon: ListTodo, section: 'Overview & Delivery', roles: ['DEVELOPER', 'ADMIN', 'PROJECT_MANAGER'] },

  // ── Zero-Code & Testing Studio ─────────────────────────────────────────────
  { key: 'zero-code-studio', label: 'Zero-Code Studio', icon: FileCheck2, section: 'Zero-Code & Testing' },
  { key: 'visual-regression', label: 'Visual Regression', icon: Monitor, section: 'Zero-Code & Testing' },
  { key: 'test-plans', label: 'Test Plans & Flows', icon: FileCode, section: 'Zero-Code & Testing', roles: ['ADMIN', 'TESTER', 'APPROVER', 'PROJECT_MANAGER'] },
  { key: 'approval-queue', label: 'QA Approval Queue', icon: CheckSquare, section: 'Zero-Code & Testing', roles: ['ADMIN', 'TESTER', 'APPROVER'] },
  { key: 'automated-runs', label: 'Automated Runs', icon: PlayCircle, section: 'Zero-Code & Testing', roles: ['ADMIN', 'TESTER', 'APPROVER'] },

  // ── Autonomous AI Suite ──────────────────────────────────────────────────
  { key: 'ai-copilot', label: 'Enterprise AI Copilot', icon: Bot, section: 'Autonomous AI Suite' },
  { key: 'digital-qa', label: 'Digital QA Engineer', icon: Brain, section: 'Autonomous AI Suite' },
  { key: 'autonomous-test-lab', label: 'Autonomous Test Lab', icon: Sparkles, section: 'Autonomous AI Suite' },
  { key: 'autonomous-regression', label: 'Autonomous Regression', icon: Activity, section: 'Autonomous AI Suite' },
  { key: 'ai-memory-center', label: 'AI Memory Center', icon: Database, section: 'Autonomous AI Suite' },

  // ── Release & Reports ─────────────────────────────────────────────────────
  { key: 'release-command-center', label: 'Release Command Center', icon: GitBranch, section: 'Release & Reports' },
  { key: 'evidence', label: 'Screenshots & Evidence', icon: Image, section: 'Release & Reports', roles: ['ADMIN', 'TESTER', 'APPROVER', 'DEVELOPER', 'PROJECT_MANAGER'] },
  { key: 'defects', label: 'Defects & Bug Loops', icon: Bug, section: 'Release & Reports', roles: ['ADMIN', 'TESTER', 'APPROVER', 'DEVELOPER', 'PROJECT_MANAGER'] },
  { key: 'reports', label: 'Reports & Analytics', icon: BarChart3, section: 'Release & Reports', roles: ['ADMIN', 'PROJECT_MANAGER', 'TESTER', 'APPROVER', 'VIEWER'] },

  // ── System & Security ───────────────────────────────────────────────────
  { key: 'task-imports', label: 'Task Imports', icon: FileInput, section: 'System & Security', roles: ['ADMIN', 'PROJECT_MANAGER'] },
  { key: 'audit-logs', label: 'Audit Logs', icon: ShieldCheck, section: 'System & Security', roles: ['ADMIN'] },
  { key: 'users', label: 'User Management', icon: Users, section: 'System & Security', roles: ['ADMIN'] },
  { key: 'settings', label: 'Settings', icon: Settings, section: 'System & Security' },
];

export function Sidebar({
  activeModule,
  onSelectModule,
  collapsed,
  onToggleCollapse,
  pendingApprovalsCount = 0,
  operatorRole,
}: SidebarProps) {
  const navItems = ALL_NAV_ITEMS
    .filter((item) => !item.roles || !operatorRole || item.roles.includes(operatorRole))
    .map((item) => ({
      ...item,
      badge: item.key === 'approval-queue' ? pendingApprovalsCount : undefined,
    }));

  const roleInfo = operatorRole ? ROLE_LABELS[operatorRole] : null;

  return (
    <aside style={{
      width: collapsed ? '68px' : '240px',
      height: '100vh',
      backgroundColor: 'var(--bg-sidebar)',
      borderRight: '1px solid var(--border-color)',
      display: 'flex',
      flexDirection: 'column',
      transition: 'width 0.2s ease',
      zIndex: 100,
      userSelect: 'none'
    }}>
      {/* Brand Header */}
      <div style={{
        height: '60px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: collapsed ? 'center' : 'space-between',
        padding: collapsed ? '0' : '0 1rem',
        borderBottom: '1px solid rgba(255, 255, 255, 0.08)'
      }}>
        {!collapsed && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.625rem' }}>
            <div style={{
              width: '32px',
              height: '32px',
              borderRadius: 'var(--radius-md)',
              background: 'linear-gradient(135deg, #2563eb, #0ea5e9)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#ffffff',
              fontWeight: 700,
              fontSize: '0.9rem'
            }}>
              i5
            </div>
            <div style={{ display: 'flex', flexDirection: 'column' }}>
              <span style={{ color: 'var(--text-on-dark)', fontWeight: 700, fontSize: '0.95rem', lineHeight: 1.2 }}>AutoQA</span>
              <span style={{ color: 'var(--text-subtle)', fontSize: '0.7rem', fontWeight: 500 }}>Enterprise Portal</span>
            </div>
          </div>
        )}

        <button
          onClick={onToggleCollapse}
          className="btn btn-ghost btn-sm"
          style={{ color: 'var(--text-subtle)', padding: '0.35rem' }}
          title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          data-testid="sidebar-toggle"
        >
          {collapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
        </button>
      </div>

      {/* Role Badge */}
      {!collapsed && roleInfo && (
        <div style={{
          padding: '0.5rem 1rem',
          borderBottom: '1px solid rgba(255, 255, 255, 0.06)',
        }}>
          <span style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.35rem',
            fontSize: '0.7rem',
            fontWeight: 700,
            padding: '0.2rem 0.55rem',
            borderRadius: 'var(--radius-full)',
            backgroundColor: `${roleInfo.color}22`,
            color: roleInfo.color,
            border: `1px solid ${roleInfo.color}44`,
            letterSpacing: '0.04em',
            textTransform: 'uppercase',
          }}>
            {roleInfo.label}
          </span>
        </div>
      )}

      {/* Nav List */}
      <nav style={{ flex: 1, overflowY: 'auto', padding: '0.75rem 0.5rem', display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
        {navItems.map((item, index) => {
          const Icon = item.icon;
          const isActive = activeModule === item.key;
          const showSectionHeader = !collapsed && item.section && (index === 0 || navItems[index - 1].section !== item.section);

          return (
            <React.Fragment key={item.key}>
              {showSectionHeader && (
                <div style={{
                  padding: index === 0 ? '0.25rem 0.5rem 0.35rem' : '0.85rem 0.5rem 0.35rem',
                  fontSize: '0.65rem',
                  fontWeight: 700,
                  color: 'var(--text-subtle)',
                  letterSpacing: '0.06em',
                  textTransform: 'uppercase',
                  opacity: 0.7
                }}>
                  {item.section}
                </div>
              )}
              <motion.button
              onClick={() => onSelectModule(item.key)}
              whileHover={{ x: collapsed ? 0 : 2 }}
              whileTap={{ scale: 0.97 }}
              transition={{ duration: 0.12 }}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.75rem',
                padding: collapsed ? '0.65rem 0' : '0.65rem 0.85rem',
                justifyContent: collapsed ? 'center' : 'flex-start',
                borderRadius: 'var(--radius-md)',
                backgroundColor: isActive ? 'var(--bg-sidebar-active)' : 'transparent',
                color: isActive ? 'var(--text-on-dark)' : 'var(--text-subtle)',
                border: 'none',
                cursor: 'pointer',
                fontSize: '0.85rem',
                fontWeight: isActive ? 600 : 500,
                position: 'relative'
              }}
              title={collapsed ? item.label : undefined}
              data-testid={`sidebar-item-${item.key}`}
            >
              {isActive && (
                <motion.span
                  layoutId="sidebar-active-indicator"
                  transition={{ type: 'spring', stiffness: 500, damping: 40 }}
                  style={{
                    position: 'absolute', left: -2, top: '15%', bottom: '15%', width: '3px',
                    borderRadius: 'var(--radius-full)', backgroundColor: 'var(--color-primary)'
                  }}
                />
              )}
              <Icon size={18} style={{ color: isActive ? 'var(--color-primary)' : 'inherit', flexShrink: 0 }} />

              {!collapsed && (
                <span style={{ flex: 1, textAlign: 'left', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                  {item.label}
                </span>
              )}

              {item.badge !== undefined && item.badge > 0 && (
                <span style={{
                  fontSize: '0.7rem',
                  fontWeight: 700,
                  padding: '0.1rem 0.45rem',
                  borderRadius: 'var(--radius-full)',
                  backgroundColor: 'var(--color-warning)',
                  color: '#ffffff'
                }}>
                  {item.badge}
                </span>
              )}
            </motion.button>
          </React.Fragment>
          );
        })}
      </nav>

      {/* Footer / Status */}
      {!collapsed && (
        <div style={{
          padding: '0.75rem 1rem',
          borderTop: '1px solid rgba(255, 255, 255, 0.08)',
          fontSize: '0.75rem',
          color: 'var(--text-subtle)',
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem'
        }}>
          <Sparkles size={14} style={{ color: 'var(--color-accent)' }} />
          <span>AutoQA Engine</span>
        </div>
      )}
    </aside>
  );
}
