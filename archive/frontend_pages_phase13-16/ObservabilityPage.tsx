import React, { useEffect, useState } from 'react';
import { fetchObservabilityDashboard, fetchMetrics, fetchTraces, fetchFailureMetrics, ingestMetric } from '../services/phase13Service';

const card = { background: '#1e293b', borderRadius: '12px', border: '1px solid #334155', padding: '20px' };
const SOURCE_COLORS: Record<string, string> = { SYSTEM: '#38bdf8', BROWSER: '#10b981', API: '#a78bfa', EXECUTION: '#f59e0b', AI: '#f472b6' };

export const ObservabilityPage: React.FC = () => {
  const [dashboard, setDashboard] = useState<any>({});
  const [metrics, setMetrics] = useState<any[]>([]);
  const [traces, setTraces] = useState<any[]>([]);
  const [failures, setFailures] = useState<any>({});
  const [loading, setLoading] = useState(true);
  const [showIngestModal, setShowIngestModal] = useState(false);
  const [ingestForm, setIngestForm] = useState({ metric_name: '', value: 0, unit: 'ms', source: 'SYSTEM' });

  const load = async () => {
    setLoading(true);
    try {
      const [d, m, t, f] = await Promise.all([fetchObservabilityDashboard(), fetchMetrics({ limit: '50' }), fetchTraces(), fetchFailureMetrics()]);
      setDashboard(d); setMetrics(m as any[]); setTraces(t as any[]); setFailures(f);
    } catch (e) { console.error(e); } finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const handleIngest = async (e: React.FormEvent) => {
    e.preventDefault();
    try { await ingestMetric(ingestForm); setShowIngestModal(false); load(); } catch (err: any) { alert(err.message); }
  };

  return (
    <div style={{ padding: '24px', maxWidth: '1400px', margin: '0 auto', color: '#f8fafc' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '28px' }}>
        <div>
          <h1 style={{ fontSize: '28px', fontWeight: 800, margin: 0, background: 'linear-gradient(90deg, #38bdf8, #10b981)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            Observability Platform
          </h1>
          <p style={{ margin: '4px 0 0', color: '#64748b', fontSize: '14px' }}>Metrics · Logs · Traces · Performance · Failures</p>
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button onClick={() => setShowIngestModal(true)} style={{ padding: '10px 18px', borderRadius: '8px', border: 'none', background: 'linear-gradient(135deg, #38bdf8, #0284c7)', color: '#fff', fontWeight: 700, cursor: 'pointer' }}>
            + Ingest Metric
          </button>
          <button onClick={load} style={{ padding: '10px 16px', borderRadius: '8px', border: '1px solid #334155', background: '#1e293b', color: '#94a3b8', cursor: 'pointer' }}>↻</button>
        </div>
      </div>

      {/* Dashboard KPIs */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '16px', marginBottom: '24px' }}>
        {[
          { label: 'Metrics (24h)', value: dashboard.total_metrics_ingested ?? 0, color: '#38bdf8' },
          { label: 'Platform Status', value: dashboard.health_status || 'HEALTHY', color: '#10b981' },
          { label: 'Total Failures', value: failures.total_failure_events ?? 0, color: '#ef4444' },
          { label: 'Failure Rate', value: `${(failures.failure_rate_pct ?? 0).toFixed(1)}%`, color: '#f59e0b' },
          { label: 'Active Traces', value: traces.length, color: '#a78bfa' },
        ].map(k => (
          <div key={k.label} style={{ ...card, textAlign: 'center' }}>
            <div style={{ fontSize: '11px', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '6px' }}>{k.label}</div>
            <div style={{ fontSize: '22px', fontWeight: 800, color: k.color }}>{k.value}</div>
          </div>
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
        {/* By Source */}
        <div style={card}>
          <h3 style={{ margin: '0 0 16px', fontSize: '16px', fontWeight: 700, color: '#38bdf8' }}>Metrics by Source</h3>
          {dashboard.by_source ? Object.entries(dashboard.by_source as Record<string, number>).map(([src, cnt]) => (
            <div key={src} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <div style={{ width: '10px', height: '10px', borderRadius: '50%', background: SOURCE_COLORS[src] || '#64748b' }} />
                <span style={{ fontSize: '13px', color: SOURCE_COLORS[src] || '#94a3b8' }}>{src}</span>
              </div>
              <span style={{ fontWeight: 700, fontSize: '16px', color: SOURCE_COLORS[src] || '#fff' }}>{cnt}</span>
            </div>
          )) : <div style={{ color: '#64748b' }}>No metrics ingested yet</div>}
        </div>

        {/* Metric Averages */}
        <div style={card}>
          <h3 style={{ margin: '0 0 16px', fontSize: '16px', fontWeight: 700, color: '#10b981' }}>Metric Averages</h3>
          {dashboard.metric_averages && Object.entries(dashboard.metric_averages as Record<string, number>).slice(0, 8).map(([name, avg]) => (
            <div key={name} style={{ marginBottom: '8px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', marginBottom: '3px' }}>
                <span style={{ color: '#94a3b8' }}>{name}</span>
                <span style={{ color: '#10b981', fontWeight: 700 }}>{avg.toFixed(1)}</span>
              </div>
              <div style={{ height: '4px', background: '#0f172a', borderRadius: '2px' }}>
                <div style={{ height: '100%', width: `${Math.min((avg / 1000) * 100, 100)}%`, background: '#10b981', borderRadius: '2px' }} />
              </div>
            </div>
          ))}
          {!dashboard.metric_averages && <div style={{ color: '#64748b' }}>No metrics to display</div>}
        </div>
      </div>

      {/* Recent Metrics */}
      <div style={{ ...card, marginTop: '20px' }}>
        <h3 style={{ margin: '0 0 16px', fontSize: '16px', fontWeight: 700, color: '#a78bfa' }}>Recent Metrics ({metrics.length})</h3>
        {metrics.length === 0 ? (
          <div style={{ color: '#64748b', textAlign: 'center', padding: '20px' }}>No metrics ingested. Click "Ingest Metric" to start.</div>
        ) : (
          <div style={{ maxHeight: '250px', overflowY: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid #334155', color: '#64748b' }}>
                  <th style={{ padding: '6px 10px', textAlign: 'left' }}>Metric</th>
                  <th style={{ padding: '6px 10px', textAlign: 'right' }}>Value</th>
                  <th style={{ padding: '6px 10px', textAlign: 'left' }}>Source</th>
                  <th style={{ padding: '6px 10px', textAlign: 'left' }}>Time</th>
                </tr>
              </thead>
              <tbody>
                {metrics.map((m: any) => (
                  <tr key={m.id} style={{ borderBottom: '1px solid #1e293b' }}>
                    <td style={{ padding: '6px 10px', fontFamily: 'monospace', color: '#94a3b8' }}>{m.metric_name}</td>
                    <td style={{ padding: '6px 10px', textAlign: 'right', fontWeight: 700, color: '#10b981' }}>{m.metric_value} {m.metric_unit}</td>
                    <td style={{ padding: '6px 10px' }}><span style={{ color: SOURCE_COLORS[m.metric_source] || '#64748b', fontWeight: 600 }}>{m.metric_source}</span></td>
                    <td style={{ padding: '6px 10px', color: '#64748b', fontSize: '11px' }}>{new Date(m.created_at).toLocaleTimeString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Distributed Traces */}
      {traces.length > 0 && (
        <div style={{ ...card, marginTop: '20px' }}>
          <h3 style={{ margin: '0 0 16px', fontSize: '16px', fontWeight: 700, color: '#f472b6' }}>Distributed Traces ({traces.length})</h3>
          {traces.map((trace: any) => (
            <div key={trace.trace_id} style={{ background: '#0f172a', borderRadius: '8px', padding: '12px 16px', marginBottom: '8px' }}>
              <div style={{ fontFamily: 'monospace', color: '#f472b6', fontWeight: 700, marginBottom: '8px', fontSize: '12px' }}>Trace: {trace.trace_id}</div>
              <div style={{ display: 'flex', gap: '4px', flexWrap: 'wrap' }}>
                {trace.spans?.map((span: any, i: number) => (
                  <div key={i} style={{ background: '#1e293b', borderRadius: '4px', padding: '4px 8px', fontSize: '11px' }}>
                    <span style={{ color: '#94a3b8' }}>{span.metric_name}: </span>
                    <span style={{ color: '#10b981', fontWeight: 700 }}>{span.metric_value}ms</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Ingest Modal */}
      {showIngestModal && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.8)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
          <div style={{ background: '#0f172a', borderRadius: '16px', border: '1px solid #334155', padding: '28px', width: '380px' }}>
            <h2 style={{ margin: '0 0 20px', fontSize: '18px', color: '#fff' }}>Ingest Metric</h2>
            <form onSubmit={handleIngest} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div>
                <label style={{ fontSize: '12px', color: '#64748b', display: 'block', marginBottom: '4px' }}>Metric Name</label>
                <input value={ingestForm.metric_name} onChange={e => setIngestForm({ ...ingestForm, metric_name: e.target.value })} required
                  style={{ width: '100%', padding: '9px 12px', borderRadius: '6px', border: '1px solid #334155', background: '#1e293b', color: '#fff', boxSizing: 'border-box' as const }} />
              </div>
              <div>
                <label style={{ fontSize: '12px', color: '#64748b', display: 'block', marginBottom: '4px' }}>Value</label>
                <input type="number" value={ingestForm.value} onChange={e => setIngestForm({ ...ingestForm, value: +e.target.value })}
                  style={{ width: '100%', padding: '9px 12px', borderRadius: '6px', border: '1px solid #334155', background: '#1e293b', color: '#fff', boxSizing: 'border-box' as const }} />
              </div>
              <div>
                <label style={{ fontSize: '12px', color: '#64748b', display: 'block', marginBottom: '4px' }}>Source</label>
                <select value={ingestForm.source} onChange={e => setIngestForm({ ...ingestForm, source: e.target.value })}
                  style={{ width: '100%', padding: '9px 12px', borderRadius: '6px', border: '1px solid #334155', background: '#1e293b', color: '#fff' }}>
                  {['SYSTEM', 'BROWSER', 'API', 'EXECUTION', 'AI'].map(s => <option key={s} value={s}>{s}</option>)}
                </select>
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
                <button type="button" onClick={() => setShowIngestModal(false)} style={{ padding: '9px 16px', borderRadius: '6px', border: '1px solid #334155', background: '#1e293b', color: '#f8fafc' }}>Cancel</button>
                <button type="submit" style={{ padding: '9px 16px', borderRadius: '6px', border: 'none', background: 'linear-gradient(135deg, #38bdf8, #0284c7)', color: '#fff', fontWeight: 700 }}>Ingest</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
