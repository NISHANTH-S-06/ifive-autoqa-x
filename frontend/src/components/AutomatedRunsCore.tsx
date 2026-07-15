import { type FormEvent, useEffect, useMemo, useState } from 'react';
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

  useEffect(() => { void load(); }, []);

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
      setMessage('Automated run draft created.');
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
      setMessage(`Automated run ${kind} completed.`);
      await load(); await openRun(next);
    } catch (reason) { setError(reason instanceof Error ? reason.message : 'Automated run action failed.'); }
  };

  const runWorker = async () => {
    try {
      await heartbeatWorker();
      const next = await runNextWorkerJob();
      setMessage(next ? `Worker completed ${next.run_key} as ${next.status}.` : 'Worker heartbeat recorded. No queued jobs.');
      await load();
      if (next) await openRun(next);
      setWorkers(await fetchExecutionWorkers().catch(() => []));
    } catch (reason) { setError(reason instanceof Error ? reason.message : 'Worker action failed.'); }
  };

  const startControlledAcceptance = async (run: AutomatedRun) => {
    try {
      await heartbeatWorker();
      const queued = run.status === 'APPROVED' ? await queueAutomatedRun(run.id) : run;
      const next = await runNextWorkerJob();
      setMessage(next ? `Controlled acceptance completed ${next.run_key} as ${next.status}.` : `Controlled acceptance queued ${queued.run_key}.`);
      await load();
      await openRun(next ?? queued);
      setWorkers(await fetchExecutionWorkers().catch(() => []));
    } catch (reason) { setError(reason instanceof Error ? reason.message : 'Controlled acceptance failed preflight.'); }
  };

  const toggleCase = (id: number, checked: boolean) => {
    setForm((current) => ({ ...current, case_ids: checked ? [...current.case_ids, id] : current.case_ids.filter((caseId) => caseId !== id) }));
  };

  return <section className="section" id="automated-runs"><div className="section-inner">
    <div className="section-title"><h2>Automated Runs</h2><p>Queue structured Chromium automation only for execution-approved non-production targets.</p></div>
    {loading && <div className="state-panel" role="status">Loading automated runs...</div>}
    {error && <div className="state-panel state-error" role="alert">{error}<button className="button button-secondary" onClick={() => void load()}>Retry</button></div>}
    {message && <div className="state-panel" role="status">{message}</div>}
    {!loading && <div className="split">
      <div className="card"><h3>Stage 11 Readiness</h3><div className="tm-row"><strong>ADMIN prerequisite</strong><span>{readiness?.admin_prerequisite_met ? 'Ready' : `Pending (${readiness?.active_admin_count ?? 0})`}</span></div><div className="tm-row"><strong>Target authorization</strong><span>{readiness?.real_target_authorized ? 'Authorized' : readiness?.real_target_status ?? 'Pending'}</span></div><div className="tm-row"><strong>DNS pinning</strong><span>{readiness?.dns_pinning_status ?? 'Checking'}</span></div><div className="tm-row"><strong>Runtime secrets</strong><span>{readiness?.runtime_secret_status ?? 'Not configured'}</span></div><div className="tm-row"><strong>Allowed risk</strong><span>{readiness?.allowed_risk_levels?.join(', ') ?? 'READ_ONLY, SAFE_INTERACTION'}</span></div>{preflight && <div className="state-panel">Preflight {preflight.status}: {preflight.risk_level}, DNS {preflight.dns_pinning_status}, secrets {preflight.runtime_secret_status}</div>}</div>
      <div className="card"><h3>Create Automated Run</h3>{executionTargets.length === 0 && <div className="state-panel">No execution-enabled targets are available.</div>}{canAuthor && executionTargets.length > 0 && <form className="admin-form" onSubmit={submitRun}><label>Automation label<input required value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} /></label><label>Execution target<select value={form.target_id} onChange={(event) => setForm({ ...form, target_id: Number(event.target.value) })}>{executionTargets.map((target) => <option key={target.id} value={target.id}>{target.target_key} {target.normalized_origin}</option>)}</select></label><label>Timeout seconds<input type="number" min={5} max={300} value={form.timeout_seconds} onChange={(event) => setForm({ ...form, timeout_seconds: Number(event.target.value) })} /></label><fieldset><legend>Approved automation cases</legend>{approvedCases.length === 0 && <span>No approved cases available.</span>}{approvedCases.map((item) => <label key={item.id}><input type="checkbox" checked={form.case_ids.includes(item.id)} onChange={(event) => toggleCase(item.id, event.target.checked)} />{item.case_key} v{item.current_version}</label>)}</fieldset><button className="button button-primary" disabled={submitting || form.target_id === 0 || form.case_ids.length === 0}>Create Run</button></form>}</div>
      <div className="card"><h3>Queue and Worker</h3><button className="button button-primary" disabled={!canReview} onClick={() => void runWorker()}>Run Local Worker</button>{workers.length === 0 && <div className="state-panel">No worker heartbeat yet.</div>}{workers.map((worker) => <div className="tm-row" key={worker.id}><strong>{worker.worker_key}</strong><span>{worker.status}</span><span>{worker.current_run_id ? `Run ${worker.current_run_id}` : 'Idle'}</span></div>)}</div>
    </div>}
    {!loading && <div className="card"><h3>Automated Run Queue</h3>{runs.length === 0 && <div className="state-panel">No automated runs yet.</div>}{runs.map((run) => <div className="ct-row" key={run.id}><strong>{run.run_key}</strong><span>{run.name}</span><span>{run.status}</span><span>{run.progress ?? `${run.completed_steps}/${run.total_steps}`}</span><span>{run.risk_level ?? 'READ_ONLY'}</span><span>{run.preflight_status ?? 'PENDING'}</span><span className="table-actions"><button className="button button-secondary" onClick={() => void openRun(run)}>Open</button>{run.status === 'DRAFT' && (operator.role === 'ADMIN' || run.created_by === operator.id) && <button className="button button-primary" onClick={() => void action('submit', run)}>Submit</button>}{run.status === 'SUBMITTED' && canReview && run.created_by !== operator.id && <button className="button button-primary" onClick={() => void action('approve', run)}>Approve</button>}{run.status === 'SUBMITTED' && canReview && run.created_by === operator.id && <button className="button button-secondary" disabled>Self Approval Blocked</button>}{run.status === 'APPROVED' && canReview && <button className="button button-primary" onClick={() => void action('queue', run)}>Queue</button>}{run.status === 'APPROVED' && canReview && <button className="button button-primary" onClick={() => void startControlledAcceptance(run)}>Start Controlled Acceptance</button>}{!['PASSED','FAILED','CANCELLED','TIMED_OUT','BLOCKED'].includes(run.status) && <button className="button button-secondary" onClick={() => void action('cancel', run)}>Cancel</button>}{['FAILED','TIMED_OUT','BLOCKED'].includes(run.status) && canReview && <button className="button button-secondary" onClick={() => void action('retry', run)}>Retry</button>}</span></div>)}</div>}
    {selected && <div className="card"><h3>Run Results</h3><p><strong>{selected.run_key}</strong> {selected.status} {selected.safe_error_message ?? ''}</p><h3>Cases</h3>{runCases.map((item) => <div className="tm-row" key={item.id}><strong>Case {item.test_case_id}</strong><span>v{item.test_case_version}</span><span>{item.status}</span><span>{item.failure_classification ?? 'safe'}</span></div>)}<h3>Step Results</h3>{steps.map((step) => <div className="ct-check-row" key={step.id}><strong>{step.step_number}</strong><span>{step.action_type}</span><span>{step.status}</span><span>{step.duration_ms ?? 0} ms</span><span>{step.safe_error_message ?? 'sanitized'}</span></div>)}<h3>Evidence</h3>{artifacts.length === 0 && <div className="state-panel">No sanitized evidence recorded.</div>}{artifacts.map((artifact) => <div className="tm-row" key={artifact.id}><strong>{artifact.artifact_type}</strong><span>{artifact.original_filename}</span><span>{artifact.size_bytes} bytes</span><span>{artifact.sha256.slice(0, 12)}</span><a className="button button-secondary" href={executionArtifactDownloadUrl(artifact.id)} target="_blank" rel="noreferrer">Download</a></div>)}</div>}
  </div></section>;
}
