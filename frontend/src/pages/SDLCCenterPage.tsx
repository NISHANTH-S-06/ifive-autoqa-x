import React, { useEffect, useState } from 'react';
import { fetchExecutiveDecisions, fetchSDLCStatus } from '../services/phase16Service';

const card = { background: '#1e293b', borderRadius: '12px', border: '1px solid #334155', padding: '20px' };
const badge = (color: string) => ({ padding: '3px 10px', borderRadius: '20px', fontSize: '11px', fontWeight: 700 as const, background: `${color}22`, color, border: `1px solid ${color}44` });

export const SDLCCenterPage: React.FC = () => {
  const [stages, setStages] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    try {
      const data: any = await fetchSDLCStatus();
      setStages(data);
    } catch (e) { console.error(e); } finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  return (
    <div style={{ padding: '24px', maxWidth: '1600px', margin: '0 auto', color: '#f8fafc' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '28px' }}>
        <div>
          <h1 style={{ fontSize: '28px', fontWeight: 900, margin: 0, background: 'linear-gradient(90deg, #10b981, #38bdf8)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            🔄 Autonomous SDLC Orchestrator
          </h1>
          <p style={{ margin: '4px 0 0', color: '#64748b', fontSize: '14px' }}>Planning → Development → Testing → Release → Production → Monitoring → Learning</p>
        </div>
        <button onClick={load} style={{ padding: '10px 16px', borderRadius: '8px', border: '1px solid #334155', background: '#1e293b', color: '#94a3b8', cursor: 'pointer' }}>↻</button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '20px' }}>
        {stages.map((s: any) => {
          const color = s.status === 'COMPLETED' ? '#10b981' : s.status === 'IN_PROGRESS' ? '#38bdf8' : '#64748b';

          return (
            <div key={s.id} style={{ ...card, borderTop: `4px solid ${color}` }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
                <h3 style={{ margin: 0, fontSize: '16px', fontWeight: 700 }}>{s.stage_name}</h3>
                <span style={badge(color)}>{s.status}</span>
              </div>
              <div style={{ background: '#0f172a', padding: '12px', borderRadius: '8px', fontSize: '12px' }}>
                <div style={{ color: '#64748b', fontWeight: 800, marginBottom: '6px' }}>Scheduled Actions</div>
                {(s.scheduled_actions || []).map((act: string, idx: number) => (
                  <div key={idx} style={{ color: '#cbd5e1', marginBottom: '4px' }}>• {act}</div>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export const ExecutiveDecisionCenterPage: React.FC = () => {
  const [decisions, setDecisions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    try {
      const data: any = await fetchExecutiveDecisions();
      setDecisions(data);
    } catch (e) { console.error(e); } finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  return (
    <div style={{ padding: '24px', maxWidth: '1600px', margin: '0 auto', color: '#f8fafc' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '28px' }}>
        <div>
          <h1 style={{ fontSize: '28px', fontWeight: 900, margin: 0, background: 'linear-gradient(90deg, #a78bfa, #f472b6)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            🧠 AI Executive Decision Engine
          </h1>
          <p style={{ margin: '4px 0 0', color: '#64748b', fontSize: '14px' }}>Autonomous Recommendations · Delay Release · Rollback · Deploy Gradually · Detailed Reasoning</p>
        </div>
        <button onClick={load} style={{ padding: '10px 16px', borderRadius: '8px', border: '1px solid #334155', background: '#1e293b', color: '#94a3b8', cursor: 'pointer' }}>↻</button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(400px, 1fr))', gap: '20px' }}>
        {decisions.map((d: any) => (
          <div key={d.id} style={{ ...card, borderLeft: '4px solid #a78bfa' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
              <span style={badge('#a78bfa')}>{d.decision_type}</span>
              <span style={{ fontSize: '12px', color: '#10b981', fontWeight: 800 }}>Confidence: {(d.confidence_score * 100).toFixed(0)}%</span>
            </div>
            <h3 style={{ margin: '0 0 10px', fontSize: '16px', fontWeight: 700 }}>{d.recommendation_summary}</h3>
            <div style={{ background: '#0f172a', padding: '12px', borderRadius: '8px', fontSize: '13px', color: '#cbd5e1', lineHeight: '1.5' }}>
              <strong style={{ color: '#a78bfa' }}>Reasoning:</strong> {d.reasoning_explanation}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
