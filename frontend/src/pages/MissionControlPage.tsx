import React, { useEffect, useState } from 'react';
import { fetchMissionControlDashboard, validateReleaseAutonomously, triggerSelfEvolving } from '../services/phase15Service';

const card = { background: '#1e293b', borderRadius: '12px', border: '1px solid #334155', padding: '20px' };

export const MissionControlPage: React.FC = () => {
  const [mc, setMc] = useState<any | null>(null);
  const [valResult, setValResult] = useState<any | null>(null);
  const [evolveResult, setEvolveResult] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    try {
      const data = await fetchMissionControlDashboard();
      setMc(data);
    } catch (e) { console.error(e); } finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const handleValidate = async () => {
    try {
      const res = await validateReleaseAutonomously('v5.0.0-RC1');
      setValResult(res);
    } catch (e) { console.error(e); }
  };

  const handleEvolve = async () => {
    try {
      const res = await triggerSelfEvolving();
      setEvolveResult(res);
    } catch (e) { console.error(e); }
  };

  if (!mc) return <div style={{ padding: '24px', color: '#fff' }}>Loading Mission Control...</div>;

  return (
    <div style={{ padding: '24px', maxWidth: '1600px', margin: '0 auto', color: '#f8fafc' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '28px' }}>
        <div>
          <h1 style={{ fontSize: '28px', fontWeight: 900, margin: 0, background: 'linear-gradient(90deg, #38bdf8, #818cf8, #a78bfa)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            🛸 Executive Mission Control
          </h1>
          <p style={{ margin: '4px 0 0', color: '#64748b', fontSize: '14px' }}>Single Executive Control Screen — Global Health · Risk · Quality · Coverage · Incidents · Cloud Costs · Self-Evolving AI</p>
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button onClick={handleValidate} style={{ padding: '10px 18px', borderRadius: '8px', border: 'none', background: 'linear-gradient(135deg, #22c55e, #16a34a)', color: '#fff', fontWeight: 700, cursor: 'pointer' }}>
            🛡️ Run 10-Gate Pre-Deploy Verification
          </button>
          <button onClick={handleEvolve} style={{ padding: '10px 18px', borderRadius: '8px', border: 'none', background: 'linear-gradient(135deg, #38bdf8, #0284c7)', color: '#fff', fontWeight: 700, cursor: 'pointer' }}>
            🧬 Trigger Self-Evolving AI
          </button>
          <button onClick={load} style={{ padding: '10px 16px', borderRadius: '8px', border: '1px solid #334155', background: '#1e293b', color: '#94a3b8', cursor: 'pointer' }}>↻</button>
        </div>
      </div>

      {valResult && (
        <div style={{ ...card, marginBottom: '20px', background: '#22c55e11', border: '1px solid #22c55e44' }}>
          <div style={{ fontSize: '16px', fontWeight: 800, color: '#22c55e', marginBottom: '4px' }}>
            ✅ Release {valResult.release_version} Status: {valResult.overall_status} ({valResult.gates_passed}/{valResult.total_gates} Quality Gates Passed)
          </div>
        </div>
      )}

      {evolveResult && (
        <div style={{ ...card, marginBottom: '20px', background: '#38bdf811', border: '1px solid #38bdf844' }}>
          <div style={{ fontSize: '16px', fontWeight: 800, color: '#38bdf8', marginBottom: '4px' }}>
            🧬 Self-Evolving Learning Cycle Completed ({evolveResult.learning_cycle})
          </div>
          <div style={{ fontSize: '13px', color: '#94a3b8' }}>
            Analyzed {evolveResult.executions_analyzed} executions & {evolveResult.healing_events_learned} healing events. Model upgraded to {evolveResult.model_version}.
          </div>
        </div>
      )}

      {/* KPI Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '20px', marginBottom: '24px' }}>
        <div style={{ ...card, borderTop: '4px solid #10b981' }}>
          <div style={{ fontSize: '11px', color: '#64748b', textTransform: 'uppercase' }}>Global Health</div>
          <div style={{ fontSize: '32px', fontWeight: 900, color: '#10b981', marginTop: '4px' }}>{mc.global_health_pct}%</div>
        </div>
        <div style={{ ...card, borderTop: '4px solid #38bdf8' }}>
          <div style={{ fontSize: '11px', color: '#64748b', textTransform: 'uppercase' }}>Overall Quality Score</div>
          <div style={{ fontSize: '32px', fontWeight: 900, color: '#38bdf8', marginTop: '4px' }}>{mc.overall_quality_score}</div>
        </div>
        <div style={{ ...card, borderTop: '4px solid #a78bfa' }}>
          <div style={{ fontSize: '11px', color: '#64748b', textTransform: 'uppercase' }}>Overall Coverage</div>
          <div style={{ fontSize: '32px', fontWeight: 900, color: '#a78bfa', marginTop: '4px' }}>{mc.overall_coverage_pct}%</div>
        </div>
        <div style={{ ...card, borderTop: '4px solid #f59e0b' }}>
          <div style={{ fontSize: '11px', color: '#64748b', textTransform: 'uppercase' }}>Overall Risk Score</div>
          <div style={{ fontSize: '32px', fontWeight: 900, color: '#f59e0b', marginTop: '4px' }}>{mc.overall_risk_score}</div>
        </div>
      </div>

      {/* Detail Operations */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
        <div style={card}>
          <h3 style={{ margin: '0 0 16px', fontSize: '16px', fontWeight: 700, color: '#38bdf8' }}>Cloud & Worker Operations</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', fontSize: '13px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}><span style={{ color: '#94a3b8' }}>Active Execution Workers:</span><strong style={{ color: '#fff' }}>{mc.active_workers} Workers</strong></div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}><span style={{ color: '#94a3b8' }}>Browser Farm Utilization:</span><strong style={{ color: '#10b981' }}>{mc.browser_farm_utilization_pct}%</strong></div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}><span style={{ color: '#94a3b8' }}>Cloud Infrastructure:</span><strong style={{ color: '#38bdf8' }}>{mc.cloud_status}</strong></div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}><span style={{ color: '#94a3b8' }}>Monthly Cloud Spend:</span><strong style={{ color: '#f59e0b' }}>${mc.monthly_cost_usd} USD</strong></div>
          </div>
        </div>

        <div style={card}>
          <h3 style={{ margin: '0 0 16px', fontSize: '16px', fontWeight: 700, color: '#a78bfa' }}>Governance & Compliance</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', fontSize: '13px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}><span style={{ color: '#94a3b8' }}>AI Confidence Rating:</span><strong style={{ color: '#a78bfa' }}>{mc.ai_confidence_pct}%</strong></div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}><span style={{ color: '#94a3b8' }}>Security Rating:</span><strong style={{ color: '#10b981' }}>{mc.security_score}%</strong></div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}><span style={{ color: '#94a3b8' }}>Compliance Score:</span><strong style={{ color: '#10b981' }}>{mc.compliance_score}%</strong></div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}><span style={{ color: '#94a3b8' }}>Executive Recommendation:</span><strong style={{ color: '#22c55e' }}>{mc.executive_recommendation}</strong></div>
          </div>
        </div>
      </div>
    </div>
  );
};
