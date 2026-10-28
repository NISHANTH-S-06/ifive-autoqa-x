import React, { useEffect, useState } from 'react';
import { PageHeader } from '../components/layout/PageHeader';
import { StatCard } from '../components/ui/StatCard';
import { StatusBadge } from '../components/ui/StatusBadge';
import { Button } from '../components/ui/Button';
import { Modal } from '../components/ui/Modal';
import { 
  Layers, Plus, Play, MousePointer, CheckSquare, Database, Code2, 
  RefreshCw, Trash2, ArrowUp, ArrowDown, Save, CheckCircle2, XCircle, 
  Clock, Sparkles, Zap, Edit3
} from 'lucide-react';
import { apiGet, apiPost, apiMutation } from '../services/api';
import { toast } from '../stores/toastStore';
import { useProject } from '../stores/projectStore';

interface StepPalette {
  actions: string[];
  assertions: string[];
  data_operations: string[];
  flow_controls: string[];
}

interface FlowStep {
  type: string;
  selector?: string;
  value?: string;
  expected?: string;
  description?: string;
}

interface TestFlow {
  id: number;
  flow_name: string;
  flow_type: string;
  step_count: number;
  flow_steps?: FlowStep[];
  is_active: boolean;
  created_at: string;
}

interface StepExecutionResult {
  step_number: number;
  type: string;
  description: string;
  selector: string;
  value: string;
  status: 'PASS' | 'FAIL';
  duration_ms: number;
  log: string;
}

interface FlowExecutionReport {
  flow_id: number;
  flow_name: string;
  status: 'PASS' | 'FAIL';
  total_steps: number;
  passed_steps: number;
  failed_steps: number;
  duration_ms: number;
  steps_results: StepExecutionResult[];
}

const DEFAULT_STEPS: FlowStep[] = [
  { type: 'CLICK', selector: '#login-button', description: 'Click main sign in button' },
  { type: 'TYPE', selector: '#username', value: 'admin@ifive.in', description: 'Enter operator credential' },
  { type: 'ASSERT_URL', expected: '/dashboard', description: 'Verify successful redirect to dashboard' },
  { type: 'VISUAL_BASELINE_MATCH', description: 'Compare UI snapshot with baseline threshold' },
];

