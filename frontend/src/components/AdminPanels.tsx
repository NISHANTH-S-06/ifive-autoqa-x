import React, { type FormEvent, useEffect, useState } from 'react';
import { useAuth } from '../authContext';
import {
  createOperator,
  getSecuritySummary,
  listAuditEvents,
  listOperators,
  listOperatorSessions,
  listSecurityOperators,
  resetOperatorPassword,
  revokeOperatorSessions,
  setOperatorRole,
  setOperatorStatus,
  verifyAudit,
} from '../services/auth';
import type { AuditEvent, Operator, OperatorRole, OperatorSecurity, SecuritySummary } from '../types/auth';
import { DataTable, Column } from './ui/DataTable';
import { StatusBadge } from './ui/StatusBadge';
import { StatCard } from './ui/StatCard';
import { Button } from './ui/Button';
import { Input } from './ui/Input';
import { Select } from './ui/Select';
import { FormField } from './ui/FormField';
import { Modal } from './ui/Modal';
import { ErrorState } from './ui/ErrorState';
import { Users, Shield, Lock, Key, Plus, RefreshCw, UserCheck, ShieldAlert } from 'lucide-react';

const roles: OperatorRole[] = ['VIEWER', 'TESTER', 'APPROVER', 'ADMIN'];
const formatDate = (value: string | null | undefined) => value ? new Date(value).toLocaleString() : 'Never';

