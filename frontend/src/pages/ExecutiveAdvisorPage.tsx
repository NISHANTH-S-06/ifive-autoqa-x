import React, { useEffect, useState } from 'react';
import { askExecutiveAdvisor, fetchExecutiveInsights } from '../services/phase14Service';

const card = { background: '#1e293b', borderRadius: '12px', border: '1px solid #334155', padding: '20px' };

const PRESETS = [
  'Can I release today?',
  "What are today's risks?",
  'Which developer introduces most defects?',
  'Predict next sprint quality',
  'Which modules are unstable?',
  'What should we automate next?',
  'Summarize all releases',
];

export const ExecutiveAdvisorPage: React.FC = () => {
  const [insights, setInsights] = useState<any[]>([]);
  const [queryInput, setQueryInput] = useState('');
  const [asking, setAsking] = useState(false);

  const load = async () => {
    try {
      const data: any = await fetchExecutiveInsights();
      setInsights(data);
    } catch (e) { console.error(e); }
  };

  useEffect(() => { load(); }, []);

  const handleAsk = async (query: string) => {
    if (!query) return;
    setAsking(true);
    try {
      await askExecutiveAdvisor(query);
      setQueryInput('');
      load();
    } catch (err: any) { alert(err.message); } finally { setAsking(false); }
  };

  return (
    <div style={{ padding: '24px', maxWidth: '1400px', margin: '0 auto', color: '#f8fafc' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '28px' }}>
        <div>
          <h1 style={{ fontSize: '28px', fontWeight: 900, margin: 0, background: 'linear-gradient(90deg, #38bdf8, #a78bfa)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            👔 AI Executive Advisor
          </h1>
          <p style={{ margin: '4px 0 0', color: '#64748b', fontSize: '14px' }}>Natural language strategic release & quality assistant for CTOs, PMs, and Executives</p>
        </div>
        <button onClick={load} style={{ padding: '10px 16px', borderRadius: '8px', border: '1px solid #334155', background: '#1e293b', color: '#94a3b8', cursor: 'pointer' }}>↻</button>
      </div>

      {/* Query Bar */}
      <div style={{ ...card, marginBottom: '24px', background: 'linear-gradient(135deg, #1e293b, #0f172a)', border: '1px solid #38bdf844' }}>
        <form onSubmit={(e) => { e.preventDefault(); handleAsk(queryInput); }} style={{ display: 'flex', gap: '12px', marginBottom: '14px' }}>
          <input
            value={queryInput}
            onChange={e => setQueryInput(e.target.value)}
            placeholder="Ask the Executive Advisor anything (e.g. Can I release today?)..."
            style={{ flex: 1, padding: '12px 16px', borderRadius: '8px', border: '1px solid #334155', background: '#0f172a', color: '#fff', fontSize: '14px' }}
          />
          <button type="submit" disabled={asking} style={{ padding: '12px 24px', borderRadius: '8px', border: 'none', background: 'linear-gradient(135deg, #38bdf8, #0284c7)', color: '#fff', fontWeight: 700, cursor: 'pointer' }}>
            {asking ? 'Thinking...' : '💬 Ask Advisor'}
          </button>
        </form>

        {/* Quick Presets */}
        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
          {PRESETS.map(p => (
            <button key={p} onClick={() => handleAsk(p)} style={{ padding: '6px 12px', borderRadius: '16px', border: '1px solid #334155', background: '#0f172a', color: '#94a3b8', fontSize: '12px', cursor: 'pointer' }}>
              💡 {p}
            </button>
          ))}
        </div>
      </div>

      {/* Insights Stream */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {insights.map(i => (
          <div key={i.id} style={{ ...card, borderLeft: '4px solid #a78bfa' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
              <div style={{ fontWeight: 700, fontSize: '15px', color: '#38bdf8' }}>❓ "{i.query_text}"</div>
              <div style={{ fontSize: '12px', color: '#a78bfa', fontWeight: 700 }}>{(i.confidence_score * 100).toFixed(0)}% Confidence</div>
            </div>

            <div style={{ background: '#0f172a', borderRadius: '8px', padding: '14px', marginBottom: '12px', border: '1px solid #a78bfa33' }}>
              <div style={{ fontSize: '11px', color: '#a78bfa', fontWeight: 700, textTransform: 'uppercase', marginBottom: '4px' }}>AI Advisor Advice</div>
              <div style={{ fontSize: '14px', fontWeight: 600, color: '#fff', lineHeight: '1.5' }}>{i.advice_summary}</div>
            </div>

            {i.details && Object.keys(i.details).length > 0 && (
              <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
                {Object.entries(i.details).map(([k, v]) => (
                  <div key={k} style={{ background: '#0f172a', padding: '6px 12px', borderRadius: '6px', fontSize: '12px' }}>
                    <span style={{ color: '#64748b' }}>{k}: </span>
                    <span style={{ color: '#10b981', fontWeight: 700 }}>{String(v)}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
