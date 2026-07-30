import React, { useCallback, useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Users, Plus, RefreshCw, Shield, UserCheck, UserX, X, Save, ChevronDown } from 'lucide-react';
import { listOperators, createOperator, setOperatorStatus, setOperatorRole } from '../services/auth';
import type { Operator, OperatorRole } from '../types/auth';

const ROLE_CONFIG: Record<OperatorRole, { label: string; color: string; desc: string }> = {
  ADMIN: { label: 'Super Admin', color: '#ef4444', desc: 'Full access to all features and user management' },
  PROJECT_MANAGER: { label: 'Project Manager', color: '#f59e0b', desc: 'Create projects, tasks, assign developers' },
  DEVELOPER: { label: 'Developer', color: '#3b82f6', desc: 'View and update assigned tasks' },
  TESTER: { label: 'Tester', color: '#8b5cf6', desc: 'Approve tasks, run AutoQA, manage defects' },
  APPROVER: { label: 'Approver', color: '#06b6d4', desc: 'Review and approve test plans' },
  VIEWER: { label: 'Viewer', color: '#64748b', desc: 'Read-only access to reports' },
};

function RoleBadge({ role }: { role: OperatorRole }) {
  const cfg = ROLE_CONFIG[role] ?? { label: role, color: '#64748b' };
  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center',
      fontSize: '0.7rem', fontWeight: 700, padding: '0.2rem 0.55rem',
      borderRadius: 'var(--radius-full)',
      backgroundColor: `${cfg.color}18`, color: cfg.color,
      border: `1px solid ${cfg.color}35`,
      textTransform: 'uppercase', letterSpacing: '0.04em',
    }}>
      {cfg.label}
    </span>
  );
}

function CreateUserModal({ onClose, onCreated }: { onClose: () => void; onCreated: () => void }) {
  const [form, setForm] = useState({ username: '', display_name: '', role: 'DEVELOPER' as OperatorRole, temporary_password: '' });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true); setError('');
    try {
      await createOperator(form);
      onCreated(); onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create user.');
    } finally { setSaving(false); }
  };

  const labelStyle: React.CSSProperties = { display: 'block', fontSize: '0.8rem', fontWeight: 600, marginBottom: '0.35rem' };
  const inputStyle: React.CSSProperties = { width: '100%', boxSizing: 'border-box' };

  return (
    <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '1rem' }}>
      <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }}
        style={{ background: 'var(--bg-card)', borderRadius: 'var(--radius-xl)', width: '100%', maxWidth: '480px', boxShadow: 'var(--shadow-xl)' }}>
        <div style={{ padding: '1.5rem', borderBottom: '1px solid var(--border-color)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <div style={{ width: '36px', height: '36px', borderRadius: 'var(--radius-md)', background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Users size={18} color="#fff" />
            </div>
            <div>
              <h2 style={{ fontSize: '1.05rem', fontWeight: 700 }}>Create User</h2>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>New operator account</p>
            </div>
          </div>
          <button className="btn btn-ghost btn-sm" onClick={onClose}><X size={18} /></button>
        </div>

        <form onSubmit={submit} style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {error && <div style={{ padding: '0.75rem', borderRadius: 'var(--radius-md)', background: 'var(--status-fail-bg)', color: 'var(--status-fail-text)', fontSize: '0.82rem' }}>{error}</div>}

          <div>
            <label style={labelStyle}>Username <span style={{ color: '#ef4444' }}>*</span></label>
            <input className="input" style={inputStyle} required value={form.username} onChange={(e) => setForm((p) => ({ ...p, username: e.target.value }))} placeholder="e.g. ravi.kumar" />
          </div>
          <div>
            <label style={labelStyle}>Display Name <span style={{ color: '#ef4444' }}>*</span></label>
            <input className="input" style={inputStyle} required value={form.display_name} onChange={(e) => setForm((p) => ({ ...p, display_name: e.target.value }))} placeholder="e.g. Ravi Kumar" />
          </div>
          <div>
            <label style={labelStyle}>Role</label>
            <select className="input" style={inputStyle} value={form.role} onChange={(e) => setForm((p) => ({ ...p, role: e.target.value as OperatorRole }))}>
              {Object.entries(ROLE_CONFIG).map(([k, v]) => <option key={k} value={k}>{v.label}</option>)}
            </select>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>{ROLE_CONFIG[form.role]?.desc}</p>
          </div>
          <div>
            <label style={labelStyle}>Temporary Password <span style={{ color: '#ef4444' }}>*</span></label>
            <input className="input" style={inputStyle} required type="password" value={form.temporary_password} onChange={(e) => setForm((p) => ({ ...p, temporary_password: e.target.value }))} placeholder="Min 12 characters" minLength={12} />
            <p style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>User must change this on first login.</p>
          </div>

          <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'flex-end', paddingTop: '0.25rem' }}>
            <button type="button" className="btn btn-secondary" onClick={onClose} disabled={saving}>Cancel</button>
            <button type="submit" className="btn btn-primary" disabled={saving} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Save size={15} /> {saving ? 'Creating...' : 'Create User'}
            </button>
          </div>
        </form>
      </motion.div>
    </div>
  );
}

