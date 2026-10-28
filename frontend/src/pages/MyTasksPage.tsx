import React, { useCallback, useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ListTodo, RefreshCw, CheckCircle2, ArrowRight, X,
  Link2, FileText, ClipboardCheck, AlertCircle, Clock, User, Trash2
} from 'lucide-react';
import { useAuth } from '../authContext';
import type { CompanyTaskListItem, CompanyTask, TaskStatus } from '../types/companyTask';
import { TASK_STATUS_LABELS, TASK_STATUS_COLORS, TASK_PRIORITY_COLORS, TASK_STATUS_PIPELINE } from '../types/companyTask';
import { getMyTasks, getTask, transitionStatus, deleteTask } from '../services/companyTasks';

function StatusChip({ status }: { status: TaskStatus }) {
  const color = TASK_STATUS_COLORS[status];
  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center',
      fontSize: '0.72rem', fontWeight: 700, padding: '0.2rem 0.6rem',
      borderRadius: 'var(--radius-full)',
      backgroundColor: `${color}20`, color, border: `1px solid ${color}40`,
      letterSpacing: '0.04em', textTransform: 'uppercase', whiteSpace: 'nowrap',
    }}>
      {TASK_STATUS_LABELS[status]}
    </span>
  );
}

// ── Status pipeline visual ─────────────────────────────────────────────────
function StatusPipeline({ status }: { status: TaskStatus }) {
  const current = TASK_STATUS_PIPELINE.indexOf(status);
  const isFail = status === 'FAILED' || status === 'BACK_TO_DEVELOPER';
  const isClosed = status === 'CLOSED';

  // If status is not in the normal pipeline, find closest logic
  let activeIndex = current;
  if (isFail) {
    activeIndex = TASK_STATUS_PIPELINE.indexOf('AUTOQA_RUNNING');
  } else if (isClosed) {
    activeIndex = TASK_STATUS_PIPELINE.length;
  }

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '0', overflowX: 'auto', paddingBottom: '0.5rem' }}>
      {TASK_STATUS_PIPELINE.map((step, idx) => {
        const done = activeIndex > idx;
        const active = activeIndex === idx;
        const color = TASK_STATUS_COLORS[step];
        const label = TASK_STATUS_LABELS[step].replace(' ', '\n');
        
        return (
          <React.Fragment key={step}>
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.25rem', minWidth: '56px' }}>
              <div style={{
                width: '20px', height: '20px', borderRadius: '50%',
                background: done ? '#10b981' : active ? color : 'var(--bg-card)',
                border: `2px solid ${done ? '#10b981' : active ? color : 'var(--border-color)'}`,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                transition: 'all 0.2s',
              }}>
                {done ? <CheckCircle2 size={10} color="#fff" /> :
                  active ? <div style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#fff' }} /> :
                    null}
              </div>
              <span style={{ fontSize: '0.55rem', fontWeight: active ? 700 : 400, color: active ? color : 'var(--text-muted)', textAlign: 'center', lineHeight: 1.1, whiteSpace: 'pre-wrap' }}>
                {label}
              </span>
            </div>
            {idx < TASK_STATUS_PIPELINE.length - 1 && (
              <div style={{ flex: 1, height: '2px', minWidth: '6px', background: done ? '#10b981' : 'var(--border-color)', marginBottom: '14px' }} />
            )}
          </React.Fragment>
        );
      })}
      {(isFail || isClosed) && (
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.25rem', minWidth: '56px', marginLeft: '6px' }}>
          <div style={{
            width: '20px', height: '20px', borderRadius: '50%',
            background: isFail ? '#ef444420' : '#6b728020',
            border: `2px solid ${isFail ? '#ef4444' : '#6b7280'}`,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            {isFail ? <AlertCircle size={10} color="#ef4444" /> : <CheckCircle2 size={10} color="#6b7280" />}
          </div>
          <span style={{ fontSize: '0.55rem', fontWeight: 700, color: isFail ? '#ef4444' : '#6b7280', textAlign: 'center' }}>
            {isFail ? 'FAIL' : 'Closed'}
          </span>
        </div>
      )}
    </div>
  );
}

