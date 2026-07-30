import React, { useEffect, useState } from 'react';
import { computeCoverage, fetchCoverageMetrics, generateMissingTests } from '../services/phase15Service';

const card = { background: '#1e293b', borderRadius: '12px', border: '1px solid #334155', padding: '20px' };
const badge = (color: string) => ({ padding: '3px 10px', borderRadius: '20px', fontSize: '11px', fontWeight: 700 as const, background: `${color}22`, color, border: `1px solid ${color}44` });

export const CoverageIntelligencePage: React.FC = () => {
  const [metrics, setMetrics] = useState<any[]>([]);
  const [genResult, setGenResult] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    try {
      let data: any = await fetchCoverageMetrics();
      if (!data || data.length === 0) data = await computeCoverage();
      setMetrics(data);
    } catch (e) { console.error(e); } finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const handleGenerate = async (dim: string) => {
    try {
      const res = await generateMissingTests(dim);
      setGenResult(res);
    } catch (e) { console.error(e); }
  };

  return (
    <div style={{ padding: '24px', maxWidth: '1600px', margin: '0 auto', color: '#f8fafc' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '28px' }}>
        <div>
          <h1 style={{ fontSize: '28px', fontWeight: 900, margin: 0, background: 'linear-gradient(90deg, #10b981, #34d399)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            🎯 AI Test Coverage Intelligence
          </h1>
          <p style={{ margin: '4px 0 0', color: '#64748b', fontSize: '14px' }}>8-Dimension Coverage Breakdown · Feature · Module · API · Requirement · Risk · Regression · Automation · Business Rule</p>
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button onClick={computeCoverage} style={{ padding: '10px 18px', borderRadius: '8px', border: 'none', background: 'linear-gradient(135deg, #10b981, #059669)', color: '#fff', fontWeight: 700, cursor: 'pointer' }}>
            ⚡ Re-Compute Coverage
          </button>
          <button onClick={load} style={{ padding: '10px 16px', borderRadius: '8px', border: '1px solid #334155', background: '#1e293b', color: '#94a3b8', cursor: 'pointer' }}>↻</button>
        </div>
      </div>

      {genResult && (
        <div style={{ ...card, marginBottom: '20px', background: '#10b98111', border: '1px solid #10b98144' }}>
          <div style={{ fontWeight: 800, color: '#10b981', marginBottom: '4px' }}>✅ Generated {genResult.generated_test_count} Missing Tests for {genResult.dimension_type}</div>
          <div style={{ fontSize: '13px', color: '#94a3b8' }}>Coverage Improvement: +{genResult.coverage_improvement_pct}%</div>
        </div>
      )}

      {/* 8-Dimension Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))', gap: '20px' }}>
        {metrics.map((m: any) => {
          const isHigh = m.coverage_pct >= 90;
          const color = isHigh ? '#10b981' : '#f59e0b';

          return (
            <div key={m.id} style={{ ...card, borderTop: `4px solid ${color}` }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
                <div>
                  <div style={{ fontSize: '11px', color: '#64748b', textTransform: 'uppercase', fontWeight: 800 }}>{m.dimension_type}</div>
                  <div style={{ fontSize: '28px', fontWeight: 900, color, marginTop: '2px' }}>{m.coverage_pct}%</div>
                </div>
                <span style={badge(color)}>{m.target_name}</span>
              </div>

              {/* Progress Bar */}
              <div style={{ background: '#0f172a', borderRadius: '6px', height: '8px', overflow: 'hidden', marginBottom: '14px' }}>
                <div style={{ width: `${m.coverage_pct}%`, height: '100%', background: color }} />
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '12px' }}>
                <span style={{ color: '#94a3b8' }}>Missing Items: <strong style={{ color: '#fff' }}>{m.missing_items_count}</strong></span>
                <button onClick={() => handleGenerate(m.dimension_type)} style={{ padding: '6px 12px', borderRadius: '6px', border: '1px solid #10b98144', background: '#10b98122', color: '#10b981', fontWeight: 700, cursor: 'pointer' }}>
                  + Auto-Generate
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
