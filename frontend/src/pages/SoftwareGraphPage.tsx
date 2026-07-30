import React, { useEffect, useState } from 'react';
import { fetchSoftwareGraph, seedSoftwareGraph, analyzeSoftwareImpact } from '../services/phase15Service';

const card = { background: '#1e293b', borderRadius: '12px', border: '1px solid #334155', padding: '20px' };
const TIER_COLORS: Record<string, string> = {
  COMPANY: '#f472b6', PRODUCT: '#a78bfa', MODULE: '#38bdf8', FEATURE: '#34d399', EPIC: '#10b981',
  STORY: '#f59e0b', TASK: '#fb923c', SOURCE_FILE: '#818cf8', API: '#ef4444', DATABASE: '#6366f1',
  INFRASTRUCTURE: '#ec4899', DEPLOYMENT: '#06b6d4', TEST: '#10b981', EXECUTION: '#8b5cf6',
  BUG: '#ef4444', INCIDENT: '#dc2626', RELEASE: '#22c55e', FEEDBACK: '#38bdf8',
};

export const SoftwareGraphPage: React.FC = () => {
  const [graph, setGraph] = useState<any>({ nodes: [], edges: [], tiers: [] });
  const [selectedTier, setSelectedTier] = useState<string | null>(null);
  const [impactAnalysis, setImpactAnalysis] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    try {
      let data: any = await fetchSoftwareGraph(selectedTier || undefined);
      if (!data.nodes || data.nodes.length === 0) data = await seedSoftwareGraph();
      setGraph(data);
    } catch (e) { console.error(e); } finally { setLoading(false); }
  };

  useEffect(() => { load(); }, [selectedTier]);

  const handleInspectNode = async (key: string) => {
    try {
      const res = await analyzeSoftwareImpact(key);
      setImpactAnalysis(res);
    } catch (e) { console.error(e); }
  };

  return (
    <div style={{ padding: '24px', maxWidth: '1600px', margin: '0 auto', color: '#f8fafc' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '28px' }}>
        <div>
          <h1 style={{ fontSize: '28px', fontWeight: 900, margin: 0, background: 'linear-gradient(90deg, #38bdf8, #a78bfa, #f472b6)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            🕸️ Enterprise Software Intelligence Graph
          </h1>
          <p style={{ margin: '4px 0 0', color: '#64748b', fontSize: '14px' }}>18-Tier Traceability & Impact Mapping — Company → Source Code → DB → Tests → Releases → Incidents</p>
        </div>
        <button onClick={load} style={{ padding: '10px 16px', borderRadius: '8px', border: '1px solid #334155', background: '#1e293b', color: '#94a3b8', cursor: 'pointer' }}>↻</button>
      </div>

      {/* Tier Selector */}
      <div style={{ display: 'flex', gap: '6px', marginBottom: '20px', flexWrap: 'wrap' }}>
        <button onClick={() => setSelectedTier(null)} style={{ padding: '6px 12px', borderRadius: '16px', border: `1px solid ${!selectedTier ? '#38bdf8' : '#334155'}`, background: !selectedTier ? '#38bdf822' : '#1e293b', color: !selectedTier ? '#38bdf8' : '#94a3b8', cursor: 'pointer', fontSize: '11px' }}>
          All Tiers ({graph.nodes?.length || 0})
        </button>
        {graph.tiers?.map((t: string) => (
          <button key={t} onClick={() => setSelectedTier(selectedTier === t ? null : t)}
            style={{ padding: '6px 12px', borderRadius: '16px', border: `1px solid ${selectedTier === t ? TIER_COLORS[t] || '#64748b' : '#334155'}`, background: selectedTier === t ? `${TIER_COLORS[t] || '#64748b'}22` : '#1e293b', color: selectedTier === t ? TIER_COLORS[t] || '#fff' : '#94a3b8', cursor: 'pointer', fontSize: '11px' }}>
            {t}
          </button>
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 360px', gap: '20px' }}>
        {/* Nodes Grid */}
        <div style={card}>
          <h3 style={{ margin: '0 0 16px', fontSize: '16px', fontWeight: 700, color: '#38bdf8' }}>Graph Nodes ({graph.nodes?.length || 0})</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))', gap: '12px' }}>
            {graph.nodes?.map((n: any) => {
              const color = TIER_COLORS[n.node_type] || '#64748b';
              return (
                <div key={n.id} onClick={() => handleInspectNode(n.node_key)}
                  style={{ background: '#0f172a', borderRadius: '8px', padding: '12px', borderLeft: `4px solid ${color}`, cursor: 'pointer' }}>
                  <div style={{ fontSize: '10px', color, fontWeight: 800, textTransform: 'uppercase' }}>{n.node_type}</div>
                  <div style={{ fontWeight: 700, fontSize: '13px', margin: '4px 0 2px' }}>{n.label}</div>
                  <div style={{ fontSize: '10px', color: '#64748b', fontFamily: 'monospace' }}>{n.node_key}</div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Impact Panel */}
        <div style={card}>
          <h3 style={{ margin: '0 0 16px', fontSize: '16px', fontWeight: 700, color: '#a78bfa' }}>Impact Analyzer</h3>
          {impactAnalysis ? (
            <div style={{ background: '#0f172a', borderRadius: '8px', padding: '16px' }}>
              <div style={{ fontSize: '12px', color: '#64748b', textTransform: 'uppercase' }}>Target Node</div>
              <div style={{ fontSize: '16px', fontWeight: 800, color: '#38bdf8', margin: '4px 0 12px' }}>{impactAnalysis.target_node}</div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', fontSize: '13px' }}>
                <span style={{ color: '#94a3b8' }}>Direct Impacted Nodes:</span>
                <span style={{ color: '#fff', fontWeight: 700 }}>{impactAnalysis.direct_impact_count}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px', marginBottom: '14px' }}>
                <span style={{ color: '#94a3b8' }}>Propagation Risk:</span>
                <span style={{ color: impactAnalysis.propagation_risk === 'HIGH' ? '#ef4444' : '#10b981', fontWeight: 800 }}>{impactAnalysis.propagation_risk}</span>
              </div>

              {impactAnalysis.impacted_nodes?.map((inod: any) => (
                <div key={inod.id} style={{ background: '#1e293b', borderRadius: '6px', padding: '8px', marginBottom: '6px', fontSize: '12px' }}>
                  <div style={{ color: TIER_COLORS[inod.node_type] || '#fff', fontWeight: 700 }}>{inod.node_type}: {inod.label}</div>
                </div>
              ))}
            </div>
          ) : (
            <div style={{ color: '#64748b', fontSize: '13px' }}>Click any graph node on the left to analyze its downstream impact propagation.</div>
          )}
        </div>
      </div>
    </div>
  );
};
