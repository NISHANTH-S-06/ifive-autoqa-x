import React, { useState } from 'react';
import { PageHeader } from '../components/layout/PageHeader';
import { StatCard } from '../components/ui/StatCard';
import { StatusBadge } from '../components/ui/StatusBadge';
import { Button } from '../components/ui/Button';
import { Zap, Play, Cpu, CheckCircle2, RefreshCw } from 'lucide-react';
import { apiGet, apiPost } from '../services/api';
import { toast } from '../stores/toastStore';

export function OptimizationCenterPage() {
  const [optimizing, setOptimizing] = useState(false);
  const [results, setResults] = useState<any | null>(null);

  const handleRunOptimization = async () => {
    setOptimizing(true);
    try {
      const res = await apiPost<any>('/api/test-evolution/evolve?project_id=1', {});
      setResults(res);
      toast.success('Self-Improving Playwright optimization complete.');
    } catch (err: any) {
      toast.error(err.message || 'Optimization failed');
    } finally {
      setOptimizing(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      <PageHeader
        breadcrumbs={[{ label: 'AI QA Brain' }, { label: 'Optimization Center' }]}
        title="Self-Improving Playwright & Optimization Center"
        description="Autonomous optimization of Playwright locators, timeouts, retry strategies, parallel execution worker allocation, and step deduplication."
        actions={(
          <Button variant="primary" size="sm" onClick={() => void handleRunOptimization()} isLoading={optimizing} leftIcon={<Zap size={14} />}>
            Run Playwright Optimization Pass
          </Button>
        )}
      />

      <div className="grid grid-cols-4">
        <StatCard title="Locator Success Rate" value="99.4%" subtitle="Auto-Healed Accuracy" icon={CheckCircle2} variant="success" />
        <StatCard title="Timeout Tuning Speedup" value="+22.4%" subtitle="Navigation Latency" icon={Zap} variant="primary" />
        <StatCard title="Parallel Worker Allocation" value="4 Workers" subtitle="Dynamic Concurrency" icon={Cpu} variant="info" />
        <StatCard title="Step Deduplication" value="-14.2%" subtitle="Redundant Code Removed" icon={RefreshCw} variant="warning" />
      </div>

      {results && (
        <div className="card" style={{ padding: '1.25rem' }}>
          <h3 style={{ margin: '0 0 1rem 0' }}>Optimization Execution Log</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {results.evolutions.map((ev: any, idx: number) => (
              <div key={idx} style={{ background: 'var(--bg-muted)', padding: '0.85rem 1rem', borderRadius: '8px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <span style={{ fontWeight: 700, fontSize: '0.85rem' }}>[{ev.action}] {ev.test_name}</span>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{ev.benefit}</div>
                </div>
                <StatusBadge status="APPROVED" label="Applied" size="sm" />
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
