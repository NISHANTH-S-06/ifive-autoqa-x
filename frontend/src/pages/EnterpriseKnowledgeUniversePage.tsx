import React, { useEffect, useState } from 'react';
import { fetchKnowledgeUniverseGraph, seedKnowledgeUniverse } from '../services/phase14Service';

const card = { background: '#1e293b', borderRadius: '12px', border: '1px solid #334155', padding: '20px' };
const TIER_COLORS: Record<string, string> = {
  COMPANY: '#f472b6', PRODUCT: '#a78bfa', MODULE: '#38bdf8', PAGE: '#10b981', COMPONENT: '#34d399',
  API: '#f59e0b', DATABASE: '#fb923c', INFRASTRUCTURE: '#818cf8', RULE: '#ef4444', TEST: '#6366f1', RELEASE: '#22c55e',
};

export const EnterpriseKnowledgeUniversePage: React.FC = () => {
  const [graph, setGraph] = useState<any>({ nodes: [], edges: [], entity_tiers: [] });
  const [selectedTier, setSelectedTier] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    try {
      let data: any = await fetchKnowledgeUniverseGraph(selectedTier || undefined);
      if (!data.nodes || data.nodes.length === 0) data = await seedKnowledgeUniverse();
      setGraph(data);
    } catch (e) { console.error(e); } finally { setLoading(false); }
  };

  useEffect(() => { load(); }, [selectedTier]);

  return (
    <div style={{ padding: '24px', maxWidth: '1600px', margin: '0 auto', color: '#f8fafc' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '28px' }}>
        <div>
          <h1 style={{ fontSize: '28px', fontWeight: 900, margin: 0, background: 'linear-gradient(90deg, #f472b6, #a78bfa, #38bdf8)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            🌌 Enterprise Knowledge Universe
          </h1>
          <p style={{ margin: '4px 0 0', color: '#64748b', fontSize: '14px' }}>18-Tier Knowledge Graph — Company → Product → Module → Page → API → DB → Infra → Rules → Tests → Releases</p>
        </div>
        <button onClick={load} style={{ padding: '10px 16px', borderRadius: '8px', border: '1px solid #334155', background: '#1e293b', color: '#94a3b8', cursor: 'pointer' }}>↻</button>
      </div>

      {/* Tier Filters */}
      <div style={{ display: 'flex', gap: '8px', marginBottom: '20px', flexWrap: 'wrap' }}>
        <button onClick={() => setSelectedTier(null)} style={{ padding: '7px 14px', borderRadius: '20px', border: `1px solid ${!selectedTier ? '#a78bfa' : '#334155'}`, background: !selectedTier ? '#a78bfa22' : '#1e293b', color: !selectedTier ? '#a78bfa' : '#94a3b8', cursor: 'pointer', fontSize: '12px' }}>
          All Tiers ({graph.nodes?.length || 0})
        </button>
        {graph.entity_tiers?.map((tier: string) => (
          <button key={tier} onClick={() => setSelectedTier(selectedTier === tier ? null : tier)}
            style={{ padding: '7px 14px', borderRadius: '20px', border: `1px solid ${selectedTier === tier ? TIER_COLORS[tier] || '#64748b' : '#334155'}`, background: selectedTier === tier ? `${TIER_COLORS[tier] || '#64748b'}22` : '#1e293b', color: selectedTier === tier ? TIER_COLORS[tier] || '#fff' : '#94a3b8', cursor: 'pointer', fontSize: '12px' }}>
            {tier}
          </button>
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 340px', gap: '20px' }}>
        {/* Interactive Graph Node Grid */}
        <div style={card}>
          <h3 style={{ margin: '0 0 16px', fontSize: '16px', fontWeight: 700, color: '#f472b6' }}>Universe Node Map</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))', gap: '12px' }}>
            {graph.nodes?.map((n: any) => {
              const color = TIER_COLORS[n.node_type] || '#64748b';
              return (
                <div key={n.id} style={{ background: '#0f172a', borderRadius: '10px', padding: '14px', borderLeft: `4px solid ${color}` }}>
                  <div style={{ fontSize: '10px', color, fontWeight: 800, textTransform: 'uppercase', marginBottom: '4px' }}>{n.node_type}</div>
                  <div style={{ fontWeight: 700, fontSize: '13px', marginBottom: '4px' }}>{n.label}</div>
                  <div style={{ fontSize: '10px', color: '#64748b', fontFamily: 'monospace' }}>{n.node_key}</div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Graph Edges / Connections */}
        <div style={card}>
          <h3 style={{ margin: '0 0 16px', fontSize: '16px', fontWeight: 700, color: '#a78bfa' }}>Entity Relationships ({graph.edges?.length || 0})</h3>
          <div style={{ maxHeight: '550px', overflowY: 'auto' }}>
            {graph.edges?.map((e: any) => (
              <div key={e.id} style={{ background: '#0f172a', borderRadius: '8px', padding: '10px 12px', marginBottom: '8px', fontSize: '12px' }}>
                <div style={{ color: '#a78bfa', fontWeight: 700, fontSize: '11px', marginBottom: '2px' }}>RELATION: {e.relationship_type}</div>
                <div style={{ color: '#94a3b8' }}>Node #{e.source} → Node #{e.target}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
