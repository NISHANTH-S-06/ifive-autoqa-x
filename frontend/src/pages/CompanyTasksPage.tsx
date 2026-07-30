import React, { useCallback, useEffect, useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Plus, Search, RefreshCw, ChevronDown, X, Save,
  ClipboardList, User, Link2, FileText, Calendar,
  CheckCircle2, AlertCircle, Clock, Zap, Filter, Activity
} from 'lucide-react';
import { useAuth } from '../authContext';
import type { CompanyTaskListItem, CompanyTaskCreate, TaskStatus, TaskPriority, TaskSeverity, TaskBrowser, AutoQARunStatusRead } from '../types/companyTask';
import {
  TASK_STATUS_LABELS, TASK_STATUS_COLORS, TASK_PRIORITY_COLORS, TASK_SEVERITY_COLORS, TASK_STATUS_PIPELINE
} from '../types/companyTask';
import {
  listTasks, createTask, assignDeveloper, transitionStatus, approveAndRunAutoQA, getTaskRunStatus, markDeliveryComplete
} from '../services/companyTasks';
import { listOperators } from '../services/auth';
import type { Operator } from '../types/auth';

// ── Status chip ────────────────────────────────────────────────────────────
function StatusChip({ status }: { status: TaskStatus }) {
  const color = TASK_STATUS_COLORS[status];
  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center', gap: '0.3rem',
      fontSize: '0.72rem', fontWeight: 700, padding: '0.2rem 0.6rem',
      borderRadius: 'var(--radius-full)',
      backgroundColor: `${color}20`, color, border: `1px solid ${color}40`,
      letterSpacing: '0.04em', textTransform: 'uppercase', whiteSpace: 'nowrap',
    }}>
      {TASK_STATUS_LABELS[status]}
    </span>
  );
}

// ── Priority & Severity chips ──────────────────────────────────────────────
function PriorityChip({ priority }: { priority: TaskPriority }) {
  const color = TASK_PRIORITY_COLORS[priority];
  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center',
      fontSize: '0.68rem', fontWeight: 700, padding: '0.15rem 0.5rem',
      borderRadius: 'var(--radius-full)',
      backgroundColor: `${color}18`, color, border: `1px solid ${color}35`,
      letterSpacing: '0.05em', textTransform: 'uppercase',
    }}>
      {priority}
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
  if (status === 'FAILED' || status === 'BACK_TO_DEVELOPER') {
    activeIndex = TASK_STATUS_PIPELINE.indexOf('AUTOQA_RUNNING');
  } else if (status === 'CLOSED') {
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
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.25rem', minWidth: '64px' }}>
              <div style={{
                width: '24px', height: '24px', borderRadius: '50%',
                background: done ? '#10b981' : active ? color : 'var(--bg-card)',
                border: `2px solid ${done ? '#10b981' : active ? color : 'var(--border-color)'}`,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                transition: 'all 0.2s',
              }}>
                {done ? <CheckCircle2 size={12} color="#fff" /> :
                  active ? <div style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#fff' }} /> :
                    null}
              </div>
              <span style={{ fontSize: '0.55rem', fontWeight: active ? 700 : 400, color: active ? color : 'var(--text-muted)', textAlign: 'center', lineHeight: 1.1, whiteSpace: 'pre-wrap' }}>
                {label}
              </span>
            </div>
            {idx < TASK_STATUS_PIPELINE.length - 1 && (
              <div style={{ flex: 1, height: '2px', minWidth: '8px', background: done ? '#10b981' : 'var(--border-color)', marginBottom: '14px' }} />
            )}
          </React.Fragment>
        );
      })}
      {(isFail || isClosed) && (
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.25rem', minWidth: '64px', marginLeft: '8px' }}>
          <div style={{
            width: '24px', height: '24px', borderRadius: '50%',
            background: isFail ? '#ef444420' : '#6b728020',
            border: `2px solid ${isFail ? '#ef4444' : '#6b7280'}`,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            {isFail ? <AlertCircle size={12} color="#ef4444" /> : <CheckCircle2 size={12} color="#6b7280" />}
          </div>
          <span style={{ fontSize: '0.55rem', fontWeight: 700, color: isFail ? '#ef4444' : '#6b7280', textAlign: 'center' }}>
            {isFail ? 'FAIL' : 'Closed'}
          </span>
        </div>
      )}
    </div>
  );
}

