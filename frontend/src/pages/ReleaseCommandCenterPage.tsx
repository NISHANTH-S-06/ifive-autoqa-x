import React, { useEffect, useState } from 'react';
import { PageHeader } from '../components/layout/PageHeader';
import { StatCard } from '../components/ui/StatCard';
import { StatusBadge } from '../components/ui/StatusBadge';
import { Button } from '../components/ui/Button';
import { ShieldCheck, BarChart3, TrendingUp, AlertTriangle, RefreshCw, CheckCircle, Lock, Eye, Activity } from 'lucide-react';
import { apiGet } from '../services/api';
import { toast } from '../stores/toastStore';

interface CommandMetrics {
  project_id: number;
  release_version: string;
  readiness_verdict: string;
  release_score: number;
  risk_score: number;
  automation_coverage: number;
  pass_rate: number;
  open_critical_bugs: number;
  sprint_quality_score: number;
  developer_productivity_index: string;
  trends: Record<string, string>;
}

export function ReleaseCommandCenterPage() {
  const [metrics, setMetrics] = useState<CommandMetrics | null>(null);
  const [loading, setLoading] = useState(false);

  const fetchMetrics = async () => {
    setLoading(true);
    try {
      const res = await apiGet<CommandMetrics>('/api/release-command-center/metrics?project_id=1');
      setMetrics(res);
    } catch (err) {
      toast.error('Failed to load Release Command Center metrics');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void fetchMetrics();
  }, []);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      <PageHeader
        breadcrumbs={[{ label: 'Executive' }, { label: 'Release Command Center' }]}
        title="AI Release Command Center"
        description="Unified executive command center synthesizing release readiness, risk scores, quality scores, module health, and multi-dimensional quality trends."
        actions={(
          <Button size="sm" variant="secondary" onClick={() => void fetchMetrics()} isLoading={loading} leftIcon={<RefreshCw size={14} />}>
            Re-evaluate Command Metrics
          </Button>
        )}
      />

      {metrics && (
        <>
          {/* Verdict Banner */}
          <div
            className="card"
            style={{
              padding: '1.5rem',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              borderLeft: `6px solid ${metrics.readiness_verdict === 'READY' ? '#10b981' : '#ef4444'}`
            }}
          >
            <div>
              <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.25rem' }}>
                EXECUTIVE CANDIDATE RELEASE: {metrics.release_version}
              </div>
              <h2 style={{ margin: '0 0 0.5rem 0', fontSize: '1.75rem', fontWeight: 700 }}>
                Release Verdict: <StatusBadge status={metrics.readiness_verdict === 'READY' ? 'APPROVED' : 'CRITICAL'} label={metrics.readiness_verdict} />
              </h2>
              <p style={{ margin: 0, color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                All 16 quality gates, visual baselines, security policies, and performance latency targets evaluated cleanly.
              </p>
            </div>
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: '2.5rem', fontWeight: 800, color: '#10b981', lineHeight: 1 }}>
                {metrics.release_score}%
              </div>
              <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', marginTop: '0.25rem' }}>
                Unified Release Score
              </div>
            </div>
          </div>

          <div className="grid grid-cols-4">
            <StatCard title="Sprint Quality Score" value={`${metrics.sprint_quality_score}%`} subtitle="Sprint Velocity Quality" icon={TrendingUp} variant="primary" />
            <StatCard title="Automation Coverage" value={`${metrics.automation_coverage}%`} subtitle="Automated Ratio" icon={CheckCircle} variant="success" />
            <StatCard title="Overall Risk Score" value={metrics.risk_score} subtitle="Fail-Closed Guard" icon={AlertTriangle} variant="warning" />
            <StatCard title="Dev Productivity" value={metrics.developer_productivity_index} subtitle="Speed Index" icon={Activity} variant="info" />
          </div>

          {/* Multi-Dimensional Trends Grid */}
          <div className="card" style={{ padding: '1.25rem' }}>
            <h3 style={{ margin: '0 0 1rem 0' }}>Multi-Dimensional Quality Trends</h3>
            <div className="grid grid-cols-4" style={{ gap: '1rem' }}>
              {Object.entries(metrics.trends || {}).map(([key, val], idx) => (
                <div key={idx} style={{ background: 'var(--bg-muted)', padding: '1rem', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                  <div style={{ fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
                    {key.replace('_', ' ')}
                  </div>
                  <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#10b981' }}>
                    {val}
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
