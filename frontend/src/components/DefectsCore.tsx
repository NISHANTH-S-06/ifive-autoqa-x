import { type FormEvent, useEffect, useMemo, useState } from 'react';
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
      setMessage(`Created ${created.defect_key}.`);
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
      const warning = await createDefectFromRun(base);
      if ('requires_confirmation' in warning) {
        setMessage(`Possible duplicates: ${warning.possible_existing.length}.`);
        if (!window.confirm('Create a defect from this failed run?')) return;
      }
      const created = await createDefectFromRun({ ...base, confirm: true });
      if ('defect_key' in created) {
        setMessage(`Created ${created.defect_key} from failed run.`);
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
      setMessage(`${next.defect_key} moved to ${next.status}.`);
      await refreshSelected(next);
    } catch (reason) { setError(reason instanceof Error ? reason.message : 'Defect action failed.'); }
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
      setMessage('Retest recorded.');
      await openDefect({ ...selected, status: retest.result_status === 'PASSED' ? 'RETEST_PASSED' : 'REOPENED' });
      await load();
    } catch (reason) { setError(reason instanceof Error ? reason.message : 'Retest recording failed.'); }
  };

  const updatePriority = async (priority: string) => {
    if (!selected) return;
    try {
      const next = await updateDefect(selected.id, { priority });
      await refreshSelected(next);
    } catch (reason) { setError(reason instanceof Error ? reason.message : 'Priority update failed.'); }
  };

  return <section className="section" id="defects"><div className="section-inner">
    <div className="section-title"><h2>Defects</h2><p>Track failed manual and automated results through triage, fix, retest, closure, and traceability.</p></div>
    {loading && <div className="state-panel" role="status">Loading defects...</div>}
    {error && <div className="state-panel state-error" role="alert">{error}<button className="button button-secondary" onClick={() => void load()}>Retry</button></div>}
    {message && <div className="state-panel" role="status">{message}</div>}
    {!loading && <div className="split">
      <div className="card"><h3>Filters</h3><form className="admin-form" onSubmit={(event) => { event.preventDefault(); void load(); }}><label>Defect query<input value={query.search} onChange={(event) => setQuery({ ...query, search: event.target.value })} /></label><label>Defect state<select value={query.status} onChange={(event) => setQuery({ ...query, status: event.target.value })}>{statusFilters.map((item) => <option key={item || 'ALL'} value={item}>{item || 'All'}</option>)}</select></label><button className="button button-secondary">Filter Defects</button></form></div>
      <div className="card"><h3>Create Defect</h3>{!canCreate && <div className="state-panel">Defect creation requires TESTER or ADMIN.</div>}{canCreate && <form className="admin-form" onSubmit={submitDefect}><label>Defect summary<input required value={form.title} onChange={(event) => setForm({ ...form, title: event.target.value })} /></label><label>Defect project<select required value={form.project_id} onChange={(event) => setForm({ ...form, project_id: Number(event.target.value) })}><option value={0}>Select project</option>{projects.map((project) => <option key={project.id} value={project.id}>{project.code} {project.name}</option>)}</select></label><label>Defect severity<select value={form.severity} onChange={(event) => setForm({ ...form, severity: event.target.value })}>{levels.map((level) => <option key={level}>{level}</option>)}</select></label><label>Defect priority<select value={form.priority} onChange={(event) => setForm({ ...form, priority: event.target.value })}>{levels.map((level) => <option key={level}>{level}</option>)}</select></label><label>Defect description<textarea value={form.description} onChange={(event) => setForm({ ...form, description: event.target.value })} /></label><button className="button button-primary" disabled={submitting || !form.project_id}>Create</button></form>}</div>
      <div className="card"><h3>From Failed Run</h3>{failedRuns.length === 0 && <div className="state-panel">No failed automated runs are available.</div>}{canCreate && failedRuns.length > 0 && <div className="admin-form"><label>Failed automated run<select value={runId} onChange={(event) => setRunId(Number(event.target.value))}>{failedRuns.map((run) => <option key={run.id} value={run.id}>{run.run_key} {run.status}</option>)}</select></label><button className="button button-primary" disabled={submitting || !runId} onClick={() => void createFromRun()}>Create From Run</button></div>}</div>
    </div>}
    {!loading && <div className="card"><h3>Defect Queue</h3>{defects.length === 0 && <div className="state-panel">No defects match the current filters.</div>}{defects.map((item) => <div className="ct-row" key={item.id}><strong>{item.defect_key}</strong><span>{item.title}</span><span>{item.status}</span><span>{item.severity}</span><span>{item.priority}</span><span className="table-actions"><button className="button button-secondary" onClick={() => void openDefect(item)}>Open</button></span></div>)}</div>}
    {selected && <div className="defect-detail"><h3>{selected.defect_key}</h3><p><strong>{selected.title}</strong> {selected.status}</p><div className="split"><div><div className="tm-row"><strong>Source</strong><span>{selected.manual_run_id ? `Manual ${selected.manual_run_id}` : selected.automated_run_id ? `Automated ${selected.automated_run_id}` : 'Standalone'}</span><span>{selected.failure_category ?? 'Unclassified'}</span><span>v{selected.test_case_version ?? '-'}</span><span /></div><div className="tm-row"><strong>Target</strong><span>{selected.target_id ? `Target ${selected.target_id} v${selected.target_version}` : selected.environment ?? 'Local'}</span><span>{selected.closed_at ? 'Closed' : 'Open'}</span><span>{selected.resolution ?? 'Pending'}</span><span /></div><label className="admin-form">Priority<select value={selected.priority} onChange={(event) => void updatePriority(event.target.value)}>{levels.map((level) => <option key={level}>{level}</option>)}</select></label></div><div className="admin-form"><label>Assigned operator id<input type="number" min={1} value={assignee} onChange={(event) => setAssignee(event.target.value)} /></label><label>Resolution or reason<textarea value={resolution} onChange={(event) => setResolution(event.target.value)} /></label><div className="table-actions">{selected.status === 'NEW' && canReview && <button className="button button-primary" onClick={() => void lifecycle('triage')}>Triage</button>}{selected.status === 'TRIAGED' && canReview && <button className="button button-primary" onClick={() => void lifecycle('assign')}>Assign</button>}{selected.status === 'ASSIGNED' && <button className="button button-primary" onClick={() => void lifecycle('start')}>Start</button>}{selected.status === 'IN_PROGRESS' && canReview && <button className="button button-primary" onClick={() => void lifecycle('fix')}>Fix</button>}{selected.status === 'FIXED' && canReview && <button className="button button-primary" onClick={() => void lifecycle('ready')}>Ready</button>}{selected.status === 'RETEST_PASSED' && canReview && <button className="button button-primary" onClick={() => void lifecycle('close')}>Close</button>}{['NEW','TRIAGED','ASSIGNED','IN_PROGRESS','FIXED','READY_FOR_RETEST'].includes(selected.status) && canReview && <button className="button button-secondary" onClick={() => void lifecycle('reject')}>Reject</button>}</div></div></div><div className="split"><div className="card"><h3>Comments</h3><div className="admin-form"><textarea value={comment} onChange={(event) => setComment(event.target.value)} /><button className="button button-secondary" onClick={() => void saveComment()}>Add Comment</button></div>{comments.map((item) => <div className="tm-row" key={item.id}><strong>{item.created_by}</strong><span>{item.body}</span><span>{new Date(item.created_at).toLocaleString()}</span><span /><span /></div>)}</div><div className="card"><h3>Retest</h3><div className="admin-form"><label>Result<select value={retest.result_status} onChange={(event) => setRetest({ ...retest, result_status: event.target.value })}>{['PASSED','FAILED','BLOCKED','PLANNED'].map((item) => <option key={item}>{item}</option>)}</select></label><label>Notes<textarea value={retest.notes} onChange={(event) => setRetest({ ...retest, notes: event.target.value })} /></label><button className="button button-secondary" disabled={selected.status !== 'READY_FOR_RETEST' || !canRetest} onClick={() => void saveRetest()}>Record Retest</button></div></div></div><div className="split"><div className="card"><h3>Evidence</h3>{evidence.length === 0 && <div className="state-panel">No evidence links.</div>}{evidence.map((item) => <div className="tm-row" key={item.id}><strong>{item.link_type}</strong><span>{item.manual_evidence_id ? `Manual evidence ${item.manual_evidence_id}` : `Execution artifact ${item.execution_artifact_id}`}</span><span>{new Date(item.created_at).toLocaleString()}</span><span /><span /></div>)}</div><div className="card"><h3>Traceability</h3>{trace && <><div className="tm-row"><strong>Project</strong><span>{String(trace.project?.name ?? trace.project?.code ?? '-')}</span><span>Case v{trace.test_case_version ?? '-'}</span><span /><span /></div><div className="tm-row"><strong>Links</strong><span>{trace.evidence_links.length} evidence</span><span>{trace.retests.length} retests</span><span /><span /></div></>}{history.map((item) => <div className="tm-row" key={item.id}><strong>{item.event_type}</strong><span>{item.old_value ?? '-'} to {item.new_value ?? '-'}</span><span>{item.safe_message ?? ''}</span><span /><span /></div>)}</div></div></div>}
  </div></section>;
}
