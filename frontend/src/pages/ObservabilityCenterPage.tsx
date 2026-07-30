import React, { useEffect, useState } from 'react';
import { fetchObservabilityMetrics } from '../services/phase16Service';

const card = { background: '#1e293b', borderRadius: '12px', border: '1px solid #334155', padding: '20px' };
const badge = (color: string) => ({ padding: '3px 10px', borderRadius: '20px', fontSize: '11px', fontWeight: 700 as const, background: `${color}22`, color, border: `1px solid ${color}44` });

export const ObservabilityCenterPage: React.FC = () => {
  const [metrics, setMetrics] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    try {
      const data: any = await fetchObservabilityMetrics();
      setMetrics(data);
    } catch (e) { console.error(e); } finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  return (
    <div style={{ padding: '24px', maxWidth: '1600px', margin: '0 auto', color: '#f8fafc' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '28px' }}>
        <div>
          <h1 style={{ fontSize: '28px', fontWeight: 900, margin: 0, background: 'linear-gradient(90deg, #38bdf8, #818cf8)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            📡 Production Observability AI
          </h1>
          <p style={{ margin: '4px 0 0', color: '#64748b', fontSize: '14px' }}>Metrics · Logs · Traces · APM · Incident Forecaster & Regression Predictor</p>
        </div>
        <button onClick={load} style={{ padding: '10px 16px', borderRadius: '8px', border: '1px solid #334155', background: '#1e293b', color: '#94a3b8', cursor: 'pointer' }}>↻</button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(360px, 1fr))', gap: '20px' }}>
        {metrics.map((m: any) => {
          const isHighRisk = m.predicted_incident_risk > 0.5;
          const color = isHighRisk ? '#ef4444' : '#10b981';

          return (
            <div key={m.id} style={{ ...card, borderLeft: `4px solid ${color}` }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
                <h3 style={{ margin: 0, fontSize: '16px', fontWeight: 700 }}>{m.service_name}</h3>
                <span style={badge(color)}>{isHighRisk ? 'RISK ELEVATED' : 'HEALTHY'}</span>
              </div>

              <div style={{ display: 'flex', gap: '16px', marginBottom: '12px' }}>
                <div>
                  <div style={{ fontSize: '11px', color: '#64748b' }}>Error Rate</div>
                  <div style={{ fontSize: '18px', fontWeight: 800, color: m.error_rate_pct > 1 ? '#ef4444' : '#10b981' }}>{m.error_rate_pct}%</div>
                </div>
                <div>
                  <div style={{ fontSize: '11px', color: '#64748b' }}>P99 Latency</div>
                  <div style={{ fontSize: '18px', fontWeight: 800, color: '#38bdf8' }}>{m.latency_p99_ms} ms</div>
                </div>
                <div>
                  <div style={{ fontSize: '11px', color: '#64748b' }}>Incident Risk</div>
                  <div style={{ fontSize: '18px', fontWeight: 800, color }}>{(m.predicted_incident_risk * 100).toFixed(0)}%</div>
                </div>
              </div>

              <p style={{ fontSize: '12px', color: '#94a3b8', background: '#0f172a', padding: '10px', borderRadius: '6px', margin: 0 }}>
                💡 {m.prediction_summary}
              </p>
            </div>
          );
        })}
      </div>
    </div>
  );
};
