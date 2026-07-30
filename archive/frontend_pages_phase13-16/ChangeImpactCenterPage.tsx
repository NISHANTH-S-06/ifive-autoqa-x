import React, { useEffect, useState } from 'react';
import { analyzeCommitImpact, fetchChangeImpactHistory } from '../services/phase15Service';

const card = { background: '#1e293b', borderRadius: '12px', border: '1px solid #334155', padding: '20px' };

export const ChangeImpactCenterPage: React.FC = () => {
  const [records, setRecords] = useState<any[]>([]);
  const [commitHash, setCommitHash] = useState('c9f8a12b');
  const [author, setAuthor] = useState('Senior Dev');
  const [filesInput, setFilesInput] = useState('backend/app/services/checkout.py, backend/app/api/checkout.py');
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    try {
      const data: any = await fetchChangeImpactHistory();
      setRecords(data);
    } catch (e) { console.error(e); } finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    const files = filesInput.split(',').map(f => f.trim()).filter(Boolean);
    try {
      await analyzeCommitImpact(commitHash, author, files);
      load();
    } catch (err: any) { alert(err.message); }
  };

  return (
    <div style={{ padding: '24px', maxWidth: '1600px', margin: '0 auto', color: '#f8fafc' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '28px' }}>
        <div>
          <h1 style={{ fontSize: '28px', fontWeight: 900, margin: 0, background: 'linear-gradient(90deg, #f97316, #ef4444)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            💥 AI Change Impact Intelligence
          </h1>
          <p style={{ margin: '4px 0 0', color: '#64748b', fontSize: '14px' }}>Commit change impact detection · Affected regression suites · Risk score & execution cost predictor</p>
        </div>
        <button onClick={load} style={{ padding: '10px 16px', borderRadius: '8px', border: '1px solid #334155', background: '#1e293b', color: '#94a3b8', cursor: 'pointer' }}>↻</button>
      </div>

      {/* Commit Input Card */}
      <div style={{ ...card, marginBottom: '24px' }}>
        <h3 style={{ margin: '0 0 16px', fontSize: '16px', fontWeight: 700, color: '#f97316' }}>Analyze New Git Commit</h3>
        <form onSubmit={handleAnalyze} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 2fr auto', gap: '12px' }}>
          <input value={commitHash} onChange={e => setCommitHash(e.target.value)} placeholder="Commit Hash" style={{ padding: '10px 14px', borderRadius: '8px', border: '1px solid #334155', background: '#0f172a', color: '#fff' }} />
          <input value={author} onChange={e => setAuthor(e.target.value)} placeholder="Author" style={{ padding: '10px 14px', borderRadius: '8px', border: '1px solid #334155', background: '#0f172a', color: '#fff' }} />
          <input value={filesInput} onChange={e => setFilesInput(e.target.value)} placeholder="Comma-separated files" style={{ padding: '10px 14px', borderRadius: '8px', border: '1px solid #334155', background: '#0f172a', color: '#fff' }} />
          <button type="submit" style={{ padding: '10px 20px', borderRadius: '8px', border: 'none', background: 'linear-gradient(135deg, #f97316, #ea580c)', color: '#fff', fontWeight: 700, cursor: 'pointer' }}>
            ⚡ Predict Impact
          </button>
        </form>
      </div>

      {/* Commit History */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(380px, 1fr))', gap: '20px' }}>
        {records.map((r: any) => (
          <div key={r.id} style={{ ...card, borderLeft: `4px solid ${r.risk_score > 50 ? '#ef4444' : '#10b981'}` }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
              <div>
                <span style={{ fontFamily: 'monospace', fontWeight: 800, color: '#f97316', fontSize: '14px' }}>#{r.commit_hash}</span>
                <span style={{ fontSize: '12px', color: '#64748b', marginLeft: '8px' }}>by {r.author}</span>
              </div>
              <div style={{ textAlign: 'right' }}>
                <div style={{ fontSize: '18px', fontWeight: 900, color: r.risk_score > 50 ? '#ef4444' : '#10b981' }}>{r.risk_score} <span style={{ fontSize: '11px', color: '#64748b' }}>Risk Score</span></div>
              </div>
            </div>

            <div style={{ background: '#0f172a', borderRadius: '8px', padding: '12px', fontSize: '12px', marginBottom: '12px' }}>
              <div style={{ fontSize: '11px', color: '#64748b', textTransform: 'uppercase', marginBottom: '4px' }}>Impacted Modules ({r.impacted_modules?.length})</div>
              <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                {r.impacted_modules?.map((m: string) => (
                  <span key={m} style={{ background: '#38bdf822', color: '#38bdf8', padding: '2px 8px', borderRadius: '4px', border: '1px solid #38bdf844' }}>{m}</span>
                ))}
              </div>
            </div>

            <div style={{ background: '#0f172a', borderRadius: '8px', padding: '12px', fontSize: '12px' }}>
              <div style={{ fontSize: '11px', color: '#64748b', textTransform: 'uppercase', marginBottom: '4px' }}>Affected Regression Suite ({r.affected_tests?.length})</div>
              {r.affected_tests?.map((t: string) => (
                <div key={t} style={{ color: '#94a3b8', margin: '2px 0' }}>• {t}</div>
              ))}
              <div style={{ marginTop: '8px', color: '#10b981', fontWeight: 700 }}>Est. Execution Cost: ${r.estimated_execution_cost_usd} USD</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
