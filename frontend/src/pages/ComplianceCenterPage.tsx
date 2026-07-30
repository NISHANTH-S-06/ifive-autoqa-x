import React, { useEffect, useState } from 'react';
import {
  fetchComplianceStandards, fetchComplianceReports, generateComplianceReport, fetchComplianceDashboard,
} from '../services/phase13Service';

const card = { background: '#1e293b', borderRadius: '12px', border: '1px solid #334155', padding: '20px' };
const badge = (color: string) => ({ padding: '3px 10px', borderRadius: '20px', fontSize: '11px', fontWeight: 700 as const, background: `${color}22`, color, border: `1px solid ${color}44` });
const STD_COLORS: Record<string, string> = { ISO_27001: '#38bdf8', SOC2: '#10b981', GDPR: '#a78bfa', HIPAA: '#f59e0b', PCI_DSS: '#ef4444' };
const STD_ICONS: Record<string, string> = { ISO_27001: '🔒', SOC2: '✅', GDPR: '🇪🇺', HIPAA: '🏥', PCI_DSS: '💳' };

export const ComplianceCenterPage: React.FC = () => {
  const [standards, setStandards] = useState<any[]>([]);
  const [reports, setReports] = useState<any[]>([]);
  const [dashboard, setDashboard] = useState<any>({});
  const [generating, setGenerating] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    try {
      const [s, r, d] = await Promise.all([fetchComplianceStandards(), fetchComplianceReports(), fetchComplianceDashboard()]);
      setStandards(s as any[]); setReports(r as any[]); setDashboard(d);
    } catch (e) { console.error(e); } finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const handleGenerate = async (standard: string) => {
    setGenerating(standard);
    try { await generateComplianceReport({ compliance_standard: standard, scope: 'PLATFORM' }); load(); } catch (err: any) { alert(err.message); } finally { setGenerating(null); }
  };

  const ScoreGauge = ({ score, color }: { score: number; color: string }) => (
    <div style={{ position: 'relative', width: '80px', height: '80px' }}>
      <svg viewBox="0 0 36 36" style={{ width: '80px', height: '80px', transform: 'rotate(-90deg)' }}>
        <circle cx="18" cy="18" r="15.9" fill="none" stroke="#0f172a" strokeWidth="3.8" />
        <circle cx="18" cy="18" r="15.9" fill="none" stroke={color} strokeWidth="3.8"
          strokeDasharray={`${score} ${100 - score}`} strokeLinecap="round" />
      </svg>
      <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 800, fontSize: '14px', color }}>{score.toFixed(0)}%</div>
    </div>
  );

  return (
    <div style={{ padding: '24px', maxWidth: '1400px', margin: '0 auto', color: '#f8fafc' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '28px' }}>
        <div>
          <h1 style={{ fontSize: '28px', fontWeight: 800, margin: 0, background: 'linear-gradient(90deg, #10b981, #38bdf8)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            Compliance Center
          </h1>
          <p style={{ margin: '4px 0 0', color: '#64748b', fontSize: '14px' }}>ISO 27001 · SOC2 · GDPR · HIPAA · PCI DSS automated audit reports</p>
        </div>
        <div style={{ textAlign: 'right' }}>
          <div style={{ fontSize: '32px', fontWeight: 800, color: '#10b981' }}>{(dashboard.overall_compliance_score ?? 0).toFixed(1)}%</div>
          <div style={{ fontSize: '12px', color: '#64748b' }}>Overall Compliance</div>
        </div>
      </div>

      {/* Dashboard Summary */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '14px', marginBottom: '24px' }}>
        {[
          { label: 'Total Reports', value: dashboard.total_reports ?? 0, color: '#38bdf8' },
          { label: 'Fully Compliant', value: dashboard.fully_compliant_standards ?? 0, color: '#10b981' },
          { label: 'Standards Covered', value: dashboard.by_standard ? Object.keys(dashboard.by_standard).length : 0, color: '#a78bfa' },
          { label: 'Overall Score', value: `${(dashboard.overall_compliance_score ?? 0).toFixed(1)}%`, color: '#34d399' },
        ].map(k => (
          <div key={k.label} style={{ ...card, textAlign: 'center' }}>
            <div style={{ fontSize: '11px', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '6px' }}>{k.label}</div>
            <div style={{ fontSize: '28px', fontWeight: 800, color: k.color }}>{k.value}</div>
          </div>
        ))}
      </div>

      {/* Standards Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '18px', marginBottom: '24px' }}>
        {standards.map((std: any) => {
          const score = dashboard.by_standard?.[std.standard] ?? 0;
          const color = STD_COLORS[std.standard] || '#64748b';
          return (
            <div key={std.standard} style={{ ...card, borderLeft: `4px solid ${color}` }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '14px' }}>
                <div>
                  <div style={{ fontSize: '20px', marginBottom: '4px' }}>{STD_ICONS[std.standard] || '📋'}</div>
                  <div style={{ fontWeight: 700, color, fontSize: '14px' }}>{std.standard.replace(/_/g, ' ')}</div>
                  <div style={{ fontSize: '11px', color: '#64748b', marginTop: '2px' }}>{std.full_name}</div>
                </div>
                {score > 0 && <ScoreGauge score={score} color={color} />}
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px', marginBottom: '14px' }}>
                {(std.categories || []).map((cat: string) => (
                  <span key={cat} style={{ fontSize: '10px', background: '#0f172a', color: '#94a3b8', borderRadius: '4px', padding: '2px 6px' }}>{cat}</span>
                ))}
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '12px', color: '#64748b' }}>{std.control_count} controls</span>
                <button onClick={() => handleGenerate(std.standard)} disabled={generating === std.standard}
                  style={{ padding: '7px 14px', borderRadius: '6px', background: generating === std.standard ? '#334155' : `${color}22`, color: generating === std.standard ? '#64748b' : color, fontWeight: 700, fontSize: '12px', cursor: generating ? 'not-allowed' : 'pointer', border: `1px solid ${color}44` }}>
                  {generating === std.standard ? '⏳ Generating...' : '📊 Generate Report'}
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Reports Table */}
      <div style={card}>
        <h3 style={{ margin: '0 0 16px', fontSize: '16px', fontWeight: 700, color: '#a78bfa' }}>Generated Reports ({reports.length})</h3>
        {reports.length === 0 ? (
          <div style={{ color: '#64748b', textAlign: 'center', padding: '24px' }}>No reports yet. Generate a report for any compliance standard above.</div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid #334155', color: '#64748b' }}>
                  <th style={{ padding: '8px 12px', textAlign: 'left' }}>Standard</th>
                  <th style={{ padding: '8px 12px', textAlign: 'left' }}>Scope</th>
                  <th style={{ padding: '8px 12px', textAlign: 'left' }}>Status</th>
                  <th style={{ padding: '8px 12px', textAlign: 'right' }}>Score</th>
                  <th style={{ padding: '8px 12px', textAlign: 'right' }}>Findings</th>
                  <th style={{ padding: '8px 12px', textAlign: 'right' }}>Generated</th>
                </tr>
              </thead>
              <tbody>
                {reports.map((r: any) => (
                  <tr key={r.id} style={{ borderBottom: '1px solid #1e293b' }}>
                    <td style={{ padding: '8px 12px' }}>
                      <span style={{ color: STD_COLORS[r.compliance_standard] || '#fff', fontWeight: 700 }}>
                        {STD_ICONS[r.compliance_standard]} {r.compliance_standard}
                      </span>
                    </td>
                    <td style={{ padding: '8px 12px', color: '#94a3b8' }}>{r.report_scope}</td>
                    <td style={{ padding: '8px 12px' }}><span style={badge('#10b981')}>{r.report_status}</span></td>
                    <td style={{ padding: '8px 12px', textAlign: 'right', fontWeight: 800, color: r.compliance_score >= 90 ? '#10b981' : r.compliance_score >= 80 ? '#f59e0b' : '#ef4444' }}>{r.compliance_score.toFixed(1)}%</td>
                    <td style={{ padding: '8px 12px', textAlign: 'right', color: '#94a3b8' }}>{r.findings_count}</td>
                    <td style={{ padding: '8px 12px', textAlign: 'right', color: '#64748b', fontSize: '12px' }}>{r.generated_at ? new Date(r.generated_at).toLocaleDateString() : '—'}</td>
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
