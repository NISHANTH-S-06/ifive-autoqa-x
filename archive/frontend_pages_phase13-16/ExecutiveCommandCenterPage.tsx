import React, { useEffect, useState } from 'react';
import {
  fetchExecutiveKPIs, fetchCompanyOverview, fetchPlatformHealth, fetchActiveAlerts, fetchKPIHistory,
} from '../services/phase13Service';

const card = { background: '#1e293b', borderRadius: '12px', border: '1px solid #334155', padding: '20px' };
const SEVERITY_COLORS: Record<string, string> = { CRITICAL: '#ef4444', HIGH: '#f97316', MEDIUM: '#f59e0b', LOW: '#38bdf8' };

function ScoreGauge({ score, color, label }: { score: number; color: string; label: string }) {
  return (
    <div style={{ textAlign: 'center' }}>
      <div style={{ position: 'relative', width: '90px', height: '90px', margin: '0 auto 8px' }}>
        <svg viewBox="0 0 36 36" style={{ width: '90px', height: '90px', transform: 'rotate(-90deg)' }}>
          <circle cx="18" cy="18" r="15.9" fill="none" stroke="#0f172a" strokeWidth="3.8" />
          <circle cx="18" cy="18" r="15.9" fill="none" stroke={color} strokeWidth="3.8"
            strokeDasharray={`${score} ${100 - score}`} strokeLinecap="round" />
        </svg>
        <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 800, fontSize: '15px', color }}>{score.toFixed(0)}%</div>
      </div>
      <div style={{ fontSize: '11px', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.04em' }}>{label}</div>
    </div>
  );
}

