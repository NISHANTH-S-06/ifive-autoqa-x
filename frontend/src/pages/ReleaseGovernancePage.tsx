import React, { useEffect, useState } from 'react';
import {
  fetchGovernanceStages, createGovernanceWorkflow, submitApproval, fetchAuditTrail,
  fetchWorkflowStatus, createRollback,
} from '../services/phase13Service';

const card = { background: '#1e293b', borderRadius: '12px', border: '1px solid #334155', padding: '20px' };
const badge = (color: string) => ({ padding: '3px 10px', borderRadius: '20px', fontSize: '11px', fontWeight: 700 as const, background: `${color}22`, color, border: `1px solid ${color}44` });
const STAGE_COLORS: Record<string, string> = { PENDING: '#64748b', APPROVED: '#10b981', REJECTED: '#ef4444', SKIPPED: '#a78bfa' };
const STAGE_META = [
  { name: 'QA_LEAD', icon: '🧪', label: 'QA Lead' },
  { name: 'QA_MANAGER', icon: '👔', label: 'QA Manager' },
  { name: 'ENGINEERING_MANAGER', icon: '⚙️', label: 'Eng. Manager' },
  { name: 'PRODUCT_OWNER', icon: '📦', label: 'Product Owner' },
  { name: 'RELEASE_MANAGER', icon: '🚀', label: 'Release Mgr' },
  { name: 'CTO', icon: '👑', label: 'CTO' },
];

