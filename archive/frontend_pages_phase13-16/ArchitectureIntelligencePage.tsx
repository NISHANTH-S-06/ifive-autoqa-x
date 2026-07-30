import React, { useEffect, useState } from 'react';
import { fetchArchitectureGraph } from '../services/phase16Service';

const card = { background: '#1e293b', borderRadius: '12px', border: '1px solid #334155', padding: '20px' };
const badge = (color: string) => ({ padding: '3px 10px', borderRadius: '20px', fontSize: '11px', fontWeight: 700 as const, background: `${color}22`, color, border: `1px solid ${color}44` });

export const ArchitectureIntelligencePage: React.FC = () => {
  const [arch, setArch] = useState<any>({ nodes: [], edges: [], critical_path: [], bottlenecks: [] });
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    try {
      const data: any = await fetchArchitectureGraph();
      setArch(data);
    } catch (e) { console.error(e); } finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  return (
    <div style={{ padding: '24px', maxWidth: '1600px', margin: '0 auto', color: '#f8fafc' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '28px' }}>
        <div>
          <h1 style={{ fontSize: '28px', fontWeight: 900, margin: 0, background: 'linear-gradient(90deg, #f59e0b, #fbbf24)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            🏛️ Architecture Intelligence
          </h1>
          <p style={{ margin: '4px 0 0', color: '#64748b', fontSize: '14px' }}>Microservices · Event-Driven (Kafka / Redis) · Databases · Critical Paths & Bottlenecks</p>
        </div>
        <button onClick={load} style={{ padding: '10px 16px', borderRadius: '8px', border: '1px solid #334155', background: '#1e293b', color: '#94a3b8', cursor: 'pointer' }}>↻</button>
      </div>

      {/* Summary Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px', marginBottom: '24px' }}>
        <div style={{ ...card, textAlign: 'center' }}>
          <div style={{ fontSize: '28px', fontWeight: 900, color: '#f59e0b' }}>{arch.architecture_risk_score}</div>
          <div style={{ fontSize: '12px', color: '#94a3b8' }}>Overall Risk Score</div>
        </div>
        <div style={{ ...card, textAlign: 'center' }}>
          <div style={{ fontSize: '28px', fontWeight: 900, color: '#38bdf8' }}>{arch.nodes.length}</div>
          <div style={{ fontSize: '12px', color: '#94a3b8' }}>Architecture Nodes</div>
        </div>
        <div style={{ ...card, textAlign: 'center' }}>
          <div style={{ fontSize: '28px', fontWeight: 900, color: '#ef4444' }}>{arch.bottlenecks.length}</div>
          <div style={{ fontSize: '12px', color: '#94a3b8' }}>Bottleneck Services</div>
        </div>
      </div>

      {/* Nodes Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '20px' }}>
        {arch.nodes.map((n: any) => (
          <div key={n.id} style={{ ...card, borderTop: `4px solid ${n.is_bottleneck ? '#ef4444' : '#10b981'}` }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
              <span style={badge('#f59e0b')}>{n.node_type}</span>
              {n.is_bottleneck && <span style={badge('#ef4444')}>⚠️ BOTTLENECK</span>}
            </div>
            <h3 style={{ margin: '4px 0 8px', fontSize: '16px', fontWeight: 700 }}>{n.label}</h3>
            <div style={{ fontSize: '12px', color: '#94a3b8', marginBottom: '8px' }}>Key: <strong style={{ color: '#fff' }}>{n.node_key}</strong></div>
            <div style={{ fontSize: '12px', color: n.risk_score > 0.7 ? '#ef4444' : '#10b981', fontWeight: 800 }}>Risk Score: {(n.risk_score * 100).toFixed(0)}%</div>
          </div>
        ))}
      </div>
    </div>
  );
};
