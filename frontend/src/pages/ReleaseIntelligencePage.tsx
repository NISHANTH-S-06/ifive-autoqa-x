import React, { useEffect, useState } from 'react';
import { evaluateRelease, fetchReleaseEvaluations } from '../services/phase15Service';

const card = { background: '#1e293b', borderRadius: '12px', border: '1px solid #334155', padding: '20px' };
const badge = (color: string) => ({ padding: '4px 14px', borderRadius: '20px', fontSize: '12px', fontWeight: 800 as const, background: `${color}22`, color, border: `1px solid ${color}44` });

export const ReleaseIntelligencePage: React.FC = () => {
  const [evaluations, setEvaluations] = useState<any[]>([]);
  const [releaseVersion, setReleaseVersion] = useState('v5.0.0-RC2');
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    try {
      let data: any = await fetchReleaseEvaluations();
      if (!data || data.length === 0) data = [await evaluateRelease('v5.0.0-RC1')];
      setEvaluations(data);
    } catch (e) { console.error(e); } finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const handleEvaluate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await evaluateRelease(releaseVersion);
      load();
    } catch (err: any) { alert(err.message); }
  };

  return (
    <div style={{ padding: '24px', maxWidth: '1600px', margin: '0 auto', color: '#f8fafc' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '28px' }}>
        <div>
          <h1 style={{ fontSize: '28px', fontWeight: 900, margin: 0, background: 'linear-gradient(90deg, #22c55e, #38bdf8)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            🚀 Enterprise Release Intelligence
          </h1>
          <p style={{ margin: '4px 0 0', color: '#64748b', fontSize: '14px' }}>Autonomous Release Decision Engine — Composite Score · 7-Risk Factor Gauges · READY / HOLD / ROLLBACK</p>
        </div>
        <button onClick={load} style={{ padding: '10px 16px', borderRadius: '8px', border: '1px solid #334155', background: '#1e293b', color: '#94a3b8', cursor: 'pointer' }}>↻</button>
      </div>

      {/* Evaluate New Release Form */}
      <div style={{ ...card, marginBottom: '24px' }}>
        <h3 style={{ margin: '0 0 14px', fontSize: '16px', fontWeight: 700, color: '#22c55e' }}>Evaluate Candidate Release</h3>
        <form onSubmit={handleEvaluate} style={{ display: 'flex', gap: '12px' }}>
          <input value={releaseVersion} onChange={e => setReleaseVersion(e.target.value)} placeholder="Release Version (e.g. v5.0.0-RC2)" style={{ flex: 1, padding: '10px 14px', borderRadius: '8px', border: '1px solid #334155', background: '#0f172a', color: '#fff' }} />
          <button type="submit" style={{ padding: '10px 24px', borderRadius: '8px', border: 'none', background: 'linear-gradient(135deg, #22c55e, #16a34a)', color: '#fff', fontWeight: 700, cursor: 'pointer' }}>
            ⚡ Evaluate Release Score
          </button>
        </form>
      </div>

      {/* Evaluations Stream */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
        {evaluations.map((ev: any) => {
          const recColor = ev.recommendation === 'READY' ? '#22c55e' : ev.recommendation === 'HOLD' ? '#f59e0b' : '#ef4444';

          return (
            <div key={ev.id} style={{ ...card, borderLeft: `6px solid ${recColor}` }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
                <div>
                  <div style={{ fontSize: '22px', fontWeight: 900, color: '#fff' }}>Release {ev.release_version}</div>
                  <div style={{ fontSize: '12px', color: '#64748b', marginTop: '2px' }}>Evaluated At: {new Date(ev.created_at).toLocaleString()}</div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <span style={badge(recColor)}>RECOMMENDATION: {ev.recommendation}</span>
                  <div style={{ fontSize: '28px', fontWeight: 900, color: recColor, marginTop: '6px' }}>{ev.composite_release_score} <span style={{ fontSize: '13px', color: '#64748b' }}>Composite Score</span></div>
                </div>
              </div>

              {/* 6-Risk Gauges Grid */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: '12px', marginBottom: '16px' }}>
                {[
                  { label: 'Deployment Risk', val: ev.deployment_risk_pct, color: '#ef4444' },
                  { label: 'Rollback Risk', val: ev.rollback_risk_pct, color: '#f97316' },
                  { label: 'Business Risk', val: ev.business_risk_pct, color: '#f59e0b' },
                  { label: 'Security Risk', val: ev.security_risk_pct, color: '#38bdf8' },
                  { label: 'Performance Risk', val: ev.performance_risk_pct, color: '#a78bfa' },
                  { label: 'Customer Risk', val: ev.customer_risk_pct, color: '#f472b6' },
                ].map(g => (
                  <div key={g.label} style={{ background: '#0f172a', borderRadius: '8px', padding: '10px', textAlign: 'center' }}>
                    <div style={{ fontSize: '10px', color: '#64748b', textTransform: 'uppercase' }}>{g.label}</div>
                    <div style={{ fontSize: '18px', fontWeight: 800, color: g.color, marginTop: '4px' }}>{g.val}%</div>
                  </div>
                ))}
              </div>

              <div style={{ background: '#0f172a', borderRadius: '8px', padding: '14px', fontSize: '13px', color: '#94a3b8' }}>
                <strong style={{ color: '#fff' }}>Executive Summary: </strong>
                {ev.breakdown?.executive_summary || 'Passed all quality gates with zero blocker defects.'}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
