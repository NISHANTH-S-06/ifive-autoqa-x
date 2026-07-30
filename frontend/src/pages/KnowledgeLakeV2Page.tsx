import React, { useEffect, useState } from 'react';
import { searchKnowledgeLakeV2, seedKnowledgeLakeV2 } from '../services/phase16Service';

const card = { background: '#1e293b', borderRadius: '12px', border: '1px solid #334155', padding: '20px' };
const badge = (color: string) => ({ padding: '3px 10px', borderRadius: '20px', fontSize: '11px', fontWeight: 700 as const, background: `${color}22`, color, border: `1px solid ${color}44` });

export const KnowledgeLakeV2Page: React.FC = () => {
  const [docs, setDocs] = useState<any[]>([]);
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    try {
      let res: any = await searchKnowledgeLakeV2(query);
      if (!res || res.length === 0) res = await seedKnowledgeLakeV2();
      setDocs(res);
    } catch (e) { console.error(e); } finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  return (
    <div style={{ padding: '24px', maxWidth: '1600px', margin: '0 auto', color: '#f8fafc' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '28px' }}>
        <div>
          <h1 style={{ fontSize: '28px', fontWeight: 900, margin: 0, background: 'linear-gradient(90deg, #38bdf8, #818cf8)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            🧠 Software Knowledge Lake V2
          </h1>
          <p style={{ margin: '4px 0 0', color: '#64748b', fontSize: '14px' }}>Multi-Source Ingestion · Vector Search · Hybrid Tagging · Automatic Graph Generation</p>
        </div>
        <button onClick={load} style={{ padding: '10px 16px', borderRadius: '8px', border: '1px solid #334155', background: '#1e293b', color: '#94a3b8', cursor: 'pointer' }}>↻</button>
      </div>

      <div style={{ marginBottom: '20px', display: 'flex', gap: '12px' }}>
        <input
          value={query}
          onChange={e => setQuery(e.target.value)}
          placeholder="Search Knowledge Lake (e.g. multi-currency, OpenAPI, Playwright)..."
          style={{ flex: 1, padding: '12px 16px', borderRadius: '8px', border: '1px solid #334155', background: '#0f172a', color: '#fff', fontSize: '14px' }}
        />
        <button onClick={load} style={{ padding: '12px 24px', borderRadius: '8px', border: 'none', background: 'linear-gradient(135deg, #38bdf8, #0284c7)', color: '#fff', fontWeight: 700, cursor: 'pointer' }}>
          🔍 Vector Search
        </button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(360px, 1fr))', gap: '20px' }}>
        {docs.map((d: any) => (
          <div key={d.id} style={card}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
              <span style={badge('#38bdf8')}>{d.source_type}</span>
              <span style={{ fontSize: '11px', color: '#64748b' }}>Vector ID #{d.id}</span>
            </div>
            <h3 style={{ margin: '0 0 8px', fontSize: '16px', fontWeight: 700, color: '#f8fafc' }}>{d.title}</h3>
            <p style={{ fontSize: '13px', color: '#94a3b8', lineHeight: '1.5', margin: '0 0 14px' }}>{d.content_text}</p>
            <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
              {(d.hybrid_search_tags || []).map((t: string) => (
                <span key={t} style={{ fontSize: '10px', background: '#0f172a', color: '#818cf8', padding: '2px 8px', borderRadius: '4px', border: '1px solid #818cf833' }}>#{t}</span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
