import React, { useEffect, useState } from 'react';
import { fetchOptimizerLogs, triggerOptimization, fetchOptimizerRecommendations } from '../services/phase13Service';

const card = { background: '#1e293b', borderRadius: '12px', border: '1px solid #334155', padding: '20px' };
const STATUS_COLORS: Record<string, string> = { APPLIED: '#10b981', PENDING: '#f59e0b', REVERTED: '#ef4444', SKIPPED: '#64748b' };
const TARGET_ICONS: Record<string, string> = { WORKER_COUNT: '⚙️', TIMEOUT: '⏱️', RETRY_STRATEGY: '🔄', LOCATOR_STRATEGY: '🎯', PARALLEL_FACTOR: '⚡', EXECUTION_PLAN: '📋', BROWSER_ALLOCATION: '🌐', INFRA_USAGE: '🏗️' };

export const WorkerManagementPage: React.FC = () => {
  const [logs, setLogs] = useState<any[]>([]);
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [optimizing, setOptimizing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [lastOptimized, setLastOptimized] = useState<string | null>(null);

  const load = async () => {
    setLoading(true);
    try {
      const [l, r] = await Promise.all([fetchOptimizerLogs(), fetchOptimizerRecommendations()]);
      setLogs(l as any[]); setRecommendations(r as any[]);
    } catch (e) { console.error(e); } finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const handleOptimize = async () => {
    setOptimizing(true);
    try {
      const result: any = await triggerOptimization();
      setLastOptimized(`Applied ${result.optimizations_applied} optimizations`);
      load();
    } catch (err: any) { alert(err.message); } finally { setOptimizing(false); }
  };

  return (
    <div style={{ padding: '24px', maxWidth: '1400px', margin: '0 auto', color: '#f8fafc' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '28px' }}>
        <div>
          <h1 style={{ fontSize: '28px', fontWeight: 800, margin: 0, background: 'linear-gradient(90deg, #f472b6, #a78bfa)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            AI Execution Optimizer
          </h1>
          <p style={{ margin: '4px 0 0', color: '#64748b', fontSize: '14px' }}>
            Autonomous AI optimization — workers · timeouts · retry · locators · parallel · browser allocation
          </p>
        </div>
        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          {lastOptimized && <span style={{ fontSize: '12px', color: '#10b981', background: '#10b98122', padding: '6px 12px', borderRadius: '6px', border: '1px solid #10b98144' }}>✅ {lastOptimized}</span>}
          <button onClick={handleOptimize} disabled={optimizing} style={{ padding: '10px 22px', borderRadius: '8px', border: 'none', background: optimizing ? '#334155' : 'linear-gradient(135deg, #f472b6, #a78bfa)', color: optimizing ? '#64748b' : '#fff', fontWeight: 700, cursor: optimizing ? 'not-allowed' : 'pointer' }}>
            {optimizing ? '🤖 Optimizing...' : '🤖 Run AI Optimization'}
          </button>
          <button onClick={load} style={{ padding: '10px 16px', borderRadius: '8px', border: '1px solid #334155', background: '#1e293b', color: '#94a3b8', cursor: 'pointer' }}>↻</button>
        </div>
      </div>

      {/* Recommendations */}
      {recommendations.length > 0 && (
        <div style={{ marginBottom: '24px' }}>
          <h2 style={{ fontSize: '18px', fontWeight: 700, marginBottom: '14px', color: '#f59e0b' }}>💡 AI Recommendations ({recommendations.length})</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '14px' }}>
            {recommendations.map((rec: any, i: number) => (
              <div key={i} style={{ ...card, border: '1px solid #f59e0b33', background: '#1a1200' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '10px' }}>
                  <span style={{ fontSize: '20px' }}>{TARGET_ICONS[rec.target] || '🔧'}</span>
                  <span style={{ fontWeight: 700, color: '#fbbf24' }}>{rec.target.replace(/_/g, ' ')}</span>
                  <span style={{ marginLeft: 'auto', fontSize: '12px', color: '#10b981', fontWeight: 700 }}>
                    {rec.impact_estimate_pct > 0 ? `+${rec.impact_estimate_pct.toFixed(1)}%` : `${rec.impact_estimate_pct.toFixed(1)}%`}
                  </span>
                </div>
                <div style={{ fontSize: '12px', color: '#94a3b8', marginBottom: '10px', lineHeight: '1.5' }}>{rec.reasoning}</div>
                <div style={{ display: 'flex', gap: '8px', fontSize: '11px' }}>
                  <div style={{ background: '#0f172a', borderRadius: '6px', padding: '6px 10px', flex: 1 }}>
                    <div style={{ color: '#64748b', marginBottom: '2px' }}>Current</div>
                    <div style={{ color: '#ef4444', fontFamily: 'monospace', fontWeight: 700 }}>{JSON.stringify(rec.current)}</div>
                  </div>
                  <div style={{ color: '#64748b', display: 'flex', alignItems: 'center' }}>→</div>
                  <div style={{ background: '#0f172a', borderRadius: '6px', padding: '6px 10px', flex: 1 }}>
                    <div style={{ color: '#64748b', marginBottom: '2px' }}>Recommended</div>
                    <div style={{ color: '#10b981', fontFamily: 'monospace', fontWeight: 700 }}>{JSON.stringify(rec.recommended)}</div>
                  </div>
                </div>
                <div style={{ marginTop: '8px', fontSize: '11px', color: '#64748b' }}>
                  Confidence: <span style={{ color: '#a78bfa', fontWeight: 700 }}>{(rec.confidence * 100).toFixed(0)}%</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Optimization Log */}
      <div style={card}>
        <h2 style={{ margin: '0 0 16px', fontSize: '16px', fontWeight: 700, color: '#a78bfa' }}>Optimization History ({logs.length})</h2>
        {logs.length === 0 ? (
          <div style={{ color: '#64748b', textAlign: 'center', padding: '32px' }}>
            No optimizations applied yet. Click "Run AI Optimization" to start autonomous tuning.
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid #334155', color: '#64748b' }}>
                  <th style={{ padding: '8px 12px', textAlign: 'left' }}>Target</th>
                  <th style={{ padding: '8px 12px', textAlign: 'left' }}>Old Value</th>
                  <th style={{ padding: '8px 12px', textAlign: 'left' }}>New Value</th>
                  <th style={{ padding: '8px 12px', textAlign: 'left' }}>Reasoning</th>
                  <th style={{ padding: '8px 12px', textAlign: 'right' }}>Confidence</th>
                  <th style={{ padding: '8px 12px', textAlign: 'right' }}>Impact</th>
                  <th style={{ padding: '8px 12px', textAlign: 'left' }}>Status</th>
                  <th style={{ padding: '8px 12px', textAlign: 'right' }}>Applied</th>
                </tr>
              </thead>
              <tbody>
                {logs.map((l: any) => (
                  <tr key={l.id} style={{ borderBottom: '1px solid #1e293b' }}>
                    <td style={{ padding: '8px 12px', fontWeight: 700 }}>
                      {TARGET_ICONS[l.optimization_target] || '🔧'} {l.optimization_target}
                    </td>
                    <td style={{ padding: '8px 12px', fontFamily: 'monospace', fontSize: '11px', color: '#ef4444' }}>{JSON.stringify(l.old_value)}</td>
                    <td style={{ padding: '8px 12px', fontFamily: 'monospace', fontSize: '11px', color: '#10b981' }}>{JSON.stringify(l.new_value)}</td>
                    <td style={{ padding: '8px 12px', color: '#94a3b8', fontSize: '12px', maxWidth: '200px' }}>{l.reasoning}</td>
                    <td style={{ padding: '8px 12px', textAlign: 'right', color: '#a78bfa', fontWeight: 700 }}>{(l.confidence_score * 100).toFixed(0)}%</td>
                    <td style={{ padding: '8px 12px', textAlign: 'right', color: l.impact_delta >= 0 ? '#10b981' : '#ef4444', fontWeight: 700 }}>
                      {l.impact_delta >= 0 ? '+' : ''}{l.impact_delta.toFixed(1)}%
                    </td>
                    <td style={{ padding: '8px 12px' }}>
                      <span style={{ padding: '3px 8px', borderRadius: '12px', fontSize: '10px', fontWeight: 700, background: `${STATUS_COLORS[l.optimization_status] || '#64748b'}22`, color: STATUS_COLORS[l.optimization_status] || '#64748b', border: `1px solid ${STATUS_COLORS[l.optimization_status] || '#64748b'}44` }}>
                        {l.optimization_status}
                      </span>
                    </td>
                    <td style={{ padding: '8px 12px', textAlign: 'right', color: '#64748b', fontSize: '11px' }}>
                      {new Date(l.created_at).toLocaleString()}
                    </td>
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
