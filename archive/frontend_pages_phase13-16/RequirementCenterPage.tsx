import React, { useEffect, useState } from 'react';
import { fetchRequirements, seedRequirements } from '../services/phase16Service';

const card = { background: '#1e293b', borderRadius: '12px', border: '1px solid #334155', padding: '20px' };
const badge = (color: string) => ({ padding: '3px 10px', borderRadius: '20px', fontSize: '11px', fontWeight: 700 as const, background: `${color}22`, color, border: `1px solid ${color}44` });

export const RequirementCenterPage: React.FC = () => {
  const [reqs, setReqs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    try {
      let data: any = await fetchRequirements();
      if (!data || data.length === 0) data = await seedRequirements();
      setReqs(data);
    } catch (e) { console.error(e); } finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  return (
    <div style={{ padding: '24px', maxWidth: '1600px', margin: '0 auto', color: '#f8fafc' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '28px' }}>
        <div>
          <h1 style={{ fontSize: '28px', fontWeight: 900, margin: 0, background: 'linear-gradient(90deg, #10b981, #34d399)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            📜 AI Requirement Intelligence
          </h1>
          <p style={{ margin: '4px 0 0', color: '#64748b', fontSize: '14px' }}>Business & Functional Requirements · Ambiguity & Conflict Detection · Acceptance Criteria Generator</p>
        </div>
        <button onClick={load} style={{ padding: '10px 16px', borderRadius: '8px', border: '1px solid #334155', background: '#1e293b', color: '#94a3b8', cursor: 'pointer' }}>↻</button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(400px, 1fr))', gap: '20px' }}>
        {reqs.map((r: any) => (
          <div key={r.id} style={{ ...card, borderLeft: `4px solid ${r.is_ambiguous ? '#f59e0b' : '#10b981'}` }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
              <div>
                <span style={badge('#10b981')}>{r.requirement_code}</span>
                <span style={{ marginLeft: '8px', ...badge('#38bdf8') }}>{r.requirement_type}</span>
              </div>
              <span style={{ fontSize: '12px', color: r.risk_score > 0.7 ? '#ef4444' : '#10b981', fontWeight: 800 }}>Risk: {(r.risk_score * 100).toFixed(0)}%</span>
            </div>

            <h3 style={{ margin: '0 0 6px', fontSize: '16px', fontWeight: 700 }}>{r.title}</h3>
            <p style={{ fontSize: '13px', color: '#94a3b8', marginBottom: '14px' }}>{r.description}</p>

            {/* Acceptance Criteria */}
            <div style={{ background: '#0f172a', borderRadius: '8px', padding: '12px', fontSize: '12px', marginBottom: '12px' }}>
              <div style={{ fontSize: '11px', color: '#64748b', fontWeight: 800, textTransform: 'uppercase', marginBottom: '6px' }}>Acceptance Criteria</div>
              {(r.acceptance_criteria || []).map((ac: string, idx: number) => (
                <div key={idx} style={{ color: '#cbd5e1', marginBottom: '4px' }}>✓ {ac}</div>
              ))}
            </div>

            {r.is_ambiguous && (
              <div style={{ background: '#f59e0b22', border: '1px solid #f59e0b44', color: '#f59e0b', padding: '8px 12px', borderRadius: '6px', fontSize: '12px' }}>
                ⚠️ Ambiguity Warning: {r.analysis_notes}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
