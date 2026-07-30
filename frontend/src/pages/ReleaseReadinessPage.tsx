import React, { useEffect, useState } from 'react';
import { PageHeader } from '../components/layout/PageHeader';
import { StatCard } from '../components/ui/StatCard';
import { StatusBadge } from '../components/ui/StatusBadge';
import { Button } from '../components/ui/Button';
import { ShieldAlert, CheckCircle, XCircle, AlertTriangle, Activity, BarChart3, RefreshCw } from 'lucide-react';
import { apiGet } from '../services/api';
import { toast } from '../stores/toastStore';

interface ReleaseEval {
  id: number;
  release_version: string;
  release_score: number;
  readiness_status: 'READY' | 'NOT_READY' | 'BLOCKED';
  automation_coverage: number;
  pass_rate: number;
  open_critical_bugs: number;
  risk_score: number;
  breakdown: Record<string, number>;
}

export function ReleaseReadinessPage() {
  const [evalData, setEvalData] = useState<ReleaseEval | null>(null);
  const [loading, setLoading] = useState(false);

  const fetchEvaluation = async () => {
    setLoading(true);
    try {
      const data = await apiGet<ReleaseEval>('/api/release-readiness/eval?project_id=1&release_version=v1.0.0');
      setEvalData(data);
    } catch (err) {
      toast.error('Failed to load release readiness evaluation');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void fetchEvaluation();
  }, []);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      <PageHeader
        breadcrumbs={[{ label: 'Release Management' }, { label: 'Release Readiness' }]}
        title="Release Readiness & Quality Forecast"
        description="Autonomous evaluation of automation coverage, pass rates, security, visual diffs, and risk metrics producing a fail-closed verdict."
        actions={(
          <Button size="sm" variant="secondary" onClick={() => void fetchEvaluation()} isLoading={loading} leftIcon={<RefreshCw size={14} />}>
            Re-evaluate Release
          </Button>
        )}
      />

      {evalData && (
        <>
          {/* Main Verdict Card */}
          <div
            className="card"
            style={{
              padding: '1.5rem',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              borderLeft: `6px solid ${evalData.readiness_status === 'READY' ? '#10b981' : evalData.readiness_status === 'BLOCKED' ? '#ef4444' : '#f59e0b'}`
            }}
          >
            <div>
              <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.25rem' }}>
                RELEASE CANDIDATE: {evalData.release_version}
              </div>
              <h2 style={{ margin: '0 0 0.5rem 0', fontSize: '1.75rem', fontWeight: 700 }}>
                Release Verdict: <StatusBadge status={evalData.readiness_status === 'READY' ? 'APPROVED' : evalData.readiness_status === 'BLOCKED' ? 'CRITICAL' : 'WARNING'} label={evalData.readiness_status} />
              </h2>
              <p style={{ margin: 0, color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                {evalData.readiness_status === 'READY'
                  ? 'All automated quality gates passed cleanly. Code candidate is approved for production deployment.'
                  : 'Critical bugs or open risk factors detected. Deployment is currently blocked by release quality policy.'}
              </p>
            </div>
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: '2.5rem', fontWeight: 800, color: evalData.release_score > 80 ? '#10b981' : '#ef4444', lineHeight: 1 }}>
                {evalData.release_score}%
              </div>
              <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', marginTop: '0.25rem' }}>
                Overall Release Score
              </div>
            </div>
          </div>

          <div className="grid grid-cols-4">
            <StatCard title="Automation Coverage" value={`${evalData.automation_coverage}%`} subtitle="Automated Test Ratio" icon={Activity} variant="primary" />
            <StatCard title="Test Pass Rate" value={`${evalData.pass_rate}%`} subtitle="Suite Execution Rate" icon={CheckCircle} variant="success" />
            <StatCard title="Open Critical Defects" value={evalData.open_critical_bugs} subtitle="Zero Tolerance Policy" icon={ShieldAlert} variant="danger" />
            <StatCard title="Overall Risk Score" value={evalData.risk_score} subtitle="Multi-Factor Risk" icon={AlertTriangle} variant="warning" />
          </div>

          {/* Risk Breakdown Heatmap */}
          <div className="card" style={{ padding: '1.25rem' }}>
            <h3 style={{ margin: '0 0 1rem 0', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <BarChart3 size={18} color="var(--color-primary)" /> Multi-Dimensional Risk Heatmap
            </h3>

            <div className="grid grid-cols-4" style={{ gap: '1rem' }}>
              {Object.entries(evalData.breakdown || {}).map(([riskKey, riskVal], idx) => (
                <div key={idx} style={{ background: 'var(--bg-muted)', padding: '1rem', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                  <div style={{ fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
                    {riskKey.replace('_', ' ')}
                  </div>
                  <div style={{ fontSize: '1.5rem', fontWeight: 800, color: Number(riskVal) > 30 ? '#ef4444' : '#10b981' }}>
                    {riskVal}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