export function AdminPanels() {
  const { operator: current } = useAuth();
  const [operators, setOperators] = useState<Operator[]>([]);
  const [securityOperators, setSecurityOperators] = useState<OperatorSecurity[]>([]);
  const [summary, setSummary] = useState<SecuritySummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);

  const [form, setForm] = useState({ username: '', display_name: '', role: 'VIEWER' as OperatorRole, temporary_password: '' });
  const [resetTarget, setResetTarget] = useState<OperatorSecurity | null>(null);
  const [resetForm, setResetForm] = useState({ temporary_password: '', confirm_temporary_password: '', reason: '' });
  const [submitting, setSubmitting] = useState(false);

  const load = async () => {
    if (current.role !== 'ADMIN') return;
    setLoading(true);
    setError('');
    try {
      const [nextOperators, nextSummary, nextSecurityOperators] = await Promise.all([
        listOperators(),
        getSecuritySummary().catch(() => null),
        listSecurityOperators().catch(() => []),
      ]);
      setOperators(nextOperators || []);
      setSummary(nextSummary);
      setSecurityOperators(nextSecurityOperators || []);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Unable to load administration data.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { void load(); }, [current.role]);

  if (current.role !== 'ADMIN') {
    return (
      <div className="card" style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>
        <ShieldAlert size={36} style={{ color: 'var(--color-warning)', margin: '0 auto 1rem' }} />
        <h4 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '0.5rem' }}>
          Administrator Privilege Required
        </h4>
        <p style={{ fontSize: '0.85rem' }}>
          Operator user management and security policy configuration is restricted to ADMIN roles.
        </p>
      </div>
    );
  }

  const submitCreate = async (event: FormEvent) => {
    event.preventDefault();
    setSubmitting(true);
    setError('');
    try {
      await createOperator(form);
      setForm({ username: '', display_name: '', role: 'VIEWER', temporary_password: '' });
      setShowCreateModal(false);
      await load();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Unable to create operator.');
    } finally {
      setSubmitting(false);
    }
  };

  const submitReset = async (event: FormEvent) => {
    event.preventDefault();
    if (!resetTarget) return;
    setSubmitting(true);
    try {
      await resetOperatorPassword(resetTarget.id, resetForm);
      setResetForm({ temporary_password: '', confirm_temporary_password: '', reason: '' });
      setResetTarget(null);
      await load();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Password reset failed.');
    } finally {
      setSubmitting(false);
    }
  };

  const changeRole = async (item: Operator, newRole: OperatorRole) => {
    try {
      await setOperatorRole(item.id, newRole);
      await load();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Role update failed.');
    }
  };

  const toggleStatus = async (item: Operator) => {
    try {
      await setOperatorStatus(item.id, !item.is_active);
      await load();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Status update failed.');
    }
  };

  const operatorColumns: Column<Operator>[] = [
    { key: 'username', header: 'Operator Username', render: (o) => <span style={{ fontWeight: 700 }}>{o.username}</span> },
    { key: 'display_name', header: 'Display Name', render: (o) => <span>{o.display_name}</span> },
    { key: 'role', header: 'Role', render: (o) => (
      <Select
        value={o.role}
        onChange={(e) => void changeRole(o, e.target.value as OperatorRole)}
        style={{ width: '130px', padding: '0.25rem 0.5rem', fontSize: '0.8rem' }}
      >
        {roles.map((r) => <option key={r} value={r}>{r}</option>)}
      </Select>
    )},
    { key: 'is_active', header: 'Status', render: (o) => <StatusBadge status={o.is_active ? 'APPROVED' : 'REJECTED'} label={o.is_active ? 'Active' : 'Inactive'} size="sm" /> },
    { key: 'actions', header: 'Actions', render: (o) => (
      <Button
        size="sm"
        variant={o.is_active ? 'danger' : 'secondary'}
        onClick={() => void toggleStatus(o)}
      >
        {o.is_active ? 'Deactivate' : 'Activate'}
      </Button>
    )}
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      {/* Security Summary Cards */}
      {summary && (
        <div className="grid grid-cols-4">
          <StatCard title="Active Operators" value={summary.active_operators} subtitle="Registered operators" icon={Users} variant="primary" loading={loading} />
          <StatCard title="Active Sessions" value={summary.active_sessions} subtitle="Current logged sessions" icon={UserCheck} variant="success" loading={loading} />
          <StatCard title="Password Required" value={summary.must_change_password_count} subtitle="Pending credential update" icon={Key} variant="warning" loading={loading} />
          <StatCard title="Audit Integrity" value={summary.audit_chain_valid ? 'VALID' : 'INVALID'} subtitle="Sequential ledger status" icon={Shield} variant={summary.audit_chain_valid ? 'success' : 'danger'} loading={loading} />
        </div>
      )}

      {error && <ErrorState message={error} onRetry={load} />}

      {/* Operators Table Card */}
      <div className="card" style={{ padding: '1.25rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
          <div>
            <h3 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-main)' }}>
              Local Operator Accounts & Governance
            </h3>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              Manage local operator credentials and RBAC roles (VIEWER, TESTER, APPROVER, ADMIN).
            </p>
          </div>

          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <Button size="sm" variant="secondary" onClick={load} isLoading={loading} leftIcon={<RefreshCw size={14} />}>
              Refresh
            </Button>
            <Button size="sm" variant="primary" onClick={() => setShowCreateModal(true)} leftIcon={<Plus size={14} />}>
              New Operator Account
            </Button>
          </div>
        </div>

        <DataTable
          columns={operatorColumns}
          data={operators}
          keyExtractor={(o) => o.id}
          loading={loading}
          emptyMessage="No operator accounts found."
        />
      </div>

      {/* Create Operator Modal */}
      <Modal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        title="Create New Local Operator Account"
        subtitle="Specify credentials, display name, and assign an initial RBAC role"
        footer={(
          <>
            <Button variant="secondary" onClick={() => setShowCreateModal(false)}>Cancel</Button>
            <Button variant="primary" onClick={submitCreate} isLoading={submitting} disabled={!form.username || !form.temporary_password}>
              Create Operator
            </Button>
          </>
        )}
      >
        <form onSubmit={submitCreate} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <FormField label="Username" required>
            <Input
              required
              placeholder="e.g. dev_tester"
              value={form.username}
              onChange={(e) => setForm({ ...form, username: e.target.value })}
            />
          </FormField>

          <FormField label="Display Name" required>
            <Input
              required
              placeholder="e.g. Jane Doe"
              value={form.display_name}
              onChange={(e) => setForm({ ...form, display_name: e.target.value })}
            />
          </FormField>

          <FormField label="RBAC Role" required>
            <Select
              value={form.role}
              onChange={(e) => setForm({ ...form, role: e.target.value as OperatorRole })}
            >
              {roles.map((r) => <option key={r} value={r}>{r}</option>)}
            </Select>
          </FormField>

          <FormField label="Temporary Password" required hint="Operator must change password on first login">
            <Input
              type="password"
              required
              placeholder="••••••••"
              value={form.temporary_password}
              onChange={(e) => setForm({ ...form, temporary_password: e.target.value })}
            />
          </FormField>
        </form>
      </Modal>

      {/* Password Reset Modal */}
      {resetTarget && (
        <Modal
          isOpen={true}
          onClose={() => setResetTarget(null)}
          title={`Reset Password for ${resetTarget.username}`}
          subtitle="Set a new temporary password. Operator will be required to change it at next login."
          footer={(
            <>
              <Button variant="secondary" onClick={() => setResetTarget(null)}>Cancel</Button>
              <Button variant="danger" onClick={submitReset} isLoading={submitting}>Reset Password</Button>
            </>
          )}
        >
          <form onSubmit={submitReset} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <FormField label="Temporary Password" required>
              <Input
                type="password"
                required
                value={resetForm.temporary_password}
                onChange={(e) => setResetForm({ ...resetForm, temporary_password: e.target.value })}
              />
            </FormField>

            <FormField label="Confirm Temporary Password" required>
              <Input
                type="password"
                required
                value={resetForm.confirm_temporary_password}
                onChange={(e) => setResetForm({ ...resetForm, confirm_temporary_password: e.target.value })}
              />
            </FormField>

            <FormField label="Reason for Reset" required>
              <Input
                required
                placeholder="e.g. Requested by user / credential rotation"
                value={resetForm.reason}
                onChange={(e) => setResetForm({ ...resetForm, reason: e.target.value })}
              />
            </FormField>
          </form>
        </Modal>
      )}
    </div>
  );
}
