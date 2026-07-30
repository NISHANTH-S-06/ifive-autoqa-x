import React, { useEffect, useState } from 'react';
import { fetchBusinessProcesses, seedBusinessProcesses, createBusinessProcess } from '../services/phase14Service';

const card = { background: '#1e293b', borderRadius: '12px', border: '1px solid #334155', padding: '20px' };
const badge = (color: string) => ({ padding: '3px 10px', borderRadius: '20px', fontSize: '11px', fontWeight: 700 as const, background: `${color}22`, color, border: `1px solid ${color}44` });
const DOMAIN_ICONS: Record<string, string> = { HRMS: '👥', PAYROLL: '💰', ERP: '⚙️', CRM: '🤝', BANKING: '🏦', HEALTHCARE: '🏥', FINANCE: '📊' };

export const BusinessProcessCenterPage: React.FC = () => {
  const [processes, setProcesses] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [addForm, setAddForm] = useState({ process_name: '', domain_type: 'HRMS', risk_score: 80, is_critical_path: true });

  const load = async () => {
    setLoading(true);
    try {
      let data: any = await fetchBusinessProcesses();
      if (data.length === 0) data = await seedBusinessProcesses();
      setProcesses(data);
    } catch (e) { console.error(e); } finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await createBusinessProcess(addForm);
      setShowAddModal(false);
      load();
    } catch (err: any) { alert(err.message); }
  };

  return (
    <div style={{ padding: '24px', maxWidth: '1600px', margin: '0 auto', color: '#f8fafc' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '28px' }}>
        <div>
          <h1 style={{ fontSize: '28px', fontWeight: 900, margin: 0, background: 'linear-gradient(90deg, #10b981, #34d399)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            🏢 AI Business Process Understanding
          </h1>
          <p style={{ margin: '4px 0 0', color: '#64748b', fontSize: '14px' }}>Deep enterprise domain flows — HRMS, ERP, Payroll, CRM, Banking, Healthcare & critical rule assertions</p>
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button onClick={() => setShowAddModal(true)} style={{ padding: '10px 18px', borderRadius: '8px', border: 'none', background: 'linear-gradient(135deg, #10b981, #059669)', color: '#fff', fontWeight: 700, cursor: 'pointer' }}>
            + Add Domain Process
          </button>
          <button onClick={load} style={{ padding: '10px 16px', borderRadius: '8px', border: '1px solid #334155', background: '#1e293b', color: '#94a3b8', cursor: 'pointer' }}>↻</button>
        </div>
      </div>

      {/* Process Cards Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(360px, 1fr))', gap: '20px' }}>
        {processes.map((p: any) => (
          <div key={p.id} style={{ ...card, borderLeft: `4px solid ${p.risk_score > 90 ? '#ef4444' : p.risk_score > 80 ? '#f59e0b' : '#10b981'}` }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
              <div>
                <span style={{ fontSize: '20px', marginRight: '8px' }}>{DOMAIN_ICONS[p.domain_type] || '💼'}</span>
                <span style={{ fontWeight: 700, fontSize: '15px' }}>{p.process_name}</span>
              </div>
              <span style={badge('#10b981')}>{p.domain_type}</span>
            </div>

            <div style={{ display: 'flex', gap: '12px', marginBottom: '14px', fontSize: '12px' }}>
              <div style={{ background: '#0f172a', padding: '6px 10px', borderRadius: '6px' }}>
                Risk Score: <span style={{ color: p.risk_score > 90 ? '#ef4444' : '#f59e0b', fontWeight: 800 }}>{p.risk_score}%</span>
              </div>
              <div style={{ background: '#0f172a', padding: '6px 10px', borderRadius: '6px' }}>
                Critical Path: <span style={{ color: p.is_critical_path ? '#10b981' : '#64748b', fontWeight: 700 }}>{p.is_critical_path ? 'YES' : 'NO'}</span>
              </div>
            </div>

            {/* Flow Graph Nodes */}
            <div style={{ marginBottom: '14px' }}>
              <div style={{ fontSize: '11px', color: '#64748b', textTransform: 'uppercase', marginBottom: '6px' }}>Flow Chain</div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                {p.flow_graph?.nodes?.map((node: string, i: number) => (
                  <span key={node} style={{ fontSize: '11px', background: '#0f172a', border: '1px solid #334155', color: '#94a3b8', padding: '3px 8px', borderRadius: '4px' }}>
                    {i + 1}. {node}
                  </span>
                ))}
              </div>
            </div>

            {/* Rules */}
            <div>
              <div style={{ fontSize: '11px', color: '#64748b', textTransform: 'uppercase', marginBottom: '6px' }}>Critical Rules ({p.rules?.length || 0})</div>
              {p.rules?.map((r: any) => (
                <div key={r.id} style={{ background: '#0f172a', borderRadius: '6px', padding: '8px 10px', marginBottom: '4px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '12px' }}>
                  <span>{r.rule_name}</span>
                  <span style={badge(r.severity === 'CRITICAL' ? '#ef4444' : '#f59e0b')}>{r.severity}</span>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Add Modal */}
      {showAddModal && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.8)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
          <div style={{ background: '#0f172a', borderRadius: '16px', border: '1px solid #334155', padding: '28px', width: '400px' }}>
            <h2 style={{ margin: '0 0 20px', fontSize: '18px', color: '#fff' }}>Add Business Process</h2>
            <form onSubmit={handleAdd} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div>
                <label style={{ fontSize: '12px', color: '#64748b', display: 'block', marginBottom: '4px' }}>Process Name</label>
                <input value={addForm.process_name} onChange={e => setAddForm({ ...addForm, process_name: e.target.value })} required
                  style={{ width: '100%', padding: '9px 12px', borderRadius: '6px', border: '1px solid #334155', background: '#1e293b', color: '#fff', boxSizing: 'border-box' as const }} />
              </div>
              <div>
                <label style={{ fontSize: '12px', color: '#64748b', display: 'block', marginBottom: '4px' }}>Domain Type</label>
                <select value={addForm.domain_type} onChange={e => setAddForm({ ...addForm, domain_type: e.target.value })}
                  style={{ width: '100%', padding: '9px 12px', borderRadius: '6px', border: '1px solid #334155', background: '#1e293b', color: '#fff' }}>
                  {['HRMS','PAYROLL','RECRUITMENT','CRM','SALES','INVENTORY','MANUFACTURING','FINANCE','PROCUREMENT','HEALTHCARE','INSURANCE','BANKING','EDUCATION','ERP'].map(d => <option key={d} value={d}>{d}</option>)}
                </select>
              </div>
              <div>
                <label style={{ fontSize: '12px', color: '#64748b', display: 'block', marginBottom: '4px' }}>Risk Score (%)</label>
                <input type="number" value={addForm.risk_score} onChange={e => setAddForm({ ...addForm, risk_score: +e.target.value })}
                  style={{ width: '100%', padding: '9px 12px', borderRadius: '6px', border: '1px solid #334155', background: '#1e293b', color: '#fff', boxSizing: 'border-box' as const }} />
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
                <button type="button" onClick={() => setShowAddModal(false)} style={{ padding: '9px 16px', borderRadius: '6px', border: '1px solid #334155', background: '#1e293b', color: '#f8fafc' }}>Cancel</button>
                <button type="submit" style={{ padding: '9px 16px', borderRadius: '6px', border: 'none', background: 'linear-gradient(135deg, #10b981, #059669)', color: '#fff', fontWeight: 700 }}>Add Process</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