export const ReleaseGovernancePage: React.FC = () => {
  const [stages, setStages] = useState<any[]>([]);
  const [auditTrail, setAuditTrail] = useState<any[]>([]);
  const [releaseVersion, setReleaseVersion] = useState('v2.0.0');
  const [status, setStatus] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showApproveModal, setShowApproveModal] = useState<number | null>(null);
  const [approveForm, setApproveForm] = useState({ approver_name: '', approver_role: 'APPROVER', decision: 'APPROVED', comments: '' });
  const [createVersion, setCreateVersion] = useState('');

  const load = async () => {
    setLoading(true);
    try {
      const [s, a] = await Promise.all([fetchGovernanceStages(releaseVersion), fetchAuditTrail(releaseVersion)]);
      setStages(s as any[]); setAuditTrail(a as any[]);
      if ((s as any[]).length > 0) {
        const ws = await fetchWorkflowStatus(releaseVersion);
        setStatus(ws);
      }
    } catch (e) { console.error(e); } finally { setLoading(false); }
  };

  useEffect(() => { load(); }, [releaseVersion]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try { await createGovernanceWorkflow({ project_id: null, release_version: createVersion }); setShowCreateModal(false); setReleaseVersion(createVersion); } catch (err: any) { alert(err.message); }
  };

  const handleApprove = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!showApproveModal) return;
    try {
      await submitApproval(showApproveModal, approveForm);
      setShowApproveModal(null);
      load();
    } catch (err: any) { alert(err.message); }
  };

  return (
    <div style={{ padding: '24px', maxWidth: '1400px', margin: '0 auto', color: '#f8fafc' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '28px' }}>
        <div>
          <h1 style={{ fontSize: '28px', fontWeight: 800, margin: 0, background: 'linear-gradient(90deg, #f59e0b, #f97316)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            Release Governance
          </h1>
          <p style={{ margin: '4px 0 0', color: '#64748b', fontSize: '14px' }}>6-stage electronic approval workflow with digital signatures and audit trail</p>
        </div>
        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          <input value={releaseVersion} onChange={e => setReleaseVersion(e.target.value)}
            style={{ padding: '8px 12px', borderRadius: '8px', border: '1px solid #334155', background: '#1e293b', color: '#fff', fontSize: '13px' }}
            placeholder="Release version..." />
          <button onClick={() => setShowCreateModal(true)} style={{ padding: '10px 18px', borderRadius: '8px', border: 'none', background: 'linear-gradient(135deg, #f59e0b, #f97316)', color: '#fff', fontWeight: 700, cursor: 'pointer' }}>
            + Create Workflow
          </button>
          <button onClick={load} style={{ padding: '10px 16px', borderRadius: '8px', border: '1px solid #334155', background: '#1e293b', color: '#94a3b8', cursor: 'pointer' }}>↻</button>
        </div>
      </div>

      {/* Workflow Status */}
      {status && (
        <div style={{ ...card, marginBottom: '20px', background: status.overall_status === 'APPROVED' ? '#0f2d1a' : status.overall_status === 'REJECTED' ? '#2d0f0f' : '#0f172a' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <span style={{ fontWeight: 700, fontSize: '16px' }}>Release {status.release_version}</span>
              <span style={{ ...badge(status.overall_status === 'APPROVED' ? '#10b981' : status.overall_status === 'REJECTED' ? '#ef4444' : '#f59e0b'), marginLeft: '12px' }}>{status.overall_status}</span>
            </div>
            <div style={{ display: 'flex', gap: '20px', fontSize: '14px' }}>
              <span style={{ color: '#10b981' }}>✅ {status.approved} Approved</span>
              <span style={{ color: '#ef4444' }}>❌ {status.rejected} Rejected</span>
              <span style={{ color: '#64748b' }}>⏳ {status.pending} Pending</span>
            </div>
          </div>
        </div>
      )}

      {/* 6-Stage Pipeline */}
      <div style={card}>
        <h3 style={{ margin: '0 0 20px', fontSize: '16px', fontWeight: 700, color: '#f59e0b' }}>
          Approval Pipeline — {releaseVersion}
        </h3>
        {stages.length === 0 ? (
          <div style={{ textAlign: 'center', color: '#64748b', padding: '40px' }}>
            No workflow for this release version. Click "Create Workflow" to start.
          </div>
        ) : (
          <div>
            {/* Pipeline progress bar */}
            <div style={{ display: 'flex', marginBottom: '20px', position: 'relative' }}>
              {stages.map((s, i) => {
                const meta = STAGE_META[i] || { icon: '⭕', label: s.stage_name };
                const color = STAGE_COLORS[s.stage_status] || '#64748b';
                return (
                  <div key={s.id} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', position: 'relative' }}>
                    {i < stages.length - 1 && (
                      <div style={{ position: 'absolute', top: '20px', left: '50%', right: '-50%', height: '2px', background: s.stage_status === 'APPROVED' ? '#10b981' : '#334155', zIndex: 0 }} />
                    )}
                    <div style={{ width: '40px', height: '40px', borderRadius: '50%', background: `${color}22`, border: `2px solid ${color}`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '16px', position: 'relative', zIndex: 1, marginBottom: '8px' }}>
                      {s.stage_status === 'APPROVED' ? '✅' : s.stage_status === 'REJECTED' ? '❌' : meta.icon}
                    </div>
                    <div style={{ textAlign: 'center' }}>
                      <div style={{ fontSize: '11px', fontWeight: 700, color }}>{meta.label}</div>
                      <div style={{ fontSize: '10px', color: '#64748b', marginTop: '2px' }}>{s.stage_status}</div>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Stage details table */}
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px', marginTop: '16px' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid #334155', color: '#64748b' }}>
                  <th style={{ padding: '8px 12px', textAlign: 'left' }}>Stage</th>
                  <th style={{ padding: '8px 12px', textAlign: 'left' }}>Required Role</th>
                  <th style={{ padding: '8px 12px', textAlign: 'left' }}>Status</th>
                  <th style={{ padding: '8px 12px', textAlign: 'left' }}>Notes</th>
                  <th style={{ padding: '8px 12px', textAlign: 'right' }}>Action</th>
                </tr>
              </thead>
              <tbody>
                {stages.map((s: any, i: number) => (
                  <tr key={s.id} style={{ borderBottom: '1px solid #1e293b' }}>
                    <td style={{ padding: '8px 12px', fontWeight: 600 }}>{STAGE_META[i]?.icon} {s.stage_name}</td>
                    <td style={{ padding: '8px 12px', color: '#94a3b8' }}>{s.required_role}</td>
                    <td style={{ padding: '8px 12px' }}><span style={badge(STAGE_COLORS[s.stage_status] || '#64748b')}>{s.stage_status}</span></td>
                    <td style={{ padding: '8px 12px', color: '#64748b', fontSize: '12px' }}>{s.notes || '—'}</td>
                    <td style={{ padding: '8px 12px', textAlign: 'right' }}>
                      {s.stage_status === 'PENDING' && (
                        <button onClick={() => setShowApproveModal(s.id)} style={{ padding: '6px 12px', borderRadius: '6px', border: '1px solid #10b981', background: '#10b98122', color: '#10b981', fontSize: '11px', cursor: 'pointer', fontWeight: 700 }}>
                          Submit Approval
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Audit Trail */}
      <div style={{ ...card, marginTop: '20px' }}>
        <h3 style={{ margin: '0 0 16px', fontSize: '16px', fontWeight: 700, color: '#a78bfa' }}>Electronic Audit Trail ({auditTrail.length} entries)</h3>
        {auditTrail.length === 0 ? (
          <div style={{ color: '#64748b' }}>No approvals recorded for this release yet.</div>
        ) : (
          <div style={{ maxHeight: '300px', overflowY: 'auto' }}>
            {auditTrail.map((a: any) => (
              <div key={a.id} style={{ background: '#0f172a', borderRadius: '8px', padding: '12px 16px', marginBottom: '8px', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <div style={{ fontWeight: 700, marginBottom: '4px' }}>{a.approver_name} <span style={{ color: '#64748b', fontWeight: 400, fontSize: '12px' }}>({a.approver_role})</span></div>
                  <div style={{ fontSize: '11px', color: '#64748b', fontFamily: 'monospace' }}>🔑 {a.digital_signature}</div>
                  {a.comments && <div style={{ fontSize: '12px', color: '#94a3b8', marginTop: '4px' }}>"{a.comments}"</div>}
                </div>
                <div style={{ textAlign: 'right' }}>
                  <span style={badge(a.decision === 'APPROVED' ? '#10b981' : '#ef4444')}>{a.decision}</span>
                  <div style={{ fontSize: '11px', color: '#64748b', marginTop: '4px' }}>{new Date(a.signed_at).toLocaleString()}</div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Create Workflow Modal */}
      {showCreateModal && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.8)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
          <div style={{ background: '#0f172a', borderRadius: '16px', border: '1px solid #334155', padding: '28px', width: '380px' }}>
            <h2 style={{ margin: '0 0 20px', fontSize: '18px', color: '#fff' }}>Create 6-Stage Workflow</h2>
            <form onSubmit={handleCreate} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div>
                <label style={{ fontSize: '12px', color: '#64748b', display: 'block', marginBottom: '4px' }}>Release Version</label>
                <input value={createVersion} onChange={e => setCreateVersion(e.target.value)} placeholder="e.g. v2.1.0"
                  style={{ width: '100%', padding: '9px 12px', borderRadius: '6px', border: '1px solid #334155', background: '#1e293b', color: '#fff', boxSizing: 'border-box' as const }} required />
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
                <button type="button" onClick={() => setShowCreateModal(false)} style={{ padding: '9px 16px', borderRadius: '6px', border: '1px solid #334155', background: '#1e293b', color: '#f8fafc' }}>Cancel</button>
                <button type="submit" style={{ padding: '9px 16px', borderRadius: '6px', border: 'none', background: 'linear-gradient(135deg, #f59e0b, #f97316)', color: '#fff', fontWeight: 700 }}>Create Workflow</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Approve Stage Modal */}
      {showApproveModal && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.8)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
          <div style={{ background: '#0f172a', borderRadius: '16px', border: '1px solid #334155', padding: '28px', width: '400px' }}>
            <h2 style={{ margin: '0 0 20px', fontSize: '18px', color: '#fff' }}>Submit Electronic Approval</h2>
            <form onSubmit={handleApprove} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              {[{ label: 'Approver Name', key: 'approver_name', type: 'text' }].map(f => (
                <div key={f.key}>
                  <label style={{ fontSize: '12px', color: '#64748b', display: 'block', marginBottom: '4px' }}>{f.label}</label>
                  <input value={(approveForm as any)[f.key]} onChange={e => setApproveForm({ ...approveForm, [f.key]: e.target.value })}
                    style={{ width: '100%', padding: '9px 12px', borderRadius: '6px', border: '1px solid #334155', background: '#1e293b', color: '#fff', boxSizing: 'border-box' as const }} required />
                </div>
              ))}
              <div>
                <label style={{ fontSize: '12px', color: '#64748b', display: 'block', marginBottom: '4px' }}>Decision</label>
                <select value={approveForm.decision} onChange={e => setApproveForm({ ...approveForm, decision: e.target.value })}
                  style={{ width: '100%', padding: '9px 12px', borderRadius: '6px', border: '1px solid #334155', background: '#1e293b', color: '#fff' }}>
                  <option value="APPROVED">APPROVED</option>
                  <option value="REJECTED">REJECTED</option>
                  <option value="CONDITIONAL">CONDITIONAL</option>
                </select>
              </div>
              <div>
                <label style={{ fontSize: '12px', color: '#64748b', display: 'block', marginBottom: '4px' }}>Comments (optional)</label>
                <textarea value={approveForm.comments} onChange={e => setApproveForm({ ...approveForm, comments: e.target.value })} rows={3}
                  style={{ width: '100%', padding: '9px 12px', borderRadius: '6px', border: '1px solid #334155', background: '#1e293b', color: '#fff', resize: 'vertical', boxSizing: 'border-box' as const }} />
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
                <button type="button" onClick={() => setShowApproveModal(null)} style={{ padding: '9px 16px', borderRadius: '6px', border: '1px solid #334155', background: '#1e293b', color: '#f8fafc' }}>Cancel</button>
                <button type="submit" style={{ padding: '9px 16px', borderRadius: '6px', border: 'none', background: approveForm.decision === 'APPROVED' ? 'linear-gradient(135deg, #10b981, #059669)' : '#dc2626', color: '#fff', fontWeight: 700 }}>
                  ✍️ Sign & Submit
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
