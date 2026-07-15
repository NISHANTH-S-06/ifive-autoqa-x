import { type FormEvent, useEffect, useState } from 'react';
import { approveTestRun, cancelTestRun, createTestRun, evidenceUrl, executeTestRun, fetchDashboardSummary, fetchProjects, fetchRecentTestRuns, fetchTestRun } from '../services/testRuns';
import type { Project } from '../types/product';
import type { DashboardSummary, TestRun, TestRunRequest } from '../types/testRun';
import { useAuth } from '../authContext';

const TERMINAL = new Set(['PASSED', 'FAILED', 'CANCELLED']);

export function TestDashboardPreview() {
  const { operator } = useAuth();
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [runs, setRuns] = useState<TestRun[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [approvalRun, setApprovalRun] = useState<TestRun | null>(null);
  const [confirmation, setConfirmation] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [form, setForm] = useState<TestRunRequest>({ project_id: 0, suite_name: '', browser: 'chromium', environment: 'local' });

  const replaceRun = (next: TestRun) => setRuns((current) => current.map((run) => run.id === next.id ? next : run));
  const projectFor = (run: TestRun) => projects.find((project) => project.id === run.project_id);
  const canExecute = (run: TestRun) => projectFor(run)?.product_code === 'AUTOQA' && run.environment === 'local' && ['dashboard-smoke', 'integration-smoke'].includes(run.suite_name);

  const load = async () => {
    setLoading(true); setError('');
    try {
      const [nextSummary, nextRuns, nextProjects] = await Promise.all([fetchDashboardSummary(), fetchRecentTestRuns(), fetchProjects()]);
      setSummary(nextSummary); setRuns(nextRuns); setProjects(nextProjects);
      setForm((current) => ({ ...current, project_id: current.project_id || nextProjects[0]?.id || 0 }));
    } catch (reason) { setError(reason instanceof Error ? reason.message : 'Unable to load dashboard.'); }
    finally { setLoading(false); }
  };

  useEffect(() => { void load(); }, []);
  useEffect(() => {
    const active = runs.filter((run) => run.status === 'RUNNING');
    if (!active.length) return;
    const timer = window.setInterval(() => {
      void Promise.all(active.map((run) => fetchTestRun(run.id))).then((details) => {
        details.forEach(replaceRun);
      }).catch((reason) => setError(reason instanceof Error ? reason.message : 'Unable to refresh execution status.'));
    }, 2500);
    return () => window.clearInterval(timer);
  }, [runs.map((run) => `${run.id}:${run.status}`).join('|')]);

  const submit = async (event: FormEvent) => {
    event.preventDefault(); setSubmitting(true); setError('');
    try { await createTestRun(form); setDialogOpen(false); setForm((current) => ({ ...current, suite_name: '' })); await load(); }
    catch (reason) { setError(reason instanceof Error ? reason.message : 'Unable to create test run.'); }
    finally { setSubmitting(false); }
  };

  const approve = async (event: FormEvent) => {
    event.preventDefault(); if (!approvalRun) return; setSubmitting(true); setError('');
    try { replaceRun(await approveTestRun(approvalRun.id, confirmation)); setApprovalRun(null); setConfirmation(''); }
    catch (reason) { setError(reason instanceof Error ? reason.message : 'Unable to approve test run.'); }
    finally { setSubmitting(false); }
  };

  const execute = async (run: TestRun) => {
    setError('');
    try { await executeTestRun(run.id); replaceRun({ ...run, status: 'RUNNING' }); }
    catch (reason) { setError(reason instanceof Error ? reason.message : 'Unable to execute test run.'); }
  };
  const cancel = async (run: TestRun) => {
    setError('');
    try { replaceRun(await cancelTestRun(run.id)); }
    catch (reason) { setError(reason instanceof Error ? reason.message : 'Unable to cancel test run.'); }
  };

  const metrics = summary ? [['Total Tests', summary.total_tests.toString()], ['Pass Rate', `${summary.pass_rate}%`], ['Passed Runs', summary.passed_runs.toString()], ['Failed Runs', summary.failed_runs.toString()], ['Queued Runs', summary.queued_runs.toString()], ['Avg Runtime', `${summary.average_duration_seconds}s`]] : [];

  return <section className="section" id="dashboard"><div className="section-inner">
    <div className="section-title"><h2>Dashboard Preview</h2><p>Approve and execute only allowlisted local AutoQA test suites.</p></div>
    {loading && <div className="state-panel" role="status">Loading dashboard…</div>}
    {error && <div className="state-panel state-error" role="alert">{error}<button className="button button-secondary" onClick={() => void load()}>Retry</button></div>}
    {!loading && summary && <div className="dashboard-shell">
      <div className="dashboard-actions">{['TESTER','ADMIN'].includes(operator.role) && <button className="button button-primary" onClick={() => setDialogOpen(true)} disabled={!projects.length}>New Test Run</button>}</div>
      <div className="metric-grid">{metrics.map(([label, value]) => <div className="metric" key={label}><span>{label}</span><strong>{value}</strong></div>)}</div>
      {runs.length === 0 ? <div className="empty-runs">No test runs yet. Queue a local run to get started.</div> : <div className="table-preview run-list" role="table" aria-label="Recent test runs">
        {runs.map((run) => <div className="run-card" role="row" key={run.id} data-testid={`run-${run.id}`}>
          <div className="table-row"><strong>{run.suite_name}</strong><span className={run.status === 'FAILED' ? 'status-fail' : 'status-pass'}>{run.status}</span><span>{run.run_code}</span><span>{run.browser}</span></div>
          <div className="run-actions">
            {['APPROVER','ADMIN'].includes(operator.role) && canExecute(run) && run.created_by_operator_id !== operator.id && run.status === 'QUEUED' && <button className="button button-secondary" onClick={() => setApprovalRun(run)}>Approve</button>}
            {['APPROVER','ADMIN'].includes(operator.role) && canExecute(run) && run.status === 'APPROVED' && <button className="button button-primary" onClick={() => void execute(run)}>Execute Locally</button>}
            {['APPROVER','ADMIN'].includes(operator.role) && canExecute(run) && run.status === 'RUNNING' && <button className="button button-secondary" onClick={() => void cancel(run)}>Cancel</button>}
          </div>
          {TERMINAL.has(run.status) && <div className="run-details"><span>Total {run.total_tests}</span><span>Passed {run.passed_tests}</span><span>Failed {run.failed_tests}</span><span>Skipped {run.skipped_tests}</span><span>Duration {run.duration_seconds}s</span>{run.error_summary && <strong className="status-fail">{run.error_summary}</strong>}
            {run.evidence?.map((item) => <a key={item.id} href={evidenceUrl(run.id, item.id)} target="_blank" rel="noreferrer">{item.evidence_type}</a>)}
          </div>}
        </div>)}
      </div>}
    </div>}
    {dialogOpen && <div className="modal-backdrop"><div className="modal" role="dialog" aria-modal="true" aria-labelledby="new-run-title"><h3 id="new-run-title">New Test Run</h3><form onSubmit={submit}>
      <label>Project<select required value={form.project_id} onChange={(e) => setForm({ ...form, project_id: Number(e.target.value) })}>{projects.map((project) => <option key={project.id} value={project.id}>{project.name}</option>)}</select></label>
      <label>Suite name<input required list="suite-options" value={form.suite_name} onChange={(e) => setForm({ ...form, suite_name: e.target.value })} /><datalist id="suite-options"><option value="dashboard-smoke"/><option value="integration-smoke"/></datalist></label>
      <label>Browser<select value="chromium" disabled><option value="chromium">chromium</option></select></label>
      <label>Environment<select value={form.environment} onChange={(e) => setForm({ ...form, environment: e.target.value as TestRunRequest['environment'] })}><option value="local">local</option><option value="qa">qa</option><option value="staging">staging</option></select></label>
      <div className="modal-actions"><button type="button" className="button button-secondary" onClick={() => setDialogOpen(false)}>Cancel</button><button className="button button-primary" disabled={submitting}>{submitting ? 'Queuing…' : 'Queue Run'}</button></div>
    </form></div></div>}
    {approvalRun && <div className="modal-backdrop"><div className="modal" role="dialog" aria-modal="true" aria-labelledby="approve-title"><h3 id="approve-title">Approve Local Execution</h3><p>Type <strong>APPROVE LOCAL TEST EXECUTION</strong> to allow this local suite to run.</p><form onSubmit={approve}><label>Safety confirmation<input aria-label="Safety confirmation" value={confirmation} onChange={(e) => setConfirmation(e.target.value)} /></label><div className="modal-actions"><button type="button" className="button button-secondary" onClick={() => setApprovalRun(null)}>Cancel</button><button className="button button-primary" disabled={submitting}>Approve Run</button></div></form></div></div>}
  </div></section>;
}
