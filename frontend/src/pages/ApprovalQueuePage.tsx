import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { PageHeader } from '../components/layout/PageHeader';
import { getPendingApproval, approveAndRunAutoQA, getTask, previewAutoQAPlan, transitionStatus } from '../services/companyTasks';
import type { CompanyTaskListItem, CompanyTask, AutoQAPreviewStep } from '../types/companyTask';
import { TASK_STATUS_COLORS, TASK_STATUS_LABELS, TASK_PRIORITY_COLORS, TASK_STATUS_PIPELINE } from '../types/companyTask';
import { useAuth } from '../authContext';
import { 
  CheckSquare, ShieldAlert, AlertTriangle, FileText, 
  CheckCircle2, Clock, Eye, Zap, ListTodo, Link2, RefreshCw, X, ArrowRight, Activity, Terminal, Trash2, Edit2, Check
} from 'lucide-react';

function StatusPipeline({ status }: { status: string }) {
  const current = TASK_STATUS_PIPELINE.indexOf(status as any);
  if (current === -1) return null;

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '0', overflowX: 'auto', paddingBottom: '0.5rem' }}>
      {TASK_STATUS_PIPELINE.map((step, idx) => {
        const done = current > idx;
        const active = current === idx;
        const color = TASK_STATUS_COLORS[step];
        const label = TASK_STATUS_LABELS[step].replace(' ', '\n');
        
        return (
          <React.Fragment key={step}>
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.25rem', minWidth: '48px' }}>
              <div style={{
                width: '18px', height: '18px', borderRadius: '50%',
                background: done ? '#10b981' : active ? color : 'var(--bg-card)',
                border: `2px solid ${done ? '#10b981' : active ? color : 'var(--border-color)'}`,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                transition: 'all 0.2s',
              }}>
                {done ? <CheckCircle2 size={10} color="#fff" /> :
                  active ? <div style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#fff' }} /> :
                    null}
              </div>
              <span style={{ fontSize: '0.5rem', fontWeight: active ? 700 : 400, color: active ? color : 'var(--text-muted)', textAlign: 'center', lineHeight: 1.1, whiteSpace: 'pre-wrap' }}>
                {label}
              </span>
            </div>
            {idx < TASK_STATUS_PIPELINE.length - 1 && (
              <div style={{ flex: 1, height: '2px', minWidth: '4px', background: done ? '#10b981' : 'var(--border-color)', marginBottom: '14px' }} />
            )}
          </React.Fragment>
        );
      })}
    </div>
  );
}

