import React, { useEffect, useState } from 'react';
import { fetchGovernancePolicies, seedGovernancePolicies, toggleGovernancePolicy } from '../services/phase14Service';

const card = { background: '#1e293b', borderRadius: '12px', border: '1px solid #334155', padding: '20px' };
const badge = (color: string) => ({ padding: '3px 10px', borderRadius: '20px', fontSize: '11px', fontWeight: 700 as const, background: `${color}22`, color, border: `1px solid ${color}44` });

export const GovernanceCenterPage: React.FC = () => {
  const [policies, setPolicies] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    try {
      let data: any = await fetchGovernancePolicies();
      if (data.length === 0) data = await seedGovernancePolicies();
      setPolicies(data);
    } catch (e) { console.error(e); } finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const handleToggle = async (id: number) => {
    try {
      await toggleGovernancePolicy(id);
      load();
    } catch (err: any) { alert(err.message); }
  };

  return (
    <div style={{ padding: '24px', maxWidth: '1600px', margin: '0 auto', color: '#f8fafc' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '28px' }}>
        <div>
          <h1 style={{ fontSize: '28px', fontWeight: 900, margin: 0, background: 'linear-gradient(90deg, #38bdf8, #818cf8)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            🛡️ Enterprise Governance Center
          </h1>
          <p style={{ margin: '4px 0 0', color: '#64748b', fontSize: '14px' }}>Release policies · Data classification · Retention policies · Security gates & audit enforcement</p>
        </div>
        <button onClick={load} style={{ padding: '10px 16px', borderRadius: '8px', border: '1px solid #334155', background: '#1e293b', color: '#94a3b8', cursor: 'pointer' }}>↻</button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(360px, 1fr))', gap: '20px' }}>
        {policies.map((p: any) => (
          <div key={p.id} style={{ ...card, borderLeft: `4px solid ${p.is_enforced ? '#10b981' : '#64748b'}` }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '14px' }}>
              <div>
                <h3 style={{ margin: '0 0 4px', fontSize: '16px', fontWeight: 700 }}>{p.policy_name}</h3>
                <span style={badge('#38bdf8')}>{p.policy_type}</span>
              </div>
              <button onClick={() => handleToggle(p.id)}
                style={{ padding: '6px 14px', borderRadius: '20px', background: p.is_enforced ? '#10b98122' : '#334155', color: p.is_enforced ? '#10b981' : '#64748b', border: `1px solid ${p.is_enforced ? '#10b98144' : '#334155'}`, fontWeight: 700, fontSize: '11px', cursor: 'pointer' }}>
                {p.is_enforced ? '✓ ENFORCED' : 'OFF'}
              </button>
            </div>

            <div style={{ background: '#0f172a', borderRadius: '8px', padding: '12px', fontSize: '12px' }}>
              <div style={{ fontSize: '11px', color: '#64748b', textTransform: 'uppercase', marginBottom: '6px' }}>Policy Rules</div>
              {Object.entries(p.rules || {}).map(([k, v]) => (
                <div key={k} style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                  <span style={{ color: '#94a3b8' }}>{k.replace(/_/g, ' ')}:</span>
                  <span style={{ color: '#fff', fontWeight: 600 }}>{String(v)}</span>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
