import React, { useEffect, useState } from 'react';
import { fetchOptimizationV2History, tuneOptimizationV2 } from '../services/phase14Service';

const card = { background: '#1e293b', borderRadius: '12px', border: '1px solid #334155', padding: '20px' };
const badge = (color: string) => ({ padding: '3px 10px', borderRadius: '20px', fontSize: '11px', fontWeight: 700 as const, background: `${color}22`, color, border: `1px solid ${color}44` });

export const OptimizationCenterV2Page: React.FC = () => {
  const [history, setHistory] = useState<any[]>([]);
  const [tuning, setTuning] = useState(false);
  const [tuneSummary, setTuneSummary] = useState<string | null>(null);

  const load = async () => {
    try {
      const data: any = await fetchOptimizationV2History();
      setHistory(data);
    } catch (e) { console.error(e); }
  };

  useEffect(() => { load(); }, []);

  const handleTune = async () => {
    setTuning(true);
    try {
      const result: any = await tuneOptimizationV2();
      setTuneSummary(`Overall Gain: +${result.overall_gain_pct}% across ${result.total_subsystems_tuned} subsystems`);
      load();
    } catch (err: any) { alert(err.message); } finally { setTuning(false); }
  };

  return (
    <div style={{ padding: '24px', maxWidth: '1600px', margin: '0 auto', color: '#f8fafc' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '28px' }}>
        <div>
          <h1 style={{ fontSize: '28px', fontWeight: 900, margin: 0, background: 'linear-gradient(90deg, #10b981, #38bdf8)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            ⚡ Autonomous Optimization Engine V2
          </h1>
          <p style={{ margin: '4px 0 0', color: '#64748b', fontSize: '14px' }}>Continuous self-tuning across browser pools, queues, locators, timeouts, AI models & infra costs</p>
        </div>
        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          {tuneSummary && <span style={{ fontSize: '12px', color: '#10b981', background: '#10b98122', padding: '6px 12px', borderRadius: '6px', border: '1px solid #10b98144' }}>✅ {tuneSummary}</span>}
          <button onClick={handleTune} disabled={tuning} style={{ padding: '10px 22px', borderRadius: '8px', border: 'none', background: tuning ? '#334155' : 'linear-gradient(135deg, #10b981, #059669)', color: tuning ? '#64748b' : '#fff', fontWeight: 700, cursor: tuning ? 'not-allowed' : 'pointer' }}>
            {tuning ? '⚙️ Tuning...' : '🤖 Trigger V2 Self-Tuning'}
          </button>
          <button onClick={load} style={{ padding: '10px 16px', borderRadius: '8px', border: '1px solid #334155', background: '#1e293b', color: '#94a3b8', cursor: 'pointer' }}>↻</button>
        </div>
      </div>

      {/* History Log */}
      <div style={card}>
        <h3 style={{ margin: '0 0 16px', fontSize: '16px', fontWeight: 700, color: '#10b981' }}>Self-Tuning Log History ({history.length})</h3>
        {history.length === 0 ? <div style={{ color: '#64748b' }}>No tuning history. Click "Trigger V2 Self-Tuning" to start.</div> : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid #334155', color: '#64748b' }}>
                  <th style={{ padding: '8px 12px', textAlign: 'left' }}>Subsystem</th>
                  <th style={{ padding: '8px 12px', textAlign: 'left' }}>State Before</th>
                  <th style={{ padding: '8px 12px', textAlign: 'left' }}>State After</th>
                  <th style={{ padding: '8px 12px', textAlign: 'right' }}>Gain</th>
                  <th style={{ padding: '8px 12px', textAlign: 'left' }}>Reasoning</th>
                  <th style={{ padding: '8px 12px', textAlign: 'right' }}>Tuned At</th>
                </tr>
              </thead>
              <tbody>
                {history.map((h: any) => (
                  <tr key={h.id} style={{ borderBottom: '1px solid #1e293b' }}>
                    <td style={{ padding: '8px 12px', fontWeight: 700 }}>
                      <span style={badge('#38bdf8')}>{h.target_subsystem}</span>
                    </td>
                    <td style={{ padding: '8px 12px', fontFamily: 'monospace', color: '#ef4444', fontSize: '11px' }}>{JSON.stringify(h.before_state)}</td>
                    <td style={{ padding: '8px 12px', fontFamily: 'monospace', color: '#10b981', fontSize: '11px' }}>{JSON.stringify(h.after_state)}</td>
                    <td style={{ padding: '8px 12px', textAlign: 'right', color: '#10b981', fontWeight: 800 }}>+{h.gain_pct.toFixed(1)}%</td>
                    <td style={{ padding: '8px 12px', color: '#94a3b8', fontSize: '12px' }}>{h.reasoning}</td>
                    <td style={{ padding: '8px 12px', textAlign: 'right', color: '#64748b', fontSize: '11px' }}>{new Date(h.created_at).toLocaleTimeString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
