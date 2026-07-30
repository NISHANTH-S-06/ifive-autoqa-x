import React, { useEffect, useState } from 'react';
import { fetchCodeQualityViolations, scanCodeSnippet } from '../services/phase16Service';

const card = { background: '#1e293b', borderRadius: '12px', border: '1px solid #334155', padding: '20px' };
const badge = (color: string) => ({ padding: '3px 10px', borderRadius: '20px', fontSize: '11px', fontWeight: 700 as const, background: `${color}22`, color, border: `1px solid ${color}44` });

export const CodeQualityGovernorPage: React.FC = () => {
  const [violations, setViolations] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    try {
      const data: any = await fetchCodeQualityViolations();
      setViolations(data);
    } catch (e) { console.error(e); } finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  return (
    <div style={{ padding: '24px', maxWidth: '1600px', margin: '0 auto', color: '#f8fafc' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '28px' }}>
        <div>
          <h1 style={{ fontSize: '28px', fontWeight: 900, margin: 0, background: 'linear-gradient(90deg, #ef4444, #f87171)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            🛡️ AI Code Quality Governor
          </h1>
          <p style={{ margin: '4px 0 0', color: '#64748b', fontSize: '14px' }}>Multi-Language Scanner · Python · TypeScript · React · Java · .NET · Go · SQL</p>
        </div>
        <button onClick={load} style={{ padding: '10px 16px', borderRadius: '8px', border: '1px solid #334155', background: '#1e293b', color: '#94a3b8', cursor: 'pointer' }}>↻</button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(360px, 1fr))', gap: '20px' }}>
        {violations.map((v: any) => (
          <div key={v.id} style={{ ...card, borderLeft: `4px solid ${v.severity === 'HIGH' ? '#ef4444' : '#f59e0b'}` }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
              <span style={badge('#ef4444')}>{v.language}</span>
              <span style={badge('#f59e0b')}>{v.category}</span>
            </div>
            <div style={{ fontSize: '13px', fontWeight: 700, color: '#f8fafc', marginBottom: '4px' }}>{v.file_path}:L{v.line_number}</div>
            <p style={{ fontSize: '13px', color: '#94a3b8', marginBottom: '12px' }}>{v.message}</p>
            <div style={{ background: '#0f172a', padding: '10px', borderRadius: '6px', fontSize: '12px', color: '#10b981' }}>
              <strong>Fix Recommendation:</strong> {v.recommendation}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
