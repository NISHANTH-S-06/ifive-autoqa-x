import React, { useEffect, useState } from 'react';
import { searchKnowledgeLake, seedKnowledgeLake } from '../services/phase15Service';

const card = { background: '#1e293b', borderRadius: '12px', border: '1px solid #334155', padding: '20px' };
const badge = (color: string) => ({ padding: '3px 10px', borderRadius: '20px', fontSize: '11px', fontWeight: 700 as const, background: `${color}22`, color, border: `1px solid ${color}44` });

export const KnowledgeLakePage: React.FC = () => {
  const [items, setItems] = useState<any[]>([]);
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(true);

  const load = async (q: string = '') => {
    setLoading(true);
    try {
      let data: any = await searchKnowledgeLake(q);
      if (!data || data.length === 0) data = await seedKnowledgeLake();
      setItems(data);
    } catch (e) { console.error(e); } finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  return (
    <div style={{ padding: '24px', maxWidth: '1600px', margin: '0 auto', color: '#f8fafc' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '28px' }}>
        <div>
          <h1 style={{ fontSize: '28px', fontWeight: 900, margin: 0, background: 'linear-gradient(90deg, #a78bfa, #f472b6)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            🌊 Enterprise Knowledge Lake
          </h1>
          <p style={{ margin: '4px 0 0', color: '#64748b', fontSize: '14px' }}>Semantic AI Search — Logs · Reports · Screenshots · Videos · Traces · Network · Baselines</p>
        </div>
        <button onClick={() => load('')} style={{ padding: '10px 16px', borderRadius: '8px', border: '1px solid #334155', background: '#1e293b', color: '#94a3b8', cursor: 'pointer' }}>↻</button>
      </div>

      {/* Semantic Search Bar */}
      <div style={{ ...card, marginBottom: '24px' }}>
        <form onSubmit={(e) => { e.preventDefault(); load(query); }} style={{ display: 'flex', gap: '12px' }}>
          <input value={query} onChange={e => setQuery(e.target.value)} placeholder="Search logs, visual baselines, OpenTelemetry traces, or screenshots..." style={{ flex: 1, padding: '12px 16px', borderRadius: '8px', border: '1px solid #334155', background: '#0f172a', color: '#fff', fontSize: '14px' }} />
          <button type="submit" style={{ padding: '12px 24px', borderRadius: '8px', border: 'none', background: 'linear-gradient(135deg, #a78bfa, #8b5cf6)', color: '#fff', fontWeight: 700, cursor: 'pointer' }}>
            🔎 Semantic Search
          </button>
        </form>
      </div>

      {/* Results List */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {items.map((i: any) => (
          <div key={i.id} style={{ ...card, borderLeft: '4px solid #a78bfa' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
              <div>
                <span style={badge('#a78bfa')}>{i.item_type}</span>
                <strong style={{ fontSize: '16px', color: '#fff', marginLeft: '10px' }}>{i.title}</strong>
              </div>
              <span style={{ fontSize: '12px', color: '#64748b' }}>{new Date(i.created_at).toLocaleString()}</span>
            </div>

            <div style={{ background: '#0f172a', borderRadius: '8px', padding: '12px', fontSize: '13px', fontFamily: 'monospace', color: '#94a3b8', marginBottom: '12px' }}>
              {i.content_text}
            </div>

            {i.media_url && (
              <div style={{ fontSize: '12px', color: '#38bdf8' }}>
                📷 Media URL: <a href={i.media_url} target="_blank" rel="noreferrer" style={{ color: '#38bdf8' }}>{i.media_url}</a>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
