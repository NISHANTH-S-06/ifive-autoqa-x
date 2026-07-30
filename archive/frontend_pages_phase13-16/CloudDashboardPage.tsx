import React, { useEffect, useState } from 'react';
import { fetchCloudRegions, fetchCloudHealth, seedCloudRegions, triggerFailover, fetchBackupStatus } from '../services/phase13Service';

const card = { background: '#1e293b', borderRadius: '12px', border: '1px solid #334155', padding: '20px' };
const badge = (color: string) => ({ padding: '3px 10px', borderRadius: '20px', fontSize: '11px', fontWeight: 700 as const, background: `${color}22`, color, border: `1px solid ${color}44` });
const STATUS_COLORS: Record<string, string> = { ACTIVE: '#10b981', FAILOVER: '#f59e0b', DEGRADED: '#f59e0b', OFFLINE: '#ef4444' };
const PROVIDER_COLORS: Record<string, string> = { AWS: '#ff9900', AZURE: '#0078d4', GCP: '#34a853', ON_PREMISE: '#64748b' };

export const CloudDashboardPage: React.FC = () => {
  const [regions, setRegions] = useState<any[]>([]);
  const [health, setHealth] = useState<any>({});
  const [backup, setBackup] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [failoverModal, setFailoverModal] = useState(false);
  const [failoverForm, setFailoverForm] = useState({ from_region_id: 0, to_region_id: 0 });

  const load = async () => {
    setLoading(true);
    try {
      const [r, h, b] = await Promise.all([fetchCloudRegions(), fetchCloudHealth(), fetchBackupStatus()]);
      setRegions(r as any[]); setHealth(h); setBackup(b as any[]);
    } catch (e) { console.error(e); } finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const handleSeed = async () => { await seedCloudRegions(); load(); };
  const handleFailover = async (e: React.FormEvent) => {
    e.preventDefault();
    try { await triggerFailover(failoverForm); setFailoverModal(false); load(); } catch (err: any) { alert(err.message); }
  };

  const byProvider = regions.reduce((acc: any, r: any) => {
    if (!acc[r.cloud_provider]) acc[r.cloud_provider] = [];
    acc[r.cloud_provider].push(r); return acc;
  }, {});

  return (
    <div style={{ padding: '24px', maxWidth: '1400px', margin: '0 auto', color: '#f8fafc' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '28px' }}>
        <div>
          <h1 style={{ fontSize: '28px', fontWeight: 800, margin: 0, background: 'linear-gradient(90deg, #ff9900, #0078d4, #34a853)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            Cloud Dashboard
          </h1>
          <p style={{ margin: '4px 0 0', color: '#64748b', fontSize: '14px' }}>Multi-region cloud deployment — AWS · Azure · GCP · On-Premise</p>
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button onClick={handleSeed} style={{ padding: '10px 18px', borderRadius: '8px', border: 'none', background: 'linear-gradient(135deg, #0078d4, #34a853)', color: '#fff', fontWeight: 700, cursor: 'pointer' }}>
            🌐 Seed Regions
          </button>
          <button onClick={() => setFailoverModal(true)} style={{ padding: '10px 16px', borderRadius: '8px', border: '1px solid #f59e0b', background: '#1c1917', color: '#fbbf24', fontWeight: 600, cursor: 'pointer' }}>
            ⚡ Trigger Failover
          </button>
          <button onClick={load} style={{ padding: '10px 16px', borderRadius: '8px', border: '1px solid #334155', background: '#1e293b', color: '#94a3b8', cursor: 'pointer' }}>↻</button>
        </div>
      </div>

      {/* Health KPIs */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: '16px', marginBottom: '24px' }}>
        {[
          { label: 'Total Regions', value: health.total_regions ?? 0, color: '#38bdf8' },
          { label: 'Active', value: health.active ?? 0, color: '#10b981' },
          { label: 'Degraded', value: health.degraded ?? 0, color: '#f59e0b' },
          { label: 'Offline', value: health.offline ?? 0, color: '#ef4444' },
          { label: 'Health Score', value: `${health.health_pct ?? 0}%`, color: '#34d399' },
        ].map(k => (
          <div key={k.label} style={{ ...card, textAlign: 'center' }}>
            <div style={{ fontSize: '11px', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '6px' }}>{k.label}</div>
            <div style={{ fontSize: '28px', fontWeight: 800, color: k.color }}>{k.value}</div>
          </div>
        ))}
      </div>

      {/* By Provider */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px', marginBottom: '20px' }}>
        {Object.entries(byProvider).map(([provider, providerRegions]: [string, any]) => (
          <div key={provider} style={{ ...card, borderLeft: `4px solid ${PROVIDER_COLORS[provider] || '#64748b'}` }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
              <h3 style={{ margin: 0, fontSize: '16px', fontWeight: 700, color: PROVIDER_COLORS[provider] || '#fff' }}>{provider}</h3>
              <span style={{ fontSize: '12px', color: '#64748b' }}>{providerRegions.length} regions</span>
            </div>
            {providerRegions.map((r: any) => (
              <div key={r.id} style={{ background: '#0f172a', borderRadius: '8px', padding: '10px 14px', marginBottom: '8px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <div style={{ fontWeight: 600, fontSize: '13px' }}>{r.region_display}</div>
                  <div style={{ fontSize: '11px', color: '#64748b', marginTop: '2px', fontFamily: 'monospace' }}>{r.region_name}</div>
                  <div style={{ display: 'flex', gap: '6px', marginTop: '4px' }}>
                    {r.is_primary && <span style={{ fontSize: '10px', background: '#38bdf822', color: '#38bdf8', border: '1px solid #38bdf844', borderRadius: '4px', padding: '1px 6px' }}>PRIMARY</span>}
                    {r.is_disaster_recovery && <span style={{ fontSize: '10px', background: '#ef444422', color: '#ef4444', border: '1px solid #ef444444', borderRadius: '4px', padding: '1px 6px' }}>DR</span>}
                    <span style={{ fontSize: '10px', color: '#64748b' }}>P{r.failover_priority}</span>
                  </div>
                </div>
                <span style={badge(STATUS_COLORS[r.region_status] || '#64748b')}>{r.region_status}</span>
              </div>
            ))}
          </div>
        ))}
      </div>

      {/* Backup Status */}
      <div style={card}>
        <h3 style={{ margin: '0 0 16px', fontSize: '16px', fontWeight: 700, color: '#a78bfa' }}>Backup & Replication Status</h3>
        {backup.length === 0 ? <div style={{ color: '#64748b' }}>No backup data available</div> : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid #334155', color: '#64748b' }}>
                  <th style={{ padding: '8px 12px', textAlign: 'left' }}>Region</th>
                  <th style={{ padding: '8px 12px', textAlign: 'left' }}>Provider</th>
                  <th style={{ padding: '8px 12px', textAlign: 'left' }}>Last Backup</th>
                  <th style={{ padding: '8px 12px', textAlign: 'right' }}>Replication Lag</th>
                </tr>
              </thead>
              <tbody>
                {backup.map((b: any, i: number) => (
                  <tr key={i} style={{ borderBottom: '1px solid #1e293b' }}>
                    <td style={{ padding: '8px 12px', fontWeight: 600 }}>{b.region_name}</td>
                    <td style={{ padding: '8px 12px' }}><span style={{ color: PROVIDER_COLORS[b.cloud_provider] || '#64748b', fontWeight: 600 }}>{b.cloud_provider}</span></td>
                    <td style={{ padding: '8px 12px', color: '#94a3b8' }}>{b.last_backup_at ? new Date(b.last_backup_at).toLocaleString() : 'Never'}</td>
                    <td style={{ padding: '8px 12px', textAlign: 'right', color: b.replication_lag_ms > 100 ? '#f59e0b' : '#10b981', fontWeight: 700 }}>{b.replication_lag_ms}ms</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Failover Modal */}
      {failoverModal && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.8)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
          <div style={{ background: '#0f172a', borderRadius: '16px', border: '1px solid #f59e0b', padding: '28px', width: '380px' }}>
            <h2 style={{ margin: '0 0 20px', fontSize: '18px', color: '#fbbf24' }}>⚡ Trigger Failover</h2>
            <form onSubmit={handleFailover} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              {[{ label: 'From Region ID', key: 'from_region_id' }, { label: 'To Region ID', key: 'to_region_id' }].map(f => (
                <div key={f.key}>
                  <label style={{ fontSize: '12px', color: '#64748b', display: 'block', marginBottom: '4px' }}>{f.label}</label>
                  <input type="number" value={(failoverForm as any)[f.key]} onChange={e => setFailoverForm({ ...failoverForm, [f.key]: +e.target.value })}
                    style={{ width: '100%', padding: '9px 12px', borderRadius: '6px', border: '1px solid #334155', background: '#1e293b', color: '#fff', boxSizing: 'border-box' as const }} />
                </div>
              ))}
              <div style={{ fontSize: '12px', color: '#f59e0b', background: '#1c110022', borderRadius: '6px', padding: '10px' }}>⚠️ This will immediately reroute traffic. Confirm with ops team before proceeding.</div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
                <button type="button" onClick={() => setFailoverModal(false)} style={{ padding: '9px 16px', borderRadius: '6px', border: '1px solid #334155', background: '#1e293b', color: '#f8fafc' }}>Cancel</button>
                <button type="submit" style={{ padding: '9px 16px', borderRadius: '6px', border: 'none', background: '#dc2626', color: '#fff', fontWeight: 700 }}>Confirm Failover</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
