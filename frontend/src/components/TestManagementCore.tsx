import { type FormEvent, useEffect, useMemo, useState } from 'react';
import { useAuth } from '../authContext';
import {
  approveTestCase,
  archiveTestCase,
  completeManualRun,
  createManualRun,
  createTestCase,
  createTestModule,
  createTestProject,
  createTestSuite,
  evidenceDownloadUrl,
  fetchManualEvidence,
  fetchManualRunCases,
  fetchManualRuns,
  fetchTestCaseVersions,
  fetchTestCases,
  fetchTestModules,
  fetchTestProjects,
  fetchTestSuites,
  rejectTestCase,
  startManualRun,
  submitTestCase,
  updateManualRunCase,
  updateManualStep,
  uploadManualEvidence,
} from '../services/testManagement';
import type { ManualEvidence, ManualRun, ManualRunCase, ManualResultStatus, TestCase, TestCaseStep, TestCaseVersion, TestModule, TestProject, TestSuite } from '../types/testManagement';

const emptyStep = (step_number: number): TestCaseStep => ({ step_number, action: '', expected_result: '', test_data: '' });

export function TestManagementCore() {
  const { operator } = useAuth();
  const [tab, setTab] = useState<'projects' | 'cases' | 'review' | 'runs'>('projects');
  const [projects, setProjects] = useState<TestProject[]>([]);
  const [modules, setModules] = useState<TestModule[]>([]);
  const [suites, setSuites] = useState<TestSuite[]>([]);
  const [cases, setCases] = useState<TestCase[]>([]);
  const [runs, setRuns] = useState<ManualRun[]>([]);
  const [runCases, setRunCases] = useState<ManualRunCase[]>([]);
  const [evidence, setEvidence] = useState<ManualEvidence[]>([]);
  const [versions, setVersions] = useState<TestCaseVersion[]>([]);
  const [selectedCase, setSelectedCase] = useState<TestCase | null>(null);
  const [selectedRun, setSelectedRun] = useState<ManualRun | null>(null);
  const [selectedRunCase, setSelectedRunCase] = useState<ManualRunCase | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  const [search, setSearch] = useState('');
  const [stateFilter, setStateFilter] = useState('');
  const [validation, setValidation] = useState('');
  const [dirty, setDirty] = useState(false);
  const canManage = operator.role === 'ADMIN';
  const canAuthor = ['TESTER', 'ADMIN'].includes(operator.role);
  const canReview = ['APPROVER', 'ADMIN'].includes(operator.role);

  const [projectForm, setProjectForm] = useState({ name: '', code: '', description: '' });
  const [moduleForm, setModuleForm] = useState({ project_id: 0, name: '', code: '', description: '' });
  const [suiteForm, setSuiteForm] = useState({ project_id: 0, module_id: 0, name: '', code: '', description: '' });
  const [caseForm, setCaseForm] = useState({
    project_id: 0, module_id: 0, suite_id: 0, case_key: '', title: '', objective: '', preconditions: '',
    test_type: 'FUNCTIONAL', priority: 'MEDIUM', severity: 'MEDIUM', tags: '', steps: [emptyStep(1), emptyStep(2)],
  });
  const [runForm, setRunForm] = useState({ project_id: 0, suite_id: 0, name: '', case_ids: [] as number[] });
  const [resultForm, setResultForm] = useState({ status: 'PASSED' as ManualResultStatus, actual_result: '', notes: '' });

  const approvedCases = useMemo(() => cases.filter((item) => item.lifecycle_state === 'APPROVED' && item.status !== 'ARCHIVED'), [cases]);
  const reviewCases = useMemo(() => cases.filter((item) => item.lifecycle_state === 'IN_REVIEW'), [cases]);

  const load = async () => {
    setLoading(true); setError('');
    try {
      const [projectList, moduleList, suiteList, caseList, runList] = await Promise.all([
        fetchTestProjects(),
        fetchTestModules(),
        fetchTestSuites(),
        fetchTestCases(`?search=${encodeURIComponent(search)}${stateFilter ? `&lifecycle_state=${stateFilter}` : ''}`),
        fetchManualRuns(),
      ]);
      const projectItems = Array.isArray(projectList.items) ? projectList.items : [];
      const moduleItems = Array.isArray(moduleList) ? moduleList : [];
      const suiteItems = Array.isArray(suiteList) ? suiteList : [];
      const caseItems = Array.isArray(caseList.items) ? caseList.items : [];
      const runItems = Array.isArray(runList) ? runList : [];
      setProjects(projectItems); setModules(moduleItems); setSuites(suiteItems); setCases(caseItems); setRuns(runItems);
      const firstProject = projectItems[0]?.id ?? 0;
      const firstModule = moduleItems[0]?.id ?? 0;
      const firstSuite = suiteItems[0]?.id ?? 0;
      setModuleForm((current) => ({ ...current, project_id: current.project_id || firstProject }));
      setSuiteForm((current) => ({ ...current, project_id: current.project_id || firstProject, module_id: current.module_id || firstModule }));
      setCaseForm((current) => ({ ...current, project_id: current.project_id || firstProject, module_id: current.module_id || firstModule, suite_id: current.suite_id || firstSuite }));
      setRunForm((current) => ({ ...current, project_id: current.project_id || firstProject, suite_id: current.suite_id || firstSuite }));
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Unable to load test management data.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { void load(); }, []);
  useEffect(() => {
    const handler = (event: BeforeUnloadEvent) => {
      if (!dirty) return;
      event.preventDefault();
      event.returnValue = '';
    };
    window.addEventListener('beforeunload', handler);
    return () => window.removeEventListener('beforeunload', handler);
  }, [dirty]);

  const submitProject = async (event: FormEvent) => {
    event.preventDefault(); setSubmitting(true); setError('');
    try { await createTestProject(projectForm); setProjectForm({ name: '', code: '', description: '' }); setMessage('Project created.'); await load(); }
    catch (reason) { setError(reason instanceof Error ? reason.message : 'Project creation failed.'); }
    finally { setSubmitting(false); }
  };

  const submitModule = async (event: FormEvent) => {
    event.preventDefault(); setSubmitting(true); setError('');
    try { await createTestModule(moduleForm); setModuleForm((current) => ({ ...current, name: '', code: '', description: '' })); setMessage('Module created.'); await load(); }
    catch (reason) { setError(reason instanceof Error ? reason.message : 'Module creation failed.'); }
    finally { setSubmitting(false); }
  };

  const submitSuite = async (event: FormEvent) => {
    event.preventDefault(); setSubmitting(true); setError('');
    try { await createTestSuite(suiteForm); setSuiteForm((current) => ({ ...current, name: '', code: '', description: '' })); setMessage('Suite created.'); await load(); }
    catch (reason) { setError(reason instanceof Error ? reason.message : 'Suite creation failed.'); }
    finally { setSubmitting(false); }
  };

  const validateCase = () => {
    if (!caseForm.title.trim() || !caseForm.case_key.trim()) return 'Case key and title are required.';
    if (caseForm.steps.some((step) => !step.action.trim() || !step.expected_result.trim())) return 'Every step needs an action and expected result.';
    return '';
  };

  const submitCase = async (event: FormEvent) => {
    event.preventDefault();
    const problem = validateCase();
    setValidation(problem);
    if (problem || submitting) return;
    setSubmitting(true); setError('');
    try {
      await createTestCase({ ...caseForm, tags: caseForm.tags.split(',').map((item) => item.trim()).filter(Boolean) });
      setCaseForm((current) => ({ ...current, case_key: '', title: '', objective: '', preconditions: '', tags: '', steps: [emptyStep(1), emptyStep(2)] }));
      setDirty(false); setMessage('Test case draft created.'); await load();
    } catch (reason) { setError(reason instanceof Error ? reason.message : 'Test case creation failed.'); }
    finally { setSubmitting(false); }
  };

  const addStep = () => { setCaseForm((current) => ({ ...current, steps: [...current.steps, emptyStep(current.steps.length + 1)] })); setDirty(true); };
  const removeStep = (index: number) => setCaseForm((current) => ({ ...current, steps: current.steps.filter((_, itemIndex) => itemIndex !== index).map((step, itemIndex) => ({ ...step, step_number: itemIndex + 1 })) }));
  const moveStep = (index: number, delta: number) => {
    const next = [...caseForm.steps];
    const target = index + delta;
    if (target < 0 || target >= next.length) return;
    [next[index], next[target]] = [next[target], next[index]];
    setCaseForm((current) => ({ ...current, steps: next.map((step, itemIndex) => ({ ...step, step_number: itemIndex + 1 })) }));
    setDirty(true);
  };

  const lifecycle = async (action: 'submit' | 'approve' | 'reject' | 'archive', item: TestCase) => {
    try {
      if (action === 'submit') await submitTestCase(item.id);
      if (action === 'approve') await approveTestCase(item.id);
      if (action === 'reject') {
        const reason = window.prompt('Rejection reason');
        if (!reason) return;
        await rejectTestCase(item.id, reason);
      }
      if (action === 'archive' && window.confirm('Archive this test case?')) await archiveTestCase(item.id);
      await load();
    } catch (reason) { setError(reason instanceof Error ? reason.message : 'Lifecycle action failed.'); }
  };

  const openVersions = async (item: TestCase) => {
    setSelectedCase(item);
    setVersions(await fetchTestCaseVersions(item.id));
  };

  const submitRun = async (event: FormEvent) => {
    event.preventDefault();
    if (!runForm.case_ids.length) { setValidation('Select at least one approved case.'); return; }
    setSubmitting(true); setError('');
    try { await createManualRun(runForm); setRunForm((current) => ({ ...current, name: '', case_ids: [] })); setMessage('Manual run created.'); await load(); }
    catch (reason) { setError(reason instanceof Error ? reason.message : 'Manual run creation failed.'); }
    finally { setSubmitting(false); }
  };

  const openRun = async (run: ManualRun) => {
    setSelectedRun(run);
    const nextCases = await fetchManualRunCases(run.id);
    setRunCases(nextCases);
    setSelectedRunCase(nextCases[0] ?? null);
    if (nextCases[0]) setEvidence(await fetchManualEvidence(run.id, nextCases[0].id));
  };

  const saveResult = async () => {
    if (!selectedRun || !selectedRunCase) return;
    if (['FAILED', 'BLOCKED'].includes(resultForm.status) && !resultForm.notes.trim()) { setValidation('Failed or blocked results require a note.'); return; }
    try {
      await updateManualStep(selectedRun.id, selectedRunCase.id, 1, resultForm);
      await updateManualRunCase(selectedRun.id, selectedRunCase.id, resultForm);
      setMessage('Manual result saved.');
      await openRun(selectedRun);
    } catch (reason) { setError(reason instanceof Error ? reason.message : 'Manual result failed.'); }
  };

  const uploadEvidence = async (file: File | undefined) => {
    if (!file || !selectedRun || !selectedRunCase) return;
    try { await uploadManualEvidence(selectedRun.id, selectedRunCase.id, file); setEvidence(await fetchManualEvidence(selectedRun.id, selectedRunCase.id)); }
    catch (reason) { setError(reason instanceof Error ? reason.message : 'Evidence upload failed.'); }
  };

  return <section className="section" id="test-management"><div className="section-inner">
    <div className="section-title"><h2>Test Management</h2><p>Manage manual test design, approval, versions, and execution.</p></div>
    <div className="tabbar" role="tablist" aria-label="Test management views">{(['projects','cases','review','runs'] as const).map((item) => <button key={item} className={`button ${tab === item ? 'button-primary' : 'button-secondary'}`} onClick={() => setTab(item)}>{item === 'projects' ? 'Projects' : item === 'cases' ? 'Test Cases' : item === 'review' ? 'Review' : 'Manual Runs'}</button>)}</div>
    {loading && <div className="state-panel" role="status">Loading test management...</div>}
    {error && <div className="state-panel state-error" role="alert">{error}<button className="button button-secondary" onClick={() => void load()}>Retry</button></div>}
    {message && <div className="state-panel" role="status">{message}</div>}
    {validation && <div className="state-panel state-error" role="alert">{validation}</div>}
    {!loading && tab === 'projects' && <div className="split">
      <div className="card"><h3>Projects</h3>{projects.length === 0 && <div className="state-panel">No test projects yet.</div>}{projects.map((project) => <div className="tm-row" key={project.id}><strong>{project.code}</strong><span>{project.name}</span><span>{project.status}</span></div>)}</div>
      {canManage && <div className="card"><h3>Create Structure</h3><form className="admin-form" onSubmit={submitProject}><label>Project name<input required value={projectForm.name} onChange={(event) => setProjectForm({ ...projectForm, name: event.target.value })} /></label><label>Project code<input required value={projectForm.code} onChange={(event) => setProjectForm({ ...projectForm, code: event.target.value })} /></label><label>Description<input value={projectForm.description} onChange={(event) => setProjectForm({ ...projectForm, description: event.target.value })} /></label><button className="button button-primary" disabled={submitting}>Create Project</button></form><form className="admin-form" onSubmit={submitModule}><label>Project<select value={moduleForm.project_id} onChange={(event) => setModuleForm({ ...moduleForm, project_id: Number(event.target.value) })}>{projects.map((project) => <option key={project.id} value={project.id}>{project.name}</option>)}</select></label><label>Module name<input required value={moduleForm.name} onChange={(event) => setModuleForm({ ...moduleForm, name: event.target.value })} /></label><label>Module code<input required value={moduleForm.code} onChange={(event) => setModuleForm({ ...moduleForm, code: event.target.value })} /></label><button className="button button-primary" disabled={submitting}>Create Module</button></form><form className="admin-form" onSubmit={submitSuite}><label>Project<select value={suiteForm.project_id} onChange={(event) => setSuiteForm({ ...suiteForm, project_id: Number(event.target.value) })}>{projects.map((project) => <option key={project.id} value={project.id}>{project.name}</option>)}</select></label><label>Module<select value={suiteForm.module_id} onChange={(event) => setSuiteForm({ ...suiteForm, module_id: Number(event.target.value) })}>{modules.filter((item) => item.project_id === suiteForm.project_id).map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}</select></label><label>Suite name<input required value={suiteForm.name} onChange={(event) => setSuiteForm({ ...suiteForm, name: event.target.value })} /></label><label>Suite code<input required value={suiteForm.code} onChange={(event) => setSuiteForm({ ...suiteForm, code: event.target.value })} /></label><button className="button button-primary" disabled={submitting}>Create Suite</button></form></div>}
    </div>}
    {!loading && tab === 'cases' && <div className="card"><h3>Test Cases</h3><div className="tm-filters"><label>Search<input value={search} onChange={(event) => setSearch(event.target.value)} /></label><label>State<select value={stateFilter} onChange={(event) => setStateFilter(event.target.value)}><option value="">All</option><option>DRAFT</option><option>IN_REVIEW</option><option>APPROVED</option><option>REJECTED</option></select></label><button className="button button-secondary" onClick={() => { setSearch(''); setStateFilter(''); void load(); }}>Clear Filters</button><button className="button button-primary" onClick={() => void load()}>Apply</button></div>{cases.length === 0 && <div className="state-panel">No test cases match the filters.</div>}<div className="tm-table">{cases.map((item) => <div className="tm-case-row" key={item.id}><strong>{item.case_key}</strong><span>{item.title}</span><span className="role-badge">{item.lifecycle_state}</span><span>{item.priority}</span><span>v{item.current_version}</span><span className="table-actions">{item.lifecycle_state === 'DRAFT' && item.created_by === operator.id && <button className="button button-secondary" onClick={() => void lifecycle('submit', item)}>Submit</button>}{canReview && item.lifecycle_state === 'IN_REVIEW' && item.created_by !== operator.id && <button className="button button-primary" onClick={() => void lifecycle('approve', item)}>Approve</button>}{canReview && item.lifecycle_state === 'IN_REVIEW' && item.created_by !== operator.id && <button className="button button-secondary" onClick={() => void lifecycle('reject', item)}>Reject</button>}{canReview && item.lifecycle_state === 'IN_REVIEW' && item.created_by === operator.id && <button className="button button-secondary" disabled>Self Approval Blocked</button>}<button className="button button-secondary" onClick={() => void openVersions(item)}>Versions</button><button className="button button-secondary" onClick={() => void lifecycle('archive', item)}>Archive</button></span></div>)}</div>{canAuthor && <form className="tm-editor" onSubmit={submitCase}><h3>Case Editor</h3><label>Project<select value={caseForm.project_id} onChange={(event) => { setCaseForm({ ...caseForm, project_id: Number(event.target.value) }); setDirty(true); }}>{projects.map((project) => <option key={project.id} value={project.id}>{project.name}</option>)}</select></label><label>Module<select value={caseForm.module_id} onChange={(event) => { setCaseForm({ ...caseForm, module_id: Number(event.target.value) }); setDirty(true); }}>{modules.filter((item) => item.project_id === caseForm.project_id).map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}</select></label><label>Suite<select value={caseForm.suite_id} onChange={(event) => { setCaseForm({ ...caseForm, suite_id: Number(event.target.value) }); setDirty(true); }}>{suites.filter((item) => item.project_id === caseForm.project_id && item.module_id === caseForm.module_id).map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}</select></label><label>Case key<input required value={caseForm.case_key} onChange={(event) => { setCaseForm({ ...caseForm, case_key: event.target.value }); setDirty(true); }} /></label><label>Title<input required value={caseForm.title} onChange={(event) => { setCaseForm({ ...caseForm, title: event.target.value }); setDirty(true); }} /></label><label>Objective<textarea value={caseForm.objective} onChange={(event) => { setCaseForm({ ...caseForm, objective: event.target.value }); setDirty(true); }} /></label><label>Preconditions<textarea value={caseForm.preconditions} onChange={(event) => { setCaseForm({ ...caseForm, preconditions: event.target.value }); setDirty(true); }} /></label><label>Priority<select value={caseForm.priority} onChange={(event) => setCaseForm({ ...caseForm, priority: event.target.value })}><option>LOW</option><option>MEDIUM</option><option>HIGH</option><option>CRITICAL</option></select></label><label>Tags<input value={caseForm.tags} onChange={(event) => setCaseForm({ ...caseForm, tags: event.target.value })} /></label><div className="tm-steps">{caseForm.steps.map((step, index) => <div className="tm-step" key={step.step_number}><strong>Step {step.step_number}</strong><label>Action<input aria-label={`Action ${step.step_number}`} value={step.action} onChange={(event) => { const next = [...caseForm.steps]; next[index] = { ...step, action: event.target.value }; setCaseForm({ ...caseForm, steps: next }); setDirty(true); }} /></label><label>Expected result<input aria-label={`Expected result ${step.step_number}`} value={step.expected_result} onChange={(event) => { const next = [...caseForm.steps]; next[index] = { ...step, expected_result: event.target.value }; setCaseForm({ ...caseForm, steps: next }); setDirty(true); }} /></label><label>Test data<input aria-label={`Test data ${step.step_number}`} value={step.test_data ?? ''} onChange={(event) => { const next = [...caseForm.steps]; next[index] = { ...step, test_data: event.target.value }; setCaseForm({ ...caseForm, steps: next }); setDirty(true); }} /></label><div className="table-actions"><button type="button" className="button button-secondary" onClick={() => moveStep(index, -1)}>Up</button><button type="button" className="button button-secondary" onClick={() => moveStep(index, 1)}>Down</button><button type="button" className="button button-secondary" onClick={() => removeStep(index)}>Remove</button></div></div>)}</div><button type="button" className="button button-secondary" onClick={addStep}>Add Step</button><button className="button button-primary" disabled={submitting}>Create Draft</button></form>}</div>}
    {!loading && tab === 'review' && <div className="card"><h3>Awaiting Review</h3>{reviewCases.length === 0 && <div className="state-panel">No cases awaiting review.</div>}{reviewCases.map((item) => <div className="tm-case-row" key={item.id}><strong>{item.case_key}</strong><span>{item.title}</span><span>Creator {item.created_by}</span><span>{item.created_by === operator.id ? 'Self approval blocked' : 'Ready'}</span><span className="table-actions"><button className="button button-primary" disabled={!canReview || item.created_by === operator.id} onClick={() => void lifecycle('approve', item)}>Approve</button><button className="button button-secondary" disabled={!canReview || item.created_by === operator.id} onClick={() => void lifecycle('reject', item)}>Reject</button></span></div>)}</div>}
    {!loading && tab === 'runs' && <div className="split"><div className="card"><h3>Manual Runs</h3>{runs.length === 0 && <div className="state-panel">No manual runs yet.</div>}{runs.map((run) => <div className="tm-row" key={run.id}><strong>{run.run_key}</strong><span>{run.name}</span><span>{run.status}</span><span>{run.progress}</span><button className="button button-secondary" onClick={() => void openRun(run)}>Open</button>{run.status === 'PLANNED' && <button className="button button-primary" onClick={() => void startManualRun(run.id).then(load)}>Start</button>}{run.status === 'IN_PROGRESS' && <button className="button button-primary" onClick={() => void completeManualRun(run.id).then(load)}>Complete</button>}</div>)}{canAuthor && <form className="admin-form" onSubmit={submitRun}><label>Project<select value={runForm.project_id} onChange={(event) => setRunForm({ ...runForm, project_id: Number(event.target.value) })}>{projects.map((project) => <option key={project.id} value={project.id}>{project.name}</option>)}</select></label><label>Suite<select value={runForm.suite_id} onChange={(event) => setRunForm({ ...runForm, suite_id: Number(event.target.value) })}>{suites.filter((suite) => suite.project_id === runForm.project_id).map((suite) => <option key={suite.id} value={suite.id}>{suite.name}</option>)}</select></label><label>Run name<input required value={runForm.name} onChange={(event) => setRunForm({ ...runForm, name: event.target.value })} /></label><fieldset><legend>Approved cases</legend>{approvedCases.map((item) => <label key={item.id}><input type="checkbox" checked={runForm.case_ids.includes(item.id)} onChange={(event) => setRunForm((current) => ({ ...current, case_ids: event.target.checked ? [...current.case_ids, item.id] : current.case_ids.filter((id) => id !== item.id) }))} />{item.case_key} v{item.current_version}</label>)}</fieldset><button className="button button-primary" disabled={submitting}>Create Manual Run</button></form>}</div><div className="card"><h3>Manual Execution</h3>{!selectedRun && <div className="state-panel">Open a manual run to record results.</div>}{selectedRun && <><p><strong>{selectedRun.run_key}</strong> {selectedRun.status}</p><select aria-label="Run case" value={selectedRunCase?.id ?? ''} onChange={async (event) => { const next = runCases.find((item) => item.id === Number(event.target.value)) ?? null; setSelectedRunCase(next); if (next) setEvidence(await fetchManualEvidence(selectedRun.id, next.id)); }}>{runCases.map((item) => <option key={item.id} value={item.id}>Case {item.test_case_id} v{item.test_case_version} - {item.status}</option>)}</select><label>Result<select value={resultForm.status} onChange={(event) => setResultForm({ ...resultForm, status: event.target.value as ManualResultStatus })}><option>PASSED</option><option>FAILED</option><option>BLOCKED</option><option>SKIPPED</option></select></label><label>Actual result<textarea value={resultForm.actual_result} onChange={(event) => setResultForm({ ...resultForm, actual_result: event.target.value })} /></label><label>Notes<textarea value={resultForm.notes} onChange={(event) => setResultForm({ ...resultForm, notes: event.target.value })} /></label><button className="button button-primary" onClick={() => void saveResult()}>Save Progress</button><label>Evidence<input type="file" onChange={(event) => void uploadEvidence(event.target.files?.[0])} /></label>{evidence.length === 0 ? <div className="state-panel">No evidence uploaded.</div> : evidence.map((item) => <div className="tm-row" key={item.id}><span>{item.original_filename}</span><span>{item.evidence_type}</span><span>{item.size_bytes} bytes</span><a className="button button-secondary" href={evidenceDownloadUrl(item.id)} target="_blank" rel="noreferrer">Download</a></div>)}</>}</div></div>}
    {selectedCase && <div className="modal-backdrop"><div className="modal" role="dialog" aria-modal="true" aria-labelledby="versions-title"><h3 id="versions-title">Version History</h3>{versions.map((version) => <div className="tm-row" key={version.id}><strong>v{version.version_number}</strong><span>{version.source_state}</span><span>{version.change_summary}</span></div>)}<div className="modal-actions"><button className="button button-secondary" onClick={() => setSelectedCase(null)}>Close</button></div></div></div>}
  </div></section>;
}
