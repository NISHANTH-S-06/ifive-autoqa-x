import React, { useEffect, useState } from 'react';
import { fetchCustomerFeedback } from '../services/phase16Service';

const card = { background: '#1e293b', borderRadius: '12px', border: '1px solid #334155', padding: '20px' };
const badge = (color: string) => ({ padding: '3px 10px', borderRadius: '20px', fontSize: '11px', fontWeight: 700 as const, background: `${color}22`, color, border: `1px solid ${color}44` });

export const CustomerExperiencePage: React.FC = () => {
  const [items, setItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    try {
      const data: any = await fetchCustomerFeedback();
      setItems(data);
    } catch (e) { console.error(e); } finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  return (
    <div style={{ padding: '24px', maxWidth: '1600px', margin: '0 auto', color: '#f8fafc' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '28px' }}>
        <div>
          <h1 style={{ fontSize: '28px', fontWeight: 900, margin: 0, background: 'linear-gradient(90deg, #f472b6, #fb7185)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            💬 Customer Experience Intelligence
          </h1>
          <p style={{ margin: '4px 0 0', color: '#64748b', fontSize: '14px' }}>Support Tickets · NPS · Feedback · Crash Reports ↓ Correlated to Bug ↓ Dev ↓ Release ↓ Root Cause</p>
        </div>
        <button onClick={load} style={{ padding: '10px 16px', borderRadius: '8px', border: '1px solid #334155', background: '#1e293b', color: '#94a3b8', cursor: 'pointer' }}>↻</button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(360px, 1fr))', gap: '20px' }}>
        {items.map((i: any) => (
          <div key={i.id} style={card}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
              <span style={badge('#f472b6')}>{i.source_type}</span>
              {i.nps_score && <span style={badge(i.nps_score >= 8 ? '#10b981' : '#ef4444')}>NPS: {i.nps_score}</span>}
            </div>

            <h3 style={{ margin: '0 0 8px', fontSize: '15px', fontWeight: 700 }}>{i.headline}</h3>

            {i.correlated_bug_key && (
              <div style={{ background: '#0f172a', padding: '10px', borderRadius: '6px', fontSize: '12px', marginTop: '10px' }}>
                <div style={{ color: '#ef4444', fontWeight: 700, marginBottom: '2px' }}>🐞 Correlated Bug: {i.correlated_bug_key}</div>
                <div style={{ color: '#94a3b8' }}>Dev: {i.assigned_developer}</div>
                <div style={{ color: '#94a3b8' }}>Release: {i.release_version}</div>
                {i.root_cause && <div style={{ color: '#fb7185', marginTop: '4px' }}>Root Cause: {i.root_cause}</div>}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
