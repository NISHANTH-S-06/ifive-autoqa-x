import React, { useEffect, useState } from 'react';
import { PageHeader } from '../components/layout/PageHeader';
import { StatCard } from '../components/ui/StatCard';
import { StatusBadge } from '../components/ui/StatusBadge';
import { Button } from '../components/ui/Button';
import { BarChart3, TrendingUp, ShieldAlert, Cpu, Award, Zap, Activity, RefreshCw } from 'lucide-react';
import { apiGet } from '../services/api';
import { toast } from '../stores/toastStore';

interface ForecastData {
  project_id: number;
  release_quality_forecast_score: number;
  failure_probability: number;
  unstable_modules: string[];
  flaky_tests_count: number;
  flaky_tests: string[];
  developer_quality_trend: string;
  module_stability_trend: string;
  predicted_bug_density: string;
  confidence_trend: string;
}

export function ExecutiveIntelligenceDashboardPage() {
  const [forecast, setForecast] = useState<ForecastData | null>(null);
  const [loading, setLoading] = useState(false);

  const fetchForecast = async () => {
    setLoading(true);
    try {
      const data = await apiGet<ForecastData>('/api/predictive/forecast?project_id=1');
      setForecast(data);
    } catch (err) {
      toast.error('Failed to load predictive forecast');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void fetchForecast();
  }, []);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      <PageHeader
        breadcrumbs={[{ label: 'Executive' }, { label: 'Executive Intelligence Dashboard' }]}
        title="Executive Intelligence Dashboard"
        description="High-level executive analytics covering AI thinking metrics, quality heatmaps, predictive failure forecasts, and release trends."
        actions={(
          <Button size="sm" variant="secondary" onClick={() => void fetchForecast()} isLoading={loading} leftIcon={<RefreshCw size={14} />}>
            Refresh Forecast
          </Button>
        )}
      />

      {forecast && (
        <>
          <div className="grid grid-cols-4">
            <StatCard title="Predicted Release Quality" value={`${forecast.release_quality_forecast_score}%`} subtitle="AI Release Forecast" icon={Award} variant="primary" />
            <StatCard title="Failure Probability" value={`${Math.round(forecast.failure_probability * 100)}%`} subtitle="Risk Expectation" icon={ShieldAlert} variant="success" />
            <StatCard title="Flaky Tests Detected" value={forecast.flaky_tests_count} subtitle="Suppressed & Monitored" icon={Zap} variant="warning" />
            <StatCard title="Developer Quality Trend" value="+4.2%" subtitle={forecast.developer_quality_trend} icon={TrendingUp} variant="info" />
          </div>

          {/* Module Stability & Bug Density Summary */}
          <div className="grid grid-cols-2" style={{ gap: '1.25rem' }}>
            <div className="card" style={{ padding: '1.25rem' }}>
              <h3 style={{ margin: '0 0 1rem 0', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Activity size={18} color="var(--color-primary)" /> Unstable Modules Warning
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {forecast.unstable_modules.map((mod, idx) => (
                  <div key={idx} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'var(--bg-muted)', padding: '0.75rem 1rem', borderRadius: '8px' }}>
                    <span style={{ fontWeight: 600 }}>{mod}</span>
                    <StatusBadge status="WARNING" label="High Maintenance Risk" size="sm" />
                  </div>
                ))}
              </div>
            </div>

            <div className="card" style={{ padding: '1.25rem' }}>
              <h3 style={{ margin: '0 0 1rem 0', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <BarChart3 size={18} color="var(--color-primary)" /> Predictive Bug Density & Stability
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                <div style={{ background: 'var(--bg-muted)', padding: '0.75rem 1rem', borderRadius: '8px' }}>
                  <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)' }}>PREDICTED BUG DENSITY</div>
                  <div style={{ fontSize: '1.25rem', fontWeight: 700, marginTop: '0.2rem' }}>{forecast.predicted_bug_density}</div>
                </div>
                <div style={{ background: 'var(--bg-muted)', padding: '0.75rem 1rem', borderRadius: '8px' }}>
                  <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)' }}>MODULE STABILITY TREND</div>
                  <div style={{ fontSize: '1.25rem', fontWeight: 700, marginTop: '0.2rem', color: '#10b981' }}>{forecast.module_stability_trend}</div>
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
