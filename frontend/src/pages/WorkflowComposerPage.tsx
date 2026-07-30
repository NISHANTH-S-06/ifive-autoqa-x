import React, { useEffect, useState } from 'react';
import { fetchWorkflowTemplates, seedWorkflowTemplates, executeWorkflow, fetchWorkflowExecutions } from '../services/phase14Service';

const card = { background: '#1e293b', borderRadius: '12px', border: '1px solid #334155', padding: '20px' };
const badge = (color: string) => ({ padding: '3px 10px', borderRadius: '20px', fontSize: '11px', fontWeight: 700 as const, background: `${color}22`, color, border: `1px solid ${color}44` });
const NODE_TYPE_COLORS: Record<string, string> = { ACTION: '#38bdf8', CONDITION: '#f59e0b', BRANCH: '#a78bfa', LOOP: '#10b981' };

export const WorkflowComposerPage: React.FC = () => {
  const [templates, setTemplates] = useState<any[]>([]);
  const [executions, setExecutions] = useState<any[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    try {
      let t: any = await fetchWorkflowTemplates();
      if (t.length === 0) t = await seedWorkflowTemplates();
      const ex: any = await fetchWorkflowExecutions();
      setTemplates(t); setExecutions(ex);
      if (t.length > 0 && !selectedTemplate) setSelectedTemplate(t[0]);
    } catch (e) { console.error(e); } finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const handleExecute = async (tplId: number, tplName: string) => {
    try {
      await executeWorkflow({ template_id: tplId, execution_name: `Run: ${tplName}` });
      load();
    } catch (err: any) { alert(err.message); }
  };

  return (
    <div style={{ padding: '24px', maxWidth: '1600px', margin: '0 auto', color: '#f8fafc' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '28px' }}>
        <div>
          <h1 style={{ fontSize: '28px', fontWeight: 900, margin: 0, background: 'linear-gradient(90deg, #38bdf8, #818cf8)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            🔀 Autonomous Workflow Composer
          </h1>
          <p style={{ margin: '4px 0 0', color: '#64748b', fontSize: '14px' }}>Visual QA flow builder — branching, loops, conditions, retries, and automated execution</p>
        </div>
        <button onClick={load} style={{ padding: '10px 16px', borderRadius: '8px', border: '1px solid #334155', background: '#1e293b', color: '#94a3b8', cursor: 'pointer' }}>↻ Refresh</button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '360px 1fr', gap: '20px' }}>
        {/* Templates Sidebar */}
        <div style={card}>
          <h3 style={{ margin: '0 0 16px', fontSize: '16px', fontWeight: 700, color: '#38bdf8' }}>Workflow Templates</h3>
          {templates.map(t => (
            <div key={t.id} onClick={() => setSelectedTemplate(t)}
              style={{ background: selectedTemplate?.id === t.id ? '#0f172a' : '#1e293b', border: `1px solid ${selectedTemplate?.id === t.id ? '#38bdf8' : '#334155'}`, borderRadius: '10px', padding: '14px', marginBottom: '10px', cursor: 'pointer' }}>
              <div style={{ fontWeight: 700, fontSize: '14px', marginBottom: '4px' }}>{t.template_name}</div>
              <div style={{ fontSize: '12px', color: '#64748b', marginBottom: '10px' }}>{t.description}</div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={badge('#38bdf8')}>{t.category}</span>
                <button onClick={(e) => { e.stopPropagation(); handleExecute(t.id, t.template_name); }}
                  style={{ padding: '5px 12px', borderRadius: '6px', border: 'none', background: 'linear-gradient(135deg, #38bdf8, #0284c7)', color: '#fff', fontWeight: 700, fontSize: '11px', cursor: 'pointer' }}>
                  ▶ Execute
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* Visual Workflow Canvas */}
        {selectedTemplate && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <div style={card}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                <div>
                  <h3 style={{ margin: 0, fontSize: '18px', fontWeight: 700, color: '#fff' }}>{selectedTemplate.template_name}</h3>
                  <span style={{ fontSize: '12px', color: '#64748b' }}>Visual Execution Flow Graph</span>
                </div>
                <button onClick={() => handleExecute(selectedTemplate.id, selectedTemplate.template_name)}
                  style={{ padding: '8px 18px', borderRadius: '8px', border: 'none', background: 'linear-gradient(135deg, #10b981, #059669)', color: '#fff', fontWeight: 700, cursor: 'pointer' }}>
                  ⚡ Trigger Workflow Execution
                </button>
              </div>

              {/* Node Sequence */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {selectedTemplate.graph_definition?.nodes?.map((node: any, i: number) => {
                  const color = NODE_TYPE_COLORS[node.type] || '#64748b';
                  return (
                    <div key={node.id} style={{ background: '#0f172a', border: `1px solid ${color}44`, borderRadius: '10px', padding: '14px 18px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
                        <div style={{ width: '28px', height: '28px', borderRadius: '50%', background: `${color}22`, border: `2px solid ${color}`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '12px', fontWeight: 800, color }}>
                          {i + 1}
                        </div>
                        <div>
                          <div style={{ fontWeight: 700, fontSize: '14px' }}>{node.label}</div>
                          <div style={{ fontSize: '11px', color: '#64748b', fontFamily: 'monospace' }}>Node ID: {node.id}</div>
                        </div>
                      </div>
                      <span style={badge(color)}>{node.type}</span>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Execution History */}
            <div style={card}>
              <h3 style={{ margin: '0 0 16px', fontSize: '16px', fontWeight: 700, color: '#818cf8' }}>Recent Executions</h3>
              {executions.length === 0 ? <div style={{ color: '#64748b' }}>No execution history yet. Click "Execute" to start a run.</div> : (
                <div style={{ overflowX: 'auto' }}>
                  <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
                    <thead>
                      <tr style={{ borderBottom: '1px solid #334155', color: '#64748b' }}>
                        <th style={{ padding: '8px 12px', textAlign: 'left' }}>Execution</th>
                        <th style={{ padding: '8px 12px', textAlign: 'left' }}>Status</th>
                        <th style={{ padding: '8px 12px', textAlign: 'left' }}>Current Step</th>
                        <th style={{ padding: '8px 12px', textAlign: 'right' }}>Started</th>
                      </tr>
                    </thead>
                    <tbody>
                      {executions.map((ex: any) => (
                        <tr key={ex.id} style={{ borderBottom: '1px solid #1e293b' }}>
                          <td style={{ padding: '8px 12px', fontWeight: 600 }}>{ex.execution_name}</td>
                          <td style={{ padding: '8px 12px' }}><span style={badge(ex.execution_status === 'RUNNING' ? '#38bdf8' : '#10b981')}>{ex.execution_status}</span></td>
                          <td style={{ padding: '8px 12px', color: '#94a3b8', fontFamily: 'monospace' }}>{ex.current_step_id || '—'}</td>
                          <td style={{ padding: '8px 12px', textAlign: 'right', color: '#64748b', fontSize: '12px' }}>{ex.started_at ? new Date(ex.started_at).toLocaleTimeString() : '—'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
