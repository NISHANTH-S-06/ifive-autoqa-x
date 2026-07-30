import React, { useContext, useEffect, useState } from 'react';
import { AuthContext } from '../authContext';
import { TestPlanEditor } from './TestPlanEditor';
import { TestPlanApproval } from './TestPlanApproval';
import { apiGet, apiPost } from '../services/api';
import { DataTable, Column } from './ui/DataTable';
import { StatusBadge } from './ui/StatusBadge';
import { StatCard } from './ui/StatCard';
import { Button } from './ui/Button';
import { Input } from './ui/Input';
import { Select } from './ui/Select';
import { Drawer } from './ui/Drawer';
import { JSONViewer } from './ui/JSONViewer';
import { 
  FileInput, RefreshCw, Sparkles, Play, Eye, 
  CheckCircle2, AlertCircle, Clock, ShieldAlert 
} from 'lucide-react';

export interface TaskImport {
  id: number;
  project_id: number;
  source_system: string;
  source_task_id: string;
  source_revision: number;
  source_status: string;
  project_name: string;
  module_name: string;
  title: string;
  description?: string;
  application_url: string;
  page_path: string;
  environment: string;
  expected_result?: string;
  acceptance_criteria?: string;
  test_data?: string;
  assigned_developer?: string;
  assigned_tester?: string;
  priority: string;
  developer_notes?: string;
  imported_at: string;
  last_synced_at: string;
  import_status: string;
  template_type?: string;
  approved_by?: string;
  approved_at?: string;
  linked_test_plan_id?: number;
  linked_run_id?: number;
  callback_status?: string;
  callback_error?: string;
}

