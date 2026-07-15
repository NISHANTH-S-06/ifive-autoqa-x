import { type FormEvent, useEffect, useState } from 'react';
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

const roles: OperatorRole[] = ['VIEWER', 'TESTER', 'APPROVER', 'ADMIN'];
const formatDate = (value: string | null | undefined) => value ? new Date(value).toLocaleString() : 'Never';

export function AdminPanels() {
  const { operator: current } = useAuth();
  const [operators, setOperators] = useState<Operator[]>([]);
  const [securityOperators, setSecurityOperators] = useState<OperatorSecurity[]>([]);
  const [summary, setSummary] = useState<SecuritySummary | null>(null);
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [integrity, setIntegrity] = useState('');
  const [loading, setLoading] = useState(true);
  const [securityLoading, setSecurityLoading] = useState(true);
  const [securityError, setSecurityError] = useState('');
  const [error, setError] = useState('');
  const [form, setForm] = useState({ username: '', display_name: '', role: 'VIEWER' as OperatorRole, temporary_password: '' });
  const [resetTarget, setResetTarget] = useState<OperatorSecurity | null>(null);
  const [resetForm, setResetForm] = useState({ temporary_password: '', confirm_temporary_password: '', reason: '' });

  const load = async () => {
    if (current.role !== 'ADMIN') return;
    setLoading(true);
    setSecurityLoading(true);
    setError('');
    setSecurityError('');
    try {
      const [nextOperators, nextEvents] = await Promise.all([
        listOperators(),
        listAuditEvents(),
      ]);
      setOperators(nextOperators);
      setEvents(nextEvents);
    } catch (reason) {
      setOperators([]);
      setEvents([]);
      setError(reason instanceof Error ? reason.message : 'Unable to load administration data.');
    } finally {
      setLoading(false);
    }
    try {
      const [nextSummary, nextSecurityOperators] = await Promise.all([getSecuritySummary(), listSecurityOperators()]);
      setSummary(nextSummary);
      setSecurityOperators(nextSecurityOperators);
    } catch (reason) {
      setSummary(null);
      setSecurityOperators([]);
      setSecurityError(reason instanceof Error ? reason.message : 'Unable to load security report.');
    } finally {
      setSecurityLoading(false);
    }
  };

  useEffect(() => { void load(); }, [current.role]);
  if (current.role !== 'ADMIN') return null;

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    setError('');
    try {
      await createOperator(form);
      setForm({ username: '', display_name: '', role: 'VIEWER', temporary_password: '' });
      await load();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Unable to create operator.');
    }
  };

  const submitReset = async (event: FormEvent) => {
    event.preventDefault();
    if (!resetTarget || !window.confirm(`Reset password for ${resetTarget.username}? This will require a password change on next login and revoke active sessions.`)) return;
    try {
      await resetOperatorPassword(resetTarget.id, resetForm);
      setResetForm({ temporary_password: '', confirm_temporary_password: '', reason: '' });
      setResetTarget(null);
      await load();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Password reset failed.');
      setResetForm({ temporary_password: '', confirm_temporary_password: '', reason: '' });
    }
  };

  const changeRole = async (item: Operator, role: OperatorRole) => {
    if (!window.confirm(`Change ${item.username} role to ${role}?`)) return;
    try { await setOperatorRole(item.id, role); await load(); } catch (reason) { setError(reason instanceof Error ? reason.message : 'Role update failed.'); }
  };

  const toggle = async (item: Operator) => {
    if (!window.confirm(`${item.is_active ? 'Deactivate' : 'Activate'} ${item.username}?`)) return;
    try { await setOperatorStatus(item.id, !item.is_active); await load(); } catch (reason) { setError(reason instanceof Error ? reason.message : 'Status update failed.'); }
  };

  const viewSessions = async (item: OperatorSecurity) => {
    try {
      const sessions = await listOperatorSessions(item.id);
      window.alert(`${item.username}: ${sessions.length} session(s), ${sessions.filter((session) => session.is_active).length} active.`);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Unable to view sessions.');
    }
  };

  const revokeSessions = async (item: OperatorSecurity) => {
    const reason = window.prompt(`Reason to revoke sessions for ${item.username}`);
    if (!reason) return;
    try { await revokeOperatorSessions(item.id, reason); await load(); } catch (reasonError) { setError(reasonError instanceof Error ? reasonError.message : 'Unable to revoke sessions.'); }
  };

  return (
    <section className="section" id="administration">
      <div className="section-inner">
        <div className="section-title"><h2>Local Administration</h2><p>Manage local operators and verify the append-only audit chain.</p></div>
        {error && <div role="alert" className="state-panel state-error">{error}</div>}
        {loading && <div className="state-panel" role="status">Loading administration data...</div>}
        {securityLoading && <div className="state-panel" role="status">Loading security report...</div>}
        {securityError && <div role="alert" className="state-panel state-error">{securityError}<button className="button button-secondary" onClick={() => void load()}>Retry</button></div>}
        {!securityLoading && !securityError && summary && <div className="security-summary-grid">
          <div className="metric"><span>Active Operators</span><strong>{summary.active_operators}</strong></div>
          <div className="metric"><span>Locked Operators</span><strong>{summary.locked_operators}</strong></div>
          <div className="metric"><span>Password Change Required</span><strong>{summary.must_change_password_count}</strong></div>
          <div className="metric"><span>Active Sessions</span><strong>{summary.active_sessions}</strong></div>
          <div className="metric"><span>Failed Logins</span><strong>{summary.failed_logins_last_24h}</strong></div>
          <div className="metric"><span>Audit Integrity</span><strong>{summary.audit_chain_valid ? 'Valid' : 'Invalid'}</strong></div>
        </div>}
        <div className="split">
          <div className="card">
            <h3>Operators</h3>
            <form className="admin-form" onSubmit={submit}>
              <input aria-label="New username" placeholder="Username" value={form.username} onChange={(event) => setForm({ ...form, username: event.target.value })} />
              <input aria-label="Display name" placeholder="Display name" value={form.display_name} onChange={(event) => setForm({ ...form, display_name: event.target.value })} />
              <select aria-label="New role" value={form.role} onChange={(event) => setForm({ ...form, role: event.target.value as OperatorRole })}>{roles.map((role) => <option key={role}>{role}</option>)}</select>
              <input aria-label="Temporary password" type="password" placeholder="Temporary password" value={form.temporary_password} onChange={(event) => setForm({ ...form, temporary_password: event.target.value })} />
            <button className="button button-primary">Create Operator</button>
            </form>
            {!loading && !error && operators.length === 0 && <div className="state-panel">No operators to display.</div>}
            {operators.map((item) => <div className="admin-row" key={item.id}><span><strong>{item.username}</strong> - {item.display_name}</span><select aria-label={`Role for ${item.username}`} value={item.role} onChange={(event) => void changeRole(item, event.target.value as OperatorRole)}>{roles.map((role) => <option key={role}>{role}</option>)}</select><button className="button button-secondary" onClick={() => void toggle(item)}>{item.is_active ? 'Deactivate' : 'Activate'}</button></div>)}
          </div>
          <div className="card">
            <h3>Audit Log</h3>
            <button className="button button-primary" onClick={() => void verifyAudit().then((result) => setIntegrity(result.valid ? `Valid (${result.total_events} events)` : 'Invalid audit chain')).catch((reason) => setError(reason instanceof Error ? reason.message : 'Verification failed.'))}>Verify Audit Integrity</button>
            {integrity && <p role="status">{integrity}</p>}
            {!loading && !error && events.length === 0 && <div className="state-panel">No audit events to display.</div>}
            <div className="audit-list">{events.map((event) => <div className="admin-row" key={event.id}><span>{event.occurred_at}</span><strong>{event.action}</strong><span>{event.outcome}</span><code>{event.request_id}</code></div>)}</div>
          </div>
        </div>
        <div className="card security-table">
          <h3>Operator Security</h3>
          {!securityLoading && !securityError && securityOperators.length === 0 && <div className="state-panel">No operator security records to display.</div>}
          {!securityLoading && !securityError && securityOperators.length > 0 && <><div className="security-table-row security-table-head"><span>Operator</span><span>Role</span><span>Status</span><span>Password State</span><span>Last Login</span><span>Sessions</span><span>Lock</span><span>Actions</span></div>
          {securityOperators.map((item) => <div className="security-table-row" key={item.id}><span><strong>{item.username}</strong><small>{item.display_name}</small></span><span>{item.role}</span><span>{item.is_active ? 'Active' : 'Inactive'}</span><span>{item.must_change_password ? 'Change required' : 'Current'}</span><span>{formatDate(item.last_login_at)}</span><span>{item.active_session_count}</span><span>{item.is_locked ? 'Locked' : 'Open'}</span><span className="table-actions"><button className="button button-secondary" onClick={() => setResetTarget(item)}>Reset</button><button className="button button-secondary" onClick={() => void viewSessions(item)}>Sessions</button><button className="button button-secondary" onClick={() => void revokeSessions(item)}>Revoke</button></span></div>)}</>}
        </div>
      </div>
      {resetTarget && <div className="modal-backdrop"><div className="modal"><h3>Reset Password</h3><form onSubmit={submitReset}><label>Temporary Password<input type="password" autoComplete="new-password" value={resetForm.temporary_password} onChange={(event) => setResetForm({ ...resetForm, temporary_password: event.target.value })} /></label><label>Confirm Temporary Password<input type="password" autoComplete="new-password" value={resetForm.confirm_temporary_password} onChange={(event) => setResetForm({ ...resetForm, confirm_temporary_password: event.target.value })} /></label><label>Reason<input value={resetForm.reason} onChange={(event) => setResetForm({ ...resetForm, reason: event.target.value })} /></label><div className="modal-actions"><button type="button" className="button button-secondary" onClick={() => { setResetTarget(null); setResetForm({ temporary_password: '', confirm_temporary_password: '', reason: '' }); }}>Cancel</button><button className="button button-primary">Reset Password</button></div></form></div></div>}
    </section>
  );
}
