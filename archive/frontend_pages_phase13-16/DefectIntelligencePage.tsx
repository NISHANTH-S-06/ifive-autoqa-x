import React, { useEffect, useState } from 'react';
import { fetchDefectClusters, seedDefectClusters, predictDuplicateDefect } from '../services/phase15Service';

const card = { background: '#1e293b', borderRadius: '12px', border: '1px solid #334155', padding: '20px' };
const badge = (color: string) => ({ padding: '3px 10px', borderRadius: '20px', fontSize: '11px', fontWeight: 700 as const, background: `${color}22`, color, border: `1px solid ${color}44` });

export const DefectIntelligencePage: React.FC = () => {
  const [clusters, setClusters] = useState<any[]>([]);
  const [descInput, setDescInput] = useState('');
  const [prediction, setPrediction] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    try {
      let data: any = await fetchDefectClusters();
      if (!data || data.length === 0) data = await seedDefectClusters();
      setClusters(data);
    } catch (e) { console.error(e); } finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const handleCheckDuplicate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!descInput) return;
    try {
      const res = await predictDuplicateDefect(descInput);
      setPrediction(res);
    } catch (err: any) { alert(err.message); }
  };

  return (
    <div style={{ padding: '24px', maxWidth: '1600px', margin: '0 auto', color: '#f8fafc' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '28px' }}>
        <div>
          <h1 style={{ fontSize: '28px', fontWeight: 900, margin: 0, background: 'linear-gradient(90deg, #ef4444, #f97316)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            🐞 AI Defect Intelligence Hub
          </h1>
          <p style={{ margin: '4px 0 0', color: '#64748b', fontSize: '14px' }}>Defect Clustering · Duplicate Prediction · Root Cause Pattern Analysis · Fix Effort & Owner Assignment</p>
        </div>
        <button onClick={load} style={{ padding: '10px 16px', borderRadius: '8px', border: '1px solid #334155', background: '#1e293b', color: '#94a3b8', cursor: 'pointer' }}>↻</button>
      </div>

      {/* Duplicate Predictor Bar */}
      <div style={{ ...card, marginBottom: '24px' }}>
        <h3 style={{ margin: '0 0 14px', fontSize: '16px', fontWeight: 700, color: '#ef4444' }}>Check Duplicate & Predict Fix Owner</h3>
        <form onSubmit={handleCheckDuplicate} style={{ display: 'flex', gap: '12px' }}>
          <input value={descInput} onChange={e => setDescInput(e.target.value)} placeholder="Enter defect description or stack trace..." style={{ flex: 1, padding: '10px 14px', borderRadius: '8px', border: '1px solid #334155', background: '#0f172a', color: '#fff' }} />
          <button type="submit" style={{ padding: '10px 24px', borderRadius: '8px', border: 'none', background: 'linear-gradient(135deg, #ef4444, #dc2626)', color: '#fff', fontWeight: 700, cursor: 'pointer' }}>
            🔍 Check Duplicate
          </button>
        </form>

        {prediction && (
          <div style={{ background: '#0f172a', borderRadius: '8px', padding: '12px 16px', marginTop: '14px', border: '1px solid #ef444444', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <span style={{ color: '#ef4444', fontWeight: 800 }}>{prediction.is_duplicate ? '⚠️ Duplicate Found: ' : '✅ New Defect: '}</span>
              <span style={{ color: '#fff' }}>Matched Cluster: <strong>{prediction.matched_cluster}</strong></span>
            </div>
            <div style={{ fontSize: '12px', color: '#94a3b8' }}>
              Suggested Owner: <strong style={{ color: '#38bdf8' }}>{prediction.suggested_owner}</strong> ({prediction.estimated_fix_hours}h fix effort)
            </div>
          </div>
        )}
      </div>

      {/* Clusters Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(360px, 1fr))', gap: '20px' }}>
        {clusters.map((c: any) => (
          <div key={c.id} style={{ ...card, borderLeft: `4px solid ${c.priority === 'CRITICAL' ? '#dc2626' : c.priority === 'HIGH' ? '#ef4444' : '#f59e0b'}` }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
              <div>
                <h3 style={{ margin: '0 0 4px', fontSize: '16px', fontWeight: 700 }}>{c.cluster_name}</h3>
                <span style={badge('#ef4444')}>{c.priority} PRIORITY</span>
              </div>
              <div style={{ fontSize: '20px', fontWeight: 900, color: '#ef4444' }}>{c.defect_count} <span style={{ fontSize: '11px', color: '#64748b' }}>Bugs</span></div>
            </div>

            <p style={{ fontSize: '13px', color: '#94a3b8', margin: '0 0 14px', lineHeight: '1.4' }}>
              <strong>Root Cause: </strong>{c.root_cause_pattern}
            </p>

            <div style={{ background: '#0f172a', borderRadius: '8px', padding: '12px', fontSize: '12px', marginBottom: '14px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                <span style={{ color: '#64748b' }}>Assigned Owner:</span>
                <span style={{ color: '#38bdf8', fontWeight: 700 }}>{c.assigned_owner}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: '#64748b' }}>Est. Fix Effort:</span>
                <span style={{ color: '#10b981', fontWeight: 700 }}>{c.estimated_fix_hours} hours</span>
              </div>
            </div>

            <div style={{ display: 'flex', gap: '4px', flexWrap: 'wrap' }}>
              {c.defects?.map((d: string) => (
                <span key={d} style={{ background: '#0f172a', color: '#94a3b8', padding: '2px 8px', borderRadius: '4px', fontSize: '11px', fontFamily: 'monospace' }}>{d}</span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
