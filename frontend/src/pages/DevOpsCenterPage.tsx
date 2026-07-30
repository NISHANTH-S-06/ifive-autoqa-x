import React, { useEffect, useState } from 'react';
import { fetchDevOpsTools, fetchPipelines, createPipeline, triggerPipeline, deletePipeline } from '../services/phase13Service';

const card = { background: '#1e293b', borderRadius: '12px', border: '1px solid #334155', padding: '20px' };
const badge = (color: string) => ({ padding: '3px 10px', borderRadius: '20px', fontSize: '11px', fontWeight: 700 as const, background: `${color}22`, color, border: `1px solid ${color}44` });
const STATUS_COLORS: Record<string, string> = { IDLE: '#64748b', RUNNING: '#f59e0b', SUCCESS: '#10b981', FAILED: '#ef4444', QUEUED: '#38bdf8' };
const TOOL_COLORS: Record<string, string> = {
  GITHUB: '#f0f6fc', GITLAB: '#fc6d26', AZURE_DEVOPS: '#0078d4', BITBUCKET: '#0052cc',
  JENKINS: '#d33833', CIRCLECI: '#343434', TEAMCITY: '#000', ARGOCD: '#ef7b4d',
  KUBERNETES: '#326ce5', DOCKER: '#2496ed', TERRAFORM: '#7b42bc',
};

