import React, { useEffect, useState } from 'react';
import { orchestrateGoal, fetchBrainRuns } from '../services/phase14Service';

const card = { background: '#1e293b', borderRadius: '12px', border: '1px solid #334155', padding: '20px' };
const badge = (color: string) => ({ padding: '3px 10px', borderRadius: '20px', fontSize: '11px', fontWeight: 700 as const, background: `${color}22`, color, border: `1px solid ${color}44` });
const STATUS_COLORS: Record<string, string> = { RUNNING: '#38bdf8', COMPLETED: '#10b981', FAILED: '#ef4444', QUEUED: '#f59e0b' };

export const EnterpriseBrainPage: React.FC = () => {
  const [runs, setRuns] = useState<any[]>([]);
  const [goalInput, setGoalInput] = useState('');
  const [priority, setPriority] = useState(5);
  const [submitting, setSubmitting] = useState(false);
  const [selectedRun, setSelectedRun] = useState<any>(null);

  const load = async () => {
    try {
      const data: any = await fetchBrainRuns();
      setRuns(data);
      if (data.length > 0 && !selectedRun) setSelectedRun(data[0]);
    } catch (e) { console.error(e); }
  };

  useEffect(() => { load(); }, []);

  const handleOrchestrate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!goalInput) return;
    setSubmitting(true);
    try {
      const result: any = await orchestrateGoal({ goal_description: goalInput, priority });
      setGoalInput('');
      setSelectedRun(result);
      load();
    } catch (err: any) { alert(err.message); } finally { setSubmitting(false); }
  };

  return (
    <div style={{ padding: '24px', maxWidth: '1600px', margin: '0 auto', color: '#f8fafc' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '28px' }}>
        <div>
          <h1 style={{ fontSize: '28px', fontWeight: 900, margin: 0, background: 'linear-gradient(90deg, #a78bfa, #f472b6)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            🧠 AI Enterprise Command Brain
          </h1>
          <p style={{ margin: '4px 0 0', color: '#64748b', fontSize: '14px' }}>Autonomous goal decomposition, decision trees, DAG orchestration & resource balancing</p>
        </div>
        <button onClick={load} style={{ padding: '10px 16px', borderRadius: '8px', border: '1px solid #334155', background: '#1e293b', color: '#94a3b8', cursor: 'pointer' }}>↻ Refresh</button>
      </div>

      {/* Goal Entry Box */}
      <div style={{ ...card, marginBottom: '24px', background: 'linear-gradient(135deg, #1e293b, #0f172a)', border: '1px solid #a78bfa44' }}>
        <h3 style={{ margin: '0 0 12px', fontSize: '16px', fontWeight: 700, color: '#a78bfa' }}>🤖 Prompt the AI Enterprise Brain</h3>
        <form onSubmit={handleOrchestrate} style={{ display: 'flex', gap: '12px' }}>
          <input
            value={goalInput}
            onChange={e => setGoalInput(e.target.value)}
            placeholder="e.g. Run full autonomous regression for ERP release v3.0, heal locators, and simulate release risk..."
            style={{ flex: 1, padding: '12px 16px', borderRadius: '8px', border: '1px solid #334155', background: '#0f172a', color: '#fff', fontSize: '14px' }}
          />
          <select value={priority} onChange={e => setPriority(+e.target.value)} style={{ padding: '12px', borderRadius: '8px', border: '1px solid #334155', background: '#0f172a', color: '#fff' }}>
            {[1,2,3,4,5,6,7,8,9,10].map(p => <option key={p} value={p}>P{p} Priority</option>)}
          </select>
          <button type="submit" disabled={submitting} style={{ padding: '12px 24px', borderRadius: '8px', border: 'none', background: 'linear-gradient(135deg, #a78bfa, #7c3aed)', color: '#fff', fontWeight: 700, cursor: 'pointer' }}>
            {submitting ? 'Decomposing...' : '⚡ Orchestrate Goal'}
          </button>
        </form>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '340px 1fr', gap: '20px' }}>
        {/* Brain Runs List */}
        <div style={card}>
          <h3 style={{ margin: '0 0 16px', fontSize: '15px', fontWeight: 700, color: '#38bdf8' }}>Orchestration History</h3>
          <div style={{ maxHeight: '550px', overflowY: 'auto' }}>
            {runs.map(r => (
              <div key={r.run_id} onClick={() => setSelectedRun(r)}
                style={{ background: selectedRun?.run_id === r.run_id ? '#0f172a' : '#1e293b', border: `1px solid ${selectedRun?.run_id === r.run_id ? '#a78bfa' : '#334155'}`, borderRadius: '8px', padding: '12px', marginBottom: '8px', cursor: 'pointer' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                  <span style={{ fontSize: '12px', fontWeight: 700, fontFamily: 'monospace', color: '#a78bfa' }}>{r.run_id}</span>
                  <span style={badge(STATUS_COLORS[r.run_status] || '#64748b')}>{r.run_status}</span>
                </div>
                <div style={{ fontSize: '12px', color: '#94a3b8', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>{r.goal_description}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Selected Run Details */}
        {selectedRun && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {/* DAG Tasks */}
            <div style={card}>
              <h3 style={{ margin: '0 0 16px', fontSize: '16px', fontWeight: 700, color: '#10b981' }}>Multi-Agent DAG Execution Graph</h3>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '12px' }}>
                {selectedRun.dag_tasks?.map((t: any) => (
                  <div key={t.id} style={{ background: '#0f172a', borderRadius: '8px', padding: '12px', borderLeft: `3px solid ${t.status === 'COMPLETED' ? '#10b981' : t.status === 'IN_PROGRESS' ? '#38bdf8' : '#64748b'}` }}>
                    <div style={{ fontSize: '11px', color: '#64748b', textTransform: 'uppercase', marginBottom: '4px' }}>{t.agent}</div>
                    <div style={{ fontWeight: 700, fontSize: '13px', marginBottom: '6px' }}>{t.name}</div>
                    <span style={badge(t.status === 'COMPLETED' ? '#10b981' : t.status === 'IN_PROGRESS' ? '#38bdf8' : '#64748b')}>{t.status}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Decision Tree & Resource Allocation */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
              <div style={card}>
                <h3 style={{ margin: '0 0 14px', fontSize: '15px', fontWeight: 700, color: '#f59e0b' }}>Autonomous Decision Tree</h3>
                {selectedRun.decision_tree?.nodes?.map((n: any) => (
                  <div key={n.id} style={{ background: '#0f172a', borderRadius: '6px', padding: '10px', marginBottom: '8px', fontSize: '12px' }}>
                    <div style={{ color: '#fbbf24', fontWeight: 600 }}>IF: {n.condition}</div>
                    <div style={{ color: '#10b981', marginTop: '2px' }}>✓ TRUE → {n.if_true}</div>
                    <div style={{ color: '#ef4444', marginTop: '2px' }}>✕ FALSE → {n.if_false}</div>
                  </div>
                ))}
              </div>

              <div style={card}>
                <h3 style={{ margin: '0 0 14px', fontSize: '15px', fontWeight: 700, color: '#38bdf8' }}>Resource Allocation & Plan</h3>
                <div style={{ fontSize: '13px', color: '#94a3b8', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  <div>Allocated Workers: <span style={{ color: '#38bdf8', fontWeight: 700 }}>{selectedRun.resource_allocation?.allocated_workers}</span></div>
                  <div>Cores / RAM: <span style={{ color: '#10b981', fontWeight: 700 }}>{selectedRun.resource_allocation?.cpu_cores} Cores · {selectedRun.resource_allocation?.memory_limit_mb} MB</span></div>
                  <div>Estimated Duration: <span style={{ color: '#a78bfa', fontWeight: 700 }}>{selectedRun.execution_plan?.estimated_total_seconds}s</span></div>
                  <div>Parallel Factor: <span style={{ color: '#f59e0b', fontWeight: 700 }}>{selectedRun.execution_plan?.parallel_factor}x</span></div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
