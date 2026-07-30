import React, { useState } from 'react';
import { PageHeader } from '../components/layout/PageHeader';
import { StatCard } from '../components/ui/StatCard';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { FormField } from '../components/ui/FormField';
import { StatusBadge } from '../components/ui/StatusBadge';
import { DataTable, Column } from '../components/ui/DataTable';
import { GitBranch, Play, Layers, ShieldCheck, CheckCircle2 } from 'lucide-react';
import { apiPost } from '../services/api';
import { toast } from '../stores/toastStore';

interface RegressionTest {
  test_id: string;
  name: string;
  module: string;
  priority: string;
}

interface ImpactReport {
  task_id: number;
  target_module: string;
  feature: string;
  impacted_modules: string[];
  total_affected_tests: number;
  estimated_duration_seconds: number;
  regression_plan: RegressionTest[];
  safety_verdict: string;
}

export function AutonomousRegressionPage() {
  const [taskId, setTaskId] = useState('1');
  const [analyzing, setAnalyzing] = useState(false);
  const [report, setReport] = useState<ImpactReport | null>(null);

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!taskId) return;
    setAnalyzing(true);
    try {
      const res = await apiPost<ImpactReport>('/api/regression/analyze-and-run', {
        task_id: Number(taskId)
      });
      setReport(res);
      toast.success('Developer change impact analysis complete.');
    } catch (err: any) {
      toast.error(err.message || 'Impact analysis failed');
    } finally {
      setAnalyzing(false);
    }
  };

  const columns: Column<RegressionTest>[] = [
    { key: 'test_id', header: 'Test ID', render: (t) => <span style={{ fontWeight: 700, fontFamily: 'var(--font-mono)' }}>{t.test_id}</span> },
    { key: 'name', header: 'Regression Test Name', render: (t) => <span style={{ fontWeight: 600 }}>{t.name}</span> },
    { key: 'module', header: 'Impacted Module', render: (t) => <StatusBadge status="INFO" label={t.module} size="sm" /> },
    { key: 'priority', header: 'Priority', render: (t) => <StatusBadge status={t.priority === 'CRITICAL' ? 'CRITICAL' : 'APPROVED'} label={t.priority} size="sm" /> }
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      <PageHeader
        breadcrumbs={[{ label: 'AI Autonomous QA' }, { label: 'Autonomous Regression' }]}
        title="Autonomous Developer Impact & Targeted Regression"
        description="Detect code modification impact across system modules, auto-generate minimal regression plans, and execute targeted test suites."
      />

      {/* Task Input Bar */}
      <div className="card" style={{ padding: '1.25rem' }}>
        <form onSubmit={handleAnalyze} style={{ display: 'flex', gap: '1rem', alignItems: 'flex-end' }}>
          <div style={{ flex: 1 }}>
            <FormField label="Developer Completed Task ID" required hint="Enter Task ID to analyze code change boundaries">
              <Input
                type="number"
                placeholder="e.g. 1"
                value={taskId}
                onChange={(e) => setTaskId(e.target.value)}
              />
            </FormField>
          </div>
          <Button variant="primary" type="submit" isLoading={analyzing} leftIcon={<GitBranch size={16} />}>
            Analyze Change Impact
          </Button>
        </form>
      </div>

      {report && (
        <>
          <div className="grid grid-cols-4">
            <StatCard title="Target Module" value={report.target_module} subtitle="Primary Modification" icon={Layers} variant="primary" />
            <StatCard title="Impacted Modules" value={report.impacted_modules.length} subtitle={report.impacted_modules.join(', ')} icon={GitBranch} variant="info" />
            <StatCard title="Targeted Tests" value={report.total_affected_tests} subtitle="Minimal Suite" icon={CheckCircle2} variant="success" />
            <StatCard title="Safety Verdict" value={report.safety_verdict} subtitle="Fail-Closed Guard" icon={ShieldCheck} variant="warning" />
          </div>

          <div className="card" style={{ padding: '1.25rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
              <h3 style={{ margin: 0 }}>Targeted Regression Suite Plan</h3>
              <Button variant="primary" size="sm" leftIcon={<Play size={14} />}>
                Execute Targeted Regression Suite
              </Button>
            </div>
            <DataTable columns={columns} data={report.regression_plan} keyExtractor={(t) => t.test_id} />
          </div>
        </>
      )}
    </div>
  );
}
