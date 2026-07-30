import React, { useEffect, useState } from 'react';
import { PageHeader } from '../components/layout/PageHeader';
import { StatCard } from '../components/ui/StatCard';
import { StatusBadge } from '../components/ui/StatusBadge';
import { Button } from '../components/ui/Button';
import { Layers, Plus, Play, Eye, MousePointer, CheckSquare, Database, Code2, RefreshCw } from 'lucide-react';
import { apiGet, apiPost } from '../services/api';
import { toast } from '../stores/toastStore';

interface StepPalette {
  actions: string[];
  assertions: string[];
  data_operations: string[];
  flow_controls: string[];
}

interface TestFlow {
  id: number;
  flow_name: string;
  flow_type: string;
  step_count: number;
  is_active: boolean;
  created_at: string;
}

export function ZeroCodeTestStudioPage() {
  const [palette, setPalette] = useState<StepPalette | null>(null);
  const [flows, setFlows] = useState<TestFlow[]>([]);
  const [loading, setLoading] = useState(false);
  const [creating, setCreating] = useState(false);
  const [newFlowName, setNewFlowName] = useState('My Test Flow');
  const [newFlowType, setNewFlowType] = useState('SCENARIO');

  const fetchData = async () => {
    setLoading(true);
    try {
      const [p, f] = await Promise.all([
        apiGet<StepPalette>('/api/test-studio/step-palette'),
        apiGet<TestFlow[]>('/api/test-studio/flows?project_id=1'),
      ]);
      setPalette(p);
      setFlows(f);
    } catch (err) {
      toast.error('Failed to load Test Studio data');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateFlow = async () => {
    setCreating(true);
    try {
      await apiPost('/api/test-studio/flows?project_id=1', {
        flow_name: newFlowName,
        flow_type: newFlowType,
        flow_steps: [
          { type: 'CLICK', selector: '#login-btn', description: 'Click Login button' },
          { type: 'TYPE', selector: '#username', value: 'test@enterprise.com', description: 'Enter username' },
          { type: 'ASSERT_URL', expected: '/dashboard', description: 'Verify dashboard redirect' },
        ],
      });
      toast.success(`Flow "${newFlowName}" created!`);
      void fetchData();
    } catch (err: any) {
      toast.error(err.message || 'Failed to create flow');
    } finally {
      setCreating(false);
    }
  };

  useEffect(() => {
    void fetchData();
  }, []);

  const CATEGORY_ICONS: Record<string, React.ReactNode> = {
    actions: <MousePointer size={16} color="var(--color-primary)" />,
    assertions: <CheckSquare size={16} color="#10b981" />,
    data_operations: <Database size={16} color="#f59e0b" />,
    flow_controls: <Code2 size={16} color="#8b5cf6" />,
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      <PageHeader
        breadcrumbs={[{ label: 'Zero-Code Ecosystem' }, { label: 'Test Studio' }]}
        title="Zero-Code Visual Test Studio"
        description="Drag & drop test builder. Build scenarios, visual assertions, API validators, and business rule flows without writing code."
        actions={
          <Button size="sm" variant="secondary" onClick={() => void fetchData()} isLoading={loading} leftIcon={<RefreshCw size={14} />}>
            Refresh
          </Button>
        }
      />

      <div className="grid grid-cols-4">
        <StatCard title="Test Flows" value={flows.length || 0} subtitle="Studio Flows Created" icon={Layers} variant="primary" />
        <StatCard title="Step Types" value="14 Actions" subtitle="Drag & Drop Palette" icon={MousePointer} variant="info" />
        <StatCard title="Assertions" value="8 Types" subtitle="Visual & DOM Checks" icon={CheckSquare} variant="success" />
        <StatCard title="Data Builders" value="7 Builders" subtitle="API, DB, Business Rules" icon={Database} variant="warning" />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '1.25rem' }}>
        {/* Step Palette */}
        {palette && (
          <div className="card" style={{ padding: '1.25rem' }}>
            <h3 style={{ margin: '0 0 1rem 0' }}>Step Palette</h3>
            {(Object.entries(palette) as [string, string[]][]).map(([category, steps]) => (
              <div key={category} style={{ marginBottom: '1rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem', fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-muted)' }}>
                  {CATEGORY_ICONS[category]} {category.replace('_', ' ')}
                </div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.35rem' }}>
                  {steps.map(step => (
                    <span
                      key={step}
                      style={{
                        background: 'var(--bg-muted)', border: '1px solid var(--border-color)',
                        borderRadius: 6, padding: '0.25rem 0.6rem', fontSize: '0.72rem', fontWeight: 600,
                        cursor: 'grab', userSelect: 'none',
                      }}
                    >
                      {step}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Flow Canvas & Create */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {/* Quick Create */}
          <div className="card" style={{ padding: '1.25rem' }}>
            <h3 style={{ margin: '0 0 1rem 0' }}>Create New Flow</h3>
            <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
              <input
                value={newFlowName}
                onChange={e => setNewFlowName(e.target.value)}
                placeholder="Flow name..."
                style={{
                  flex: 1, minWidth: 200, padding: '0.6rem 0.9rem',
                  background: 'var(--bg-muted)', border: '1px solid var(--border-color)',
                  borderRadius: 8, color: 'var(--text-primary)', fontSize: '0.9rem',
                }}
              />
              <select
                value={newFlowType}
                onChange={e => setNewFlowType(e.target.value)}
                style={{
                  padding: '0.6rem 0.9rem', background: 'var(--bg-muted)',
                  border: '1px solid var(--border-color)', borderRadius: 8,
                  color: 'var(--text-primary)', fontSize: '0.9rem',
                }}
              >
                {['SCENARIO', 'VISUAL_ASSERTION', 'API', 'DB_VALIDATION', 'BUSINESS_RULE'].map(t => (
                  <option key={t} value={t}>{t}</option>
                ))}
              </select>
              <Button variant="primary" onClick={() => void handleCreateFlow()} isLoading={creating} leftIcon={<Plus size={14} />}>
                Create Flow
              </Button>
            </div>
          </div>

          {/* Flow List */}
          <div className="card" style={{ padding: '1.25rem' }}>
            <h3 style={{ margin: '0 0 1rem 0' }}>Saved Test Flows</h3>
            {flows.length === 0 ? (
              <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>No flows created yet. Use the palette and create button above.</p>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {flows.map(flow => (
                  <div key={flow.id} style={{ background: 'var(--bg-muted)', padding: '0.85rem 1rem', borderRadius: 8, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <div style={{ fontWeight: 700, fontSize: '0.9rem' }}>{flow.flow_name}</div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{flow.flow_type} · {flow.step_count} steps</div>
                    </div>
                    <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                      <StatusBadge status={flow.is_active ? 'APPROVED' : 'WARNING'} label={flow.is_active ? 'Active' : 'Inactive'} size="sm" />
                      <Button size="sm" variant="secondary" leftIcon={<Play size={12} />}>Run</Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
