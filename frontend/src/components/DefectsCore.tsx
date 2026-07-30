import React, { type FormEvent, useEffect, useMemo, useState } from 'react';
import { useAuth } from '../authContext';
import { fetchAutomatedRunCases, fetchAutomatedRuns } from '../services/automatedExecution';
import {
  addDefectComment,
  assignDefect,
  closeDefect,
  createDefect,
  createDefectFromRun,
  createDefectRetest,
  fetchDefectComments,
  fetchDefectEvidence,
  fetchDefectHistory,
  fetchDefects,
  fetchDefectTraceability,
  fixDefect,
  readyForRetest,
  rejectDefect,
  startDefect,
  triageDefect,
  updateDefect,
} from '../services/defects';
import { fetchTestProjects } from '../services/testManagement';
import type { AutomatedRun } from '../types/automatedExecution';
import type { Defect, DefectComment, DefectEvidenceLink, DefectHistory, DefectTraceability } from '../types/defect';
import type { TestProject } from '../types/testManagement';
import { DataTable, Column } from './ui/DataTable';
import { StatusBadge } from './ui/StatusBadge';
import { StatCard } from './ui/StatCard';
import { Button } from './ui/Button';
import { Input } from './ui/Input';
import { Select } from './ui/Select';
import { FormField } from './ui/FormField';
import { Modal } from './ui/Modal';
import { Drawer } from './ui/Drawer';
import { JSONViewer } from './ui/JSONViewer';
import {
  Bug, AlertTriangle, CheckCircle2, Clock, Plus,
  RefreshCw, Filter, Eye, MessageSquare, ShieldAlert, Layers
} from 'lucide-react';

const levels = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'];
const statusFilters = ['', 'NEW', 'TRIAGED', 'ASSIGNED', 'IN_PROGRESS', 'FIXED', 'READY_FOR_RETEST', 'RETEST_PASSED', 'REOPENED', 'CLOSED', 'REJECTED', 'DUPLICATE'];

