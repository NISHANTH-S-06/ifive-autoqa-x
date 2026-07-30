import React, { useEffect, useState } from 'react';
import { fetchForecastMetrics, generateForecasts } from '../services/phase14Service';

const card = { background: '#1e293b', borderRadius: '12px', border: '1px solid #334155', padding: '20px' };
const METRIC_COLORS: Record<string, string> = { BUG_DENSITY: '#ef4444', TECH_DEBT: '#f97316', VELOCITY: '#10b981', AUTOMATION_GROWTH: '#38bdf8', EXECUTION_COST: '#fb923c', CLOUD_USAGE: '#a78bfa', FLAKY_TESTS: '#f59e0b' };

export const ForecastCenterPage: React.FC = () => {
  const [metrics, setMetrics] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    try {
      let data: any = await fetchForecastMetrics();
      if (data.length === 0) data = await generateForecasts();
      setMetrics(data);
    } catch (e) { console.error(e); } finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const handleReForecast = async () => {
    setLoading(true);
    try {
      const data: any = await generateForecasts(30);
      setMetrics(data);
    } catch (e) { console.error(e); } finally { setLoading(false); }
  };

  return (
    <div style={{ padding: '24px', maxWidth: '1600px', margin: '0 auto', color: '#f8fafc' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '28px' }}>
        <div>
          <h1 style={{ fontSize: '28px', fontWeight: 900, margin: 0, background: 'linear-gradient(90deg, #f59e0b, #fbbf24)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            🔮 AI Forecast Center
          </h1>
          <p style={{ margin: '4px 0 0', color: '#64748b', fontSize: '14px' }}>Predictive forecasting — Bug Density · Technical Debt · Velocity · Automation Growth · Execution Cost</p>
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button onClick={handleReForecast} style={{ padding: '10px 18px', borderRadius: '8px', border: 'none', background: 'linear-gradient(135deg, #f59e0b, #d97706)', color: '#fff', fontWeight: 700, cursor: 'pointer' }}>
            ⚡ Re-Run AI Forecast
          </button>
          <button onClick={load} style={{ padding: '10px 16px', borderRadius: '8px', border: '1px solid #334155', background: '#1e293b', color: '#94a3b8', cursor: 'pointer' }}>↻</button>
        </div>
      </div>

      {/* Metric Cards Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))', gap: '20px' }}>
        {metrics.map((m: any) => {
          const color = METRIC_COLORS[m.metric_type] || '#38bdf8';
          const trend = m.trend?.values || [];
          return (
            <div key={m.id} style={{ ...card, borderTop: `4px solid ${color}` }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
                <div>
                  <div style={{ fontSize: '11px', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.04em' }}>{m.metric_type.replace(/_/g, ' ')}</div>
                  <div style={{ fontSize: '28px', fontWeight: 900, color, marginTop: '4px' }}>{m.forecasted_value} <span style={{ fontSize: '12px', color: '#94a3b8', fontWeight: 400 }}>{m.trend?.unit}</span></div>
                </div>
                <div style={{ textAlign: 'right', fontSize: '11px', color: '#64748b' }}>
                  Horizon: <span style={{ color: '#fff', fontWeight: 700 }}>{m.horizon_days}d</span>
                </div>
              </div>

              {/* Confidence Interval */}
              <div style={{ background: '#0f172a', borderRadius: '6px', padding: '8px 12px', marginBottom: '16px', fontSize: '12px', display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: '#64748b' }}>95% Confidence Interval:</span>
                <span style={{ color: '#94a3b8', fontWeight: 600 }}>{m.confidence_interval_low} — {m.confidence_interval_high}</span>
              </div>

              {/* Mini Sparkline Chart */}
              {trend.length > 0 && (
                <div>
                  <div style={{ fontSize: '11px', color: '#64748b', marginBottom: '8px' }}>Historical Trend & Forecast</div>
                  <div style={{ display: 'flex', alignItems: 'flex-end', gap: '8px', height: '60px' }}>
                    {trend.map((val: number, idx: number) => {
                      const maxVal = Math.max(...trend, 1);
                      const pct = (val / maxVal) * 100;
                      return (
                        <div key={idx} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '4px' }}>
                          <span style={{ fontSize: '10px', color }}>{val}</span>
                          <div style={{ width: '100%', height: `${pct * 0.4}px`, background: color, borderRadius: '3px', opacity: idx === trend.length - 1 ? 1 : 0.6 }} />
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
