import React, { useState } from 'react';
import { PageHeader } from '../components/layout/PageHeader';
import { AdminPanels } from '../components/AdminPanels';
import { ConnectionTargetsCore } from '../components/ConnectionTargetsCore';
import { AccountSecurityPanel } from '../components/AccountSecurityPanel';
import { ChangePasswordPanel } from '../components/PasswordControls';
import { Users, Shield, Target, Key } from 'lucide-react';

export function SettingsPage() {
  const [activeTab, setActiveTab] = useState<'operators' | 'targets' | 'security' | 'password'>('operators');

  return (
    <div>
      <PageHeader
        breadcrumbs={[{ label: 'Settings' }]}
        title="Platform Administration & System Settings"
        description="Manage operators, RBAC roles, active sessions, target environments, and security controls."
      />

      {/* Tab Navigation */}
      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.25rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.5rem' }}>
        <button
          className={`btn ${activeTab === 'operators' ? 'btn-primary' : 'btn-ghost'}`}
          onClick={() => setActiveTab('operators')}
        >
          <Users size={15} />
          Operators & Roles
        </button>
        <button
          className={`btn ${activeTab === 'targets' ? 'btn-primary' : 'btn-ghost'}`}
          onClick={() => setActiveTab('targets')}
        >
          <Target size={15} />
          Connection Targets
        </button>
        <button
          className={`btn ${activeTab === 'security' ? 'btn-primary' : 'btn-ghost'}`}
          onClick={() => setActiveTab('security')}
        >
          <Shield size={15} />
          Sessions & Security
        </button>
        <button
          className={`btn ${activeTab === 'password' ? 'btn-primary' : 'btn-ghost'}`}
          onClick={() => setActiveTab('password')}
        >
          <Key size={15} />
          Password Controls
        </button>
      </div>

      <div className="card" style={{ padding: '1.25rem' }}>
        {activeTab === 'operators' && <AdminPanels />}
        {activeTab === 'targets' && <ConnectionTargetsCore />}
        {activeTab === 'security' && <AccountSecurityPanel />}
        {activeTab === 'password' && <ChangePasswordPanel username="operator" displayName="Local Operator" />}
      </div>
    </div>
  );
}