// ── Task Detail Panel ──────────────────────────────────────────────────────
function TaskDetailPanel({
  taskId,
  onClose,
  onUpdated,
  onNavigate,
}: {
  taskId: number;
  onClose: () => void;
  onUpdated: () => void;
  onNavigate?: (module: any) => void;
}) {
  const { operator } = useAuth();
  const isAdmin = operator?.role === 'ADMIN';
  const [task, setTask] = useState<CompanyTask | null>(null);
  const [loading, setLoading] = useState(true);
  const [transitioning, setTransitioning] = useState(false);
  const [error, setError] = useState('');
  const [confirmL2, setConfirmL2] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState(false);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    void getTask(taskId).then(setTask).catch((e) => setError(e.message)).finally(() => setLoading(false));
  }, [taskId]);

  const markInProgress = async () => {
    if (!task) return;
    setTransitioning(true);
    try {
      await transitionStatus(task.id, { status: 'IN_PROGRESS' });
      onUpdated();
      onClose();
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed.');
    } finally {
      setTransitioning(false);
    }
  };

  const markTestingL2 = async () => {
    if (!task) return;
    setTransitioning(true);
    try {
      await transitionStatus(task.id, { status: 'DEVELOPER_COMPLETED', notes: 'Developer marked as completed.' });
      onUpdated();
      onClose();
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed.');
    } finally {
      setTransitioning(false);
      setConfirmL2(false);
    }
  };

  const handleDelete = async () => {
    if (!task) return;
    setDeleting(true);
    try {
      await deleteTask(task.id);
      onUpdated();
      onClose();
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to delete task.');
    } finally {
      setDeleting(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.55)', zIndex: 1000 }}
      onClick={onClose}
    >
      <motion.div
        initial={{ x: '100%' }}
        animate={{ x: 0 }}
        exit={{ x: '100%' }}
        transition={{ type: 'spring', stiffness: 280, damping: 28 }}
        onClick={(e) => e.stopPropagation()}
        style={{
          position: 'absolute', right: 0, top: 0, bottom: 0, width: '500px',
          background: 'var(--bg-card)', overflowY: 'auto', padding: '1.5rem',
          boxShadow: '-8px 0 32px rgba(0,0,0,0.25)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem' }}>
          <h2 style={{ fontSize: '1rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <ClipboardCheck size={18} style={{ color: 'var(--color-primary)' }} /> Task Details
          </h2>
          <button className="btn btn-ghost btn-sm" onClick={onClose}><X size={18} /></button>
        </div>

        {loading && <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '2rem' }}>Loading...</p>}

        {error && (
          <div style={{ padding: '0.75rem', borderRadius: 'var(--radius-md)', background: 'var(--status-fail-bg)', color: 'var(--status-fail-text)', marginBottom: '1rem', fontSize: '0.82rem' }}>
            {error}
          </div>
        )}

        {task && !loading && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.1rem' }}>
            {/* Status Pipeline */}
            <div style={{ background: 'var(--bg-app)', borderRadius: 'var(--radius-md)', padding: '1rem' }}>
              <StatusPipeline status={task.status as TaskStatus} />
            </div>

            {/* Title + Module */}
            <div>
              <p style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.35rem' }}>
                {task.module}{task.feature ? ` › ${task.feature}` : ''}
              </p>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 700, lineHeight: 1.3 }}>{task.title}</h3>
              <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.5rem', flexWrap: 'wrap' }}>
                <StatusChip status={task.status as TaskStatus} />
                <span style={{
                  fontSize: '0.68rem', fontWeight: 700, padding: '0.15rem 0.5rem',
                  borderRadius: 'var(--radius-full)',
                  backgroundColor: `${TASK_PRIORITY_COLORS[task.priority as keyof typeof TASK_PRIORITY_COLORS]}18`,
                  color: TASK_PRIORITY_COLORS[task.priority as keyof typeof TASK_PRIORITY_COLORS],
                  textTransform: 'uppercase',
                }}>
                  {task.priority}
                </span>
              </div>
            </div>

            {/* Description */}
            {task.description && (
              <div>
                <p style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.4rem' }}>Description</p>
                <p style={{ fontSize: '0.875rem', lineHeight: 1.6, color: 'var(--text-main)' }}>{task.description}</p>
              </div>
            )}

            {/* Target URL */}
            {task.target_url && (
              <div>
                <p style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.4rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                  <Link2 size={12} /> Target URL
                </p>
                <a href={task.target_url} target="_blank" rel="noreferrer"
                  style={{ fontSize: '0.82rem', color: 'var(--color-primary)', wordBreak: 'break-all', textDecoration: 'none' }}
                  onClick={(e) => e.stopPropagation()}>
                  {task.target_url}
                </a>
              </div>
            )}

            {/* Expected Flow */}
            {task.expected_flow && (
              <div>
                <p style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.4rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                  <ArrowRight size={12} /> Expected Flow (AutoQA will follow this)
                </p>
                <pre style={{
                  fontSize: '0.82rem', lineHeight: 1.7, color: 'var(--text-main)',
                  background: 'var(--bg-app)', borderRadius: 'var(--radius-md)',
                  padding: '0.75rem', whiteSpace: 'pre-wrap', wordBreak: 'break-word',
                  border: '1px solid var(--border-color)', fontFamily: 'inherit',
                }}>
                  {task.expected_flow}
                </pre>
              </div>
            )}

            {/* Acceptance Criteria */}
            {task.acceptance_criteria && (
              <div>
                <p style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.4rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                  <CheckCircle2 size={12} /> Acceptance Criteria
                </p>
                <div style={{
                  fontSize: '0.85rem', lineHeight: 1.6, color: 'var(--text-main)',
                  background: '#10b98110', borderRadius: 'var(--radius-md)',
                  padding: '0.75rem', border: '1px solid #10b98130',
                }}>
                  {task.acceptance_criteria}
                </div>
              </div>
            )}

            {/* Target Date */}
            {task.target_date && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.82rem', color: 'var(--text-muted)' }}>
                <Clock size={14} />
                Due: <strong style={{ color: new Date(task.target_date) < new Date() ? '#ef4444' : 'var(--text-main)' }}>
                  {new Date(task.target_date).toLocaleDateString()}
                </strong>
                {new Date(task.target_date) < new Date() && (
                  <span style={{ color: '#ef4444', fontSize: '0.75rem', fontWeight: 700 }}> ⚠ OVERDUE</span>
                )}
              </div>
            )}

            {/* Creator */}
            {task.creator && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                <User size={13} /> Created by {task.creator.display_name}
              </div>
            )}

            {/* AutoQA result */}
            {task.autoqa_result && (
              <div style={{
                padding: '0.75rem', borderRadius: 'var(--radius-md)',
                background: task.autoqa_result === 'PASS' ? '#10b98115' : '#ef444415',
                border: `1px solid ${task.autoqa_result === 'PASS' ? '#10b98140' : '#ef444440'}`,
              }}>
                <p style={{ fontSize: '0.8rem', fontWeight: 700, color: task.autoqa_result === 'PASS' ? '#10b981' : '#ef4444', marginBottom: '0.3rem' }}>
                  {task.autoqa_result === 'PASS' ? '✅ AutoQA PASSED' : '❌ AutoQA FAILED'}
                  {task.retest_count > 0 && ` (Retest #${task.retest_count})`}
                </p>
                {task.autoqa_notes && <p style={{ fontSize: '0.8rem', color: 'var(--text-main)' }}>{task.autoqa_notes}</p>}
              </div>
            )}

            {/* Developer Actions */}
            <div style={{ paddingTop: '0.75rem', borderTop: '1px solid var(--border-color)', display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
              {['NEW', 'ASSIGNED'].includes(task.status) && (
                <button
                  className="btn btn-primary"
                  style={{ width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}
                  onClick={markInProgress}
                  disabled={transitioning}
                >
                  <ArrowRight size={15} /> {transitioning ? 'Updating...' : 'Start Working (Mark In Progress)'}
                </button>
              )}

              {task.status === 'IN_PROGRESS' && !confirmL2 && (
                <button
                  className="btn"
                  style={{ width: '100%', background: '#f59e0b', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem', border: 'none', cursor: 'pointer', padding: '0.65rem 1rem', borderRadius: 'var(--radius-md)', fontWeight: 600 }}
                  onClick={() => setConfirmL2(true)}
                >
                  <CheckCircle2 size={15} /> Mark as Testing L2 (Done)
                </button>
              )}

              {task.status === 'IN_PROGRESS' && confirmL2 && (
                <div style={{ background: '#f59e0b15', border: '1px solid #f59e0b40', borderRadius: 'var(--radius-md)', padding: '1rem' }}>
                  <p style={{ fontSize: '0.85rem', fontWeight: 600, marginBottom: '0.5rem' }}>
                    Are you sure the fix is complete?
                  </p>
                  <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '0.75rem' }}>
                    The tester will review your work before AutoQA is executed.
                  </p>
                  <div style={{ display: 'flex', gap: '0.5rem' }}>
                    <button className="btn btn-secondary btn-sm" onClick={() => setConfirmL2(false)}>Cancel</button>
                    <button
                      className="btn btn-primary btn-sm"
                      onClick={markTestingL2}
                      disabled={transitioning}
                      style={{ flex: 1, background: '#f59e0b', border: 'none' }}
                    >
                      {transitioning ? 'Updating...' : '✓ Yes, Mark as Completed'}
                    </button>
                  </div>
                </div>
              )}

              {['TESTING_L2', 'TEST_APPROVED', 'AUTOQA_RUNNING'].includes(task.status) && (
                <div style={{ background: '#3b82f615', border: '1px solid #3b82f640', borderRadius: 'var(--radius-md)', padding: '0.75rem', textAlign: 'center', display: 'flex', flexDirection: 'column', gap: '0.5rem', alignItems: 'center' }}>
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-main)' }}>
                    Task is currently in testing workflow.
                  </p>
                  {onNavigate && (
                    <button
                      className="btn btn-primary btn-sm"
                      style={{ background: '#3b82f6', borderColor: '#3b82f6', fontSize: '0.78rem' }}
                      onClick={() => {
                        onClose();
                        onNavigate('automated-runs');
                      }}
                    >
                      ⚡ View Live Automated Run Execution
                    </button>
                  )}
                </div>
              )}

              {task.status === 'DEVELOPER_COMPLETED' && (
                <div style={{ background: '#f59e0b15', border: '1px solid #f59e0b40', borderRadius: 'var(--radius-md)', padding: '0.75rem', textAlign: 'center' }}>
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-main)' }}>
                    Waiting for L2 Tester review.
                  </p>
                  <button className="btn btn-ghost btn-sm" onClick={markInProgress} style={{ marginTop: '0.5rem' }}>
                    Take Back (Mark In Progress)
                  </button>
                </div>
              )}

              {(task.status === 'FAILED' || task.status === 'BACK_TO_DEVELOPER') && (
                <div style={{ background: '#ef444415', border: '1px solid #ef444440', borderRadius: 'var(--radius-md)', padding: '1rem' }}>
                  <p style={{ fontSize: '0.85rem', fontWeight: 700, color: '#ef4444', marginBottom: '0.5rem' }}>
                    <AlertCircle size={14} style={{ display: 'inline', marginRight: '0.3rem' }} />
                    Fix required (Sent back from Testing)
                  </p>
                  {task.autoqa_notes && <p style={{ fontSize: '0.8rem', color: 'var(--text-main)', marginBottom: '0.75rem' }}>{task.autoqa_notes}</p>}
                  <button
                    className="btn btn-primary btn-sm"
                    onClick={markInProgress}
                    disabled={transitioning}
                    style={{ width: '100%' }}
                  >
                    {transitioning ? 'Updating...' : 'Start Fix (Mark In Progress)'}
                  </button>
                </div>
              )}

              {isAdmin && !confirmDelete && (
                <button
                  className="btn btn-ghost btn-sm"
                  style={{ width: '100%', color: '#ef4444', border: '1px solid #ef444440', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.4rem', marginTop: '0.5rem' }}
                  onClick={() => setConfirmDelete(true)}
                >
                  <Trash2 size={14} /> Delete Task
                </button>
              )}
              {isAdmin && confirmDelete && (
                <div style={{ background: '#ef444415', border: '1px solid #ef444440', borderRadius: 'var(--radius-md)', padding: '0.75rem', marginTop: '0.5rem' }}>
                  <p style={{ fontSize: '0.8rem', fontWeight: 600, color: '#ef4444', marginBottom: '0.5rem' }}>
                    Are you sure you want to delete this task?
                  </p>
                  <div style={{ display: 'flex', gap: '0.5rem' }}>
                    <button className="btn btn-secondary btn-sm" onClick={() => setConfirmDelete(false)} disabled={deleting}>Cancel</button>
                    <button className="btn btn-sm" style={{ background: '#ef4444', color: '#fff', border: 'none', flex: 1 }} onClick={handleDelete} disabled={deleting}>
                      {deleting ? 'Deleting...' : 'Confirm Delete'}
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </motion.div>
    </motion.div>
  );
}

// ── Main Page ──────────────────────────────────────────────────────────────
export function MyTasksPage({ onNavigate }: { onNavigate?: (module: any) => void } = {}) {
  const { operator } = useAuth();
  const [tasks, setTasks] = useState<CompanyTaskListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedId, setSelectedId] = useState<number | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const data = await getMyTasks();
      setTasks(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load tasks.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { void load(); }, [load]);

  const statusGroups = [
    { status: 'BACK_TO_DEVELOPER' as TaskStatus, label: '❌ Needs Fix', urgent: true },
    { status: 'FAILED' as TaskStatus, label: '❌ AutoQA Failed', urgent: true },
    { status: 'ASSIGNED' as TaskStatus, label: 'Assigned — Not Started', urgent: false },
    { status: 'NEW' as TaskStatus, label: 'Assigned — Not Started', urgent: false },
    { status: 'IN_PROGRESS' as TaskStatus, label: '🔧 In Progress', urgent: false },
    { status: 'DEVELOPER_COMPLETED' as TaskStatus, label: '⏳ Waiting for Review', urgent: false },
    { status: 'TESTING_L2' as TaskStatus, label: '⏳ In L2 Testing', urgent: false },
    { status: 'TEST_APPROVED' as TaskStatus, label: '🤖 AutoQA Pending', urgent: false },
    { status: 'AUTOQA_RUNNING' as TaskStatus, label: '🤖 AutoQA Running', urgent: false },
    { status: 'PASSED' as TaskStatus, label: '✅ Passed', urgent: false },
    { status: 'DELIVERY_COMPLETED' as TaskStatus, label: '🚀 Delivered', urgent: false },
  ].filter((g) => tasks.some((t) => t.status === g.status));

  return (
    <div style={{ maxWidth: '900px' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '1.5rem' }}>
        <div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 800, display: 'flex', alignItems: 'center', gap: '0.625rem' }}>
            <ListTodo size={24} style={{ color: 'var(--color-primary)' }} /> My Tasks
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem', marginTop: '0.25rem' }}>
            Hello, {operator?.display_name} — here are your assigned tasks
          </p>
        </div>
        <button className="btn btn-ghost btn-sm" onClick={load} style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <RefreshCw size={14} /> Refresh
        </button>
      </div>

      {/* Summary chips */}
      {!loading && (
        <div style={{ display: 'flex', gap: '0.6rem', marginBottom: '1.25rem', flexWrap: 'wrap' }}>
          {[
            { label: 'Active', value: tasks.filter((t) => ['NEW', 'ASSIGNED', 'IN_PROGRESS', 'BACK_TO_DEVELOPER'].includes(t.status)).length, color: '#3b82f6' },
            { label: 'In Testing', value: tasks.filter((t) => ['DEVELOPER_COMPLETED', 'TESTING_L2', 'TEST_APPROVED', 'AUTOQA_RUNNING'].includes(t.status)).length, color: '#f59e0b' },
            { label: 'Failed — Fix Needed', value: tasks.filter((t) => ['FAILED', 'BACK_TO_DEVELOPER'].includes(t.status)).length, color: '#ef4444' },
            { label: 'Passed', value: tasks.filter((t) => ['PASSED', 'DELIVERY_COMPLETED'].includes(t.status)).length, color: '#10b981' },
          ].map((s) => (
            <div key={s.label} style={{ background: 'var(--bg-card)', border: '1px solid var(--border-color)', borderRadius: 'var(--radius-lg)', padding: '0.5rem 1rem', display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
              <span style={{ fontSize: '1.2rem', fontWeight: 800, color: s.color }}>{s.value}</span>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{s.label}</span>
            </div>
          ))}
        </div>
      )}

      {/* Error */}
      {error && (
        <div style={{ padding: '0.75rem 1rem', borderRadius: 'var(--radius-md)', background: 'var(--status-fail-bg)', color: 'var(--status-fail-text)', marginBottom: '1rem', fontSize: '0.875rem' }}>
          {error}
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
          <RefreshCw size={24} style={{ animation: 'spin 1s linear infinite', display: 'block', margin: '0 auto 0.75rem' }} />
          Loading your tasks...
        </div>
      )}

      {/* No tasks */}
      {!loading && tasks.length === 0 && (
        <div style={{ textAlign: 'center', padding: '4rem 2rem', background: 'var(--bg-card)', borderRadius: 'var(--radius-xl)', border: '1px solid var(--border-color)' }}>
          <ListTodo size={48} style={{ color: 'var(--text-muted)', opacity: 0.4, display: 'block', margin: '0 auto 1rem' }} />
          <h3 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '0.5rem' }}>No tasks assigned</h3>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>
            Your Project Manager will assign tasks here. Check back soon!
          </p>
        </div>
      )}

      {/* Task groups */}
      {!loading && tasks.length > 0 && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {statusGroups.map((group) => {
            const groupTasks = tasks.filter((t) => t.status === group.status);
            if (groupTasks.length === 0) return null;
            return (
              <div key={group.status}>
                <h3 style={{ fontSize: '0.85rem', fontWeight: 700, marginBottom: '0.75rem', color: group.urgent ? '#ef4444' : 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  {group.label}
                  <span style={{ fontSize: '0.72rem', fontWeight: 500, color: 'var(--text-muted)' }}>({groupTasks.length})</span>
                </h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
                  {groupTasks.map((task) => {
                    const isOverdue = task.target_date && new Date(task.target_date) < new Date() && !['PASSED', 'DELIVERY_COMPLETED'].includes(task.status);
                    return (
                      <motion.div
                        key={task.id}
                        whileHover={{ x: 3 }}
                        onClick={() => setSelectedId(task.id)}
                        style={{
                          background: 'var(--bg-card)',
                          border: `1px solid ${group.urgent ? '#ef444435' : 'var(--border-color)'}`,
                          borderLeft: `4px solid ${TASK_STATUS_COLORS[task.status]}`,
                          borderRadius: 'var(--radius-lg)',
                          padding: '1rem 1.25rem',
                          cursor: 'pointer',
                          transition: 'all 0.15s',
                        }}
                      >
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '1rem' }}>
                          <div style={{ flex: 1 }}>
                            <p style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: '0.2rem' }}>
                              {task.module}{task.feature ? ` › ${task.feature}` : ''}
                            </p>
                            <h4 style={{ fontSize: '0.95rem', fontWeight: 600, lineHeight: 1.35 }}>{task.title}</h4>
                          </div>
                          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '0.3rem', flexShrink: 0 }}>
                            <span style={{
                              fontSize: '0.68rem', fontWeight: 700, padding: '0.15rem 0.5rem',
                              borderRadius: 'var(--radius-full)',
                              backgroundColor: `${TASK_PRIORITY_COLORS[task.priority]}18`,
                              color: TASK_PRIORITY_COLORS[task.priority],
                              textTransform: 'uppercase',
                            }}>
                              {task.priority}
                            </span>
                            {isOverdue && (
                              <span style={{ fontSize: '0.68rem', color: '#ef4444', fontWeight: 700 }}>⚠ OVERDUE</span>
                            )}
                          </div>
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginTop: '0.6rem', flexWrap: 'wrap' }}>
                          <StatusChip status={task.status} />
                          {task.target_date && (
                            <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '0.2rem' }}>
                              <Clock size={11} /> {new Date(task.target_date).toLocaleDateString()}
                            </span>
                          )}
                          <span style={{ marginLeft: 'auto', fontSize: '0.75rem', color: 'var(--color-primary)', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                            View Details <ArrowRight size={12} />
                          </span>
                        </div>
                      </motion.div>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Detail Panel */}
      <AnimatePresence>
        {selectedId !== null && (
          <TaskDetailPanel
            taskId={selectedId}
            onClose={() => setSelectedId(null)}
            onUpdated={load}
            onNavigate={onNavigate}
          />
        )}
      </AnimatePresence>
    </div>
  );
}
