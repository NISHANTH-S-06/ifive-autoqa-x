import React, { useState } from 'react';
import { PageHeader } from '../components/layout/PageHeader';
import { StatCard } from '../components/ui/StatCard';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { FormField } from '../components/ui/FormField';
import { StatusBadge } from '../components/ui/StatusBadge';
import { Brain, Cpu, Compass, Layers, Sparkles, CheckCircle2, Shield, Activity, RefreshCw } from 'lucide-react';
import { apiPost, apiGet } from '../services/api';
import { toast } from '../stores/toastStore';

interface ReasoningNode {
  question: string;
  answer: string;
  confidence: number;
}

interface ReasoningTree {
  goal: string;
  module: string;
  nodes: ReasoningNode[];
}

interface ReasoningResponse {
  page_url: string;
  module: string;
  overall_confidence: number;
  strategy_recommendation: string;
  reasoning_tree: ReasoningTree;
  explanation: string;
}

export function DigitalQAEngineerPage() {
  const [targetUrl, setTargetUrl] = useState('https://app.example.com/checkout');
  const [moduleName, setModuleName] = useState('Sales');
  const [analyzing, setAnalyzing] = useState(false);
  const [reasoning, setReasoning] = useState<ReasoningResponse | null>(null);
  const [strategies, setStrategies] = useState<Record<string, any> | null>(null);

  const handleRunSeniorQA = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!targetUrl) return;
    setAnalyzing(true);
    try {
      const res = await apiPost<ReasoningResponse>('/api/digital-qa/reason', {
        page_url: targetUrl,
        module_name: moduleName
      });
      setReasoning(res);

      const stratRes = await apiPost<any>('/api/digital-qa/strategy', {
        project_name: 'Enterprise ERP',
        target_url: targetUrl
      });
      setStrategies(stratRes.strategies);

      toast.success('AI Digital QA Engineer reasoning complete.');
    } catch (err: any) {
      toast.error(err.message || 'Senior QA evaluation failed');
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      <PageHeader
        breadcrumbs={[{ label: 'AI Autonomous QA' }, { label: 'AI Digital QA Engineer' }]}
        title="AI Digital QA Engineer Workspace"
        description="Autonomous Senior QA reasoning engine evaluating page testability, mandatory vs optional checks, 16 test strategies, and application topology."
      />

      {/* Senior QA Trigger Form */}
      <div className="card" style={{ padding: '1.25rem' }}>
        <form onSubmit={handleRunSeniorQA} style={{ display: 'flex', gap: '1rem', alignItems: 'flex-end' }}>
          <div style={{ flex: 2 }}>
            <FormField label="Target Page URL" required hint="URL of page for Senior QA AI reasoning">
              <Input placeholder="https://app.example.com/checkout" value={targetUrl} onChange={(e) => setTargetUrl(e.target.value)} />
            </FormField>
          </div>
          <div style={{ flex: 1 }}>
            <FormField label="System Module" required>
              <Input placeholder="Sales" value={moduleName} onChange={(e) => setModuleName(e.target.value)} />
            </FormField>
          </div>
          <Button variant="primary" type="submit" isLoading={analyzing} leftIcon={<Brain size={16} />}>
            Run Senior QA Analysis
          </Button>
        </form>
      </div>

      {reasoning && (
        <>
          <div className="grid grid-cols-4">
            <StatCard title="Overall Confidence" value={`${Math.round(reasoning.overall_confidence * 100)}%`} subtitle="Senior QA Verdict" icon={Brain} variant="primary" />
            <StatCard title="Strategy Recommendation" value={reasoning.strategy_recommendation} subtitle="Recommended Approach" icon={Compass} variant="info" />
            <StatCard title="Target Module" value={reasoning.module} subtitle="Primary Boundary" icon={Layers} variant="success" />
            <StatCard title="16-Category Suite" value="16 Strategies" subtitle="Active Test Strategies" icon={Shield} variant="warning" />
          </div>

          {/* Senior QA Reasoning Tree */}
          <div className="card" style={{ padding: '1.25rem' }}>
            <h3 style={{ margin: '0 0 1rem 0', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Cpu size={18} color="var(--color-primary)" /> Senior QA AI Thinking & Reasoning Tree
            </h3>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {reasoning.reasoning_tree.nodes.map((node, idx) => (
                <div key={idx} style={{ background: 'var(--bg-muted)', padding: '1rem', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem' }}>
                    <span style={{ fontWeight: 700, color: 'var(--color-primary)', fontSize: '0.9rem' }}>
                      Q{idx + 1}: {node.question}
                    </span>
                    <StatusBadge status="APPROVED" label={`Confidence: ${Math.round(node.confidence * 100)}%`} size="sm" />
                  </div>
                  <div style={{ fontSize: '0.85rem', color: 'var(--text-main)', lineHeight: '1.5' }}>
                    {node.answer}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* 16-Category Strategy Cards */}
          {strategies && (
            <div className="card" style={{ padding: '1.25rem' }}>
              <h3 style={{ margin: '0 0 1rem 0', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Sparkles size={18} color="var(--color-primary)" /> Generated 16-Category Enterprise Test Strategies
              </h3>

              <div className="grid grid-cols-4" style={{ gap: '1rem' }}>
                {Object.entries(strategies).map(([catKey, strat], sIdx) => (
                  <div key={sIdx} style={{ background: 'var(--bg-muted)', padding: '0.85rem', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem' }}>
                      <span style={{ fontWeight: 700, fontSize: '0.75rem', textTransform: 'uppercase' }}>
                        {strat.category}
                      </span>
                      <StatusBadge status={strat.priority === 'HIGH' ? 'APPROVED' : 'INFO'} label={strat.priority} size="sm" />
                    </div>
                    <div style={{ fontSize: '0.8rem', fontWeight: 600, marginBottom: '0.25rem' }}>
                      {strat.title}
                    </div>
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                      Automation: {Math.round(strat.automation_ratio * 100)}%
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
