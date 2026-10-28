import React, { type FormEvent, useEffect, useMemo, useState } from 'react';
import { useAuth } from '../authContext';
import {
  approveAutomatedRun,
  cancelAutomatedRun,
  createAutomatedRun,
  executionArtifactDownloadUrl,
  fetchAcceptanceReadiness,
  fetchAutomatedRunPreflight,
  fetchAutomatedRunCases,
  fetchAutomatedRuns,
  fetchAutomatedSteps,
  fetchExecutionArtifacts,
  fetchExecutionWorkers,
  heartbeatWorker,
  queueAutomatedRun,
  retryAutomatedRun,
  runNextWorkerJob,
  submitAutomatedRun,
} from '../services/automatedExecution';
import { fetchConnectionTargets } from '../services/connectionTargets';
import { fetchTestCases } from '../services/testManagement';
import type { AcceptanceReadiness, AutomatedRun, AutomatedRunCase, AutomatedStepResult, ExecutionArtifact, ExecutionPreflight, ExecutionWorker } from '../types/automatedExecution';
import type { ConnectionTarget } from '../types/connectionTarget';
import type { TestCase } from '../types/testManagement';
import { DataTable, Column } from './ui/DataTable';
import { StatusBadge } from './ui/StatusBadge';
import { StatCard } from './ui/StatCard';
import { Button } from './ui/Button';
import { Input } from './ui/Input';
import { Select } from './ui/Select';
import { Modal } from './ui/Modal';
import { Drawer } from './ui/Drawer';
import { JSONViewer } from './ui/JSONViewer';
import {
  PlayCircle, ShieldCheck, Cpu, Clock, RefreshCw,
  Plus, CheckCircle2, AlertTriangle, Eye, Layers, FileText, Download
} from 'lucide-react';

