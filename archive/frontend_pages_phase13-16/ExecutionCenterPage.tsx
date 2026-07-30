import React, { useEffect, useState } from 'react';
import {
  fetchWorkers, fetchQueue, fetchQueueAnalytics, fetchCostReport,
  fetchScaleRecommendation, fetchWorkerHealth, registerWorker, submitJob, retryFailedJobs,
} from '../services/phase13Service';

const card = {
  background: '#1e293b', borderRadius: '12px', border: '1px solid #334155', padding: '20px',
};
const badge = (color: string) => ({
  padding: '3px 10px', borderRadius: '20px', fontSize: '11px', fontWeight: 700,
  background: `${color}22`, color, border: `1px solid ${color}44`,
});
const STATUS_COLORS: Record<string, string> = {
  IDLE: '#10b981', BUSY: '#f59e0b', UNHEALTHY: '#ef4444', OFFLINE: '#6b7280', DRAINING: '#a78bfa',
};
const QUEUE_COLORS: Record<string, string> = {
  QUEUED: '#38bdf8', ASSIGNED: '#a78bfa', RUNNING: '#10b981', COMPLETED: '#34d399', FAILED: '#ef4444',
};

export const ExecutionCenterPage: React.FC = () => {
  const [workers, setWorkers] = useState<any[]>([]);
  const [queue, setQueue] = useState<any>({});
  const [analytics, setAnalytics] = useState<any>({});
  const [cost, setCost] = useState<any>({});
  const [scale, setScale] = useState<any>({});
  const [health, setHealth] = useState<any>({});
  const [loading, setLoading] = useState(true);
  const [showRegisterModal, setShowRegisterModal] = useState(false);
  const [registerForm, setRegisterForm] = useState({ worker_name: '', region: 'local', capacity: 5, browser_types: ['CHROMIUM'] });
  const [showJobModal, setShowJobModal] = useState(false);
  const [jobForm, setJobForm] = useState({ browser_type: 'CHROMIUM', priority: 5, estimated_duration_ms: 60000 });

  const load = async () => {
    setLoading(true);
    try {
      const [w, q, a, c, s, h] = await Promise.all([
        fetchWorkers(), fetchQueue(), fetchQueueAnalytics(), fetchCostReport(),
        fetchScaleRecommendation(), fetchWorkerHealth(),
      ]);
      setWorkers(w as any[]); setQueue(q); setAnalytics(a); setCost(c); setScale(s); setHealth(h);
    } catch (e) { console.error(e); } finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const handleRegisterWorker = async (e: React.FormEvent) => {
    e.preventDefault();
    try { await registerWorker(registerForm); setShowRegisterModal(false); load(); } catch (err: any) { alert(err.message); }
  };

  const handleSubmitJob = async (e: React.FormEvent) => {
    e.preventDefault();
    try { await submitJob(jobForm); setShowJobModal(false); load(); } catch (err: any) { alert(err.message); }
  };

  return (
    <div style={{ padding: '24px', maxWidth: '1400px', margin: '0 auto', color: '#f8fafc' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '28px' }}>
        <div>
          <h1 style={{ fontSize: '28px', fontWeight: 800, margin: 0, background: 'linear-gradient(90deg, #38bdf8, #a78bfa)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            Execution Center
          </h1>
          <p style={{ margin: '4px 0 0', color: '#64748b', fontSize: '14px' }}>
            Distributed AI execution orchestrator — workers, queue, cost tracking
          </p>
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button onClick={() => setShowJobModal(true)} style={{ padding: '10px 18px', borderRadius: '8px', border: 'none', background: 'linear-gradient(135deg, #7c3aed, #6366f1)', color: '#fff', fontWeight: 700, cursor: 'pointer' }}>
            + Submit Job
          </button>
          <button onClick={() => setShowRegisterModal(true)} style={{ padding: '10px 18px', borderRadius: '8px', border: '1px solid #334155', background: '#1e293b', color: '#f8fafc', fontWeight: 600, cursor: 'pointer' }}>
            + Register Worker
          </button>
          <button onClick={load} style={{ padding: '10px 16px', borderRadius: '8px', border: '1px solid #334155', background: '#1e293b', color: '#94a3b8', cursor: 'pointer' }}>
            ↻ Refresh
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '16px', marginBottom: '24px' }}>
        {[
          { label: 'Total Workers', value: health.total_workers ?? 0, color: '#38bdf8' },
          { label: 'Idle Workers', value: health.idle ?? 0, color: '#10b981' },
          { label: 'Busy Workers', value: health.busy ?? 0, color: '#f59e0b' },
          { label: 'Unhealthy', value: health.unhealthy ?? 0, color: '#ef4444' },
          { label: 'Total Jobs', value: analytics.total_jobs ?? 0, color: '#a78bfa' },
          { label: 'Completed', value: analytics.completed ?? 0, color: '#34d399' },
          { label: 'Failed', value: analytics.failed ?? 0, color: '#f87171' },
          { label: 'Total Cost', value: `$${(cost.total_cost_usd ?? 0).toFixed(4)}`, color: '#fb923c' },
        ].map((k) => (
          <div key={k.label} style={{ ...card, textAlign: 'center' }}>
            <div style={{ fontSize: '11px', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '6px' }}>{k.label}</div>
            <div style={{ fontSize: '28px', fontWeight: 800, color: k.color }}>{k.value}</div>
          </div>
        ))}
      </div>

      {/* Scale Recommendation */}
      {scale.recommendation && scale.recommendation !== 'NO_ACTION' && (
        <div style={{ background: scale.recommendation === 'SCALE_UP' ? '#1c1917' : '#0f2d1a', border: `1px solid ${scale.recommendation === 'SCALE_UP' ? '#f59e0b' : '#10b981'}`, borderRadius: '10px', padding: '14px 18px', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span style={{ fontSize: '20px' }}>{scale.recommendation === 'SCALE_UP' ? '⬆️' : '⬇️'}</span>
          <span style={{ fontWeight: 600, color: scale.recommendation === 'SCALE_UP' ? '#fbbf24' : '#34d399' }}>
            AI Recommends: {scale.recommendation} — {scale.queued_jobs} queued jobs, {scale.idle_workers} idle workers
          </span>
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
        {/* Workers Table */}
        <div style={card}>
          <h3 style={{ margin: '0 0 16px', fontSize: '16px', fontWeight: 700, color: '#38bdf8' }}>Worker Registry</h3>
          {loading ? (
            <div style={{ color: '#64748b', textAlign: 'center', padding: '20px' }}>Loading workers...</div>
          ) : workers.length === 0 ? (
            <div style={{ color: '#64748b', textAlign: 'center', padding: '20px' }}>No workers registered. Click "Register Worker" to add one.</div>
          ) : (
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid #334155', color: '#64748b' }}>
                    <th style={{ padding: '8px 10px', textAlign: 'left' }}>Name</th>
                    <th style={{ padding: '8px 10px', textAlign: 'left' }}>Status</th>
                    <th style={{ padding: '8px 10px', textAlign: 'left' }}>Region</th>
                    <th style={{ padding: '8px 10px', textAlign: 'right' }}>Jobs</th>
                  </tr>
                </thead>
                <tbody>
                  {workers.map((w: any) => (
                    <tr key={w.id} style={{ borderBottom: '1px solid #1e293b' }}>
                      <td style={{ padding: '8px 10px', fontWeight: 600 }}>{w.worker_name}</td>
                      <td style={{ padding: '8px 10px' }}>
                        <span style={badge(STATUS_COLORS[w.worker_status] || '#64748b')}>{w.worker_status}</span>
                      </td>
                      <td style={{ padding: '8px 10px', color: '#94a3b8' }}>{w.region}</td>
                      <td style={{ padding: '8px 10px', textAlign: 'right', color: '#94a3b8' }}>{w.active_jobs}/{w.capacity}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Queue Status */}
        <div style={card}>
          <h3 style={{ margin: '0 0 16px', fontSize: '16px', fontWeight: 700, color: '#a78bfa' }}>Queue Status</h3>
          <div style={{ marginBottom: '16px' }}>
            {queue.by_status && Object.entries(queue.by_status as Record<string, number>).map(([status, count]) => (
              <div key={status} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <span style={badge(QUEUE_COLORS[status] || '#64748b')}>{status}</span>
                <span style={{ fontWeight: 700, fontSize: '18px', color: QUEUE_COLORS[status] || '#94a3b8' }}>{count}</span>
              </div>
            ))}
          </div>
          {queue.queued && queue.queued.length > 0 && (
            <div>
              <div style={{ fontSize: '12px', color: '#64748b', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Recent Items</div>
              {queue.queued.slice(0, 5).map((item: any) => (
                <div key={item.job_id} style={{ background: '#0f172a', borderRadius: '6px', padding: '8px 12px', marginBottom: '6px', fontSize: '12px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ color: '#38bdf8', fontWeight: 600 }}>{item.job_id}</span>
                    <span style={badge(QUEUE_COLORS[item.queue_status] || '#64748b')}>{item.queue_status}</span>
                  </div>
                  <div style={{ color: '#64748b', marginTop: '4px' }}>P{item.priority} • {item.browser_type}</div>
                </div>
              ))}
            </div>
          )}
          <div style={{ marginTop: '12px', display: 'flex', gap: '8px' }}>
            <button onClick={retryFailedJobs} style={{ padding: '8px 14px', borderRadius: '6px', border: '1px solid #334155', background: '#0f172a', color: '#f59e0b', fontSize: '12px', cursor: 'pointer', fontWeight: 600 }}>
              Retry Failed
            </button>
          </div>
        </div>
      </div>

      {/* Cost Breakdown */}
      <div style={{ ...card, marginTop: '20px' }}>
        <h3 style={{ margin: '0 0 16px', fontSize: '16px', fontWeight: 700, color: '#fb923c' }}>Cost Breakdown</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
          <div>
            <div style={{ fontSize: '12px', color: '#64748b', marginBottom: '6px' }}>By Browser</div>
            {cost.by_browser && Object.entries(cost.by_browser as Record<string, number>).map(([b, v]) => (
              <div key={b} style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px', fontSize: '13px' }}>
                <span style={{ color: '#94a3b8' }}>{b}</span><span style={{ color: '#fb923c', fontWeight: 700 }}>${v.toFixed(4)}</span>
              </div>
            ))}
          </div>
          <div>
            <div style={{ fontSize: '12px', color: '#64748b', marginBottom: '6px' }}>By Region</div>
            {cost.by_region && Object.entries(cost.by_region as Record<string, number>).map(([r, v]) => (
              <div key={r} style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px', fontSize: '13px' }}>
                <span style={{ color: '#94a3b8' }}>{r}</span><span style={{ color: '#fb923c', fontWeight: 700 }}>${v.toFixed(4)}</span>
              </div>
            ))}
          </div>
          <div>
            <div style={{ fontSize: '12px', color: '#64748b', marginBottom: '6px' }}>Averages</div>
            <div style={{ fontSize: '13px', color: '#94a3b8', marginBottom: '4px' }}>Avg duration: <span style={{ color: '#f8fafc', fontWeight: 700 }}>{analytics.avg_duration_ms ?? 0}ms</span></div>
            <div style={{ fontSize: '13px', color: '#94a3b8' }}>Cost/exec: <span style={{ color: '#f8fafc', fontWeight: 700 }}>${(cost.cost_per_execution_avg ?? 0).toFixed(6)}</span></div>
          </div>
        </div>
      </div>

      {/* Register Worker Modal */}
      {showRegisterModal && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.8)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
          <div style={{ background: '#0f172a', borderRadius: '16px', border: '1px solid #334155', padding: '28px', width: '420px' }}>
            <h2 style={{ margin: '0 0 20px', fontSize: '18px', color: '#fff' }}>Register Worker Node</h2>
            <form onSubmit={handleRegisterWorker} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              {[{ label: 'Worker Name', key: 'worker_name', type: 'text' }, { label: 'Region', key: 'region', type: 'text' }].map(f => (
                <div key={f.key}>
                  <label style={{ fontSize: '12px', color: '#64748b', display: 'block', marginBottom: '4px' }}>{f.label}</label>
                  <input value={(registerForm as any)[f.key]} onChange={e => setRegisterForm({ ...registerForm, [f.key]: e.target.value })}
                    style={{ width: '100%', padding: '9px 12px', borderRadius: '6px', border: '1px solid #334155', background: '#1e293b', color: '#fff', boxSizing: 'border-box' }} />
                </div>
              ))}
              <div>
                <label style={{ fontSize: '12px', color: '#64748b', display: 'block', marginBottom: '4px' }}>Capacity</label>
                <input type="number" value={registerForm.capacity} onChange={e => setRegisterForm({ ...registerForm, capacity: +e.target.value })}
                  style={{ width: '100%', padding: '9px 12px', borderRadius: '6px', border: '1px solid #334155', background: '#1e293b', color: '#fff', boxSizing: 'border-box' }} />
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
                <button type="button" onClick={() => setShowRegisterModal(false)} style={{ padding: '9px 16px', borderRadius: '6px', border: '1px solid #334155', background: '#1e293b', color: '#f8fafc' }}>Cancel</button>
                <button type="submit" style={{ padding: '9px 16px', borderRadius: '6px', border: 'none', background: 'linear-gradient(135deg, #7c3aed, #6366f1)', color: '#fff', fontWeight: 700 }}>Register</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Submit Job Modal */}
      {showJobModal && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.8)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
          <div style={{ background: '#0f172a', borderRadius: '16px', border: '1px solid #334155', padding: '28px', width: '380px' }}>
            <h2 style={{ margin: '0 0 20px', fontSize: '18px', color: '#fff' }}>Submit Execution Job</h2>
            <form onSubmit={handleSubmitJob} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div>
                <label style={{ fontSize: '12px', color: '#64748b', display: 'block', marginBottom: '4px' }}>Browser Type</label>
                <select value={jobForm.browser_type} onChange={e => setJobForm({ ...jobForm, browser_type: e.target.value })}
                  style={{ width: '100%', padding: '9px 12px', borderRadius: '6px', border: '1px solid #334155', background: '#1e293b', color: '#fff' }}>
                  {['CHROMIUM','FIREFOX','WEBKIT','EDGE','CHROME','MOBILE_CHROME','MOBILE_SAFARI'].map(b => <option key={b} value={b}>{b}</option>)}
                </select>
              </div>
              <div>
                <label style={{ fontSize: '12px', color: '#64748b', display: 'block', marginBottom: '4px' }}>Priority (1=highest)</label>
                <input type="number" min={1} max={10} value={jobForm.priority} onChange={e => setJobForm({ ...jobForm, priority: +e.target.value })}
                  style={{ width: '100%', padding: '9px 12px', borderRadius: '6px', border: '1px solid #334155', background: '#1e293b', color: '#fff', boxSizing: 'border-box' }} />
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
                <button type="button" onClick={() => setShowJobModal(false)} style={{ padding: '9px 16px', borderRadius: '6px', border: '1px solid #334155', background: '#1e293b', color: '#f8fafc' }}>Cancel</button>
                <button type="submit" style={{ padding: '9px 16px', borderRadius: '6px', border: 'none', background: 'linear-gradient(135deg, #7c3aed, #6366f1)', color: '#fff', fontWeight: 700 }}>Submit</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
