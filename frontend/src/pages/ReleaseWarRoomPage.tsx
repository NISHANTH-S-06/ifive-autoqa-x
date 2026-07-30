import React, { useEffect, useState } from 'react';
import { PageHeader } from '../components/layout/PageHeader';
import { StatCard } from '../components/ui/StatCard';
import { StatusBadge } from '../components/ui/StatusBadge';
import { Button } from '../components/ui/Button';
import { ShieldCheck, AlertTriangle, Activity, Building2, RefreshCw, TrendingUp, CheckCircle2, XCircle } from 'lucide-react';
import { apiGet } from '../services/api';
import { toast } from '../stores/toastStore';

interface WarRoomMetrics {
  total_projects: number;
  total_companies: number;
  running_executions: number;
  overall_risk_score: number;
  overall_coverage_pct: number;
  open_critical_defects: number;
  release_health_score: number;
  deployment_recommendation: string;
  rollback_recommendation: string;
  executive_kpis: Record<string, number | string>;
  project_snapshots: Array<{ project: string; status: string; pass_rate: number; risk: string }>;
}

export function ReleaseWarRoomPage() {
  const [metrics, setMetrics] = useState<WarRoomMetrics | null>(null);
  const [loading, setLoading] = useState(false);

  const fetchMetrics = async () => {
    setLoading(true);
    try {
      const res = await apiGet<WarRoomMetrics>('/api/war-room/metrics');
      setMetrics(res);
    } catch (err) {
      toast.error('Failed to load Release War Room metrics');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void fetchMetrics();
    const interval = setInterval(() => void fetchMetrics(), 30000);
    return () => clearInterval(interval);
  }, []);

  const isGo = metrics?.deployment_recommendation === 'GO';

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      <PageHeader
        breadcrumbs={[{ label: 'Enterprise Executive' }, { label: 'Release War Room' }]}
        title="Enterprise Release War Room"
        description="Real-time single-pane view across all companies, projects, executions, risk, coverage, defects, and deployment recommendation."
        actions={
          <Button size="sm" variant="secondary" onClick={() => void fetchMetrics()} isLoading={loading} leftIcon={<RefreshCw size={14} />}>
            Live Refresh
          </Button>
        }
      />

      {metrics && (
        <>
          {/* Deployment Recommendation Banner */}
          <div
            className="card"
            style={{
              padding: '1.5rem 2rem',
              display: 'flex', justifyContent: 'space-between', alignItems: 'center',
              borderLeft: `6px solid ${isGo ? '#10b981' : '#ef4444'}`,
              background: isGo ? 'rgba(16,185,129,0.06)' : 'rgba(239,68,68,0.06)',
            }}
          >
            <div>
              <div style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-muted)', marginBottom: '0.25rem', textTransform: 'uppercase' }}>
                Enterprise Deployment Recommendation
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                <span style={{ fontSize: '2rem', fontWeight: 800, color: isGo ? '#10b981' : '#ef4444' }}>
                  {metrics.deployment_recommendation}
                </span>
                {isGo ? <CheckCircle2 size={28} color="#10b981" /> : <XCircle size={28} color="#ef4444" />}
              </div>
              <p style={{ margin: '0.5rem 0 0 0', color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                Rollback Status: <strong>{metrics.rollback_recommendation}</strong>
              </p>
            </div>
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: '3rem', fontWeight: 800, color: isGo ? '#10b981' : '#f59e0b', lineHeight: 1 }}>
                {metrics.release_health_score}%
              </div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>Release Health Score</div>
            </div>
          </div>

          <div className="grid grid-cols-4">
            <StatCard title="All Companies" value={metrics.total_companies} subtitle="Connected Tenants" icon={Building2} variant="primary" />
            <StatCard title="Active Projects" value={metrics.total_projects} subtitle="Registered Projects" icon={Activity} variant="info" />
            <StatCard title="Running Executions" value={metrics.running_executions} subtitle="Live Test Runs" icon={TrendingUp} variant="warning" />
            <StatCard title="Critical Defects" value={metrics.open_critical_defects} subtitle="Open & Blocking" icon={AlertTriangle} variant={metrics.open_critical_defects > 0 ? 'danger' : 'success'} />
          </div>

          {/* Executive KPIs */}
          <div className="card" style={{ padding: '1.25rem' }}>
            <h3 style={{ margin: '0 0 1rem 0' }}>Executive QA KPIs</h3>
            <div className="grid grid-cols-3" style={{ gap: '0.75rem' }}>
              {Object.entries(metrics.executive_kpis).map(([key, val]) => (
                <div key={key} style={{ background: 'var(--bg-muted)', padding: '1rem', borderRadius: 8 }}>
                  <div style={{ fontSize: '0.7rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '0.3rem' }}>
                    {key.replace(/_/g, ' ')}
                  </div>
                  <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#10b981' }}>{String(val)}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Project Snapshots */}
          <div className="card" style={{ padding: '1.25rem' }}>
            <h3 style={{ margin: '0 0 1rem 0' }}>Project Release Snapshots</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {metrics.project_snapshots.map((snap, idx) => (
                <div key={idx} style={{ background: 'var(--bg-muted)', padding: '1rem', borderRadius: 8, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <div style={{ fontWeight: 700, fontSize: '0.9rem' }}>{snap.project}</div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Pass Rate: {snap.pass_rate}% · Risk: {snap.risk}</div>
                  </div>
                  <StatusBadge status={snap.status === 'READY' ? 'APPROVED' : 'WARNING'} label={snap.status} />
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
