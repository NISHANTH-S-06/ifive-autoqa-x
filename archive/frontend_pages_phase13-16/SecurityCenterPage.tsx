import React, { useEffect, useState } from 'react';
import {
  fetchVaultSecrets, addSecret, rotateSecret, deleteSecret, fetchSecurityDashboard, fetchSSOConfig,
} from '../services/phase13Service';

const card = { background: '#1e293b', borderRadius: '12px', border: '1px solid #334155', padding: '20px' };
const badge = (color: string) => ({ padding: '3px 10px', borderRadius: '20px', fontSize: '11px', fontWeight: 700 as const, background: `${color}22`, color, border: `1px solid ${color}44` });
const STATUS_COLORS: Record<string, string> = { ACTIVE: '#10b981', ROTATED: '#a78bfa', EXPIRED: '#ef4444', REVOKED: '#6b7280' };
const TYPE_ICONS: Record<string, string> = { API_KEY: '🔑', DB_PASSWORD: '🗄️', OAUTH_SECRET: '🔐', CERTIFICATE: '📜', SSH_KEY: '💻', ENV_VAR: '⚙️' };

export const SecurityCenterPage: React.FC = () => {
  const [secrets, setSecrets] = useState<any[]>([]);
  const [dashboard, setDashboard] = useState<any>({});
  const [ssoConfig, setSsoConfig] = useState<any>({});
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [showRotateModal, setShowRotateModal] = useState<number | null>(null);
  const [addForm, setAddForm] = useState({ key_name: '', secret_type: 'API_KEY', value: '', rotation_schedule_days: 90 });
  const [rotateForm, setRotateForm] = useState({ new_value: '' });
  const [activeTab, setActiveTab] = useState<'vault' | 'sso'>('vault');

  const load = async () => {
    setLoading(true);
    try {
      const [s, d, sso] = await Promise.all([fetchVaultSecrets(), fetchSecurityDashboard(), fetchSSOConfig()]);
      setSecrets(s as any[]); setDashboard(d); setSsoConfig(sso);
    } catch (e) { console.error(e); } finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const handleAddSecret = async (e: React.FormEvent) => {
    e.preventDefault();
    try { await addSecret(addForm); setShowAddModal(false); setAddForm({ key_name: '', secret_type: 'API_KEY', value: '', rotation_schedule_days: 90 }); load(); } catch (err: any) { alert(err.message); }
  };

  const handleRotate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!showRotateModal) return;
    try { await rotateSecret(showRotateModal, rotateForm); setShowRotateModal(null); load(); } catch (err: any) { alert(err.message); }
  };

  const handleDelete = async (id: number, keyName: string) => {
    if (!confirm(`Delete secret "${keyName}"?`)) return;
    try { await deleteSecret(id); load(); } catch (err: any) { alert(err.message); }
  };

  return (
    <div style={{ padding: '24px', maxWidth: '1400px', margin: '0 auto', color: '#f8fafc' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '28px' }}>
        <div>
          <h1 style={{ fontSize: '28px', fontWeight: 800, margin: 0, background: 'linear-gradient(90deg, #ef4444, #f97316)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            Security Center
          </h1>
          <p style={{ margin: '4px 0 0', color: '#64748b', fontSize: '14px' }}>Secrets vault · Key rotation · SSO/MFA/SAML/LDAP configuration</p>
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: '28px', fontWeight: 800, color: dashboard.security_score >= 90 ? '#10b981' : '#f59e0b' }}>{dashboard.security_score ?? 0}%</div>
            <div style={{ fontSize: '11px', color: '#64748b' }}>Security Score</div>
          </div>
          <button onClick={() => setShowAddModal(true)} style={{ padding: '10px 18px', borderRadius: '8px', border: 'none', background: 'linear-gradient(135deg, #ef4444, #dc2626)', color: '#fff', fontWeight: 700, cursor: 'pointer' }}>
            + Add Secret
          </button>
          <button onClick={load} style={{ padding: '10px 16px', borderRadius: '8px', border: '1px solid #334155', background: '#1e293b', color: '#94a3b8', cursor: 'pointer' }}>↻</button>
        </div>
      </div>

      {/* Dashboard KPIs */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: '14px', marginBottom: '24px' }}>
        {[
          { label: 'Total Secrets', value: dashboard.total_secrets ?? 0, color: '#38bdf8' },
          { label: 'Active', value: dashboard.active_secrets ?? 0, color: '#10b981' },
          { label: 'Expiring Soon', value: dashboard.expiring_soon ?? 0, color: '#f59e0b' },
          { label: 'Overdue Rotation', value: dashboard.overdue_rotation ?? 0, color: '#ef4444' },
          { label: 'MFA Enforced', value: dashboard.mfa_enforced ? 'YES' : 'NO', color: dashboard.mfa_enforced ? '#10b981' : '#ef4444' },
          { label: 'Encryption', value: 'AES-256', color: '#a78bfa' },
        ].map(k => (
          <div key={k.label} style={{ ...card, textAlign: 'center' }}>
            <div style={{ fontSize: '11px', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '6px' }}>{k.label}</div>
            <div style={{ fontSize: '22px', fontWeight: 800, color: k.color }}>{k.value}</div>
          </div>
        ))}
      </div>

      {/* Tab navigation */}
      <div style={{ display: 'flex', gap: '8px', marginBottom: '20px' }}>
        {([['vault', '🔐 Secrets Vault'], ['sso', '🔒 SSO & Auth Config']] as [string, string][]).map(([key, label]) => (
          <button key={key} onClick={() => setActiveTab(key as any)} style={{ padding: '8px 18px', borderRadius: '20px', border: `1px solid ${activeTab === key ? '#ef4444' : '#334155'}`, background: activeTab === key ? '#ef444422' : '#1e293b', color: activeTab === key ? '#f87171' : '#94a3b8', fontWeight: activeTab === key ? 700 : 400, cursor: 'pointer' }}>
            {label}
          </button>
        ))}
      </div>

      {activeTab === 'vault' && (
        <div style={card}>
          <h3 style={{ margin: '0 0 16px', fontSize: '16px', fontWeight: 700, color: '#ef4444' }}>Secrets Vault ({secrets.length} entries)</h3>
          {secrets.length === 0 ? (
            <div style={{ color: '#64748b', textAlign: 'center', padding: '24px' }}>No secrets stored. Click "Add Secret" to add your first secret.</div>
          ) : (
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid #334155', color: '#64748b' }}>
                    <th style={{ padding: '8px 12px', textAlign: 'left' }}>Key</th>
                    <th style={{ padding: '8px 12px', textAlign: 'left' }}>Type</th>
                    <th style={{ padding: '8px 12px', textAlign: 'left' }}>Status</th>
                    <th style={{ padding: '8px 12px', textAlign: 'left' }}>Next Rotation</th>
                    <th style={{ padding: '8px 12px', textAlign: 'right' }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {secrets.map((s: any) => {
                    const isExpiring = s.next_rotation_at && new Date(s.next_rotation_at) < new Date(Date.now() + 30 * 86400000);
                    return (
                      <tr key={s.id} style={{ borderBottom: '1px solid #1e293b' }}>
                        <td style={{ padding: '8px 12px' }}>
                          <span style={{ fontFamily: 'monospace', fontWeight: 600 }}>{s.key_name}</span>
                        </td>
                        <td style={{ padding: '8px 12px' }}>
                          <span style={{ color: '#94a3b8' }}>{TYPE_ICONS[s.secret_type] || '🔒'} {s.secret_type}</span>
                        </td>
                        <td style={{ padding: '8px 12px' }}><span style={badge(STATUS_COLORS[s.entry_status] || '#64748b')}>{s.entry_status}</span></td>
                        <td style={{ padding: '8px 12px', color: isExpiring ? '#f59e0b' : '#64748b', fontSize: '12px' }}>
                          {s.next_rotation_at ? new Date(s.next_rotation_at).toLocaleDateString() : '—'}
                          {isExpiring && <span style={{ color: '#f59e0b', marginLeft: '4px' }}>⚠️ Soon</span>}
                        </td>
                        <td style={{ padding: '8px 12px', textAlign: 'right', display: 'flex', gap: '6px', justifyContent: 'flex-end' }}>
                          <button onClick={() => setShowRotateModal(s.id)} style={{ padding: '5px 10px', borderRadius: '5px', border: '1px solid #a78bfa', background: '#a78bfa22', color: '#a78bfa', fontSize: '11px', cursor: 'pointer' }}>🔄 Rotate</button>
                          <button onClick={() => handleDelete(s.id, s.key_name)} style={{ padding: '5px 10px', borderRadius: '5px', border: '1px solid #ef4444', background: '#ef444422', color: '#ef4444', fontSize: '11px', cursor: 'pointer' }}>🗑️</button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {activeTab === 'sso' && (
        <div style={card}>
          <h3 style={{ margin: '0 0 16px', fontSize: '16px', fontWeight: 700, color: '#38bdf8' }}>SSO & Authentication Configuration</h3>
          {ssoConfig.configurations && Object.entries(ssoConfig.configurations as Record<string, any>).map(([method, conf]) => (
            <div key={method} style={{ background: '#0f172a', borderRadius: '10px', padding: '16px', marginBottom: '10px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <span style={{ fontWeight: 700, color: '#38bdf8' }}>{method}</span>
                <span style={badge(conf.status === 'ENABLED' || conf.status === 'CONFIGURED' ? '#10b981' : '#f59e0b')}>{conf.status}</span>
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '12px' }}>
                {Object.entries(conf).filter(([k]) => k !== 'status').map(([k, v]) => (
                  <div key={k} style={{ fontSize: '12px' }}>
                    <span style={{ color: '#64748b' }}>{k}: </span>
                    <span style={{ color: '#94a3b8' }}>{Array.isArray(v) ? v.join(', ') : String(v)}</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Add Secret Modal */}
      {showAddModal && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.8)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
          <div style={{ background: '#0f172a', borderRadius: '16px', border: '1px solid #334155', padding: '28px', width: '420px' }}>
            <h2 style={{ margin: '0 0 20px', fontSize: '18px', color: '#fff' }}>🔑 Add Secret</h2>
            <form onSubmit={handleAddSecret} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div>
                <label style={{ fontSize: '12px', color: '#64748b', display: 'block', marginBottom: '4px' }}>Key Name</label>
                <input value={addForm.key_name} onChange={e => setAddForm({ ...addForm, key_name: e.target.value })} required
                  style={{ width: '100%', padding: '9px 12px', borderRadius: '6px', border: '1px solid #334155', background: '#1e293b', color: '#fff', boxSizing: 'border-box' as const }} />
              </div>
              <div>
                <label style={{ fontSize: '12px', color: '#64748b', display: 'block', marginBottom: '4px' }}>Type</label>
                <select value={addForm.secret_type} onChange={e => setAddForm({ ...addForm, secret_type: e.target.value })}
                  style={{ width: '100%', padding: '9px 12px', borderRadius: '6px', border: '1px solid #334155', background: '#1e293b', color: '#fff' }}>
                  {['API_KEY', 'DB_PASSWORD', 'OAUTH_SECRET', 'CERTIFICATE', 'SSH_KEY', 'ENV_VAR'].map(t => <option key={t} value={t}>{t}</option>)}
                </select>
              </div>
              <div>
                <label style={{ fontSize: '12px', color: '#64748b', display: 'block', marginBottom: '4px' }}>Secret Value</label>
                <input type="password" value={addForm.value} onChange={e => setAddForm({ ...addForm, value: e.target.value })} required
                  style={{ width: '100%', padding: '9px 12px', borderRadius: '6px', border: '1px solid #334155', background: '#1e293b', color: '#fff', boxSizing: 'border-box' as const }} />
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
                <button type="button" onClick={() => setShowAddModal(false)} style={{ padding: '9px 16px', borderRadius: '6px', border: '1px solid #334155', background: '#1e293b', color: '#f8fafc' }}>Cancel</button>
                <button type="submit" style={{ padding: '9px 16px', borderRadius: '6px', border: 'none', background: 'linear-gradient(135deg, #ef4444, #dc2626)', color: '#fff', fontWeight: 700 }}>Add Secret</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Rotate Modal */}
      {showRotateModal && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.8)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
          <div style={{ background: '#0f172a', borderRadius: '16px', border: '1px solid #a78bfa', padding: '28px', width: '380px' }}>
            <h2 style={{ margin: '0 0 20px', fontSize: '18px', color: '#a78bfa' }}>🔄 Rotate Secret</h2>
            <form onSubmit={handleRotate} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div>
                <label style={{ fontSize: '12px', color: '#64748b', display: 'block', marginBottom: '4px' }}>New Secret Value</label>
                <input type="password" value={rotateForm.new_value} onChange={e => setRotateForm({ new_value: e.target.value })} required
                  style={{ width: '100%', padding: '9px 12px', borderRadius: '6px', border: '1px solid #334155', background: '#1e293b', color: '#fff', boxSizing: 'border-box' as const }} />
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
                <button type="button" onClick={() => setShowRotateModal(null)} style={{ padding: '9px 16px', borderRadius: '6px', border: '1px solid #334155', background: '#1e293b', color: '#f8fafc' }}>Cancel</button>
                <button type="submit" style={{ padding: '9px 16px', borderRadius: '6px', border: 'none', background: 'linear-gradient(135deg, #7c3aed, #6366f1)', color: '#fff', fontWeight: 700 }}>Rotate</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