// ── Task Card ──────────────────────────────────────────────────────────────
function TaskCard({
  task,
  onSelect,
  role,
}: {
  task: CompanyTaskListItem;
  onSelect: (task: CompanyTaskListItem) => void;
  role: string;
}) {
  const isOverdue = task.target_date && new Date(task.target_date) < new Date() &&
    !['PASSED', 'DELIVERY_COMPLETED', 'CLOSED'].includes(task.status);

  const isFail = task.status === 'FAILED' || task.status === 'BACK_TO_DEVELOPER';

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0 }}
      whileHover={{ y: -2, boxShadow: '0 8px 24px rgba(0,0,0,0.12)' }}
      onClick={() => onSelect(task)}
      style={{
        background: 'var(--bg-card)',
        border: `1px solid ${isFail ? '#ef444440' : task.status === 'PASSED' ? '#10b98140' : 'var(--border-color)'}`,
        borderRadius: 'var(--radius-lg)',
        padding: '1rem',
        cursor: 'pointer',
        transition: 'all 0.18s',
      }}
    >
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '0.75rem', marginBottom: '0.5rem' }}>
        <div style={{ flex: 1 }}>
          <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '0.2rem', display: 'flex', gap: '0.4rem', alignItems: 'center' }}>
            {task.module}{task.feature ? ` › ${task.feature}` : ''}
            {task.retest_count > 0 && <span style={{ color: '#ef4444', fontWeight: 600, fontSize: '0.7rem' }}> (Retest #{task.retest_count})</span>}
          </p>
          <h3 style={{ fontSize: '0.92rem', fontWeight: 600, color: 'var(--text-main)', lineHeight: 1.3 }}>
            {task.title}
          </h3>
        </div>
        <PriorityChip priority={task.priority} />
      </div>

      {/* Status pipeline */}
      <div style={{ marginBottom: '0.75rem' }}>
        <StatusPipeline status={task.status} />
      </div>

      {/* Footer */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
          <StatusChip status={task.status} />
          {task.assigned_developer && (
            <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              <User size={12} /> {task.assigned_developer.display_name}
            </span>
          )}
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          {isOverdue && (
            <span style={{ fontSize: '0.7rem', color: '#ef4444', display: 'flex', alignItems: 'center', gap: '0.2rem' }}>
              <Clock size={11} /> Overdue
            </span>
          )}
          {task.target_date && (
            <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
              {new Date(task.target_date).toLocaleDateString()}
            </span>
          )}
        </div>
      </div>
    </motion.div>
  );
}

// ── Create Task Modal ──────────────────────────────────────────────────────
function CreateTaskModal({
  onClose,
  onCreated,
  operators,
}: {
  onClose: () => void;
  onCreated: () => void;
  operators: Operator[];
}) {
  const developers = operators.filter(o => o.role === 'DEVELOPER' || o.role === 'ADMIN');
  const testers = operators.filter(o => o.role === 'TESTER' || o.role === 'APPROVER' || o.role === 'ADMIN');

  const [form, setForm] = useState<CompanyTaskCreate>({
    title: '',
    module: '',
    feature: '',
    description: '',
    target_url: '',
    expected_flow: '',
    acceptance_criteria: '',
    expected_result: '',
    api_endpoint: '',
    browser: 'CHROMIUM',
    environment: 'local',
    priority: 'MEDIUM',
    severity: 'MEDIUM',
    estimated_hours: undefined,
    assigned_developer_id: undefined,
    assigned_tester_id: undefined,
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const handle = (field: keyof CompanyTaskCreate) =>
    (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
      let value: any = e.target.value;
      if (field === 'assigned_developer_id' || field === 'assigned_tester_id') {
        value = value ? Number(value) : undefined;
      } else if (field === 'estimated_hours') {
        value = value ? parseFloat(value) : undefined;
      }
      setForm((prev) => ({ ...prev, [field]: value }));
    };

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.title.trim()) { setError('Task title is required.'); return; }
    setSaving(true); setError('');
    try {
      await createTask(form);
      onCreated();
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create task.');
    } finally {
      setSaving(false);
    }
  };

  const labelStyle: React.CSSProperties = { display: 'block', fontSize: '0.8rem', fontWeight: 600, marginBottom: '0.35rem', color: 'var(--text-main)' };
  const inputStyle: React.CSSProperties = { width: '100%', boxSizing: 'border-box' };

  return (
    <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '1rem' }}>
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        style={{ background: 'var(--bg-card)', borderRadius: 'var(--radius-xl)', width: '100%', maxWidth: '800px', maxHeight: '90vh', overflowY: 'auto', boxShadow: 'var(--shadow-xl)' }}
      >
        <div style={{ padding: '1.5rem', borderBottom: '1px solid var(--border-color)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <div style={{ width: '36px', height: '36px', borderRadius: 'var(--radius-md)', background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <ClipboardList size={18} color="#fff" />
            </div>
            <div>
              <h2 style={{ fontSize: '1.1rem', fontWeight: 700 }}>Create Company Task</h2>
              <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Enterprise workflow with AutoQA orchestration</p>
            </div>
          </div>
          <button className="btn btn-ghost btn-sm" onClick={onClose}><X size={18} /></button>
        </div>

        <form onSubmit={submit} style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {error && (
            <div style={{ padding: '0.75rem', borderRadius: 'var(--radius-md)', background: 'var(--status-fail-bg)', color: 'var(--status-fail-text)', fontSize: '0.82rem' }}>
              {error}
            </div>
          )}

          {/* Core Info */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <h3 style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--text-main)', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.5rem' }}>Core Information</h3>
            <div>
              <label style={labelStyle}>Task Title <span style={{ color: '#ef4444' }}>*</span></label>
              <input className="input" style={inputStyle} required value={form.title} onChange={handle('title')} placeholder="e.g. Verify Sales Order Creation" />
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <div>
                <label style={labelStyle}>Module</label>
                <input className="input" style={inputStyle} value={form.module ?? ''} onChange={handle('module')} placeholder="e.g. Sales" />
              </div>
              <div>
                <label style={labelStyle}>Feature</label>
                <input className="input" style={inputStyle} value={form.feature ?? ''} onChange={handle('feature')} placeholder="e.g. Create Order" />
              </div>
            </div>
            <div>
              <label style={labelStyle}>Description</label>
              <textarea className="input" style={{ ...inputStyle, resize: 'vertical', minHeight: '60px' }} value={form.description ?? ''} onChange={handle('description')} placeholder="Developer context..." />
            </div>
          </div>

          {/* AutoQA Inputs */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <h3 style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--color-primary)', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Zap size={14} /> AutoQA Execution Params
            </h3>
            
            <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr 1fr', gap: '1rem' }}>
              <div>
                <label style={labelStyle}>Target URL <span style={{ color: '#ef4444' }}>*</span></label>
                <input className="input" style={inputStyle} required value={form.target_url ?? ''} onChange={handle('target_url')} placeholder="https://..." />
              </div>
              <div>
                <label style={labelStyle}>Environment</label>
                <select className="input" style={inputStyle} value={form.environment} onChange={handle('environment')}>
                  <option value="local">Local</option>
                  <option value="staging">Staging</option>
                  <option value="qa">QA</option>
                </select>
              </div>
              <div>
                <label style={labelStyle}>Browser</label>
                <select className="input" style={inputStyle} value={form.browser} onChange={handle('browser')}>
                  <option value="CHROMIUM">Chromium</option>
                  <option value="FIREFOX">Firefox</option>
                  <option value="WEBKIT">WebKit</option>
                </select>
              </div>
            </div>

            <div>
              <label style={labelStyle}>Expected Flow <span style={{ color: '#ef4444' }}>*</span></label>
              <textarea
                className="input"
                required
                style={{ ...inputStyle, resize: 'vertical', minHeight: '80px', fontFamily: 'monospace', fontSize: '0.82rem' }}
                value={form.expected_flow ?? ''}
                onChange={handle('expected_flow')}
                placeholder="Home → Products → iFive IoT → Page Opens"
              />
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <div>
                <label style={labelStyle}>Acceptance Criteria</label>
                <textarea className="input" style={{ ...inputStyle, resize: 'vertical', minHeight: '60px' }} value={form.acceptance_criteria ?? ''} onChange={handle('acceptance_criteria')} placeholder={`"Success" is visible`} />
              </div>
              <div>
                <label style={labelStyle}>Expected Final State</label>
                <textarea className="input" style={{ ...inputStyle, resize: 'vertical', minHeight: '60px' }} value={form.expected_result ?? ''} onChange={handle('expected_result')} placeholder="Order appears in list" />
              </div>
            </div>
          </div>

          {/* Meta & Assign */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <h3 style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--text-main)', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.5rem' }}>Assignments & Meta</h3>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr 1fr', gap: '1rem' }}>
              <div>
                <label style={labelStyle}>Priority</label>
                <select className="input" style={inputStyle} value={form.priority} onChange={handle('priority')}>
                  <option value="LOW">Low</option>
                  <option value="MEDIUM">Medium</option>
                  <option value="HIGH">High</option>
                  <option value="CRITICAL">Critical</option>
                </select>
              </div>
              <div>
                <label style={labelStyle}>Severity</label>
                <select className="input" style={inputStyle} value={form.severity} onChange={handle('severity')}>
                  <option value="LOW">Low</option>
                  <option value="MEDIUM">Medium</option>
                  <option value="HIGH">High</option>
                  <option value="CRITICAL">Critical</option>
                </select>
              </div>
              <div>
                <label style={labelStyle}>Est. Hours</label>
                <input className="input" style={inputStyle} type="number" step="0.5" value={form.estimated_hours ?? ''} onChange={handle('estimated_hours')} placeholder="e.g. 2.5" />
              </div>
              <div>
                <label style={labelStyle}>Target Date</label>
                <input className="input" style={inputStyle} type="date" value={form.target_date ? String(form.target_date).substring(0, 10) : ''} onChange={handle('target_date')} />
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <div>
                <label style={labelStyle}>Assign Developer</label>
                <select className="input" style={inputStyle} value={form.assigned_developer_id ?? ''} onChange={handle('assigned_developer_id')}>
                  <option value="">Unassigned</option>
                  {developers.map((d) => (
                    <option key={d.id} value={d.id}>{d.display_name}</option>
                  ))}
                </select>
              </div>
              <div>
                <label style={labelStyle}>Assign Tester (L2)</label>
                <select className="input" style={inputStyle} value={form.assigned_tester_id ?? ''} onChange={handle('assigned_tester_id')}>
                  <option value="">Unassigned</option>
                  {testers.map((t) => (
                    <option key={t.id} value={t.id}>{t.display_name}</option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'flex-end', paddingTop: '1rem', borderTop: '1px solid var(--border-color)' }}>
            <button type="button" className="btn btn-secondary" onClick={onClose} disabled={saving}>Cancel</button>
            <button type="submit" className="btn btn-primary" disabled={saving} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Save size={15} /> {saving ? 'Creating...' : 'Create Task'}
            </button>
          </div>
        </form>
      </motion.div>
    </div>
  );
}

