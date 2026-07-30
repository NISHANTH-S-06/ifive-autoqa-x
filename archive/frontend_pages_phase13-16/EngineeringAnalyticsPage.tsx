import React, { useEffect, useState } from 'react';
import { computeEngineeringMetrics, fetchEngineeringMetrics } from '../services/phase15Service';

const card = { background: '#1e293b', borderRadius: '12px', border: '1px solid #334155', padding: '20px' };
const METRIC_COLORS: Record<string, string> = {
  CYCLE_TIME_HOURS: '#38bdf8', LEAD_TIME_HOURS: '#a78bfa', MTTR_MINUTES: '#ef4444',
  BUG_LEAKAGE_PCT: '#f59e0b', DEV_PRODUCTIVITY_SCORE: '#10b981', QA_PRODUCTIVITY_SCORE: '#34d399',
  AUTOMATION_GROWTH_PCT: '#f472b6',
};

export const EngineeringAnalyticsPage: React.FC = () => {
  const [metrics, setMetrics] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    try {
      let data: any = await fetchEngineeringMetrics();
      if (!data || data.length === 0) data = await computeEngineeringMetrics();
      setMetrics(data);
    } catch (e) { console.error(e); } finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  return (
    <div style={{ padding: '24px', maxWidth: '1600px', margin: '0 auto', color: '#f8fafc' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '28px' }}>
        <div>
          <h1 style={{ fontSize: '28px', fontWeight: 900, margin: 0, background: 'linear-gradient(90deg, #38bdf8, #818cf8)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            📈 Enterprise Engineering Analytics
          </h1>
          <p style={{ margin: '4px 0 0', color: '#64748b', fontSize: '14px' }}>Cycle Time · Lead Time · MTTR · Bug Leakage · Automation Growth · Developer & QA Productivity</p>
        </div>
        <button onClick={load} style={{ padding: '10px 16px', borderRadius: '8px', border: '1px solid #334155', background: '#1e293b', color: '#94a3b8', cursor: 'pointer' }}>↻</button>
      </div>

      {/* Metrics Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))', gap: '20px' }}>
        {metrics.map((m: any) => {
          const color = METRIC_COLORS[m.metric_name] || '#38bdf8';
          const trendVals = m.trend?.values || [];

          return (
            <div key={m.id} style={{ ...card, borderTop: `4px solid ${color}` }}>
              <div style={{ fontSize: '11px', color: '#64748b', textTransform: 'uppercase', fontWeight: 800 }}>{m.metric_name.replace(/_/g, ' ')}</div>
              <div style={{ fontSize: '32px', fontWeight: 900, color, margin: '6px 0 12px' }}>
                {m.metric_value} <span style={{ fontSize: '13px', color: '#94a3b8', fontWeight: 400 }}>{m.unit}</span>
              </div>

              {/* Sparkline Visual */}
              {trendVals.length > 0 && (
                <div>
                  <div style={{ fontSize: '11px', color: '#64748b', marginBottom: '8px' }}>4-Week Trend</div>
                  <div style={{ display: 'flex', alignItems: 'flex-end', gap: '10px', height: '50px' }}>
                    {trendVals.map((val: number, idx: number) => {
                      const maxVal = Math.max(...trendVals, 1);
                      const pct = (val / maxVal) * 100;
                      return (
                        <div key={idx} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '4px' }}>
                          <span style={{ fontSize: '10px', color }}>{val}</span>
                          <div style={{ width: '100%', height: `${pct * 0.35}px`, background: color, borderRadius: '3px', opacity: idx === trendVals.length - 1 ? 1 : 0.5 }} />
                          <span style={{ fontSize: '9px', color: '#64748b' }}>{m.trend?.weeks?.[idx]}</span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
