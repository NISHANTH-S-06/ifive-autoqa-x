import React, { useEffect, useState } from 'react';
import { PageHeader } from '../components/layout/PageHeader';
import { StatCard } from '../components/ui/StatCard';
import { StatusBadge } from '../components/ui/StatusBadge';
import { Button } from '../components/ui/Button';
import { Award, TrendingUp, ShieldAlert, Zap, RefreshCw } from 'lucide-react';
import { apiGet } from '../services/api';
import { toast } from '../stores/toastStore';

interface PredV2Data {
  project_id: number;
  sprint_quality_score: number;
  release_quality_score: number;
  predicted_future_bugs: number;
  unstable_module: string;
  regression_probability: number;
  developer_risk_score: string;
  customer_impact_risk: string;
  confidence_percentage: number;
}

export function PredictionCenterPage() {
  const [data, setData] = useState<PredV2Data | null>(null);
  const [loading, setLoading] = useState(false);

  const fetchForecast = async () => {
    setLoading(true);
    try {
      const res = await apiGet<PredV2Data>('/api/predictive/forecast?project_id=1');
      setData(res);
    } catch (err) {
      toast.error('Failed to load quality prediction forecast');
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
        breadcrumbs={[{ label: 'AI QA Brain' }, { label: 'Prediction Center' }]}
        title="Quality Prediction Engine V2"
        description="Predicts future bugs, module instability, sprint quality, release quality, regression probability, developer risk, and customer impact."
        actions={(
          <Button size="sm" variant="secondary" onClick={() => void fetchForecast()} isLoading={loading} leftIcon={<RefreshCw size={14} />}>
            Re-run Forecast
          </Button>
        )}
      />

      {data && (
        <>
          <div className="grid grid-cols-4">
            <StatCard title="Sprint Quality Score" value={`${data.sprint_quality_score}%`} subtitle="Sprint Forecast" icon={Award} variant="primary" />
            <StatCard title="Release Quality Score" value={`${data.release_quality_score}%`} subtitle="Release Candidate" icon={TrendingUp} variant="success" />
            <StatCard title="Predicted Future Bugs" value={data.predicted_future_bugs} subtitle="Bug Density Forecast" icon={ShieldAlert} variant="warning" />
            <StatCard title="AI Confidence" value={`${data.confidence_percentage}%`} subtitle="Prediction Model Accuracy" icon={Zap} variant="info" />
          </div>

          <div className="card" style={{ padding: '1.25rem' }}>
            <h3 style={{ margin: '0 0 1rem 0' }}>Detailed Predictive Quality Analytics</h3>
            <div className="grid grid-cols-2" style={{ gap: '1rem' }}>
              <div style={{ background: 'var(--bg-muted)', padding: '1rem', borderRadius: '8px' }}>
                <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)' }}>UNSTABLE MODULE WARNING</div>
                <div style={{ fontSize: '1.25rem', fontWeight: 700, marginTop: '0.25rem' }}>{data.unstable_module}</div>
              </div>
              <div style={{ background: 'var(--bg-muted)', padding: '1rem', borderRadius: '8px' }}>
                <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)' }}>REGRESSION PROBABILITY</div>
                <div style={{ fontSize: '1.25rem', fontWeight: 700, marginTop: '0.25rem', color: '#10b981' }}>{Math.round(data.regression_probability * 100)}%</div>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
