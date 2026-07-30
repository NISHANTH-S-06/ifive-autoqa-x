import React, { useEffect, useState } from 'react';
import { fetchCodeReviewHistory, reviewCodeFile } from '../services/phase15Service';

const card = { background: '#1e293b', borderRadius: '12px', border: '1px solid #334155', padding: '20px' };
const badge = (color: string) => ({ padding: '3px 10px', borderRadius: '20px', fontSize: '11px', fontWeight: 700 as const, background: `${color}22`, color, border: `1px solid ${color}44` });

export const CodeReviewCenterPage: React.FC = () => {
  const [reviews, setReviews] = useState<any[]>([]);
  const [filePath, setFilePath] = useState('backend/app/services/checkout.py');
  const [language, setLanguage] = useState('PYTHON');
  const [codeSnippet, setCodeSnippet] = useState('def checkout(): query = "SELECT * FROM orders"; eval(user_input)');
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    try {
      const data: any = await fetchCodeReviewHistory();
      setReviews(data);
    } catch (e) { console.error(e); } finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const handleReview = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await reviewCodeFile(filePath, language, codeSnippet);
      load();
    } catch (err: any) { alert(err.message); }
  };

  return (
    <div style={{ padding: '24px', maxWidth: '1600px', margin: '0 auto', color: '#f8fafc' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '28px' }}>
        <div>
          <h1 style={{ fontSize: '28px', fontWeight: 900, margin: 0, background: 'linear-gradient(90deg, #818cf8, #a78bfa)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            🔍 Enterprise AI Code Reviewer
          </h1>
          <p style={{ margin: '4px 0 0', color: '#64748b', fontSize: '14px' }}>Multi-Language Review — Python · TypeScript · React · SQL · Playwright · FastAPI</p>
        </div>
        <button onClick={load} style={{ padding: '10px 16px', borderRadius: '8px', border: '1px solid #334155', background: '#1e293b', color: '#94a3b8', cursor: 'pointer' }}>↻</button>
      </div>

      {/* Code Review Form */}
      <div style={{ ...card, marginBottom: '24px' }}>
        <h3 style={{ margin: '0 0 16px', fontSize: '16px', fontWeight: 700, color: '#818cf8' }}>Trigger AI File Review</h3>
        <form onSubmit={handleReview} style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '12px' }}>
            <input value={filePath} onChange={e => setFilePath(e.target.value)} placeholder="File Path" style={{ padding: '10px 14px', borderRadius: '8px', border: '1px solid #334155', background: '#0f172a', color: '#fff' }} />
            <select value={language} onChange={e => setLanguage(e.target.value)} style={{ padding: '10px 14px', borderRadius: '8px', border: '1px solid #334155', background: '#0f172a', color: '#fff' }}>
              <option value="PYTHON">Python</option>
              <option value="TYPESCRIPT">TypeScript</option>
              <option value="REACT">React</option>
              <option value="SQL">SQL</option>
              <option value="PLAYWRIGHT">Playwright</option>
              <option value="FASTAPI">FastAPI</option>
            </select>
          </div>
          <textarea value={codeSnippet} onChange={e => setCodeSnippet(e.target.value)} rows={3} placeholder="Paste Code Snippet to review..." style={{ padding: '10px 14px', borderRadius: '8px', border: '1px solid #334155', background: '#0f172a', color: '#fff', fontFamily: 'monospace' }} />
          <button type="submit" style={{ alignSelf: 'flex-start', padding: '10px 24px', borderRadius: '8px', border: 'none', background: 'linear-gradient(135deg, #818cf8, #6366f1)', color: '#fff', fontWeight: 700, cursor: 'pointer' }}>
            🤖 AI Code Review
          </button>
        </form>
      </div>

      {/* Review History */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {reviews.map((r: any) => (
          <div key={r.id} style={{ ...card, borderLeft: '4px solid #818cf8' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
              <div>
                <span style={{ fontWeight: 800, fontSize: '15px', color: '#fff' }}>📄 {r.file_path}</span>
                <span style={{ marginLeft: '10px', ...badge('#818cf8') }}>{r.language}</span>
              </div>
              <div style={{ display: 'flex', gap: '8px', fontSize: '12px' }}>
                <span style={{ color: '#ef4444' }}>🛑 {r.bugs_found_count} Bugs</span>
                <span style={{ color: '#f59e0b' }}>🔒 {r.security_issues_count} Security</span>
                <span style={{ color: '#38bdf8' }}>⚠️ {r.code_smells_count} Smells</span>
                <span style={{ color: '#a78bfa' }}>🧪 {r.test_gaps_count} Gaps</span>
              </div>
            </div>

            {/* Comments List */}
            <div style={{ background: '#0f172a', borderRadius: '8px', padding: '14px' }}>
              <div style={{ fontSize: '11px', color: '#64748b', textTransform: 'uppercase', marginBottom: '8px' }}>AI Inline Suggestions ({r.comments?.length})</div>
              {r.comments?.map((c: any, idx: number) => (
                <div key={idx} style={{ borderBottom: '1px solid #1e293b', padding: '8px 0', fontSize: '13px', display: 'flex', gap: '12px' }}>
                  <span style={{ color: '#818cf8', fontFamily: 'monospace', fontWeight: 700 }}>Line {c.line}:</span>
                  <span style={{ color: c.type === 'SECURITY' ? '#ef4444' : '#94a3b8' }}>[{c.type}] {c.message}</span>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
