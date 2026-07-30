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
  badge?: number;
  roles?: OperatorRole[]; // if undefined â†’ visible to all roles
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
  // â”€â”€ Dashboard & AI QA Brain Command Center (all roles) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
  { key: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { key: 'release-war-room', label: 'Release War Room', icon: ShieldCheck, roles: ['ADMIN', 'PROJECT_MANAGER', 'APPROVER'] },
  { key: 'release-command-center', label: 'Release Command Center', icon: ShieldCheck, roles: ['ADMIN', 'PROJECT_MANAGER', 'APPROVER'] },
  { key: 'self-evolution-dashboard', label: 'Self Evolution Dashboard', icon: Brain },
  { key: 'ai-memory-center', label: 'AI Memory Center', icon: Sparkles },
  { key: 'pattern-recognition', label: 'Pattern Recognition', icon: Activity },
  { key: 'prediction-center', label: 'Prediction Center', icon: BarChart3 },
  { key: 'knowledge-graph-viewer', label: 'Knowledge Graph Viewer', icon: FolderGit2 },
  { key: 'optimization-center', label: 'Optimization Center', icon: Settings },
  { key: 'executive-analytics', label: 'Executive Analytics', icon: BarChart3, roles: ['ADMIN', 'PROJECT_MANAGER', 'APPROVER'] },

  // â”€â”€ Zero-Code Ecosystem â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
  { key: 'project-onboarding', label: 'Onboarding Wizard', icon: Globe },
  { key: 'zero-code-studio', label: 'Zero-Code Test Studio', icon: Layers2 },
  { key: 'autonomous-test-lab', label: 'Autonomous Test Lab', icon: Monitor },
  { key: 'data-factory', label: 'Test Data Factory', icon: Database },
  { key: 'plugin-marketplace', label: 'Plugin Marketplace', icon: Package },
  { key: 'enterprise-integrations', label: 'Enterprise Integrations', icon: Globe2 },

  // Phase 13-16 "Enterprise Universe" nav items archived on 2026-07-30
  // (see archive/backend_api_phase13-16/ and archive/frontend_pages_phase13-16/).

  { key: 'digital-qa', label: 'AI Digital QA Engineer', icon: Brain },
  { key: 'executive-intelligence', label: 'Executive Intelligence', icon: BarChart3, roles: ['ADMIN', 'PROJECT_MANAGER', 'APPROVER'] },
  { key: 'continuous-monitoring', label: 'Autonomous Monitoring', icon: Activity, roles: ['ADMIN', 'PROJECT_MANAGER', 'TESTER', 'DEVELOPER'] },
  { key: 'ai-copilot', label: 'AI Copilot', icon: Bot },
  { key: 'release-readiness', label: 'Release Readiness', icon: ShieldCheck, roles: ['ADMIN', 'PROJECT_MANAGER', 'APPROVER', 'TESTER'] },
  { key: 'autonomous-regression', label: 'Autonomous Regression', icon: GitBranch, roles: ['ADMIN', 'PROJECT_MANAGER', 'DEVELOPER', 'TESTER'] },
  { key: 'enterprise-discovery', label: 'AI Flow Discovery', icon: Globe, roles: ['ADMIN', 'TESTER', 'PROJECT_MANAGER', 'APPROVER'] },
  { key: 'enterprise-mgmt', label: 'Enterprise Setup', icon: Building2, roles: ['ADMIN', 'PROJECT_MANAGER'] },

  // â”€â”€ Company Task Workflow â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
  {
    key: 'company-tasks',
    label: 'Company Tasks',
    icon: ClipboardList,
    roles: ['ADMIN', 'PROJECT_MANAGER'],
  },
  {
    key: 'my-tasks',
    label: 'My Tasks',
    icon: ListTodo,
    roles: ['DEVELOPER', 'ADMIN'],
  },

  // â”€â”€ QA / Tester workflow â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
  {
    key: 'approval-queue',
    label: 'Approval Queue',
    icon: CheckSquare,
    roles: ['ADMIN', 'TESTER', 'APPROVER'],
  },
  {
    key: 'automated-runs',
    label: 'Automated Runs',
    icon: PlayCircle,
    roles: ['ADMIN', 'TESTER', 'APPROVER'],
  },
  {
    key: 'visual-regression',
    label: 'Visual Regression',
    icon: Image,
    roles: ['ADMIN', 'TESTER', 'APPROVER', 'PROJECT_MANAGER', 'DEVELOPER'],
  },
  {
    key: 'evidence',
    label: 'Evidence',
    icon: Image,
    roles: ['ADMIN', 'TESTER', 'APPROVER'],
  },

  {
    key: 'defects',
    label: 'Defects',
    icon: Bug,
    roles: ['ADMIN', 'TESTER', 'APPROVER', 'DEVELOPER'],
  },

  // â”€â”€ Project / Test Management (PM + Admin) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
  {
    key: 'projects',
    label: 'Projects',
    icon: FolderGit2,
    roles: ['ADMIN', 'PROJECT_MANAGER'],
  },
  {
    key: 'task-imports',
    label: 'Task Imports',
    icon: FileInput,
    roles: ['ADMIN', 'PROJECT_MANAGER'],
  },
  {
    key: 'test-plans',
    label: 'Test Plans',
    icon: FileCode,
    roles: ['ADMIN', 'TESTER', 'APPROVER', 'PROJECT_MANAGER'],
  },
  {
    key: 'advanced-validation',
    label: 'Advanced Validation',
    icon: ShieldCheck,
    roles: ['ADMIN', 'TESTER', 'APPROVER'],
  },

  // â”€â”€ Reports (PM, Tester, Viewer, Admin) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
  {
    key: 'reports',
    label: 'Reports',
    icon: BarChart3,
    roles: ['ADMIN', 'PROJECT_MANAGER', 'TESTER', 'APPROVER', 'VIEWER'],
  },

  // â”€â”€ Admin-only â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
  {
    key: 'schedules',
    label: 'Local Schedules',
    icon: CalendarClock,
    roles: ['ADMIN'],
  },
  {
    key: 'audit-logs',
    label: 'Audit Logs',
    icon: FileCheck2,
    roles: ['ADMIN'],
  },
  {
    key: 'users',
    label: 'Users',
    icon: Users,
    roles: ['ADMIN'],
  },
  {
    key: 'settings',
    label: 'Settings',
    icon: Settings,
  },
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
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeModule === item.key;

          return (
            <motion.button
              key={item.key}
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