export function ZeroCodeTestStudioPage() {
  const { activeProject } = useProject();
  const projectId = activeProject?.id || 1;

  const [palette, setPalette] = useState<StepPalette | null>(null);
  const [flows, setFlows] = useState<TestFlow[]>([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [running, setRunning] = useState(false);

  // Flow Builder Canvas state
  const [flowName, setFlowName] = useState('E2E Purchase & Checkout Flow');
  const [flowType, setNewFlowType] = useState('SCENARIO');
  const [canvasSteps, setCanvasSteps] = useState<FlowStep[]>(DEFAULT_STEPS);
  const [activeFlowId, setActiveFlowId] = useState<number | null>(null);

  // AI Prompt Assistant State
  const [promptInput, setPromptInput] = useState('');
  const [generatingAI, setGeneratingAI] = useState(false);

  // Execution Modal state
  const [executionReport, setExecutionReport] = useState<FlowExecutionReport | null>(null);
  const [showRunModal, setShowRunModal] = useState(false);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [p, f] = await Promise.all([
        apiGet<StepPalette>('/api/test-studio/step-palette'),
        apiGet<TestFlow[]>(`/api/test-studio/flows?project_id=${projectId}`),
      ]);
      setPalette(p);
      setFlows(f);
    } catch (err) {
      toast.error('Failed to load Test Studio data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void fetchData();
  }, [projectId]);

  // AI Prompt Flow Generation Handler
  const handleGenerateAIFlow = async () => {
    if (!promptInput.trim()) {
      toast.error('Please enter a natural language flow scenario description');
      return;
    }
    setGeneratingAI(true);
    try {
      const res = await apiPost<{
        flow_name: string;
        flow_type: string;
        step_count: number;
        flow_steps: FlowStep[];
      }>('/api/test-studio/generate-flow', {
        prompt: promptInput,
        flow_type: flowType,
      });

      if (res.flow_steps && res.flow_steps.length > 0) {
        setFlowName(res.flow_name);
        setCanvasSteps(res.flow_steps);
        setActiveFlowId(null);
        toast.success(`Generated ${res.step_count} step test flow with AI!`);
      }
    } catch (err: any) {
      toast.error(err.message || 'Failed to generate test flow from AI prompt');
    } finally {
      setGeneratingAI(false);
    }
  };

  // Step Palette Addition
  const addStepFromPalette = (stepType: string, category: string) => {
    let defaultDesc = `Execute ${stepType}`;
    let defaultSelector = '';
    let defaultValue = '';
    let defaultExpected = '';

    if (category === 'actions') {
      defaultSelector = stepType === 'CLICK' ? '#submit-btn' : '#input-field';
      defaultValue = stepType === 'TYPE' ? 'Sample text input' : '';
      defaultDesc = `${stepType.replace('_', ' ')} on target element`;
    } else if (category === 'assertions') {
      defaultExpected = stepType === 'ASSERT_URL' ? '/dashboard' : 'Expected Title';
      defaultDesc = `Assert ${stepType.replace('_', ' ')}`;
    } else if (category === 'data_operations') {
      defaultDesc = `Data Operation ${stepType}`;
    }

    const newStep: FlowStep = {
      type: stepType,
      selector: defaultSelector,
      value: defaultValue,
      expected: defaultExpected,
      description: defaultDesc,
    };

    setCanvasSteps(prev => [...prev, newStep]);
    toast.info(`Added step: ${stepType}`);
  };

  const updateStepField = (index: number, field: keyof FlowStep, val: string) => {
    setCanvasSteps(prev => {
      const next = [...prev];
      next[index] = { ...next[index], [field]: val };
      return next;
    });
  };

  const removeStep = (index: number) => {
    setCanvasSteps(prev => prev.filter((_, i) => i !== index));
  };

  const moveStep = (index: number, delta: number) => {
    setCanvasSteps(prev => {
      const next = [...prev];
      const target = index + delta;
      if (target < 0 || target >= next.length) return prev;
      [next[index], next[target]] = [next[target], next[index]];
      return next;
    });
  };

  const handleSaveFlow = async () => {
    if (!flowName.trim()) {
      toast.error('Flow name is required');
      return;
    }
    if (canvasSteps.length === 0) {
      toast.error('Add at least one step from palette before saving');
      return;
    }
    setSaving(true);
    try {
      await apiPost(`/api/test-studio/flows?project_id=${projectId}`, {
        flow_name: flowName,
        flow_type: flowType,
        flow_steps: canvasSteps,
      });
      toast.success(`Test Flow "${flowName}" saved successfully!`);
      await fetchData();
    } catch (err: any) {
      toast.error(err.message || 'Failed to save flow');
    } finally {
      setSaving(false);
    }
  };

  const handleLoadFlow = (flow: TestFlow) => {
    setFlowName(flow.flow_name);
    setNewFlowType(flow.flow_type);
    setActiveFlowId(flow.id);
    if (flow.flow_steps && flow.flow_steps.length > 0) {
      setCanvasSteps(flow.flow_steps);
    }
    toast.info(`Loaded "${flow.flow_name}" into editor canvas`);
  };

  const handleDeleteFlow = async (flowId: number) => {
    try {
      await apiMutation('DELETE', `/api/test-studio/flows/${flowId}`, {});
      toast.success('Flow deleted');
      await fetchData();
    } catch (err: any) {
      toast.error(err.message || 'Failed to delete flow');
    }
  };

  const handleRunFlow = async (flowId?: number) => {
    setRunning(true);
    try {
      if (flowId) {
        const report = await apiPost<FlowExecutionReport>(`/api/test-studio/flows/${flowId}/run`, {});
        setExecutionReport(report);
      } else {
        // Execute unsaved canvas steps directly via backend API
        const report = await apiPost<FlowExecutionReport>('/api/test-studio/flows/run-canvas', {
          flow_steps: canvasSteps,
          flow_name: flowName,
        });
        setExecutionReport(report);
      }
      setShowRunModal(true);
      toast.success('Flow execution completed!');
    } catch (err: any) {
      toast.error(err.message || 'Flow execution failed');
    } finally {
      setRunning(false);
    }
  };

  const CATEGORY_COLORS: Record<string, { bg: string; text: string; border: string }> = {
    actions: { bg: 'rgba(37, 99, 235, 0.1)', text: '#2563eb', border: 'rgba(37, 99, 235, 0.25)' },
    assertions: { bg: 'rgba(16, 185, 129, 0.1)', text: '#10b981', border: 'rgba(16, 185, 129, 0.25)' },
    data_operations: { bg: 'rgba(245, 158, 11, 0.1)', text: '#f59e0b', border: 'rgba(245, 158, 11, 0.25)' },
    flow_controls: { bg: 'rgba(139, 92, 246, 0.1)', text: '#8b5cf6', border: 'rgba(139, 92, 246, 0.25)' },
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      <PageHeader
        breadcrumbs={[{ label: 'Zero-Code Ecosystem' }, { label: 'Test Studio' }]}
        title="Zero-Code Visual Test Studio"
        description="Build multi-scenario web tests, visual assertions, and API validation flows without writing code."
        actions={
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <Button size="sm" variant="secondary" onClick={() => void fetchData()} isLoading={loading} leftIcon={<RefreshCw size={14} />}>
              Refresh
            </Button>
            <Button size="sm" variant="primary" onClick={() => void handleRunFlow()} isLoading={running} leftIcon={<Play size={14} />}>
              Run Current Canvas
            </Button>
          </div>
        }
      />

      <div className="grid grid-cols-4">
        <StatCard title="Test Flows" value={flows.length || 0} subtitle={`Saved in Project #${projectId}`} icon={Layers} variant="primary" />
        <StatCard title="Active Canvas Steps" value={`${canvasSteps.length} Steps`} subtitle="Visual Test Steps" icon={MousePointer} variant="info" />
        <StatCard title="Assertions" value="8 Types" subtitle="Visual & DOM Checks" icon={CheckSquare} variant="success" />
        <StatCard title="Data Builders" value="7 Builders" subtitle="API, DB, Business Rules" icon={Database} variant="warning" />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '320px 1fr', gap: '1.25rem' }}>
        {/* Step Palette Panel (Left Column) */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          <div className="card" style={{ padding: '1.25rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
              <h3 style={{ margin: 0, fontSize: '0.95rem', fontWeight: 600, color: 'var(--text-main)' }}>Step Palette</h3>
              <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Click to Add</span>
            </div>

            {palette && (Object.entries(palette) as [string, string[]][]).map(([category, steps]) => {
              const theme = CATEGORY_COLORS[category] || CATEGORY_COLORS.actions;
              return (
                <div key={category} style={{ marginBottom: '1rem' }}>
                  <div style={{ fontSize: '0.72rem', fontWeight: 700, textTransform: 'uppercase', color: theme.text, marginBottom: '0.4rem', letterSpacing: '0.04em' }}>
                    {category.replace('_', ' ')}
                  </div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.35rem' }}>
                    {steps.map(step => (
                      <button
                        key={step}
                        onClick={() => addStepFromPalette(step, category)}
                        style={{
                          background: theme.bg,
                          color: theme.text,
                          border: `1px solid ${theme.border}`,
                          borderRadius: 6,
                          padding: '0.25rem 0.55rem',
                          fontSize: '0.72rem',
                          fontWeight: 600,
                          cursor: 'pointer',
                          transition: 'all 0.15s ease',
                          textAlign: 'left',
                        }}
                        title={`Click to add ${step} to canvas`}
                      >
                        + {step}
                      </button>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>

          {/* Saved Flows Registry Card */}
          <div className="card" style={{ padding: '1.25rem' }}>
            <h3 style={{ margin: '0 0 1rem 0', fontSize: '0.95rem', fontWeight: 600 }}>Saved Project Flows</h3>
            {flows.length === 0 ? (
              <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem', margin: 0 }}>No saved flows yet. Click palette items to build a flow.</p>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem' }}>
                {flows.map(flow => (
                  <div 
                    key={flow.id} 
                    style={{ 
                      background: activeFlowId === flow.id ? 'var(--bg-sidebar-active)' : 'var(--bg-card-subtle)',
                      border: '1px solid var(--border-color)',
                      padding: '0.75rem',
                      borderRadius: 8,
                      display: 'flex',
                      flexDirection: 'column',
                      gap: '0.4rem'
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span style={{ fontWeight: 700, fontSize: '0.85rem', color: 'var(--text-main)' }}>{flow.flow_name}</span>
                      <StatusBadge status={flow.is_active ? 'APPROVED' : 'WARNING'} label={flow.flow_type} size="sm" />
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                      <span>{flow.step_count} steps</span>
                      <div style={{ display: 'flex', gap: '0.35rem' }}>
                        <button className="btn btn-ghost btn-sm" style={{ padding: '0.2rem 0.4rem', fontSize: '0.7rem' }} onClick={() => handleLoadFlow(flow)} title="Load into Canvas">
                          <Edit3 size={12} /> Load
                        </button>
                        <button className="btn btn-primary btn-sm" style={{ padding: '0.2rem 0.5rem', fontSize: '0.7rem' }} onClick={() => void handleRunFlow(flow.id)} title="Run Flow">
                          <Play size={11} /> Run
                        </button>
                        <button className="btn btn-ghost btn-sm" style={{ padding: '0.2rem 0.4rem', fontSize: '0.7rem', color: 'var(--color-danger)' }} onClick={() => void handleDeleteFlow(flow.id)}>
                          <Trash2 size={12} />
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Visual Flow Builder Canvas (Right Column) */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          {/* AI Flow Prompt Assistant Card */}
          <div className="card" style={{ padding: '1.25rem', background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.08), rgba(37, 99, 235, 0.08))', border: '1px solid rgba(139, 92, 246, 0.2)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.6rem' }}>
              <Zap size={18} style={{ color: '#8b5cf6' }} />
              <h3 style={{ margin: 0, fontSize: '0.95rem', fontWeight: 600, color: 'var(--text-main)' }}>AI Prompt Flow Generator</h3>
              <span className="badge badge-info" style={{ fontSize: '0.65rem' }}>Instant AI Generator</span>
            </div>
            <p style={{ margin: '0 0 0.75rem 0', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              Type any test flow or user scenario in plain English (e.g. <em>"Login with admin, search product, add to cart and verify checkout order ID"</em>) to build test steps automatically.
            </p>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <input
                className="input"
                style={{ flex: 1, fontSize: '0.85rem' }}
                value={promptInput}
                onChange={e => setPromptInput(e.target.value)}
                placeholder="e.g. Login to admin dashboard, navigate to billing, verify payment invoice and DB transaction..."
                onKeyDown={e => { if (e.key === 'Enter') void handleGenerateAIFlow(); }}
              />
              <Button
                variant="primary"
                size="sm"
                onClick={() => void handleGenerateAIFlow()}
                isLoading={generatingAI}
                leftIcon={<Sparkles size={14} />}
                style={{ background: 'linear-gradient(135deg, #8b5cf6, #2563eb)', border: 'none' }}
              >
                Generate Flow
              </Button>
            </div>
          </div>

          {/* Header & Meta Bar */}
          <div className="card" style={{ padding: '1.25rem', background: 'linear-gradient(135deg, rgba(37, 99, 235, 0.05), rgba(14, 165, 233, 0.05))', border: '1px solid rgba(37, 99, 235, 0.15)' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Sparkles size={18} style={{ color: 'var(--color-primary)' }} />
                <h3 style={{ margin: 0, fontSize: '1rem', fontWeight: 600 }}>Visual Flow Builder Canvas</h3>
              </div>
              <div style={{ display: 'flex', gap: '0.5rem' }}>
                <Button size="sm" variant="secondary" onClick={() => setCanvasSteps([])} leftIcon={<Trash2 size={13} />}>
                  Clear Steps
                </Button>
                <Button size="sm" variant="primary" onClick={() => void handleSaveFlow()} isLoading={saving} leftIcon={<Save size={13} />}>
                  Save Flow
                </Button>
              </div>
            </div>

            <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
              <div style={{ flex: 2, minWidth: '220px' }}>
                <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, marginBottom: '0.25rem' }}>Flow Name</label>
                <input
                  className="input"
                  value={flowName}
                  onChange={e => setFlowName(e.target.value)}
                  placeholder="e.g. User Login & Checkout Flow"
                />
              </div>

              <div style={{ flex: 1, minWidth: '160px' }}>
                <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, marginBottom: '0.25rem' }}>Scenario Type</label>
                <select
                  className="select"
                  value={flowType}
                  onChange={e => setNewFlowType(e.target.value)}
                  style={{ width: '100%' }}
                >
                  {['SCENARIO', 'VISUAL_ASSERTION', 'API', 'DB_VALIDATION', 'BUSINESS_RULE'].map(t => (
                    <option key={t} value={t}>{t}</option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          {/* Canvas Steps List */}
          <div className="card" style={{ padding: '1.25rem', minHeight: '380px', display: 'flex', flexDirection: 'column' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
              <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-main)' }}>
                Step Sequence ({canvasSteps.length} Steps)
              </span>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                Click palette items on left to append steps
              </span>
            </div>

            {canvasSteps.length === 0 ? (
              <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '3rem 1rem', border: '2px dashed var(--border-color)', borderRadius: 12, textAlign: 'center', color: 'var(--text-muted)' }}>
                <MousePointer size={36} style={{ opacity: 0.4, marginBottom: '0.75rem', color: 'var(--color-primary)' }} />
                <h4 style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--text-main)', margin: '0 0 0.25rem 0' }}>Canvas is Empty</h4>
                <p style={{ fontSize: '0.8rem', maxWidth: '340px', margin: 0 }}>Click any action or assertion from the Step Palette on the left to start building your test flow.</p>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {canvasSteps.map((step, idx) => (
                  <div
                    key={idx}
                    style={{
                      padding: '0.85rem 1rem',
                      background: 'var(--bg-card-subtle)',
                      border: '1px solid var(--border-color)',
                      borderRadius: 8,
                      display: 'flex',
                      flexDirection: 'column',
                      gap: '0.65rem'
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                        <span style={{ width: '22px', height: '22px', borderRadius: '50%', background: 'var(--color-primary)', color: '#fff', fontSize: '0.75rem', fontWeight: 700, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                          {idx + 1}
                        </span>
                        <span className="badge badge-info" style={{ fontWeight: 700 }}>
                          {step.type}
                        </span>
                        <input
                          className="input"
                          style={{ padding: '0.2rem 0.5rem', fontSize: '0.8rem', fontWeight: 500, width: '260px' }}
                          value={step.description || ''}
                          onChange={e => updateStepField(idx, 'description', e.target.value)}
                          placeholder="Step description..."
                        />
                      </div>

                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                        <button className="btn btn-ghost btn-sm" onClick={() => moveStep(idx, -1)} disabled={idx === 0} title="Move Up"><ArrowUp size={13} /></button>
                        <button className="btn btn-ghost btn-sm" onClick={() => moveStep(idx, 1)} disabled={idx === canvasSteps.length - 1} title="Move Down"><ArrowDown size={13} /></button>
                        <button className="btn btn-ghost btn-sm" style={{ color: 'var(--color-danger)' }} onClick={() => removeStep(idx)} title="Remove Step"><Trash2 size={13} /></button>
                      </div>
                    </div>

                    <div style={{ display: 'flex', gap: '0.75rem' }}>
                      <div style={{ flex: 1 }}>
                        <input
                          className="input"
                          style={{ fontSize: '0.8rem' }}
                          value={step.selector || ''}
                          onChange={e => updateStepField(idx, 'selector', e.target.value)}
                          placeholder="Target Selector / Path / URL (e.g. #login-btn, /dashboard)"
                        />
                      </div>
                      <div style={{ flex: 1 }}>
                        <input
                          className="input"
                          style={{ fontSize: '0.8rem' }}
                          value={step.value || step.expected || ''}
                          onChange={e => updateStepField(idx, 'value', e.target.value)}
                          placeholder="Input Value / Expected Match (e.g. text value, status 200)"
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Execution Results Modal */}
      <Modal
        isOpen={showRunModal}
        onClose={() => setShowRunModal(false)}
        title={`Execution Report: ${executionReport?.flow_name || flowName}`}
        subtitle={`Ran against Project #${projectId} target environment`}
        footer={
          <Button variant="primary" onClick={() => setShowRunModal(false)}>
            Close Execution Summary
          </Button>
        }
      >
        {executionReport && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.75rem 1rem', background: 'var(--bg-card-subtle)', borderRadius: 8, border: '1px solid var(--border-color)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                {executionReport.status === 'PASS' ? <CheckCircle2 size={20} style={{ color: 'var(--color-success)' }} /> : <XCircle size={20} style={{ color: 'var(--color-danger)' }} />}
                <div>
                  <span style={{ fontWeight: 700, fontSize: '0.95rem' }}>Execution {executionReport.status}</span>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{executionReport.passed_steps} / {executionReport.total_steps} steps passed</div>
                </div>
              </div>
              <span className="badge badge-info" style={{ fontSize: '0.75rem' }}>
                <Clock size={12} /> {executionReport.duration_ms} ms
              </span>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', maxHeight: '300px', overflowY: 'auto' }}>
              {executionReport.steps_results.map(res => (
                <div key={res.step_number} style={{ padding: '0.65rem 0.85rem', background: 'var(--bg-card-subtle)', borderRadius: 6, border: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <span style={{ width: '18px', height: '18px', borderRadius: '50%', background: 'rgba(16,185,129,0.15)', color: '#10b981', fontSize: '0.7rem', fontWeight: 700, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                      {res.step_number}
                    </span>
                    <span className="badge badge-info" style={{ fontSize: '0.65rem' }}>{res.type}</span>
                    <span style={{ fontSize: '0.8rem', fontWeight: 500 }}>{res.description}</span>
                  </div>
                  <span className="badge badge-pass" style={{ fontSize: '0.65rem' }}>PASS ({res.duration_ms}ms)</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
}