// ── Task Review Drawer ─────────────────────────────────────────────────────
function ReviewDrawer({
  taskId,
  onClose,
  onApproved,
  onNavigate,
}: {
  taskId: number;
  onClose: () => void;
  onApproved: () => void;
  onNavigate?: (module: any) => void;
}) {
  const [task, setTask] = useState<CompanyTask | null>(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [approving, setApproving] = useState(false);
  const [previewPlan, setPreviewPlan] = useState<AutoQAPreviewStep[] | null>(null);
  const [editingIndex, setEditingIndex] = useState<number | null>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    void getTask(taskId).then(setTask).catch((e) => setError(e.message)).finally(() => setLoading(false));
  }, [taskId]);

  const handleGeneratePlan = async () => {
    setGenerating(true);
    setError('');
    try {
      const steps = await previewAutoQAPlan(taskId);
      setPreviewPlan(steps);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate preview.');
    } finally {
      setGenerating(false);
    }
  };

  const handleApprove = async () => {
    setApproving(true);
    try {
      await approveAndRunAutoQA(taskId, previewPlan || undefined);
      onApproved();
      onClose();
      if (onNavigate) {
        onNavigate('automated-runs');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to approve AutoQA.');
      setApproving(false);
    }
  };

  const handleUpdateStep = (index: number, field: keyof AutoQAPreviewStep, value: string) => {
    if (!previewPlan) return;
    const newPlan = [...previewPlan];
    newPlan[index] = { ...newPlan[index], [field]: value };
    setPreviewPlan(newPlan);
  };

  const handleDeleteStep = (index: number) => {
    if (!previewPlan) return;
    const newPlan = [...previewPlan];
    newPlan.splice(index, 1);
    // Re-number steps
    newPlan.forEach((step, i) => step.step_number = i + 1);
    setPreviewPlan(newPlan);
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.6)', zIndex: 1000 }}
      onClick={onClose}
    >
      <motion.div
        initial={{ x: '100%' }}
        animate={{ x: 0 }}
        exit={{ x: '100%' }}
        transition={{ type: 'spring', stiffness: 280, damping: 28 }}
        onClick={(e) => e.stopPropagation()}
        style={{
          position: 'absolute', right: 0, top: 0, bottom: 0, width: '560px', maxWidth: '90vw',
          background: 'var(--bg-card)', overflowY: 'auto', padding: '1.5rem',
          boxShadow: '-8px 0 32px rgba(0,0,0,0.25)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem' }}>
          <h2 style={{ fontSize: '1.1rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <CheckSquare size={20} style={{ color: 'var(--color-primary)' }} /> QA Review & Approve
          </h2>
          <button className="btn btn-ghost btn-sm" onClick={onClose}><X size={18} /></button>
        </div>

        {loading && <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '2rem' }}>Loading details...</p>}
        {error && <div style={{ padding: '0.75rem', borderRadius: 'var(--radius-md)', background: 'var(--status-fail-bg)', color: 'var(--status-fail-text)', marginBottom: '1rem', fontSize: '0.82rem' }}>{error}</div>}

        {task && !loading && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            <div style={{ background: 'var(--bg-app)', borderRadius: 'var(--radius-md)', padding: '1rem' }}>
              <StatusPipeline status={task.status} />
            </div>

            <div>
              <h3 style={{ fontSize: '1.2rem', fontWeight: 700, lineHeight: 1.3 }}>{task.title}</h3>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
                {task.module}{task.feature ? ` › ${task.feature}` : ''}
              </p>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <div style={{ background: 'var(--bg-base)', padding: '0.8rem', borderRadius: 'var(--radius-md)' }}>
                <p style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.2rem' }}>Developer</p>
                <p style={{ fontSize: '0.9rem', fontWeight: 600 }}>{task.assigned_developer?.display_name || '—'}</p>
              </div>
              <div style={{ background: 'var(--bg-base)', padding: '0.8rem', borderRadius: 'var(--radius-md)' }}>
                <p style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.2rem' }}>Target Platform</p>
                <p style={{ fontSize: '0.9rem', fontWeight: 600 }}>{task.browser} / {task.environment}</p>
              </div>
            </div>

            <div>
              <h4 style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <Link2 size={14} /> Target URL
              </h4>
              <div style={{ padding: '0.75rem', background: '#3b82f610', border: '1px solid #3b82f630', borderRadius: 'var(--radius-md)', fontSize: '0.85rem', wordBreak: 'break-all' }}>
                <a href={task.target_url || '#'} target="_blank" rel="noreferrer" style={{ color: '#3b82f6', textDecoration: 'none', fontWeight: 600 }}>
                  {task.target_url || 'No URL provided'}
                </a>
              </div>
              {!task.target_url && <p style={{ fontSize: '0.75rem', color: '#ef4444', marginTop: '0.4rem' }}>AutoQA cannot run without a target URL.</p>}
            </div>

            <div>
              <h4 style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <ArrowRight size={14} /> Expected Flow
              </h4>
              <pre style={{
                padding: '0.85rem', background: 'var(--bg-base)', border: '1px solid var(--border-color)', borderRadius: 'var(--radius-md)',
                fontSize: '0.85rem', fontFamily: 'monospace', whiteSpace: 'pre-wrap', color: 'var(--text-main)', lineHeight: 1.6
              }}>
                {task.expected_flow || 'No flow provided.'}
              </pre>
              {!task.expected_flow && <p style={{ fontSize: '0.75rem', color: '#ef4444', marginTop: '0.4rem' }}>AutoQA cannot generate steps without a flow.</p>}
            </div>

            {(task.acceptance_criteria || task.expected_result) && (
              <div>
                <h4 style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                  <CheckCircle2 size={14} /> Acceptance Criteria
                </h4>
                <div style={{ padding: '0.85rem', background: '#10b98110', border: '1px solid #10b98130', borderRadius: 'var(--radius-md)', fontSize: '0.85rem', color: 'var(--text-main)', lineHeight: 1.6 }}>
                  {task.acceptance_criteria && <div><strong>Criteria:</strong> {task.acceptance_criteria}</div>}
                  {task.expected_result && <div style={{ marginTop: '0.5rem' }}><strong>Expected Result:</strong> {task.expected_result}</div>}
                </div>
              </div>
            )}

            <div style={{ marginTop: '1.5rem', paddingTop: '1.25rem', borderTop: '1px solid var(--border-color)' }}>
              {!previewPlan ? (
                <>
                  <div style={{ background: '#8b5cf615', border: '1px solid #8b5cf640', borderRadius: 'var(--radius-md)', padding: '1rem', marginBottom: '1rem' }}>
                    <h4 style={{ fontSize: '0.9rem', fontWeight: 700, color: '#8b5cf6', display: 'flex', alignItems: 'center', gap: '0.4rem', marginBottom: '0.5rem' }}>
                      <Activity size={16} /> AI Test Plan Generation
                    </h4>
                    <p style={{ fontSize: '0.8rem', color: 'var(--text-main)', lineHeight: 1.5 }}>
                      Before executing, generate a preview of the AI actions based on the expected flow. You must review the plan before execution can begin.
                    </p>
                  </div>

                  <div style={{ display: 'flex', gap: '0.75rem' }}>
                    <button className="btn btn-secondary" style={{ flex: 1 }} onClick={onClose} disabled={generating}>Cancel</button>
                    <button
                      className="btn btn-primary"
                      style={{ flex: 2, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem', background: '#8b5cf6', borderColor: '#8b5cf6' }}
                      onClick={async () => {
                        if (task.status === 'DEVELOPER_COMPLETED') {
                          await transitionStatus(task.id, { status: 'TESTING_L2' });
                          setTask(prev => prev ? { ...prev, status: 'TESTING_L2' } : null);
                        }
                        await handleGeneratePlan();
                      }}
                      disabled={generating || !task.target_url || !task.expected_flow}
                    >
                      <Activity size={16} /> {generating ? 'Generating...' : task.status === 'DEVELOPER_COMPLETED' ? 'Pickup & Generate AutoQA Plan' : 'Generate AutoQA Plan'}
                    </button>
                  </div>
                </>
              ) : (
                <>
                  <h4 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <Terminal size={18} style={{ color: '#8b5cf6' }} /> AI Test Case Editor
                  </h4>
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>
                    Review, edit, or delete the AI-generated steps below before executing.
                  </p>
                  
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', marginBottom: '1.5rem' }}>
                    {previewPlan.map((step, idx) => (
                      <div key={idx} style={{ 
                        display: 'flex', alignItems: 'flex-start', gap: '0.75rem', 
                        background: 'var(--bg-base)', border: '1px solid var(--border-color)', 
                        padding: '0.75rem', borderRadius: 'var(--radius-md)' 
                      }}>
                        <div style={{ width: '24px', height: '24px', borderRadius: '50%', background: '#8b5cf620', color: '#8b5cf6', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.75rem', fontWeight: 700, flexShrink: 0, marginTop: '0.2rem' }}>
                          {step.step_number}
                        </div>
                        <div style={{ flex: 1 }}>
                          {editingIndex === idx ? (
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                              <div style={{ display: 'flex', gap: '0.5rem' }}>
                                <select 
                                  value={step.action_type} 
                                  onChange={(e) => handleUpdateStep(idx, 'action_type', e.target.value)}
                                  style={{ padding: '0.25rem', fontSize: '0.75rem', borderRadius: '4px', border: '1px solid var(--border-color)', background: 'var(--bg-card)' }}
                                >
                                  <option value="NAVIGATE">NAVIGATE</option>
                                  <option value="ASSERT_VISIBLE">ASSERT_VISIBLE</option>
                                  <option value="ASSERT_URL">ASSERT_URL</option>
                                  <option value="CLICK">CLICK</option>
                                  <option value="FILL">FILL</option>
                                  <option value="SCREENSHOT">SCREENSHOT</option>
                                </select>
                                {step.action_type !== 'SCREENSHOT' && (
                                  <input 
                                    type="text" 
                                    value={step.target} 
                                    onChange={(e) => handleUpdateStep(idx, 'target', e.target.value)}
                                    placeholder="Target / Locator"
                                    style={{ flex: 1, padding: '0.25rem 0.5rem', fontSize: '0.75rem', borderRadius: '4px', border: '1px solid var(--border-color)', background: 'var(--bg-card)', fontFamily: 'monospace' }}
                                  />
                                )}
                              </div>
                              <input 
                                type="text" 
                                value={step.expected_result} 
                                onChange={(e) => handleUpdateStep(idx, 'expected_result', e.target.value)}
                                placeholder="Expected Result"
                                style={{ width: '100%', padding: '0.25rem 0.5rem', fontSize: '0.75rem', borderRadius: '4px', border: '1px solid var(--border-color)', background: 'var(--bg-card)' }}
                              />
                            </div>
                          ) : (
                            <>
                              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                <span style={{ fontSize: '0.75rem', fontWeight: 800, color: 'var(--text-main)', textTransform: 'uppercase' }}>
                                  {step.action_type}
                                </span>
                                {step.target && (
                                  <span style={{ fontSize: '0.75rem', fontFamily: 'monospace', background: 'var(--bg-card)', padding: '0.1rem 0.4rem', borderRadius: '4px', border: '1px solid var(--border-color)', color: '#3b82f6', wordBreak: 'break-all' }}>
                                    {step.target}
                                  </span>
                                )}
                              </div>
                              <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>{step.expected_result}</p>
                            </>
                          )}
                        </div>
                        <div style={{ display: 'flex', gap: '0.25rem', marginTop: '0.2rem' }}>
                          {editingIndex === idx ? (
                            <button className="btn btn-ghost btn-sm" onClick={() => setEditingIndex(null)} style={{ padding: '0.25rem' }}>
                              <Check size={14} color="#10b981" />
                            </button>
                          ) : (
                            <button className="btn btn-ghost btn-sm" onClick={() => setEditingIndex(idx)} style={{ padding: '0.25rem' }}>
                              <Edit2 size={14} />
                            </button>
                          )}
                          <button className="btn btn-ghost btn-sm" onClick={() => handleDeleteStep(idx)} style={{ padding: '0.25rem' }}>
                            <Trash2 size={14} color="#ef4444" />
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>

                  <div style={{ display: 'flex', gap: '0.75rem' }}>
                    <button className="btn btn-secondary" style={{ flex: 1 }} onClick={onClose} disabled={approving}>Cancel</button>
                    <button
                      className="btn btn-primary"
                      style={{ flex: 2, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem', background: '#10b981', borderColor: '#10b981' }}
                      onClick={handleApprove}
                      disabled={approving}
                    >
                      <Zap size={16} /> {approving ? 'Triggering...' : 'Approve & Execute Plan'}
                    </button>
                  </div>
                </>
              )}
            </div>
          </div>
        )}
      </motion.div>
    </motion.div>
  );
}


// ── Main Page ──────────────────────────────────────────────────────────────
export function ApprovalQueuePage({ onNavigate }: { onNavigate?: (module: any) => void } = {}) {
  const { operator } = useAuth();
  const currentUserId = operator?.id || 1;

  const [queue, setQueue] = useState<CompanyTaskListItem[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const load = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const data = await getPendingApproval();
      setQueue(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load approval queue.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { void load(); }, [load]);

  const inReview = queue.filter(t => t.status === 'TESTING_L2');
  const upcoming = queue.filter(t => t.status === 'DEVELOPER_COMPLETED');
  const readyCount = inReview.length;
  
  return (
    <div style={{ maxWidth: '1000px' }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '1.5rem' }}>
        <div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 800, display: 'flex', alignItems: 'center', gap: '0.625rem' }}>
            <CheckSquare size={24} style={{ color: 'var(--color-primary)' }} /> Tester Approval Queue
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem', marginTop: '0.25rem' }}>
            Review developer tasks and approve them to trigger AutoQA orchestration.
          </p>
        </div>
        <button className="btn btn-ghost btn-sm" onClick={load} style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <RefreshCw size={14} /> Refresh
        </button>
      </div>

      <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem' }}>
        <div style={{ flex: 1, background: 'var(--bg-card)', border: '1px solid var(--border-color)', borderRadius: 'var(--radius-lg)', padding: '1.25rem', display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <div style={{ width: '48px', height: '48px', borderRadius: '50%', background: '#f59e0b20', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <CheckSquare size={24} color="#f59e0b" />
          </div>
          <div>
            <h3 style={{ fontSize: '2rem', fontWeight: 800, color: '#f59e0b', lineHeight: 1 }}>{readyCount}</h3>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 600 }}>Ready for Review (TESTING_L2)</p>
          </div>
        </div>
        <div style={{ flex: 1, background: 'var(--bg-card)', border: '1px solid var(--border-color)', borderRadius: 'var(--radius-lg)', padding: '1.25rem', display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <div style={{ width: '48px', height: '48px', borderRadius: '50%', background: '#3b82f620', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Clock size={24} color="#3b82f6" />
          </div>
          <div>
            <h3 style={{ fontSize: '2rem', fontWeight: 800, color: '#3b82f6', lineHeight: 1 }}>{upcoming.length}</h3>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 600 }}>Upcoming (DEV_COMPLETED)</p>
          </div>
        </div>
      </div>

      {error && <div style={{ padding: '1rem', borderRadius: 'var(--radius-md)', background: 'var(--status-fail-bg)', color: 'var(--status-fail-text)', marginBottom: '1.5rem' }}>{error}</div>}

      {loading && (
        <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
          <RefreshCw size={24} style={{ animation: 'spin 1s linear infinite', display: 'block', margin: '0 auto 0.75rem' }} />
          Loading queue...
        </div>
      )}

      {!loading && queue.length === 0 && (
        <div style={{ textAlign: 'center', padding: '4rem 2rem', background: 'var(--bg-card)', borderRadius: 'var(--radius-xl)', border: '1px solid var(--border-color)' }}>
          <CheckSquare size={48} style={{ color: 'var(--text-muted)', opacity: 0.4, display: 'block', margin: '0 auto 1rem' }} />
          <h3 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '0.5rem' }}>Queue is empty</h3>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>
            No tasks are currently waiting for tester review. You're all caught up!
          </p>
        </div>
      )}

      {!loading && inReview.length > 0 && (
        <div style={{ marginBottom: '2rem' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '1rem', color: '#f59e0b', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <AlertTriangle size={16} /> Needs Review (TESTING_L2)
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '1rem' }}>
            {inReview.map(task => (
              <motion.div
                key={task.id}
                whileHover={{ y: -2 }}
                style={{
                  background: 'var(--bg-card)', border: '1px solid var(--border-color)', borderLeft: '4px solid #f59e0b',
                  borderRadius: 'var(--radius-lg)', padding: '1rem', cursor: 'pointer', boxShadow: '0 2px 8px rgba(0,0,0,0.05)'
                }}
                onClick={() => setSelectedId(task.id)}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
                  <h4 style={{ fontSize: '0.95rem', fontWeight: 700, lineHeight: 1.3 }}>{task.title}</h4>
                  <span style={{ fontSize: '0.65rem', padding: '0.15rem 0.4rem', borderRadius: '4px', background: `${TASK_PRIORITY_COLORS[task.priority]}15`, color: TASK_PRIORITY_COLORS[task.priority], fontWeight: 700 }}>
                    {task.priority}
                  </span>
                </div>
                <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.75rem' }}>
                  {task.module}{task.feature ? ` › ${task.feature}` : ''}
                </p>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                    <div style={{ width: '20px', height: '20px', borderRadius: '50%', background: '#3b82f6', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.6rem', fontWeight: 700 }}>
                      {task.assigned_developer?.display_name.charAt(0) || '?'}
                    </div>
                    {task.assigned_developer?.display_name || 'Unassigned'}
                  </span>
                  <button className="btn btn-primary btn-sm" style={{ padding: '0.25rem 0.6rem', fontSize: '0.75rem' }} onClick={(e) => { e.stopPropagation(); setSelectedId(task.id); }}>
                    Review
                  </button>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      )}

      {!loading && upcoming.length > 0 && (
        <div>
          <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '1rem', color: '#3b82f6', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Clock size={16} /> Upcoming (Developer Completed, not yet submitted)
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '1rem' }}>
            {upcoming.map(task => (
              <motion.div
                key={task.id}
                whileHover={{ y: -2 }}
                onClick={() => setSelectedId(task.id)}
                style={{
                  background: 'var(--bg-card)', border: '1px solid var(--border-color)', borderLeft: '4px solid #3b82f6',
                  borderRadius: 'var(--radius-lg)', padding: '1rem', cursor: 'pointer', boxShadow: '0 2px 8px rgba(0,0,0,0.05)'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
                  <h4 style={{ fontSize: '0.9rem', fontWeight: 600, lineHeight: 1.3 }}>{task.title}</h4>
                  <span style={{ fontSize: '0.68rem', padding: '0.15rem 0.5rem', borderRadius: '4px', background: '#3b82f615', color: '#3b82f6', fontWeight: 700 }}>
                    Review Task
                  </span>
                </div>
                <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  Developer: {task.assigned_developer?.display_name || '—'}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      )}

      <AnimatePresence>
        {selectedId !== null && (
          <ReviewDrawer
            taskId={selectedId}
            onClose={() => setSelectedId(null)}
            onApproved={load}
            onNavigate={onNavigate}
          />
        )}
      </AnimatePresence>
    </div>
  );
}
