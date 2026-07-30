import React, { useEffect, useState } from 'react';
import { PageHeader } from '../components/layout/PageHeader';
import { StatCard } from '../components/ui/StatCard';
import { StatusBadge } from '../components/ui/StatusBadge';
import { Button } from '../components/ui/Button';
import { Activity, ShieldAlert, CheckCircle, RefreshCw, BarChart } from 'lucide-react';
import { apiGet } from '../services/api';
import { toast } from '../stores/toastStore';

interface PatternData {
  project_id: number;
  pattern_score: number;
  detected_patterns_count: number;
  patterns: Array<{
    pattern_type: string;
    key: string;
    description: string;
    frequency: number;
    severity: string;
  }>;
}

export function PatternRecognitionPage() {
  const [data, setData] = useState<PatternData | null>(null);
  const [loading, setLoading] = useState(false);

  const fetchPatterns = async () => {
    setLoading(true);
    try {
      const res = await apiGet<PatternData>('/api/pattern-recognition/analyze?project_id=1');
      setData(res);
    } catch (err) {
      toast.error('Failed to load pattern recognition data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void fetchPatterns();
  }, []);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      <PageHeader
        breadcrumbs={[{ label: 'AI QA Brain' }, { label: 'Pattern Recognition' }]}
        title="Pattern Recognition Engine"
        description="Identifies repeated failures, developer mistakes, module instability, API failures, UI drift, and calculates a unified Pattern Score."
        actions={(
          <Button size="sm" variant="secondary" onClick={() => void fetchPatterns()} isLoading={loading} leftIcon={<RefreshCw size={14} />}>
            Re-Analyze Patterns
          </Button>
        )}
      />

      {data && (
        <>
          <div className="grid grid-cols-4">
            <StatCard title="Pattern Score" value={`${data.pattern_score}`} subtitle="Stability Health Score" icon={Activity} variant="primary" />
            <StatCard title="Detected Patterns" value={data.detected_patterns_count} subtitle="Recurrent Signatures" icon={ShieldAlert} variant="warning" />
            <StatCard title="Developer Risk" value="LOW" subtitle="Mistake Frequency" icon={CheckCircle} variant="success" />
            <StatCard title="Module Drift" value="0.05%" subtitle="UI Mutation Rate" icon={BarChart} variant="info" />
          </div>

          <div className="card" style={{ padding: '1.25rem' }}>
            <h3 style={{ margin: '0 0 1rem 0' }}>Detected Recurrent Failure Signatures</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {data.patterns.map((p, idx) => (
                <div key={idx} style={{ background: 'var(--bg-muted)', padding: '1rem', borderRadius: '8px', border: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <div style={{ fontWeight: 700, fontSize: '0.9rem', marginBottom: '0.2rem' }}>
                      [{p.pattern_type}] {p.key}
                    </div>
                    <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                      {p.description}
                    </div>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <StatusBadge status={p.severity === 'HIGH' ? 'CRITICAL' : 'WARNING'} label={p.severity} size="sm" />
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.3rem' }}>
                      Frequency: {p.frequency}x
                    </div>
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
