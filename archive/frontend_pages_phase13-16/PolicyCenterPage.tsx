import React, { useEffect, useState } from 'react';
import { evaluatePolicies, fetchPolicies } from '../services/phase16Service';

const card = { background: '#1e293b', borderRadius: '12px', border: '1px solid #334155', padding: '20px' };
const badge = (color: string) => ({ padding: '3px 10px', borderRadius: '20px', fontSize: '11px', fontWeight: 700 as const, background: `${color}22`, color, border: `1px solid ${color}44` });

export const PolicyCenterPage: React.FC = () => {
  const [policies, setPolicies] = useState<any[]>([]);
  const [evalResult, setEvalResult] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    try {
      const data: any = await fetchPolicies();
      setPolicies(data);
    } catch (e) { console.error(e); } finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const handleEvaluate = async () => {
    try {
      const res = await evaluatePolicies({ coverage_pct: 92, high_security_vulnerabilities: 0 });
      setEvalResult(res);
    } catch (e) { console.error(e); }
  };

  return (
    <div style={{ padding: '24px', maxWidth: '1600px', margin: '0 auto', color: '#f8fafc' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '28px' }}>
        <div>
          <h1 style={{ fontSize: '28px', fontWeight: 900, margin: 0, background: 'linear-gradient(90deg, #38bdf8, #818cf8)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            ⚙️ Enterprise Policy Engine
          </h1>
          <p style={{ margin: '4px 0 0', color: '#64748b', fontSize: '14px' }}>Quality · Release · Security · Naming · Testing Policies & Auto-Enforcement</p>
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button onClick={handleEvaluate} style={{ padding: '10px 18px', borderRadius: '8px', border: 'none', background: 'linear-gradient(135deg, #38bdf8, #0284c7)', color: '#fff', fontWeight: 700, cursor: 'pointer' }}>
            ⚡ Evaluate Policies
          </button>
          <button onClick={load} style={{ padding: '10px 16px', borderRadius: '8px', border: '1px solid #334155', background: '#1e293b', color: '#94a3b8', cursor: 'pointer' }}>↻</button>
        </div>
      </div>

      {evalResult && (
        <div style={{ ...card, marginBottom: '20px', background: evalResult.is_compliant ? '#10b98111' : '#ef444411', border: `1px solid ${evalResult.is_compliant ? '#10b98144' : '#ef444444'}` }}>
          <div style={{ fontWeight: 800, color: evalResult.is_compliant ? '#10b981' : '#ef4444' }}>
            {evalResult.is_compliant ? '✅ Context Satisfies All Enterprise Policies' : '❌ Policy Violations Detected'}
          </div>
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(360px, 1fr))', gap: '20px' }}>
        {policies.map((p: any) => (
          <div key={p.id} style={{ ...card, borderLeft: `4px solid ${p.is_active ? '#10b981' : '#64748b'}` }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
              <span style={badge('#38bdf8')}>{p.policy_category}</span>
              <span style={badge(p.is_active ? '#10b981' : '#64748b')}>{p.is_active ? 'ACTIVE' : 'INACTIVE'}</span>
            </div>
            <h3 style={{ margin: '0 0 8px', fontSize: '15px', fontWeight: 700 }}>{p.rule_name}</h3>
            <div style={{ fontSize: '12px', color: '#94a3b8', background: '#0f172a', padding: '10px', borderRadius: '6px' }}>
              <div>Rule: <code>{p.rule_condition}</code></div>
              <div style={{ color: '#ef4444', marginTop: '4px' }}>Action: {p.action_on_violation}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
