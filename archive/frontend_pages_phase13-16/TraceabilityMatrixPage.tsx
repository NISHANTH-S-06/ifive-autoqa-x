import React, { useEffect, useState } from 'react';
import { fetchTraceabilityGapReport, fetchTraceabilityMatrix, seedTraceability } from '../services/phase16Service';

const card = { background: '#1e293b', borderRadius: '12px', border: '1px solid #334155', padding: '20px' };
const badge = (color: string) => ({ padding: '3px 10px', borderRadius: '20px', fontSize: '11px', fontWeight: 700 as const, background: `${color}22`, color, border: `1px solid ${color}44` });

export const TraceabilityMatrixPage: React.FC = () => {
  const [matrix, setMatrix] = useState<any[]>([]);
  const [gapReport, setGapReport] = useState<any>({});
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    try {
      let data: any = await fetchTraceabilityMatrix();
      if (!data || data.length === 0) data = await seedTraceability();
      setMatrix(data);
      const gap = await fetchTraceabilityGapReport();
      setGapReport(gap);
    } catch (e) { console.error(e); } finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  return (
    <div style={{ padding: '24px', maxWidth: '1600px', margin: '0 auto', color: '#f8fafc' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '28px' }}>
        <div>
          <h1 style={{ fontSize: '28px', fontWeight: 900, margin: 0, background: 'linear-gradient(90deg, #a78bfa, #f472b6)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            🔗 10-Tier Requirement → Release Traceability Matrix
          </h1>
          <p style={{ margin: '4px 0 0', color: '#64748b', fontSize: '14px' }}>Requirement ↓ Story ↓ Design ↓ API ↓ DB ↓ UI ↓ Test ↓ Evidence ↓ Defect ↓ Release</p>
        </div>
        <button onClick={load} style={{ padding: '10px 16px', borderRadius: '8px', border: '1px solid #334155', background: '#1e293b', color: '#94a3b8', cursor: 'pointer' }}>↻</button>
      </div>

      {/* Gap Summary Banner */}
      <div style={{ ...card, marginBottom: '24px', display: 'flex', justifyContent: 'space-around', textAlign: 'center', background: '#a78bfa11', border: '1px solid #a78bfa44' }}>
        <div>
          <div style={{ fontSize: '28px', fontWeight: 900, color: '#a78bfa' }}>{gapReport.completeness_pct}%</div>
          <div style={{ fontSize: '12px', color: '#94a3b8' }}>Traceability Completeness</div>
        </div>
        <div>
          <div style={{ fontSize: '28px', fontWeight: 900, color: '#10b981' }}>{gapReport.total_requirements_mapped}</div>
          <div style={{ fontSize: '12px', color: '#94a3b8' }}>Mapped Requirements</div>
        </div>
        <div>
          <div style={{ fontSize: '28px', fontWeight: 900, color: gapReport.incomplete_coverage_count > 0 ? '#ef4444' : '#10b981' }}>{gapReport.incomplete_coverage_count}</div>
          <div style={{ fontSize: '12px', color: '#94a3b8' }}>Coverage Gaps</div>
        </div>
      </div>

      {/* Matrix Table */}
      <div style={card}>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid #334155', color: '#64748b', textAlign: 'left' }}>
                <th style={{ padding: '10px' }}>Requirement</th>
                <th style={{ padding: '10px' }}>User Story</th>
                <th style={{ padding: '10px' }}>Design Doc</th>
                <th style={{ padding: '10px' }}>API Endpoint</th>
                <th style={{ padding: '10px' }}>DB Table</th>
                <th style={{ padding: '10px' }}>Test Scenario</th>
                <th style={{ padding: '10px' }}>Release</th>
                <th style={{ padding: '10px' }}>Status</th>
              </tr>
            </thead>
            <tbody>
              {matrix.map((m: any) => (
                <tr key={m.id} style={{ borderBottom: '1px solid #1e293b' }}>
                  <td style={{ padding: '10px', fontWeight: 700, color: '#38bdf8' }}>{m.requirement_code}</td>
                  <td style={{ padding: '10px', color: '#cbd5e1' }}>{m.user_story_key}</td>
                  <td style={{ padding: '10px', color: '#94a3b8' }}>{m.design_doc_ref}</td>
                  <td style={{ padding: '10px', color: '#a78bfa' }}>{m.api_endpoint}</td>
                  <td style={{ padding: '10px', color: '#cbd5e1' }}>{m.db_table}</td>
                  <td style={{ padding: '10px', color: '#34d399' }}>{m.test_scenario}</td>
                  <td style={{ padding: '10px', color: '#f472b6', fontWeight: 700 }}>{m.release_version}</td>
                  <td style={{ padding: '10px' }}>
                    <span style={badge(m.is_coverage_complete ? '#10b981' : '#ef4444')}>
                      {m.is_coverage_complete ? 'COMPLETE' : 'GAP DETECTED'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