export function TaskImportsCore() {
  const auth = useContext(AuthContext);
  const currentUsername = auth?.operator?.username || 'admin';

  const [imports, setImports] = useState<TaskImport[]>([]);
  const [loading, setLoading] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [actionId, setActionId] = useState<number | null>(null);
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [error, setError] = useState('');
  const [selectedTask, setSelectedTask] = useState<TaskImport | null>(null);

  const [editingPlanId, setEditingPlanId] = useState<number | null>(null);
  const [approvingPlanId, setApprovingPlanId] = useState<number | null>(null);

  const fetchImports = async () => {
    setLoading(true);
    setError('');
    try {
      const url = statusFilter
        ? `/api/task-imports?import_status=${encodeURIComponent(statusFilter)}`
        : '/api/task-imports';
      const data = await apiGet<TaskImport[]>(url);
      setImports(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error loading task imports');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void fetchImports();
  }, [statusFilter]);

  const handleSync = async () => {
    setSyncing(true);
    setError('');
    try {
      await apiPost('/api/task-imports/sync', {});
      await fetchImports();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Sync failed');
    } finally {
      setSyncing(false);
    }
  };

  const handleAnalyze = async (id: number) => {
    setActionId(id);
    setError('');
    try {
      const plan = await apiPost<any>(`/api/task-imports/${id}/generate-plan`, {});
      setEditingPlanId(plan.id);
      await fetchImports();
    } catch (err: any) {
      setError(err instanceof Error ? err.message : 'Generate Plan failed');
      await fetchImports();
    } finally {
      setActionId(null);
    }
  };

  const handleApprove = async (id: number) => {
    setActionId(id);
    setError('');
    try {
      const plans = await apiGet<any[]>(`/api/task-imports/${id}/plans`);
      if (plans.length > 0) {
        setApprovingPlanId(plans[0].id);
      } else {
        throw new Error('No plan found to approve');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load plan for approval');
    } finally {
      setActionId(null);
    }
  };

  const handleEditPlan = async (id: number) => {
    setActionId(id);
    setError('');
    try {
      const plans = await apiGet<any[]>(`/api/task-imports/${id}/plans`);
      if (plans.length > 0) {
        setEditingPlanId(plans[0].id);
      } else {
        throw new Error('No plan found to edit');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load plan for editing');
    } finally {
      setActionId(null);
    }
  };

  const handleRun = async (id: number) => {
    setActionId(id);
    setError('');
    try {
      await apiPost(`/api/task-imports/${id}/run`, {});
      await fetchImports();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Execution failed');
    } finally {
      setActionId(null);
    }
  };

  const columns: Column<TaskImport>[] = [
    { key: 'source_task_id', header: 'Task ID', render: (t) => <span style={{ fontWeight: 600, fontFamily: 'var(--font-mono)' }}>#{t.source_task_id} (r{t.source_revision})</span> },
    { key: 'title', header: 'Requirement Title', render: (t) => <span style={{ fontWeight: 600 }}>{t.title}</span> },
    { key: 'source_system', header: 'Source', render: (t) => <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{t.source_system}</span> },
    { key: 'assigned_developer', header: 'Assigned Dev', render: (t) => <span style={{ fontSize: '0.8rem' }}>{t.assigned_developer || 'Unassigned'}</span> },
    { key: 'import_status', header: 'Plan Status', render: (t) => <StatusBadge status={t.import_status} size="sm" /> },
    { key: 'last_synced_at', header: 'Last Synced', render: (t) => <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{t.last_synced_at ? new Date(t.last_synced_at).toLocaleTimeString() : '-'}</span> },
    { key: 'id', header: 'Actions', render: (item) => {
      const isDevSelf = Boolean(
        item.assigned_developer &&
          item.assigned_developer.toLowerCase() === currentUsername.toLowerCase()
      );

      return (
        <div style={{ display: 'flex', gap: '0.35rem', flexWrap: 'wrap' }}>
          <Button size="sm" variant="secondary" onClick={() => setSelectedTask(item)} leftIcon={<Eye size={13} />}>
            Inspect
          </Button>

          {item.import_status === 'DRAFT' && (
            <Button size="sm" variant="primary" onClick={() => void handleAnalyze(item.id)} isLoading={actionId === item.id} leftIcon={<Sparkles size={13} />}>
              AI Plan
            </Button>
          )}

          {item.import_status === 'PLAN_PREPARED' && (
            <>
              <Button size="sm" variant="secondary" onClick={() => void handleEditPlan(item.id)}>
                Edit
              </Button>
              <Button size="sm" variant="primary" onClick={() => void handleApprove(item.id)} disabled={isDevSelf} title={isDevSelf ? 'Developers cannot self-approve' : undefined}>
                {isDevSelf ? 'Self-Blocked' : 'Review'}
              </Button>
            </>
          )}

          {item.import_status === 'APPROVED' && (
            <Button size="sm" variant="primary" onClick={() => void handleRun(item.id)} isLoading={actionId === item.id} leftIcon={<Play size={13} />}>
              Run
            </Button>
          )}
        </div>
      );
    }}
  ];

  const totalTasks = imports.length;
  const approvedTasks = imports.filter(i => i.import_status === 'APPROVED').length;
  const pendingTasks = imports.filter(i => i.import_status === 'DRAFT' || i.import_status === 'PLAN_PREPARED').length;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      {/* Stat Cards */}
      <div className="grid grid-cols-3">
        <StatCard title="Total Synced Tasks" value={totalTasks} subtitle="Backlog requirement items" icon={FileInput} variant="primary" loading={loading} />
        <StatCard title="Pending Analysis" value={pendingTasks} subtitle="Draft & prepared plans" icon={Clock} variant="warning" loading={loading} />
        <StatCard title="Approved Plans" value={approvedTasks} subtitle="Execution-ready test plans" icon={CheckCircle2} variant="success" loading={loading} />
      </div>

      {error && <div className="state-panel state-error" role="alert">{error}</div>}

      {/* Main Table Card */}
      <div className="card" style={{ padding: '1.25rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem', flexWrap: 'wrap', gap: '0.75rem' }}>
          <div>
            <h3 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-main)' }}>
              Task Integration & Backlog Synchronization
            </h3>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              Synchronize backlog task requirements and convert them into structured test plans.
            </p>
          </div>

          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <Select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              style={{ width: '160px' }}
            >
              <option value="">All Statuses</option>
              <option value="DRAFT">DRAFT</option>
              <option value="PLAN_PREPARED">PLAN_PREPARED</option>
              <option value="APPROVED">APPROVED</option>
              <option value="RUNNING">RUNNING</option>
              <option value="COMPLETED">COMPLETED</option>
            </Select>

            <Button size="sm" variant="primary" onClick={handleSync} isLoading={syncing} leftIcon={<RefreshCw size={14} />}>
              Sync Backlog Tasks
            </Button>
          </div>
        </div>

        <DataTable
          columns={columns}
          data={imports}
          keyExtractor={(i) => i.id}
          loading={loading}
          emptyMessage="No task imports found. Click 'Sync Backlog Tasks' to fetch."
        />
      </div>

      {/* Selected Task Inspection Drawer */}
      {selectedTask && (
        <Drawer
          isOpen={true}
          onClose={() => setSelectedTask(null)}
          title={`Task #${selectedTask.source_task_id}: ${selectedTask.title}`}
          subtitle={`Source System: ${selectedTask.source_system} • Revision ${selectedTask.source_revision}`}
          width="680px"
        >
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div className="card" style={{ padding: '1rem', background: 'var(--bg-card-subtle)' }}>
              <div className="grid grid-cols-2" style={{ fontSize: '0.85rem', gap: '0.75rem' }}>
                <div><span style={{ color: 'var(--text-muted)' }}>Import Status:</span> <StatusBadge status={selectedTask.import_status} size="sm" /></div>
                <div><span style={{ color: 'var(--text-muted)' }}>App Path:</span> <code>{selectedTask.page_path}</code></div>
                <div><span style={{ color: 'var(--text-muted)' }}>Assigned Developer:</span> <strong>{selectedTask.assigned_developer || 'Unassigned'}</strong></div>
                <div><span style={{ color: 'var(--text-muted)' }}>Assigned Tester:</span> <strong>{selectedTask.assigned_tester || 'Unassigned'}</strong></div>
              </div>
            </div>

            <div>
              <h4 style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '0.5rem' }}>
                Acceptance Criteria & Requirement Text
              </h4>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-main)', background: 'var(--bg-card-subtle)', padding: '0.75rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)' }}>
                {selectedTask.acceptance_criteria || selectedTask.description || 'No detailed acceptance criteria provided.'}
              </p>
            </div>

            <JSONViewer data={selectedTask} title="Full Task Import Metadata Payload" maxHeight="300px" />
          </div>
        </Drawer>
      )}

      {editingPlanId && (
        <TestPlanEditor 
          planId={editingPlanId} 
          onClose={() => setEditingPlanId(null)} 
          onRefresh={fetchImports} 
        />
      )}
      
      {approvingPlanId && (
        <TestPlanApproval 
          planId={approvingPlanId} 
          onClose={() => setApprovingPlanId(null)} 
          onRefresh={fetchImports} 
        />
      )}
    </div>
  );
}