export const DevOpsCenterPage: React.FC = () => {
  const [tools, setTools] = useState<any[]>([]);
  const [pipelines, setPipelines] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [createForm, setCreateForm] = useState({ pipeline_name: '', ci_tool: 'GITHUB', repo_url: '', branch: 'main' });

  const load = async () => {
    setLoading(true);
    try {
      const [t, p] = await Promise.all([fetchDevOpsTools(), fetchPipelines()]);
      setTools(t as any[]); setPipelines(p as any[]);
    } catch (e) { console.error(e); } finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try { await createPipeline(createForm); setShowCreateModal(false); load(); } catch (err: any) { alert(err.message); }
  };

  const handleTrigger = async (pipelineId: number) => {
    try { await triggerPipeline(pipelineId); load(); } catch (err: any) { alert(err.message); }
  };

  const handleDelete = async (pipelineId: number) => {
    if (!confirm('Delete this pipeline?')) return;
    try { await deletePipeline(pipelineId); load(); } catch (err: any) { alert(err.message); }
  };

  return (
    <div style={{ padding: '24px', maxWidth: '1400px', margin: '0 auto', color: '#f8fafc' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '28px' }}>
        <div>
          <h1 style={{ fontSize: '28px', fontWeight: 800, margin: 0, background: 'linear-gradient(90deg, #f97316, #fbbf24)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            DevOps Center
          </h1>
          <p style={{ margin: '4px 0 0', color: '#64748b', fontSize: '14px' }}>CI/CD integrations — GitHub · GitLab · Azure · Jenkins · CircleCI · K8s · Docker · Terraform</p>
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button onClick={() => setShowCreateModal(true)} style={{ padding: '10px 18px', borderRadius: '8px', border: 'none', background: 'linear-gradient(135deg, #f97316, #ea580c)', color: '#fff', fontWeight: 700, cursor: 'pointer' }}>
            + Configure Pipeline
          </button>
          <button onClick={load} style={{ padding: '10px 16px', borderRadius: '8px', border: '1px solid #334155', background: '#1e293b', color: '#94a3b8', cursor: 'pointer' }}>↻</button>
        </div>
      </div>

      {/* Tool Connection Status */}
      <div style={card}>
        <h3 style={{ margin: '0 0 16px', fontSize: '16px', fontWeight: 700, color: '#f97316' }}>Integration Status</h3>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px' }}>
          {tools.map((t: any) => (
            <div key={t.ci_tool} style={{ background: '#0f172a', borderRadius: '10px', padding: '12px 16px', display: 'flex', alignItems: 'center', gap: '10px', border: `1px solid ${t.connected ? TOOL_COLORS[t.ci_tool] + '44' : '#334155'}` }}>
              <div style={{ width: '10px', height: '10px', borderRadius: '50%', background: t.connected ? '#10b981' : '#334155', boxShadow: t.connected ? '0 0 8px #10b981' : 'none' }} />
              <span style={{ fontWeight: 700, fontSize: '13px', color: t.connected ? TOOL_COLORS[t.ci_tool] || '#fff' : '#64748b' }}>{t.ci_tool}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Pipelines Table */}
      <div style={{ ...card, marginTop: '20px' }}>
        <h3 style={{ margin: '0 0 16px', fontSize: '16px', fontWeight: 700, color: '#fbbf24' }}>Configured Pipelines ({pipelines.length})</h3>
        {pipelines.length === 0 ? (
          <div style={{ color: '#64748b', textAlign: 'center', padding: '32px' }}>No pipelines configured. Click "Configure Pipeline" to add one.</div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid #334155', color: '#64748b' }}>
                  <th style={{ padding: '8px 12px', textAlign: 'left' }}>Pipeline</th>
                  <th style={{ padding: '8px 12px', textAlign: 'left' }}>Tool</th>
                  <th style={{ padding: '8px 12px', textAlign: 'left' }}>Branch</th>
                  <th style={{ padding: '8px 12px', textAlign: 'left' }}>Status</th>
                  <th style={{ padding: '8px 12px', textAlign: 'left' }}>Last Run</th>
                  <th style={{ padding: '8px 12px', textAlign: 'right' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {pipelines.map((p: any) => (
                  <tr key={p.id} style={{ borderBottom: '1px solid #1e293b' }}>
                    <td style={{ padding: '8px 12px', fontWeight: 600 }}>{p.pipeline_name}</td>
                    <td style={{ padding: '8px 12px' }}>
                      <span style={{ color: TOOL_COLORS[p.ci_tool] || '#fff', fontWeight: 700 }}>{p.ci_tool}</span>
                    </td>
                    <td style={{ padding: '8px 12px', color: '#94a3b8', fontFamily: 'monospace' }}>{p.branch}</td>
                    <td style={{ padding: '8px 12px' }}><span style={badge(STATUS_COLORS[p.pipeline_status] || '#64748b')}>{p.pipeline_status}</span></td>
                    <td style={{ padding: '8px 12px', color: '#64748b', fontSize: '12px' }}>
                      {p.last_triggered_at ? new Date(p.last_triggered_at).toLocaleString() : 'Never'}
                    </td>
                    <td style={{ padding: '8px 12px', textAlign: 'right', display: 'flex', gap: '6px', justifyContent: 'flex-end' }}>
                      <button onClick={() => handleTrigger(p.id)} style={{ padding: '5px 10px', borderRadius: '5px', border: '1px solid #f59e0b', background: '#f59e0b22', color: '#fbbf24', fontSize: '11px', cursor: 'pointer' }}>▶ Trigger</button>
                      <button onClick={() => handleDelete(p.id)} style={{ padding: '5px 10px', borderRadius: '5px', border: '1px solid #ef4444', background: '#ef444422', color: '#ef4444', fontSize: '11px', cursor: 'pointer' }}>🗑️</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Create Pipeline Modal */}
      {showCreateModal && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.8)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
          <div style={{ background: '#0f172a', borderRadius: '16px', border: '1px solid #334155', padding: '28px', width: '440px' }}>
            <h2 style={{ margin: '0 0 20px', fontSize: '18px', color: '#fff' }}>Configure Pipeline</h2>
            <form onSubmit={handleCreate} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div>
                <label style={{ fontSize: '12px', color: '#64748b', display: 'block', marginBottom: '4px' }}>Pipeline Name</label>
                <input value={createForm.pipeline_name} onChange={e => setCreateForm({ ...createForm, pipeline_name: e.target.value })} required
                  style={{ width: '100%', padding: '9px 12px', borderRadius: '6px', border: '1px solid #334155', background: '#1e293b', color: '#fff', boxSizing: 'border-box' as const }} />
              </div>
              <div>
                <label style={{ fontSize: '12px', color: '#64748b', display: 'block', marginBottom: '4px' }}>CI/CD Tool</label>
                <select value={createForm.ci_tool} onChange={e => setCreateForm({ ...createForm, ci_tool: e.target.value })}
                  style={{ width: '100%', padding: '9px 12px', borderRadius: '6px', border: '1px solid #334155', background: '#1e293b', color: '#fff' }}>
                  {['GITHUB','GITLAB','AZURE_DEVOPS','BITBUCKET','JENKINS','CIRCLECI','TEAMCITY','ARGOCD','KUBERNETES','DOCKER','TERRAFORM'].map(t => <option key={t} value={t}>{t}</option>)}
                </select>
              </div>
              <div>
                <label style={{ fontSize: '12px', color: '#64748b', display: 'block', marginBottom: '4px' }}>Repository URL</label>
                <input value={createForm.repo_url} onChange={e => setCreateForm({ ...createForm, repo_url: e.target.value })} placeholder="https://github.com/org/repo"
                  style={{ width: '100%', padding: '9px 12px', borderRadius: '6px', border: '1px solid #334155', background: '#1e293b', color: '#fff', boxSizing: 'border-box' as const }} />
              </div>
              <div>
                <label style={{ fontSize: '12px', color: '#64748b', display: 'block', marginBottom: '4px' }}>Branch</label>
                <input value={createForm.branch} onChange={e => setCreateForm({ ...createForm, branch: e.target.value })}
                  style={{ width: '100%', padding: '9px 12px', borderRadius: '6px', border: '1px solid #334155', background: '#1e293b', color: '#fff', boxSizing: 'border-box' as const }} />
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
                <button type="button" onClick={() => setShowCreateModal(false)} style={{ padding: '9px 16px', borderRadius: '6px', border: '1px solid #334155', background: '#1e293b', color: '#f8fafc' }}>Cancel</button>
                <button type="submit" style={{ padding: '9px 16px', borderRadius: '6px', border: 'none', background: 'linear-gradient(135deg, #f97316, #ea580c)', color: '#fff', fontWeight: 700 }}>Configure</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