// ── Live Run Poller Component ──────────────────────────────────────────────
function LiveRunPoller({ taskId, initialStatus, onComplete }: { taskId: number; initialStatus: string; onComplete: () => void }) {
  const [run, setRun] = useState<AutoQARunStatusRead | null>(null);
  
  useEffect(() => {
    let active = true;
    const poll = async () => {
      try {
        const data = await getTaskRunStatus(taskId);
        if (!active) return;
        setRun(data);
        if (data.task_status !== 'AUTOQA_RUNNING') {
          onComplete();
        }
      } catch (err) {
        console.error(err);
      }
    };
    
    // poll immediately, then every 2s
    void poll();
    const interval = setInterval(poll, 2000);
    return () => { active = false; clearInterval(interval); };
  }, [taskId, onComplete]);

  if (!run || run.task_status !== 'AUTOQA_RUNNING') {
    return null;
  }

  const percent = run.total_steps > 0 ? Math.round((run.completed_steps / run.total_steps) * 100) : 0;

  return (
    <div style={{ marginTop: '1rem', padding: '1rem', borderRadius: 'var(--radius-md)', background: '#06b6d410', border: '1px solid #06b6d440' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
        <h4 style={{ fontSize: '0.85rem', fontWeight: 700, color: '#06b6d4', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <Activity size={14} style={{ animation: 'pulse 2s infinite' }} /> AutoQA Running
        </h4>
        <span style={{ fontSize: '0.8rem', fontWeight: 600, color: '#06b6d4' }}>{percent}%</span>
      </div>
      <div style={{ width: '100%', height: '6px', background: '#06b6d420', borderRadius: '3px', overflow: 'hidden', marginBottom: '0.5rem' }}>
        <div style={{ width: `${percent}%`, height: '100%', background: '#06b6d4', transition: 'width 0.5s ease-out' }} />
      </div>
      <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
        {run.progress || `Completed ${run.completed_steps} of ${run.total_steps} steps`}
      </p>
    </div>
  );
}

// ── Main Page ──────────────────────────────────────────────────────────────
export function CompanyTasksPage() {
  const { operator } = useAuth();
  const role = operator?.role ?? 'VIEWER';

  const [tasks, setTasks] = useState<CompanyTaskListItem[]>([]);
  const [operators, setOperators] = useState<Operator[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [search, setSearch] = useState('');
  const [filterStatus, setFilterStatus] = useState('');
  const [filterPriority, setFilterPriority] = useState('');
  const [showCreate, setShowCreate] = useState(false);
  const [selectedTask, setSelectedTask] = useState<CompanyTaskListItem | null>(null);
  
  // Track drawer task refreshing
  const refreshSelected = useRef(false);

  const load = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const [taskList, ops] = await Promise.all([
        listTasks({ status: filterStatus || undefined, priority: filterPriority || undefined }),
        listOperators(),
      ]);
      setTasks(taskList);
      setOperators(ops);
      
      if (refreshSelected.current && selectedTask) {
        const updated = taskList.find(t => t.id === selectedTask.id);
        if (updated) setSelectedTask(updated);
        refreshSelected.current = false;
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load tasks.');
    } finally {
      setLoading(false);
    }
  }, [filterStatus, filterPriority, selectedTask]);

  useEffect(() => { void load(); }, [load]);

  const handleApproveAutoQA = async (id: number) => {
    try {
      await approveAndRunAutoQA(id);
      refreshSelected.current = true;
      void load();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to trigger AutoQA.');
    }
  };

  const handleMarkDeliveryComplete = async (id: number) => {
    try {
      await markDeliveryComplete(id);
      refreshSelected.current = true;
      void load();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to mark as delivered.');
    }
  };

  const filtered = tasks.filter((t) =>
    !search || t.title.toLowerCase().includes(search.toLowerCase()) ||
    (t.module ?? '').toLowerCase().includes(search.toLowerCase()) ||
    (t.feature ?? '').toLowerCase().includes(search.toLowerCase())
  );

  const groups: { label: string; status: TaskStatus; color: string }[] = (
    [
      { label: 'New', status: 'NEW' as TaskStatus, color: TASK_STATUS_COLORS['NEW'] },
      { label: 'Assigned', status: 'ASSIGNED' as TaskStatus, color: TASK_STATUS_COLORS['ASSIGNED'] },
      { label: 'In Progress', status: 'IN_PROGRESS' as TaskStatus, color: TASK_STATUS_COLORS['IN_PROGRESS'] },
      { label: 'Dev Completed', status: 'DEVELOPER_COMPLETED' as TaskStatus, color: TASK_STATUS_COLORS['DEVELOPER_COMPLETED'] },
      { label: 'Testing L2', status: 'TESTING_L2' as TaskStatus, color: TASK_STATUS_COLORS['TESTING_L2'] },
      { label: 'Test Approved', status: 'TEST_APPROVED' as TaskStatus, color: TASK_STATUS_COLORS['TEST_APPROVED'] },
      { label: 'AutoQA Running', status: 'AUTOQA_RUNNING' as TaskStatus, color: TASK_STATUS_COLORS['AUTOQA_RUNNING'] },
      { label: 'Passed ✅', status: 'PASSED' as TaskStatus, color: TASK_STATUS_COLORS['PASSED'] },
      { label: 'Failed ❌', status: 'FAILED' as TaskStatus, color: TASK_STATUS_COLORS['FAILED'] },
      { label: 'Back to Dev ⚠️', status: 'BACK_TO_DEVELOPER' as TaskStatus, color: TASK_STATUS_COLORS['BACK_TO_DEVELOPER'] },
      { label: 'Delivered 🚀', status: 'DELIVERY_COMPLETED' as TaskStatus, color: TASK_STATUS_COLORS['DELIVERY_COMPLETED'] },
      { label: 'Closed', status: 'CLOSED' as TaskStatus, color: TASK_STATUS_COLORS['CLOSED'] },
    ] as { label: string; status: TaskStatus; color: string }[]
  ).filter((g) => filtered.some((t) => t.status === g.status));

  return (
    <div style={{ maxWidth: '1400px' }}>
      {/* Page Header */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 800, display: 'flex', alignItems: 'center', gap: '0.625rem' }}>
            <ClipboardList size={24} style={{ color: 'var(--color-primary)' }} /> Company Tasks
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem', marginTop: '0.25rem' }}>
            Enterprise task lifecycle — from delivery to AutoQA orchestration
          </p>
        </div>
        <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
          <button className="btn btn-ghost btn-sm" onClick={load} title="Refresh" style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <RefreshCw size={14} />
          </button>
          {(role === 'PROJECT_MANAGER' || role === 'ADMIN') && (
            <button className="btn btn-primary" onClick={() => setShowCreate(true)} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Plus size={16} /> Create Task
            </button>
          )}
        </div>
      </div>

      {/* Stats row */}
      <div style={{ display: 'flex', gap: '0.75rem', marginBottom: '1.25rem', flexWrap: 'wrap' }}>
        {[
          { label: 'Total', value: tasks.length, color: '#64748b' },
          { label: 'In Progress', value: tasks.filter((t) => ['IN_PROGRESS', 'BACK_TO_DEVELOPER'].includes(t.status)).length, color: '#3b82f6' },
          { label: 'Ready for Test', value: tasks.filter((t) => ['DEVELOPER_COMPLETED', 'TESTING_L2'].includes(t.status)).length, color: '#f59e0b' },
          { label: 'AutoQA Running', value: tasks.filter((t) => ['TEST_APPROVED', 'AUTOQA_RUNNING'].includes(t.status)).length, color: '#06b6d4' },
          { label: 'Passed', value: tasks.filter((t) => t.status === 'PASSED').length, color: '#10b981' },
          { label: 'Failed', value: tasks.filter((t) => t.status === 'FAILED').length, color: '#ef4444' },
        ].map((stat) => (
          <div key={stat.label} style={{
            background: 'var(--bg-card)', border: '1px solid var(--border-color)', borderRadius: 'var(--radius-lg)',
            padding: '0.6rem 1rem', display: 'flex', flexDirection: 'column', alignItems: 'center', minWidth: '80px',
          }}>
            <span style={{ fontSize: '1.4rem', fontWeight: 800, color: stat.color }}>{stat.value}</span>
            <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 500 }}>{stat.label}</span>
          </div>
        ))}
      </div>

      {/* Filters */}
      <div style={{ display: 'flex', gap: '0.75rem', marginBottom: '1.25rem', flexWrap: 'wrap', alignItems: 'center' }}>
        <div style={{ position: 'relative', flex: '1', minWidth: '200px', maxWidth: '340px' }}>
          <Search size={15} style={{ position: 'absolute', left: '0.75rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)', pointerEvents: 'none' }} />
          <input className="input" style={{ paddingLeft: '2.2rem', width: '100%', boxSizing: 'border-box' }} placeholder="Search tasks..." value={search} onChange={(e) => setSearch(e.target.value)} />
        </div>
        <select className="input" style={{ minWidth: '130px' }} value={filterStatus} onChange={(e) => setFilterStatus(e.target.value)}>
          <option value="">All Statuses</option>
          {Object.entries(TASK_STATUS_LABELS).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
        </select>
        <select className="input" style={{ minWidth: '120px' }} value={filterPriority} onChange={(e) => setFilterPriority(e.target.value)}>
          <option value="">All Priorities</option>
          {['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'].map((p) => <option key={p} value={p}>{p}</option>)}
        </select>
        {(filterStatus || filterPriority || search) && (
          <button className="btn btn-ghost btn-sm" onClick={() => { setFilterStatus(''); setFilterPriority(''); setSearch(''); }} style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
            <X size={13} /> Clear
          </button>
        )}
      </div>

      {/* Error */}
      {error && (
        <div style={{ padding: '0.75rem 1rem', borderRadius: 'var(--radius-md)', background: 'var(--status-fail-bg)', color: 'var(--status-fail-text)', marginBottom: '1rem', fontSize: '0.875rem' }}>
          {error}
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
          <RefreshCw size={24} style={{ animation: 'spin 1s linear infinite', marginBottom: '0.75rem', display: 'block', margin: '0 auto 0.75rem' }} />
          Loading tasks...
        </div>
      )}

      {/* No tasks */}
      {!loading && filtered.length === 0 && (
        <div style={{ textAlign: 'center', padding: '4rem 2rem', background: 'var(--bg-card)', borderRadius: 'var(--radius-xl)', border: '1px solid var(--border-color)' }}>
          <ClipboardList size={48} style={{ color: 'var(--text-muted)', marginBottom: '1rem', opacity: 0.5 }} />
          <h3 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '0.5rem' }}>No tasks found</h3>
          <p style={{ color: 'var(--text-muted)', marginBottom: '1.5rem' }}>
            {role === 'PROJECT_MANAGER' || role === 'ADMIN'
              ? 'Create your first enterprise task to start the workflow.'
              : 'No tasks match your current filters.'}
          </p>
          {(role === 'PROJECT_MANAGER' || role === 'ADMIN') && (
            <button className="btn btn-primary" onClick={() => setShowCreate(true)} style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem' }}>
              <Plus size={16} /> Create First Task
            </button>
          )}
        </div>
      )}

      {/* Task groups */}
      {!loading && filtered.length > 0 && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {groups.map((group) => {
            const groupTasks = filtered.filter((t) => t.status === group.status);
            if (groupTasks.length === 0) return null;
            return (
              <div key={group.status}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem' }}>
                  <div style={{ width: '10px', height: '10px', borderRadius: '50%', background: group.color }} />
                  <h3 style={{ fontSize: '0.85rem', fontWeight: 700, color: group.color, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                    {group.label}
                  </h3>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 500 }}>({groupTasks.length})</span>
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(380px, 1fr))', gap: '0.75rem' }}>
                  <AnimatePresence>
                    {groupTasks.map((task) => (
                      <TaskCard
                        key={task.id}
                        task={task}
                        onSelect={setSelectedTask}
                        role={role}
                      />
                    ))}
                  </AnimatePresence>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Create Modal */}
      <AnimatePresence>
        {showCreate && (
          <CreateTaskModal onClose={() => setShowCreate(false)} onCreated={load} operators={operators} />
        )}
      </AnimatePresence>

      {/* Task Detail Drawer */}
      <AnimatePresence>
        {selectedTask && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', zIndex: 1000 }}
            onClick={() => setSelectedTask(null)}
          >
            <motion.div
              initial={{ x: '100%' }}
              animate={{ x: 0 }}
              exit={{ x: '100%' }}
              transition={{ type: 'spring', stiffness: 300, damping: 30 }}
              onClick={(e) => e.stopPropagation()}
              style={{
                position: 'absolute', right: 0, top: 0, bottom: 0, width: '480px', maxWidth: '90vw',
                background: 'var(--bg-card)', overflowY: 'auto', padding: '1.5rem',
                boxShadow: '-8px 0 32px rgba(0,0,0,0.2)',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem' }}>
                <h2 style={{ fontSize: '1.1rem', fontWeight: 700 }}>Task Overview</h2>
                <button className="btn btn-ghost btn-sm" onClick={() => setSelectedTask(null)}><X size={18} /></button>
              </div>
              <StatusPipeline status={selectedTask.status} />
              
              <div style={{ marginTop: '1.25rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <div>
                  <h3 style={{ fontSize: '1.15rem', fontWeight: 700, lineHeight: 1.3 }}>{selectedTask.title}</h3>
                  {selectedTask.module && <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>{selectedTask.module}{selectedTask.feature ? ` › ${selectedTask.feature}` : ''}</p>}
                </div>
                
                <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                  <StatusChip status={selectedTask.status} />
                  <PriorityChip priority={selectedTask.priority} />
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', background: 'var(--bg-base)', padding: '1rem', borderRadius: 'var(--radius-lg)' }}>
                  {selectedTask.assigned_developer && (
                    <div>
                      <p style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.25rem' }}>Developer</p>
                      <p style={{ fontSize: '0.85rem', fontWeight: 600 }}>{selectedTask.assigned_developer.display_name}</p>
                    </div>
                  )}
                  {selectedTask.assigned_tester && (
                    <div>
                      <p style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.25rem' }}>QA Tester</p>
                      <p style={{ fontSize: '0.85rem', fontWeight: 600 }}>{selectedTask.assigned_tester.display_name}</p>
                    </div>
                  )}
                  {selectedTask.target_date && (
                    <div>
                      <p style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.25rem' }}>Target Date</p>
                      <p style={{ fontSize: '0.85rem' }}>{new Date(selectedTask.target_date).toLocaleDateString()}</p>
                    </div>
                  )}
                  <div>
                    <p style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.25rem' }}>Platform</p>
                    <p style={{ fontSize: '0.85rem' }}>{selectedTask.browser} / {selectedTask.environment}</p>
                  </div>
                </div>

                {/* AutoQA Status block */}
                {selectedTask.status === 'AUTOQA_RUNNING' && (
                  <LiveRunPoller 
                    taskId={selectedTask.id} 
                    initialStatus={selectedTask.status} 
                    onComplete={() => { refreshSelected.current = true; void load(); }}
                  />
                )}

                {selectedTask.autoqa_result && selectedTask.status !== 'AUTOQA_RUNNING' && (
                  <div style={{ padding: '1rem', borderRadius: 'var(--radius-md)', background: selectedTask.autoqa_result === 'PASS' ? '#10b98115' : '#ef444415', border: `1px solid ${selectedTask.autoqa_result === 'PASS' ? '#10b98140' : '#ef444440'}` }}>
                    <p style={{ fontSize: '0.8rem', fontWeight: 700, color: selectedTask.autoqa_result === 'PASS' ? '#10b981' : '#ef4444', display: 'flex', alignItems: 'center', gap: '0.4rem', marginBottom: '0.25rem' }}>
                      {selectedTask.autoqa_result === 'PASS' ? <CheckCircle2 size={16} /> : <AlertCircle size={16} />}
                      AutoQA Result: {selectedTask.autoqa_result}
                    </p>
                    {/* The backend provides autoqa_notes now */}
                  </div>
                )}
              </div>

              {/* Action Buttons */}
              <div style={{ marginTop: '2rem', paddingTop: '1.25rem', borderTop: '1px solid var(--border-color)', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {selectedTask.status === 'TESTING_L2' && (role === 'TESTER' || role === 'APPROVER' || role === 'ADMIN') && (
                  <button
                    className="btn btn-primary"
                    style={{ width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem', padding: '0.75rem' }}
                    onClick={() => handleApproveAutoQA(selectedTask.id)}
                  >
                    <Zap size={16} /> Approve & Run AutoQA Orchestration
                  </button>
                )}

                {selectedTask.status === 'PASSED' && (role === 'PROJECT_MANAGER' || role === 'ADMIN') && (
                  <button
                    className="btn btn-primary"
                    style={{ width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem', background: '#059669', padding: '0.75rem' }}
                    onClick={() => handleMarkDeliveryComplete(selectedTask.id)}
                  >
                    <CheckCircle2 size={16} /> Mark Delivery Complete
                  </button>
                )}
                
                <p style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textAlign: 'center' }}>
                  ID: CT-{selectedTask.id}
                </p>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
