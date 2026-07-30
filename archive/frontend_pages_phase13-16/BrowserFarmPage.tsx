import React, { useEffect, useState } from 'react';
import {
  fetchBrowserPool, fetchLiveSessions, fetchFarmMetrics, fetchBrowserFarmHealth,
  provisionBrowserPool, autoCleanup,
} from '../services/phase13Service';

const card = { background: '#1e293b', borderRadius: '12px', border: '1px solid #334155', padding: '20px' };
const badge = (color: string) => ({ padding: '3px 10px', borderRadius: '20px', fontSize: '11px', fontWeight: 700 as const, background: `${color}22`, color, border: `1px solid ${color}44` });
const STATUS_COLORS: Record<string, string> = {
  AVAILABLE: '#10b981', RESERVED: '#f59e0b', ACTIVE: '#38bdf8', UNHEALTHY: '#ef4444', CLEANUP: '#a78bfa', TERMINATED: '#6b7280',
};
const BROWSER_ICONS: Record<string, string> = {
  CHROMIUM: '🔵', FIREFOX: '🦊', WEBKIT: '🌐', EDGE: '🔷', CHROME: '🟢', MOBILE_CHROME: '📱', MOBILE_SAFARI: '🍎',
};

export const BrowserFarmPage: React.FC = () => {
  const [pool, setPool] = useState<any>({});
  const [sessions, setSessions] = useState<any[]>([]);
  const [metrics, setMetrics] = useState<any>({});
  const [health, setHealth] = useState<any>({});
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    try {
      const [p, s, m, h] = await Promise.all([fetchBrowserPool(), fetchLiveSessions(), fetchFarmMetrics(), fetchBrowserFarmHealth()]);
      setPool(p); setSessions(s as any[]); setMetrics(m); setHealth(h);
    } catch (e) { console.error(e); } finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const handleProvision = async () => { await provisionBrowserPool(); load(); };
  const handleCleanup = async () => { await autoCleanup(); load(); };

  return (
    <div style={{ padding: '24px', maxWidth: '1400px', margin: '0 auto', color: '#f8fafc' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '28px' }}>
        <div>
          <h1 style={{ fontSize: '28px', fontWeight: 800, margin: 0, background: 'linear-gradient(90deg, #10b981, #38bdf8)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            Cloud Browser Farm
          </h1>
          <p style={{ margin: '4px 0 0', color: '#64748b', fontSize: '14px' }}>
            Multi-browser session pool — {pool.total_sessions ?? 0} sessions across 7 browser types
          </p>
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button onClick={handleProvision} style={{ padding: '10px 18px', borderRadius: '8px', border: 'none', background: 'linear-gradient(135deg, #10b981, #059669)', color: '#fff', fontWeight: 700, cursor: 'pointer' }}>
            ⚡ Provision Pool
          </button>
          <button onClick={handleCleanup} style={{ padding: '10px 16px', borderRadius: '8px', border: '1px solid #334155', background: '#1e293b', color: '#f59e0b', fontWeight: 600, cursor: 'pointer' }}>
            🧹 Auto Cleanup
          </button>
          <button onClick={load} style={{ padding: '10px 16px', borderRadius: '8px', border: '1px solid #334155', background: '#1e293b', color: '#94a3b8', cursor: 'pointer' }}>
            ↻
          </button>
        </div>
      </div>

      {/* Farm Overview */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: '16px', marginBottom: '24px' }}>
        {[
          { label: 'Total Sessions', value: metrics.total_sessions ?? 0, color: '#38bdf8' },
          { label: 'Available', value: metrics.available ?? 0, color: '#10b981' },
          { label: 'Active', value: metrics.active ?? 0, color: '#a78bfa' },
          { label: 'Reserved', value: metrics.reserved ?? 0, color: '#f59e0b' },
          { label: 'Utilization', value: `${metrics.utilization_pct ?? 0}%`, color: '#fb923c' },
          { label: 'Avg Health', value: `${metrics.avg_health_score ?? 100}%`, color: '#34d399' },
          { label: 'Unhealthy', value: health.unhealthy_count ?? 0, color: '#ef4444' },
          { label: 'Health Score', value: `${health.overall_health_pct ?? 100}%`, color: '#10b981' },
        ].map(k => (
          <div key={k.label} style={{ ...card, textAlign: 'center' }}>
            <div style={{ fontSize: '11px', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '6px' }}>{k.label}</div>
            <div style={{ fontSize: '26px', fontWeight: 800, color: k.color }}>{k.value}</div>
          </div>
        ))}
      </div>

      {/* Utilization Bar */}
      <div style={{ ...card, marginBottom: '20px' }}>
        <h3 style={{ margin: '0 0 14px', fontSize: '15px', fontWeight: 700, color: '#fb923c' }}>Farm Utilization</h3>
        <div style={{ background: '#0f172a', borderRadius: '8px', height: '20px', overflow: 'hidden', marginBottom: '8px' }}>
          <div style={{ height: '100%', width: `${metrics.utilization_pct ?? 0}%`, background: metrics.utilization_pct > 80 ? '#ef4444' : metrics.utilization_pct > 60 ? '#f59e0b' : '#10b981', borderRadius: '8px', transition: 'width 0.5s ease' }} />
        </div>
        <div style={{ fontSize: '13px', color: '#64748b' }}>{metrics.utilization_pct ?? 0}% of {metrics.total_sessions ?? 0} sessions in use</div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
        {/* By Browser Type */}
        <div style={card}>
          <h3 style={{ margin: '0 0 16px', fontSize: '16px', fontWeight: 700, color: '#38bdf8' }}>Browser Pool Breakdown</h3>
          {pool.by_browser ? Object.entries(pool.by_browser as Record<string, any>).map(([browser, info]) => (
            <div key={browser} style={{ marginBottom: '16px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                <span style={{ fontWeight: 600 }}>{BROWSER_ICONS[browser] || '🌐'} {browser}</span>
                <span style={{ fontSize: '12px', color: '#64748b' }}>{info.available}/{info.total} available</span>
              </div>
              <div style={{ display: 'flex', gap: '4px' }}>
                {(['available', 'active', 'reserved', 'unhealthy'] as const).map(s => (
                  info[s] > 0 && (
                    <div key={s} title={`${s}: ${info[s]}`} style={{ flex: info[s], height: '8px', borderRadius: '4px', background: STATUS_COLORS[s.toUpperCase()] || '#64748b' }} />
                  )
                ))}
              </div>
            </div>
          )) : <div style={{ color: '#64748b' }}>No pool data. Click "Provision Pool" to initialize.</div>}
        </div>

        {/* Live Sessions */}
        <div style={card}>
          <h3 style={{ margin: '0 0 16px', fontSize: '16px', fontWeight: 700, color: '#a78bfa' }}>Live Sessions ({sessions.length})</h3>
          {sessions.length === 0 ? (
            <div style={{ color: '#64748b', textAlign: 'center', padding: '20px' }}>No active sessions currently</div>
          ) : (
            <div style={{ maxHeight: '320px', overflowY: 'auto' }}>
              {sessions.map((s: any) => (
                <div key={s.session_id} style={{ background: '#0f172a', borderRadius: '8px', padding: '12px', marginBottom: '8px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                    <span style={{ fontSize: '13px', fontWeight: 700, color: '#38bdf8' }}>{BROWSER_ICONS[s.browser_type]} {s.browser_type}</span>
                    <span style={badge(STATUS_COLORS[s.session_status] || '#64748b')}>{s.session_status}</span>
                  </div>
                  <div style={{ fontSize: '11px', color: '#64748b', fontFamily: 'monospace' }}>{s.session_id}</div>
                  {s.reserved_by_job_id && <div style={{ fontSize: '11px', color: '#94a3b8', marginTop: '4px' }}>Job: {s.reserved_by_job_id}</div>}
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '6px' }}>
                    <div style={{ flex: 1, height: '4px', background: '#1e293b', borderRadius: '2px' }}>
                      <div style={{ height: '100%', width: `${s.health_score}%`, background: s.health_score > 70 ? '#10b981' : '#ef4444', borderRadius: '2px' }} />
                    </div>
                    <span style={{ fontSize: '11px', color: '#94a3b8' }}>{s.health_score.toFixed(0)}%</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