export function UsersPage() {
  const [operators, setOperators] = useState<Operator[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showCreate, setShowCreate] = useState(false);
  const [search, setSearch] = useState('');
  const [filterRole, setFilterRole] = useState('');
  const [updatingId, setUpdatingId] = useState<number | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError('');
    try { setOperators(await listOperators()); }
    catch (err) { setError(err instanceof Error ? err.message : 'Failed to load users.'); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => { void load(); }, [load]);

  const toggleStatus = async (op: Operator) => {
    setUpdatingId(op.id);
    try { await setOperatorStatus(op.id, !op.is_active); void load(); }
    catch (err) { alert(err instanceof Error ? err.message : 'Failed.'); }
    finally { setUpdatingId(null); }
  };

  const changeRole = async (op: Operator, role: OperatorRole) => {
    setUpdatingId(op.id);
    try { await setOperatorRole(op.id, role); void load(); }
    catch (err) { alert(err instanceof Error ? err.message : 'Failed.'); }
    finally { setUpdatingId(null); }
  };

  const filtered = operators.filter((op) =>
    (!filterRole || op.role === filterRole) &&
    (!search || op.display_name.toLowerCase().includes(search.toLowerCase()) || op.username.toLowerCase().includes(search.toLowerCase()))
  );

  // Stats
  const byRole = Object.keys(ROLE_CONFIG).reduce((acc, r) => {
    acc[r] = operators.filter((o) => o.role === r).length;
    return acc;
  }, {} as Record<string, number>);

  return (
    <div style={{ maxWidth: '1100px' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 800, display: 'flex', alignItems: 'center', gap: '0.625rem' }}>
            <Users size={24} style={{ color: 'var(--color-primary)' }} /> User Management
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem', marginTop: '0.25rem' }}>
            Manage operator accounts and role assignments
          </p>
        </div>
        <div style={{ display: 'flex', gap: '0.75rem' }}>
          <button className="btn btn-ghost btn-sm" onClick={load} style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}><RefreshCw size={14} /></button>
          <button className="btn btn-primary" onClick={() => setShowCreate(true)} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Plus size={16} /> Create User
          </button>
        </div>
      </div>

      {/* Role stats */}
      <div style={{ display: 'flex', gap: '0.6rem', marginBottom: '1.25rem', flexWrap: 'wrap' }}>
        <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border-color)', borderRadius: 'var(--radius-lg)', padding: '0.5rem 1rem', display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          <span style={{ fontSize: '1.2rem', fontWeight: 800, color: 'var(--color-primary)' }}>{operators.length}</span>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Total Users</span>
        </div>
        {Object.entries(ROLE_CONFIG).filter(([k]) => byRole[k] > 0).map(([role, cfg]) => (
          <div key={role} style={{ background: 'var(--bg-card)', border: '1px solid var(--border-color)', borderRadius: 'var(--radius-lg)', padding: '0.5rem 1rem', display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
            <span style={{ fontSize: '1.2rem', fontWeight: 800, color: cfg.color }}>{byRole[role]}</span>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{cfg.label}</span>
          </div>
        ))}
      </div>

      {/* Filters */}
      <div style={{ display: 'flex', gap: '0.75rem', marginBottom: '1.25rem', flexWrap: 'wrap' }}>
        <input className="input" style={{ flex: '1', minWidth: '200px', maxWidth: '300px' }} placeholder="Search users..." value={search} onChange={(e) => setSearch(e.target.value)} />
        <select className="input" style={{ minWidth: '160px' }} value={filterRole} onChange={(e) => setFilterRole(e.target.value)}>
          <option value="">All Roles</option>
          {Object.entries(ROLE_CONFIG).map(([k, v]) => <option key={k} value={k}>{v.label}</option>)}
        </select>
      </div>

      {/* Error */}
      {error && (
        <div style={{ padding: '0.75rem 1rem', borderRadius: 'var(--radius-md)', background: 'var(--status-fail-bg)', color: 'var(--status-fail-text)', marginBottom: '1rem', fontSize: '0.875rem' }}>{error}</div>
      )}

      {/* Table */}
      {!loading && (
        <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border-color)', borderRadius: 'var(--radius-xl)', overflow: 'hidden' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border-color)', background: 'var(--bg-app)' }}>
                {['User', 'Role', 'Status', 'Last Login', 'Actions'].map((h) => (
                  <th key={h} style={{ padding: '0.75rem 1rem', textAlign: 'left', fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              <AnimatePresence>
                {filtered.map((op, idx) => (
                  <motion.tr
                    key={op.id}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: idx * 0.03 }}
                    style={{ borderBottom: '1px solid var(--border-color)', opacity: op.is_active ? 1 : 0.6 }}
                  >
                    <td style={{ padding: '0.85rem 1rem' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                        <div style={{
                          width: '36px', height: '36px', borderRadius: '50%', flexShrink: 0,
                          background: `linear-gradient(135deg, ${ROLE_CONFIG[op.role as OperatorRole]?.color ?? '#64748b'}88, ${ROLE_CONFIG[op.role as OperatorRole]?.color ?? '#64748b'}44)`,
                          display: 'flex', alignItems: 'center', justifyContent: 'center',
                          fontWeight: 700, fontSize: '0.9rem', color: '#fff',
                        }}>
                          {op.display_name.charAt(0).toUpperCase()}
                        </div>
                        <div>
                          <p style={{ fontWeight: 600, fontSize: '0.875rem' }}>{op.display_name}</p>
                          <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>@{op.username}</p>
                        </div>
                      </div>
                    </td>
                    <td style={{ padding: '0.85rem 1rem' }}>
                      <div style={{ position: 'relative', display: 'inline-block' }}>
                        <select
                          className="input"
                          style={{ fontSize: '0.75rem', padding: '0.25rem 1.5rem 0.25rem 0.5rem', minWidth: '140px', appearance: 'none' }}
                          value={op.role}
                          disabled={updatingId === op.id}
                          onChange={(e) => void changeRole(op, e.target.value as OperatorRole)}
                        >
                          {Object.entries(ROLE_CONFIG).map(([k, v]) => <option key={k} value={k}>{v.label}</option>)}
                        </select>
                        <ChevronDown size={12} style={{ position: 'absolute', right: '0.4rem', top: '50%', transform: 'translateY(-50%)', pointerEvents: 'none', color: 'var(--text-muted)' }} />
                      </div>
                    </td>
                    <td style={{ padding: '0.85rem 1rem' }}>
                      <span style={{
                        display: 'inline-flex', alignItems: 'center', gap: '0.3rem',
                        fontSize: '0.72rem', fontWeight: 700, padding: '0.2rem 0.55rem',
                        borderRadius: 'var(--radius-full)',
                        backgroundColor: op.is_active ? '#10b98120' : '#64748b15',
                        color: op.is_active ? '#10b981' : '#64748b',
                        border: `1px solid ${op.is_active ? '#10b98140' : '#64748b30'}`,
                      }}>
                        {op.is_active ? <UserCheck size={11} /> : <UserX size={11} />}
                        {op.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td style={{ padding: '0.85rem 1rem', fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                      {op.last_login_at ? new Date(op.last_login_at).toLocaleDateString() : '—'}
                    </td>
                    <td style={{ padding: '0.85rem 1rem' }}>
                      <button
                        className={`btn btn-sm ${op.is_active ? 'btn-danger' : 'btn-secondary'}`}
                        style={{ fontSize: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.35rem' }}
                        disabled={updatingId === op.id}
                        onClick={() => void toggleStatus(op)}
                      >
                        {op.is_active ? <><UserX size={13} /> Deactivate</> : <><UserCheck size={13} /> Activate</>}
                      </button>
                    </td>
                  </motion.tr>
                ))}
              </AnimatePresence>
            </tbody>
          </table>
          {filtered.length === 0 && (
            <div style={{ padding: '2.5rem', textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.875rem' }}>
              No users found matching your filters.
            </div>
          )}
        </div>
      )}

      {loading && (
        <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
          <RefreshCw size={24} style={{ animation: 'spin 1s linear infinite', display: 'block', margin: '0 auto 0.75rem' }} />
          Loading users...
        </div>
      )}

      <AnimatePresence>
        {showCreate && <CreateUserModal onClose={() => setShowCreate(false)} onCreated={load} />}
      </AnimatePresence>
    </div>
  );
}