export const ExecutiveCommandCenterPage: React.FC = () => {
  const [kpis, setKpis] = useState<any>({});
  const [companies, setCompanies] = useState<any[]>([]);
  const [health, setHealth] = useState<any>({});
  const [alerts, setAlerts] = useState<any[]>([]);
  const [history, setHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    try {
      const [k, c, h, a, hist] = await Promise.all([
        fetchExecutiveKPIs(), fetchCompanyOverview(), fetchPlatformHealth(), fetchActiveAlerts(), fetchKPIHistory(),
      ]);
      setKpis(k); setCompanies(c as any[]); setHealth(h); setAlerts(a as any[]); setHistory(hist as any[]);
    } catch (e) { console.error(e); } finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  return (
    <div style={{ padding: '24px', maxWidth: '1600px', margin: '0 auto', color: '#f8fafc' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '28px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '4px' }}>
            <h1 style={{ fontSize: '30px', fontWeight: 900, margin: 0, background: 'linear-gradient(90deg, #38bdf8, #a78bfa, #f472b6)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
              Global Command Center
            </h1>
            <div style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#10b981', boxShadow: '0 0 12px #10b981', animation: 'pulse 2s infinite' }} />
          </div>
          <p style={{ margin: 0, color: '#64748b', fontSize: '14px' }}>Enterprise AI QA Platform — Global Executive Dashboard</p>
        </div>
        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          <div style={{ background: '#0f172a', borderRadius: '10px', padding: '10px 16px', border: '1px solid #334155' }}>
            <div style={{ fontSize: '11px', color: '#64748b', textTransform: 'uppercase' }}>Platform Status</div>
            <div style={{ fontWeight: 800, fontSize: '16px', color: health.platform_status === 'HEALTHY' ? '#10b981' : '#f59e0b', marginTop: '2px' }}>
              ● {health.platform_status || '—'}
            </div>
          </div>
          <button onClick={load} style={{ padding: '10px 16px', borderRadius: '8px', border: '1px solid #334155', background: '#1e293b', color: '#94a3b8', cursor: 'pointer' }}>↻ Refresh</button>
        </div>
      </div>

      {/* Active Alerts */}
      {alerts.length > 0 && (
        <div style={{ marginBottom: '20px' }}>
          {alerts.map((alert: any, i: number) => (
            <div key={i} style={{ background: `${SEVERITY_COLORS[alert.severity] || '#334155'}11`, border: `1px solid ${SEVERITY_COLORS[alert.severity] || '#334155'}44`, borderRadius: '10px', padding: '12px 16px', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '12px' }}>
              <span style={{ fontSize: '18px' }}>{alert.severity === 'CRITICAL' ? '🚨' : alert.severity === 'HIGH' ? '⚠️' : '💡'}</span>
              <span style={{ color: SEVERITY_COLORS[alert.severity] || '#fff', fontWeight: 600 }}>[{alert.severity}] {alert.message}</span>
              <span style={{ marginLeft: 'auto', fontSize: '11px', color: '#64748b', background: '#0f172a', padding: '2px 8px', borderRadius: '4px' }}>{alert.category}</span>
            </div>
          ))}
        </div>
      )}

      {/* Top KPI Row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '14px', marginBottom: '24px' }}>
        {[
          { label: 'Companies', value: kpis.total_companies ?? 0, color: '#38bdf8', icon: '🏢' },
          { label: 'Projects', value: kpis.total_projects ?? 0, color: '#a78bfa', icon: '📁' },
          { label: 'Active Workers', value: kpis.active_workers ?? 0, color: '#10b981', icon: '⚙️' },
          { label: 'Executions Today', value: kpis.total_executions_today ?? 0, color: '#f59e0b', icon: '▶️' },
          { label: 'Browser Sessions', value: kpis.total_browser_sessions ?? 0, color: '#34d399', icon: '🌐' },
          { label: 'Farm Utilization', value: `${kpis.browser_farm_utilization_pct ?? 0}%`, color: '#fb923c', icon: '📊' },
        ].map(k => (
          <div key={k.label} style={{ ...card, textAlign: 'center' }}>
            <div style={{ fontSize: '20px', marginBottom: '4px' }}>{k.icon}</div>
            <div style={{ fontSize: '10px', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '4px' }}>{k.label}</div>
            <div style={{ fontSize: '28px', fontWeight: 800, color: k.color }}>{k.value}</div>
          </div>
        ))}
      </div>

      {/* Score Gauges */}
      <div style={{ ...card, marginBottom: '24px' }}>
        <h3 style={{ margin: '0 0 20px', fontSize: '16px', fontWeight: 700, color: '#a78bfa' }}>Global Score Gauges</h3>
        <div style={{ display: 'flex', gap: '32px', flexWrap: 'wrap', justifyContent: 'center' }}>
          <ScoreGauge score={kpis.overall_quality_score ?? 90} color="#a78bfa" label="Overall Quality" />
          <ScoreGauge score={kpis.ai_health_score ?? 100} color="#10b981" label="AI Health" />
          <ScoreGauge score={kpis.release_readiness_score ?? 85} color="#f59e0b" label="Release Readiness" />
          <ScoreGauge score={kpis.compliance_score ?? 95} color="#38bdf8" label="Compliance" />
          <ScoreGauge score={kpis.security_score ?? 98} color="#ef4444" label="Security" />
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
        {/* Company Overview */}
        <div style={card}>
          <h3 style={{ margin: '0 0 16px', fontSize: '16px', fontWeight: 700, color: '#38bdf8' }}>Company Overview</h3>
          {companies.length === 0 ? (
            <div style={{ color: '#64748b', textAlign: 'center', padding: '20px' }}>No companies registered</div>
          ) : (
            <div style={{ maxHeight: '280px', overflowY: 'auto' }}>
              {companies.map((c: any) => (
                <div key={c.id} style={{ background: '#0f172a', borderRadius: '8px', padding: '12px 16px', marginBottom: '8px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <div style={{ fontWeight: 700 }}>{c.name}</div>
                    <div style={{ fontSize: '12px', color: '#64748b' }}>{c.industry} · {c.products} products</div>
                  </div>
                  <div style={{ fontSize: '11px', background: '#10b98122', color: '#10b981', border: '1px solid #10b98144', borderRadius: '4px', padding: '2px 8px' }}>ACTIVE</div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Worker Health */}
        <div style={card}>
          <h3 style={{ margin: '0 0 16px', fontSize: '16px', fontWeight: 700, color: '#10b981' }}>Platform Infrastructure</h3>
          {health.worker_health && (
            <div style={{ marginBottom: '16px' }}>
              <div style={{ fontSize: '13px', color: '#64748b', marginBottom: '10px' }}>Worker Node Health</div>
              <div style={{ display: 'flex', gap: '16px' }}>
                {[
                  { label: 'Total', value: health.worker_health.total, color: '#38bdf8' },
                  { label: 'Healthy', value: health.worker_health.healthy, color: '#10b981' },
                  { label: 'Unhealthy', value: health.worker_health.unhealthy, color: '#ef4444' },
                ].map(w => (
                  <div key={w.label} style={{ flex: 1, background: '#0f172a', borderRadius: '8px', padding: '12px', textAlign: 'center' }}>
                    <div style={{ fontSize: '22px', fontWeight: 800, color: w.color }}>{w.value}</div>
                    <div style={{ fontSize: '11px', color: '#64748b' }}>{w.label}</div>
                  </div>
                ))}
              </div>
            </div>
          )}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
            {[
              { label: 'API Latency', value: `${health.api_latency_ms ?? 0}ms`, color: '#38bdf8' },
              { label: 'DB Response', value: `${health.db_response_ms ?? 0}ms`, color: '#10b981' },
              { label: 'Uptime', value: `${health.uptime_pct ?? 0}%`, color: '#34d399' },
              { label: 'Platform', value: health.platform_status || '—', color: health.platform_status === 'HEALTHY' ? '#10b981' : '#f59e0b' },
            ].map(m => (
              <div key={m.label} style={{ background: '#0f172a', borderRadius: '8px', padding: '10px 14px' }}>
                <div style={{ fontSize: '11px', color: '#64748b' }}>{m.label}</div>
                <div style={{ fontSize: '18px', fontWeight: 800, color: m.color, marginTop: '2px' }}>{m.value}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* KPI History */}
      {history.length > 0 && (
        <div style={{ ...card, marginTop: '20px' }}>
          <h3 style={{ margin: '0 0 16px', fontSize: '16px', fontWeight: 700, color: '#f472b6' }}>KPI Snapshot History ({history.length})</h3>
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid #334155', color: '#64748b' }}>
                  <th style={{ padding: '8px 10px', textAlign: 'left' }}>Snapshot</th>
                  <th style={{ padding: '8px 10px', textAlign: 'right' }}>Quality</th>
                  <th style={{ padding: '8px 10px', textAlign: 'right' }}>Compliance</th>
                  <th style={{ padding: '8px 10px', textAlign: 'right' }}>Security</th>
                  <th style={{ padding: '8px 10px', textAlign: 'right' }}>AI Health</th>
                  <th style={{ padding: '8px 10px', textAlign: 'right' }}>Created</th>
                </tr>
              </thead>
              <tbody>
                {history.map((h: any) => (
                  <tr key={h.id} style={{ borderBottom: '1px solid #1e293b' }}>
                    <td style={{ padding: '8px 10px', fontFamily: 'monospace', color: '#94a3b8' }}>{h.snapshot_label}</td>
                    <td style={{ padding: '8px 10px', textAlign: 'right', fontWeight: 700, color: '#a78bfa' }}>{h.overall_quality_score}%</td>
                    <td style={{ padding: '8px 10px', textAlign: 'right', color: '#38bdf8' }}>{h.compliance_score}%</td>
                    <td style={{ padding: '8px 10px', textAlign: 'right', color: '#ef4444' }}>{h.security_score}%</td>
                    <td style={{ padding: '8px 10px', textAlign: 'right', color: '#10b981' }}>{h.ai_health_score}%</td>
                    <td style={{ padding: '8px 10px', textAlign: 'right', color: '#64748b' }}>{new Date(h.created_at).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