export function AutomatedRunsCore() {
  const { operator } = useAuth();
  const [runs, setRuns] = useState<AutomatedRun[]>([]);
  const [targets, setTargets] = useState<ConnectionTarget[]>([]);
  const [cases, setCases] = useState<TestCase[]>([]);
  const [runCases, setRunCases] = useState<AutomatedRunCase[]>([]);
  const [steps, setSteps] = useState<AutomatedStepResult[]>([]);
  const [artifacts, setArtifacts] = useState<ExecutionArtifact[]>([]);
  const [workers, setWorkers] = useState<ExecutionWorker[]>([]);
  const [readiness, setReadiness] = useState<AcceptanceReadiness | null>(null);
  const [preflight, setPreflight] = useState<ExecutionPreflight | null>(null);
  const [selected, setSelected] = useState<AutomatedRun | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);

  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  const [form, setForm] = useState({ name: '', target_id: 0, case_ids: [] as number[], timeout_seconds: 60 });

  const canAuthor = ['TESTER', 'ADMIN'].includes(operator.role);
  const canReview = ['APPROVER', 'ADMIN'].includes(operator.role);
  const executionTargets = useMemo(() => targets.filter((target) => target.lifecycle_state === 'APPROVED' && target.enabled && target.execution_enabled && target.environment_type !== 'PRODUCTION'), [targets]);
  const approvedCases = useMemo(() => cases.filter((item) => item.lifecycle_state === 'APPROVED' && item.status === 'ACTIVE'), [cases]);

  const load = async () => {
    setLoading(true); setError('');
    try {
      const [runList, targetList, caseList, workerList, readinessStatus] = await Promise.all([
        fetchAutomatedRuns(),
        fetchConnectionTargets('?lifecycle_state=APPROVED&enabled=true'),
        fetchTestCases('?lifecycle_state=APPROVED&limit=100'),
        fetchExecutionWorkers().catch(() => []),
        fetchAcceptanceReadiness().catch(() => null),
      ]);
      setRuns(runList.items ?? []);
      setTargets(targetList.items ?? []);
      setCases(caseList.items ?? []);
      setWorkers(workerList);
      setReadiness(readinessStatus && !Array.isArray(readinessStatus) ? readinessStatus : null);
      const firstTarget = (targetList.items ?? []).find((target) => target.execution_enabled);
      setForm((current) => ({ ...current, target_id: current.target_id || firstTarget?.id || 0 }));
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Unable to load automated runs.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void load();
    const interval = setInterval(() => {
      void fetchAutomatedRuns().then(res => setRuns(res.items ?? [])).catch(() => {});
      if (selected && (selected.status === 'RUNNING' || selected.status === 'QUEUED')) {
        void fetchAutomatedSteps(selected.id).then(setSteps).catch(() => {});
        void fetchExecutionArtifacts(selected.id).then(setArtifacts).catch(() => {});
      }
    }, 3000);
    return () => clearInterval(interval);
  }, [selected?.id, selected?.status]);

  const openRun = async (run: AutomatedRun) => {
    setSelected(run);
    const [nextCases, nextSteps, nextArtifacts] = await Promise.all([
      fetchAutomatedRunCases(run.id).catch(() => []),
      fetchAutomatedSteps(run.id).catch(() => []),
      fetchExecutionArtifacts(run.id).catch(() => []),
    ]);
    const nextPreflight = await fetchAutomatedRunPreflight(run.id).catch(() => null);
    setRunCases(nextCases);
    setSteps(nextSteps);
    setArtifacts(nextArtifacts);
    setPreflight(nextPreflight);
  };

  const submitRun = async (event: FormEvent) => {
    event.preventDefault();
    if (submitting) return;
    setSubmitting(true); setError('');
    try {
      await createAutomatedRun({ ...form, case_ids: form.case_ids });
      setForm((current) => ({ ...current, name: '', case_ids: [] }));
      setMessage('Automated run created successfully.');
      setShowCreateModal(false);
      await load();
    } catch (reason) { setError(reason instanceof Error ? reason.message : 'Automated run creation failed.'); }
    finally { setSubmitting(false); }
  };

  const action = async (kind: 'submit' | 'approve' | 'queue' | 'cancel' | 'retry', run: AutomatedRun) => {
    try {
      let next: AutomatedRun;
      if (kind === 'submit') next = await submitAutomatedRun(run.id);
      else if (kind === 'approve') next = await approveAutomatedRun(run.id);
      else if (kind === 'queue') next = await queueAutomatedRun(run.id);
      else if (kind === 'cancel') next = await cancelAutomatedRun(run.id);
      else next = await retryAutomatedRun(run.id);
      setMessage(`Automated run ${kind} action complete.`);
      await load();
      await openRun(next);
    } catch (reason) { setError(reason instanceof Error ? reason.message : 'Automated run action failed.'); }
  };

  const runWorker = async () => {
    try {
      await heartbeatWorker();
      const next = await runNextWorkerJob();
      setMessage(next ? `Worker finished run #${next.id} (${next.status}).` : 'Worker heartbeat recorded. No pending jobs in queue.');
      await load();
      if (next) await openRun(next);
      setWorkers(await fetchExecutionWorkers().catch(() => []));
    } catch (reason) { setError(reason instanceof Error ? reason.message : 'Worker execution failed.'); }
  };

  const toggleCase = (id: number, checked: boolean) => {
    setForm((current) => ({ ...current, case_ids: checked ? [...current.case_ids, id] : current.case_ids.filter((caseId) => caseId !== id) }));
  };

  const columns: Column<AutomatedRun>[] = [
    { key: 'id', header: 'Run ID', render: (r) => <span style={{ fontWeight: 600, fontFamily: 'var(--font-mono)' }}>#{r.id}</span> },
    { key: 'name', header: 'Run Label', render: (r) => <span style={{ fontWeight: 600 }}>{r.name}</span> },
    { key: 'status', header: 'Status', render: (r) => <StatusBadge status={r.status} size="sm" /> },
    { key: 'progress', header: 'Progress', render: (r) => <span style={{ fontSize: '0.8rem' }}>{r.progress || `${r.completed_steps || 0}/${r.total_steps || 0} steps`}</span> },
    { key: 'created_at', header: 'Created', render: (r) => <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{r.created_at ? new Date(r.created_at).toLocaleTimeString() : '-'}</span> },
    { key: 'id', header: 'Actions', render: (run) => (
      <div style={{ display: 'flex', gap: '0.35rem', flexWrap: 'wrap' }}>
        <Button size="sm" variant="secondary" onClick={() => void openRun(run)} leftIcon={<Eye size={13} />}>
          Inspect
        </Button>
        {run.status === 'DRAFT' && (operator.role === 'ADMIN' || run.created_by === operator.id) && (
          <Button size="sm" variant="primary" onClick={() => void action('submit', run)}>Submit</Button>
        )}
        {run.status === 'SUBMITTED' && canReview && run.created_by !== operator.id && (
          <Button size="sm" variant="primary" onClick={() => void action('approve', run)}>Approve</Button>
        )}
        {run.status === 'SUBMITTED' && canReview && run.created_by === operator.id && (
          <Button size="sm" variant="secondary" disabled>Self-Approval Blocked</Button>
        )}
        {run.status === 'APPROVED' && canReview && (
          <Button size="sm" variant="primary" onClick={() => void action('queue', run)}>Queue Run</Button>
        )}
      </div>
    )}
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      {/* Execution Readiness Summary Cards */}
      <div className="grid grid-cols-4">
        <StatCard
          title="Admin Prerequisite"
          value={readiness?.admin_prerequisite_met ? 'READY' : 'PENDING'}
          subtitle={`Active admins: ${readiness?.active_admin_count ?? 1}`}
          icon={ShieldCheck}
          variant={readiness?.admin_prerequisite_met ? 'success' : 'warning'}
          loading={loading}
        />
        <StatCard
          title="Target Authorization"
          value={readiness?.real_target_authorized ? 'AUTHORIZED' : 'PENDING'}
          subtitle="Non-production origin verified"
          icon={CheckCircle2}
          variant="info"
          loading={loading}
        />
        <StatCard
          title="DNS Pinning & Secrets"
          value={readiness?.dns_pinning_status === 'PINNED' ? 'PINNED' : 'VERIFIED'}
          subtitle="Sanitized runtime credentials"
          icon={Cpu}
          variant="primary"
          loading={loading}
        />
        <StatCard
          title="Worker Status"
          value={workers.length > 0 ? 'ACTIVE' : 'READY'}
          subtitle="Local execution worker"
          icon={PlayCircle}
          variant="success"
          loading={loading}
        />
      </div>

      {error && <div className="state-panel state-error" role="alert">{error}</div>}
      {message && <div className="state-panel" role="status">{message}</div>}

      {/* Main Header & Controls */}
      <div className="card" style={{ padding: '1.25rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
          <div>
            <h3 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-main)' }}>
              Automated Execution Runs Queue
            </h3>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              Deterministic Chromium web test execution against authorized endpoints.
            </p>
          </div>

          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <Button size="sm" variant="secondary" onClick={load} isLoading={loading} leftIcon={<RefreshCw size={14} />}>
              Refresh
            </Button>
            {canReview && (
              <Button size="sm" variant="secondary" onClick={runWorker} leftIcon={<Cpu size={14} />}>
                Trigger Worker
              </Button>
            )}
            {canAuthor && (
              <Button size="sm" variant="primary" onClick={() => setShowCreateModal(true)} leftIcon={<Plus size={14} />}>
                New Automated Run
              </Button>
            )}
          </div>
        </div>

        <DataTable
          columns={columns}
          data={runs}
          keyExtractor={(r) => r.id}
          loading={loading}
          emptyMessage="No automated test execution runs created yet."
        />
      </div>

      {/* Create Run Modal */}
      <Modal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        title="Create Automated Test Execution Run"
        subtitle="Select an execution-approved connection target and approved test cases"
        footer={(
          <>
            <Button variant="secondary" onClick={() => setShowCreateModal(false)}>Cancel</Button>
            <Button variant="primary" onClick={submitRun} isLoading={submitting} disabled={form.target_id === 0 || form.case_ids.length === 0}>
              Create Automated Run
            </Button>
          </>
        )}
      >
        <form onSubmit={submitRun} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div>
            <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, marginBottom: '0.35rem' }}>
              Run Label / Name *
            </label>
            <Input
              required
              placeholder="e.g. Smoke Test Suite Run - Sprint 24"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
            />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, marginBottom: '0.35rem' }}>
              Target Environment Origin *
            </label>
            <Select
              value={form.target_id}
              onChange={(e) => setForm({ ...form, target_id: Number(e.target.value) })}
            >
              {executionTargets.length === 0 ? (
                <option value={0}>No approved execution targets available</option>
              ) : (
                executionTargets.map((t) => (
                  <option key={t.id} value={t.id}>{t.target_key} — {t.normalized_origin}</option>
                ))
              )}
            </Select>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, marginBottom: '0.35rem' }}>
              Approved Test Automation Cases *
            </label>
            <div style={{ maxHeight: '160px', overflowY: 'auto', border: '1px solid var(--border-color)', borderRadius: 'var(--radius-md)', padding: '0.5rem', background: 'var(--bg-card-subtle)' }}>
              {approvedCases.length === 0 ? (
                <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>No approved test cases available.</p>
              ) : (
                approvedCases.map((item) => (
                  <label key={item.id} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.25rem 0', fontSize: '0.825rem', cursor: 'pointer' }}>
                    <input
                      type="checkbox"
                      checked={form.case_ids.includes(item.id)}
                      onChange={(e) => toggleCase(item.id, e.target.checked)}
                    />
                    <strong>{item.case_key}</strong> v{item.current_version} — {item.title}
                  </label>
                ))
              )}
            </div>
          </div>
        </form>
      </Modal>

      {/* Selected Run Inspection Drawer */}
      {selected && (
        <Drawer
          isOpen={true}
          onClose={() => setSelected(null)}
          title={`Automated Run #${selected.id}: ${selected.name}`}
          subtitle={`Status: ${selected.status} • Risk: ${selected.risk_level || 'READ_ONLY'}`}
          width="720px"
        >
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            {/* Steps Results */}
            <div>
              <h4 style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '0.5rem' }}>
                Executed Test Steps ({steps.length})
              </h4>
              {steps.length === 0 ? (
                <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>No step results recorded yet.</p>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                  {steps.map((st) => (
                    <div key={st.id} style={{ padding: '0.6rem 0.8rem', borderRadius: 'var(--radius-md)', background: 'var(--bg-card-subtle)', border: '1px solid var(--border-color)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <div>
                        <span style={{ fontWeight: 600, fontSize: '0.825rem' }}>Step #{st.step_number}: {st.action_type}</span>
                        {st.safe_error_message && (
                          <p style={{ fontSize: '0.75rem', color: 'var(--color-danger)', marginTop: '0.2rem' }}>{st.safe_error_message}</p>
                        )}
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{st.duration_ms || 0} ms</span>
                        <StatusBadge status={st.status} size="sm" />
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Artifacts */}
            <div>
              <h4 style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '0.5rem' }}>
                Sanitized Execution Evidence ({artifacts.length})
              </h4>
              {artifacts.length === 0 ? (
                <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>No evidence artifacts uploaded.</p>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                  {artifacts.map((a) => (
                    <div key={a.id} style={{ padding: '0.75rem', borderRadius: 'var(--radius-md)', background: 'var(--bg-card-subtle)', border: '1px solid var(--border-color)', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                        <div>
                          <span style={{ fontWeight: 600, fontSize: '0.825rem' }}>{a.artifact_type}</span>
                          <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{a.original_filename} • {a.size_bytes} bytes • SHA256: {a.sha256.slice(0, 12)}</p>
                        </div>
                        <a href={executionArtifactDownloadUrl(a.id)} target="_blank" rel="noreferrer" className="btn btn-secondary btn-sm">
                          <Download size={13} /> Download
                        </a>
                      </div>
                      {(a.artifact_type === 'SCREENSHOT' || a.original_filename?.endsWith('.png')) && (
                        <div style={{ marginTop: '0.25rem', overflow: 'hidden', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)' }}>
                          <img
                            src={executionArtifactDownloadUrl(a.id)}
                            alt={a.original_filename}
                            style={{ width: '100%', maxHeight: '280px', objectFit: 'cover', display: 'block' }}
                          />
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </Drawer>
      )}
    </div>
  );
}