export function DefectsCore() {
  const { operator } = useAuth();
  const [defects, setDefects] = useState<Defect[]>([]);
  const [projects, setProjects] = useState<TestProject[]>([]);
  const [runs, setRuns] = useState<AutomatedRun[]>([]);
  const [selected, setSelected] = useState<Defect | null>(null);
  const [comments, setComments] = useState<DefectComment[]>([]);
  const [history, setHistory] = useState<DefectHistory[]>([]);
  const [evidence, setEvidence] = useState<DefectEvidenceLink[]>([]);
  const [trace, setTrace] = useState<DefectTraceability | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);

  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  const [query, setQuery] = useState({ search: '', status: '' });
  const [form, setForm] = useState({ title: '', project_id: 0, severity: 'MEDIUM', priority: 'MEDIUM', description: '' });
  const [comment, setComment] = useState('');
  const [resolution, setResolution] = useState('');
  const [assignee, setAssignee] = useState(String(operator.id));
  const [retest, setRetest] = useState({ result_status: 'PASSED', notes: '' });
  const [runId, setRunId] = useState(0);

  const canCreate = ['TESTER', 'ADMIN'].includes(operator.role);
  const canReview = ['APPROVER', 'ADMIN'].includes(operator.role);
  const canRetest = ['TESTER', 'ADMIN'].includes(operator.role);
  const failedRuns = useMemo(() => runs.filter((run) => ['FAILED', 'TIMED_OUT', 'BLOCKED'].includes(run.status)), [runs]);

  const load = async () => {
    setLoading(true); setError('');
    try {
      const params = new URLSearchParams();
      if (query.search.trim()) params.set('search', query.search.trim());
      if (query.status) params.set('status', query.status);
      const [defectList, projectList, runList] = await Promise.all([
        fetchDefects(params.size ? `?${params.toString()}` : ''),
        fetchTestProjects('?limit=100').catch(() => ({ items: [] })),
        fetchAutomatedRuns('?limit=100').catch(() => ({ items: [] })),
      ]);
      setDefects(defectList.items ?? []);
      setProjects(projectList.items ?? []);
      setRuns(runList.items ?? []);
      const firstProject = projectList.items?.[0];
      setForm((current) => ({ ...current, project_id: current.project_id || firstProject?.id || 0 }));
      setRunId((current) => current || (runList.items ?? []).find((run) => ['FAILED', 'TIMED_OUT', 'BLOCKED'].includes(run.status))?.id || 0);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Unable to load defects.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { void load(); }, []);

  const openDefect = async (item: Defect) => {
    setSelected(item);
    const [nextComments, nextHistory, nextEvidence, nextTrace] = await Promise.all([
      fetchDefectComments(item.id).catch(() => []),
      fetchDefectHistory(item.id).catch(() => []),
      fetchDefectEvidence(item.id).catch(() => []),
      fetchDefectTraceability(item.id).catch(() => null),
    ]);
    setComments(nextComments);
    setHistory(nextHistory);
    setEvidence(nextEvidence);
    setTrace(nextTrace);
    setResolution(item.resolution ?? '');
    setAssignee(String(item.assigned_to ?? operator.id));
  };

  const refreshSelected = async (item: Defect) => {
    await load();
    await openDefect(item);
  };

  const submitDefect = async (event: FormEvent) => {
    event.preventDefault();
    if (submitting) return;
    setSubmitting(true); setError('');
    try {
      const created = await createDefect({ ...form, project_id: Number(form.project_id), description: form.description || null });
      setForm((current) => ({ ...current, title: '', description: '' }));
      setMessage(`Defect ${created.defect_key} logged successfully.`);
      setShowCreateModal(false);
      await refreshSelected(created);
    } catch (reason) { setError(reason instanceof Error ? reason.message : 'Defect creation failed.'); }
    finally { setSubmitting(false); }
  };

  const createFromRun = async () => {
    if (!runId) return;
    setSubmitting(true); setError('');
    try {
      const runCases = await fetchAutomatedRunCases(runId).catch(() => []);
      const failedCase = runCases.find((item) => ['FAILED', 'BLOCKED'].includes(item.status));
      const base = { automated_run_id: runId, automated_run_case_id: failedCase?.id, source_type: failedCase ? 'AUTOMATED_RUN_CASE' : 'AUTOMATED_RUN', severity: 'HIGH', priority: 'HIGH' };
      const created = await createDefectFromRun({ ...base, confirm: true });
      if ('defect_key' in created) {
        setMessage(`Created ${created.defect_key} from failed run #${runId}.`);
        await refreshSelected(created);
      }
    } catch (reason) { setError(reason instanceof Error ? reason.message : 'Failed-run defect creation failed.'); }
    finally { setSubmitting(false); }
  };

  const lifecycle = async (kind: string) => {
    if (!selected) return;
    try {
      let next: Defect;
      if (kind === 'triage') next = await triageDefect(selected.id);
      else if (kind === 'assign') next = await assignDefect(selected.id, Number(assignee));
      else if (kind === 'start') next = await startDefect(selected.id);
      else if (kind === 'fix') next = await fixDefect(selected.id);
      else if (kind === 'ready') next = await readyForRetest(selected.id);
      else if (kind === 'close') next = await closeDefect(selected.id, resolution);
      else next = await rejectDefect(selected.id, resolution || 'Rejected after review.');
      setMessage(`${next.defect_key} updated to ${next.status}.`);
      await refreshSelected(next);
    } catch (reason) { setError(reason instanceof Error ? reason.message : 'Defect lifecycle action failed.'); }
  };

  const saveComment = async () => {
    if (!selected || !comment.trim()) return;
    try {
      await addDefectComment(selected.id, comment);
      setComment('');
      await openDefect(selected);
    } catch (reason) { setError(reason instanceof Error ? reason.message : 'Comment rejected.'); }
  };

  const saveRetest = async () => {
    if (!selected) return;
    try {
      await createDefectRetest(selected.id, retest);
      setMessage('Defect retest result recorded.');
      await openDefect({ ...selected, status: retest.result_status === 'PASSED' ? 'RETEST_PASSED' : 'REOPENED' });
      await load();
    } catch (reason) { setError(reason instanceof Error ? reason.message : 'Retest recording failed.'); }
  };

  const totalDefects = defects.length;
  const criticalDefects = defects.filter(d => d.severity === 'CRITICAL' || d.severity === 'HIGH').length;
  const openDefects = defects.filter(d => !['CLOSED', 'REJECTED'].includes(d.status)).length;
  const fixedDefects = defects.filter(d => d.status === 'CLOSED' || d.status === 'RETEST_PASSED').length;

  const columns: Column<Defect>[] = [
    { key: 'defect_key', header: 'Defect ID', render: (d) => <span style={{ fontWeight: 600, fontFamily: 'var(--font-mono)', color: 'var(--color-danger)' }}>{d.defect_key}</span> },
    { key: 'title', header: 'Summary Title', render: (d) => <span style={{ fontWeight: 600 }}>{d.title}</span> },
    { key: 'severity', header: 'Severity', render: (d) => (
      <span className="badge" style={{
        backgroundColor: d.severity === 'CRITICAL' || d.severity === 'HIGH' ? 'var(--status-rejected-bg)' : 'var(--status-draft-bg)',
        color: d.severity === 'CRITICAL' || d.severity === 'HIGH' ? 'var(--status-rejected-text)' : 'var(--status-draft-text)'
      }}>
        {d.severity}
      </span>
    )},
    { key: 'status', header: 'Status', render: (d) => <StatusBadge status={d.status} size="sm" /> },
    { key: 'assigned_to', header: 'Assignee', render: (d) => <span style={{ fontSize: '0.8rem' }}>{d.assigned_to ? `Operator #${d.assigned_to}` : 'Unassigned'}</span> },
    { key: 'updated_at', header: 'Updated', render: (d) => <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{d.updated_at ? new Date(d.updated_at).toLocaleTimeString() : '-'}</span> },
    { key: 'id', header: 'Actions', render: (d) => (
      <Button size="sm" variant="secondary" onClick={() => void openDefect(d)} leftIcon={<Eye size={13} />}>
        Inspect
      </Button>
    )}
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      {/* KPI Stat Cards */}
      <div className="grid grid-cols-4">
        <StatCard title="Total Defects" value={totalDefects} subtitle="All tracked defects" icon={Bug} variant="primary" loading={loading} />
        <StatCard title="Open Defects" value={openDefects} subtitle="Active defect lifecycle" icon={AlertTriangle} variant="warning" loading={loading} />
        <StatCard title="Critical / High" value={criticalDefects} subtitle="High severity items" icon={ShieldAlert} variant="danger" loading={loading} />
        <StatCard title="Resolved / Closed" value={fixedDefects} subtitle="Verified fixes" icon={CheckCircle2} variant="success" loading={loading} />
      </div>

      {error && <div className="state-panel state-error" role="alert">{error}</div>}
      {message && <div className="state-panel" role="status">{message}</div>}

      {/* Main Table Card & Filters */}
      <div className="card" style={{ padding: '1.25rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem', flexWrap: 'wrap', gap: '0.75rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <Input
              placeholder="Search defects..."
              value={query.search}
              onChange={(e) => setQuery({ ...query, search: e.target.value })}
              style={{ width: '220px' }}
            />
            <Select
              value={query.status}
              onChange={(e) => setQuery({ ...query, status: e.target.value })}
              style={{ width: '160px' }}
            >
              {statusFilters.map((st) => (
                <option key={st || 'ALL'} value={st}>{st || 'All Statuses'}</option>
              ))}
            </Select>
            <Button size="sm" variant="secondary" onClick={load} leftIcon={<Filter size={14} />}>
              Filter
            </Button>
          </div>

          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <Button size="sm" variant="secondary" onClick={load} isLoading={loading} leftIcon={<RefreshCw size={14} />}>
              Refresh
            </Button>
            {failedRuns.length > 0 && (
              <Button size="sm" variant="secondary" onClick={createFromRun} leftIcon={<Bug size={14} />}>
                Import From Failed Run
              </Button>
            )}
            {canCreate && (
              <Button size="sm" variant="primary" onClick={() => setShowCreateModal(true)} leftIcon={<Plus size={14} />}>
                Create Defect
              </Button>
            )}
          </div>
        </div>

        <DataTable
          columns={columns}
          data={defects}
          keyExtractor={(d) => d.id}
          loading={loading}
          emptyMessage="No defect records found matching current criteria."
        />
      </div>

      {/* Create Defect Modal */}
      <Modal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        title="Log New Quality Defect"
        subtitle="Record defect details, severity, priority, and link to a test project"
        footer={(
          <>
            <Button variant="secondary" onClick={() => setShowCreateModal(false)}>Cancel</Button>
            <Button variant="primary" onClick={submitDefect} isLoading={submitting} disabled={!form.project_id || !form.title.trim()}>
              Create Defect
            </Button>
          </>
        )}
      >
        <form onSubmit={submitDefect} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <FormField label="Summary Title" required>
            <Input
              required
              placeholder="e.g. Navigation bar menu fails to expand on mobile viewport"
              value={form.title}
              onChange={(e) => setForm({ ...form, title: e.target.value })}
            />
          </FormField>

          <div className="grid grid-cols-2" style={{ gap: '0.75rem' }}>
            <FormField label="Target Project" required>
              <Select
                value={form.project_id}
                onChange={(e) => setForm({ ...form, project_id: Number(e.target.value) })}
              >
                <option value={0}>Select Project</option>
                {projects.map((p) => (
                  <option key={p.id} value={p.id}>{p.code} — {p.name}</option>
                ))}
              </Select>
            </FormField>

            <FormField label="Severity">
              <Select value={form.severity} onChange={(e) => setForm({ ...form, severity: e.target.value })}>
                {levels.map((l) => <option key={l} value={l}>{l}</option>)}
              </Select>
            </FormField>
          </div>

          <FormField label="Detailed Description">
            <textarea
              className="textarea"
              placeholder="Provide exact steps to reproduce, error text, or expected behavior..."
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
              style={{ minHeight: '80px' }}
            />
          </FormField>
        </form>
      </Modal>

      {/* Defect Detail Drawer */}
      {selected && (
        <Drawer
          isOpen={true}
          onClose={() => setSelected(null)}
          title={`Defect ${selected.defect_key}: ${selected.title}`}
          subtitle={`Status: ${selected.status} • Severity: ${selected.severity} • Priority: ${selected.priority}`}
          width="740px"
        >
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            {/* Status & Lifecycle Actions */}
            <div className="card" style={{ padding: '1rem', background: 'var(--bg-card-subtle)' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
                <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-main)' }}>Lifecycle Actions</span>
                <StatusBadge status={selected.status} />
              </div>
              <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                {selected.status === 'NEW' && canReview && (
                  <Button size="sm" variant="primary" onClick={() => void lifecycle('triage')}>Triage</Button>
                )}
                {selected.status === 'TRIAGED' && canReview && (
                  <Button size="sm" variant="primary" onClick={() => void lifecycle('assign')}>Assign</Button>
                )}
                {selected.status === 'ASSIGNED' && (
                  <Button size="sm" variant="primary" onClick={() => void lifecycle('start')}>Start Work</Button>
                )}
                {selected.status === 'IN_PROGRESS' && canReview && (
                  <Button size="sm" variant="primary" onClick={() => void lifecycle('fix')}>Mark Fixed</Button>
                )}
                {selected.status === 'FIXED' && canReview && (
                  <Button size="sm" variant="primary" onClick={() => void lifecycle('ready')}>Ready for Retest</Button>
                )}
                {selected.status === 'RETEST_PASSED' && canReview && (
                  <Button size="sm" variant="primary" onClick={() => void lifecycle('close')}>Close Defect</Button>
                )}
              </div>
            </div>

            {/* Comments & Retests */}
            <div className="grid grid-cols-2" style={{ gap: '1rem' }}>
              <div>
                <h4 style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '0.5rem' }}>
                  Comments & Discussion ({comments.length})
                </h4>
                <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.75rem' }}>
                  <Input
                    placeholder="Add comment..."
                    value={comment}
                    onChange={(e) => setComment(e.target.value)}
                  />
                  <Button size="sm" variant="secondary" onClick={saveComment}>Add</Button>
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', maxHeight: '180px', overflowY: 'auto' }}>
                  {comments.map((c) => (
                    <div key={c.id} style={{ padding: '0.5rem', borderRadius: 'var(--radius-sm)', background: 'var(--bg-card-subtle)', border: '1px solid var(--border-color)', fontSize: '0.8rem' }}>
                      <strong>Operator #{c.created_by}:</strong> {c.body}
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <h4 style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '0.5rem' }}>
                  Record Retest
                </h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                  <Select value={retest.result_status} onChange={(e) => setRetest({ ...retest, result_status: e.target.value })}>
                    <option value="PASSED">PASSED</option>
                    <option value="FAILED">FAILED</option>
                    <option value="BLOCKED">BLOCKED</option>
                  </Select>
                  <Input placeholder="Retest notes..." value={retest.notes} onChange={(e) => setRetest({ ...retest, notes: e.target.value })} />
                  <Button size="sm" variant="primary" onClick={saveRetest} disabled={selected.status !== 'READY_FOR_RETEST' || !canRetest}>
                    Record Retest
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </Drawer>
      )}
    </div>
  );
}
