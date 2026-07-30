import React, { type FormEvent, useEffect, useMemo, useState } from 'react';
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
import { fetchProjects as fetchCoreProjects } from '../services/testRuns';
import type { Project } from '../types/product';
import { 
  FolderKanban, FileText, CheckSquare, PlayCircle, FolderPlus, 
  Layers, PackagePlus, Search, Filter, CheckCircle2, XCircle, 
  AlertCircle, Eye, Plus, ArrowUp, ArrowDown, Trash2
} from 'lucide-react';

const emptyStep = (step_number: number): TestCaseStep => ({ step_number, action: '', expected_result: '', test_data: '' });

interface TestManagementCoreProps {
  hideTitle?: boolean;
}

export function TestManagementCore({ hideTitle = false }: TestManagementCoreProps) {
  const { operator } = useAuth();
  const [tab, setTab] = useState<'projects' | 'cases' | 'review' | 'runs'>('projects');
  const [projects, setProjects] = useState<TestProject[]>([]);
  const [coreProjects, setCoreProjects] = useState<Project[]>([]);
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

  const [projectForm, setProjectForm] = useState({ access_project_id: 0, name: '', code: '', description: '' });
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
      const [projectList, coreProjectList, moduleList, suiteList, caseList, runList] = await Promise.all([
        fetchTestProjects(),
        fetchCoreProjects(),
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
      setProjects(projectItems); setCoreProjects(coreProjectList); setModules(moduleItems); setSuites(suiteItems); setCases(caseItems); setRuns(runItems);
      const firstProject = projectItems[0]?.id ?? 0;
      const firstModule = moduleItems[0]?.id ?? 0;
      const firstSuite = suiteItems[0]?.id ?? 0;
      setProjectForm((current) => ({ ...current, access_project_id: current.access_project_id || coreProjectList[0]?.id || 0 }));
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
    try { await createTestProject(projectForm); setProjectForm((current) => ({ ...current, name: '', code: '', description: '' })); setMessage('Project created.'); await load(); }
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

  return (
    <section className="section" id="test-management">
      {!hideTitle && (
        <div className="section-title">
          <h2>Test Management</h2>
          <p>Manage manual test design, approval, versions, and execution.</p>
        </div>
      )}

      {/* Styled Glassmorphic Tab Navigator with Bulletproof Fallback Styles */}
      <div 
        className="tabbar" 
        role="tablist" 
        aria-label="Test management views"
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
          padding: '0.4rem',
          backgroundColor: 'var(--bg-card-subtle, rgba(255, 255, 255, 0.03))',
          border: '1px solid var(--border-color, rgba(255, 255, 255, 0.1))',
          borderRadius: 'var(--radius-lg, 12px)',
          marginBottom: '1.25rem',
          flexWrap: 'wrap'
        }}
      >
        <button 
          className={`btn ${tab === 'projects' ? 'btn-primary button-primary' : 'btn-secondary button-secondary'}`} 
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.5rem',
            padding: '0.5rem 1rem',
            borderRadius: '8px',
            fontWeight: 600,
            fontSize: '0.85rem',
            cursor: 'pointer',
            border: 'none',
            backgroundColor: tab === 'projects' ? 'var(--color-primary, #2563eb)' : 'transparent',
            color: tab === 'projects' ? '#ffffff' : 'var(--text-muted, #94a3b8)',
            transition: 'all 0.15s ease'
          }}
          onClick={() => setTab('projects')}
        >
          <FolderKanban size={16} /> Projects & Structure
        </button>
        <button 
          className={`btn ${tab === 'cases' ? 'btn-primary button-primary' : 'btn-secondary button-secondary'}`} 
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.5rem',
            padding: '0.5rem 1rem',
            borderRadius: '8px',
            fontWeight: 600,
            fontSize: '0.85rem',
            cursor: 'pointer',
            border: 'none',
            backgroundColor: tab === 'cases' ? 'var(--color-primary, #2563eb)' : 'transparent',
            color: tab === 'cases' ? '#ffffff' : 'var(--text-muted, #94a3b8)',
            transition: 'all 0.15s ease'
          }}
          onClick={() => setTab('cases')}
        >
          <FileText size={16} /> Test Cases
        </button>
        <button 
          className={`btn ${tab === 'review' ? 'btn-primary button-primary' : 'btn-secondary button-secondary'}`} 
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.5rem',
            padding: '0.5rem 1rem',
            borderRadius: '8px',
            fontWeight: 600,
            fontSize: '0.85rem',
            cursor: 'pointer',
            border: 'none',
            backgroundColor: tab === 'review' ? 'var(--color-primary, #2563eb)' : 'transparent',
            color: tab === 'review' ? '#ffffff' : 'var(--text-muted, #94a3b8)',
            transition: 'all 0.15s ease'
          }}
          onClick={() => setTab('review')}
        >
          <CheckSquare size={16} /> Awaiting Review {reviewCases.length > 0 && <span className="badge badge-warning" style={{ fontSize: '0.65rem', marginLeft: '0.2rem' }}>{reviewCases.length}</span>}
        </button>
        <button 
          className={`btn ${tab === 'runs' ? 'btn-primary button-primary' : 'btn-secondary button-secondary'}`} 
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.5rem',
            padding: '0.5rem 1rem',
            borderRadius: '8px',
            fontWeight: 600,
            fontSize: '0.85rem',
            cursor: 'pointer',
            border: 'none',
            backgroundColor: tab === 'runs' ? 'var(--color-primary, #2563eb)' : 'transparent',
            color: tab === 'runs' ? '#ffffff' : 'var(--text-muted, #94a3b8)',
            transition: 'all 0.15s ease'
          }}
          onClick={() => setTab('runs')}
        >
          <PlayCircle size={16} /> Manual Execution Runs
        </button>
      </div>

      {loading && <div className="state-panel" role="status">Loading test management...</div>}
      {error && <div className="state-panel state-error" role="alert">{error}<button className="btn btn-secondary button-secondary" onClick={() => void load()}>Retry</button></div>}
      {message && <div className="state-panel" role="status">{message}</div>}
      {validation && <div className="state-panel state-error" role="alert">{validation}</div>}

      {/* TAB 1: PROJECTS & STRUCTURE */}
      {!loading && tab === 'projects' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {/* Projects List Card */}
          <div className="card" style={{ padding: '1.25rem' }}>
            <h3 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <FolderKanban size={18} style={{ color: 'var(--color-primary)' }} />
              Active Test Projects
            </h3>

            {projects.length === 0 ? (
              <div className="state-panel">No test projects created yet.</div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem' }}>
                {projects.map((project) => (
                  <div 
                    className="tm-row" 
                    key={project.id}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      padding: '0.75rem 1rem',
                      backgroundColor: 'var(--bg-card-subtle, rgba(255,255,255,0.02))',
                      border: '1px solid var(--border-color, rgba(255,255,255,0.08))',
                      borderRadius: '8px'
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                      <span style={{ fontWeight: 700, fontFamily: 'var(--font-mono)', color: 'var(--color-primary, #3b82f6)', fontSize: '0.9rem' }}>{project.code}</span>
                      <span style={{ fontWeight: 500, fontSize: '0.9rem' }}>{project.name}</span>
                    </div>
                    <span className="badge badge-pass">{project.status || 'ACTIVE'}</span>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* 3-Column Creation Grid */}
          {canManage && (
            <div>
              <h3 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: '1rem' }}>
                Create Test Structure
              </h3>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.25rem' }}>
                {/* Form 1: Create Project */}
                <div className="card" style={{ padding: '1.25rem', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                  <div>
                    <h4 style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                      <FolderPlus size={18} style={{ color: 'var(--color-primary)' }} />
                      Create Project
                    </h4>
                    <form id="proj-form" style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }} onSubmit={submitProject}>
                      <label style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)' }}>
                        Access project
                        <select className="input select" required value={projectForm.access_project_id} onChange={(event) => setProjectForm({ ...projectForm, access_project_id: Number(event.target.value) })} style={{ width: '100%', padding: '0.5rem 0.75rem', borderRadius: '6px', backgroundColor: 'var(--bg-input)', border: '1px solid var(--border-color)', color: 'var(--text-main)' }}>
                          {coreProjects.map((project) => <option key={project.id} value={project.id}>{project.name}</option>)}
                        </select>
                      </label>
                      <label style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)' }}>
                        Project name
                        <input className="input" required value={projectForm.name} onChange={(event) => setProjectForm({ ...projectForm, name: event.target.value })} placeholder="e.g. Demo ERP" style={{ width: '100%', padding: '0.5rem 0.75rem', borderRadius: '6px', backgroundColor: 'var(--bg-input)', border: '1px solid var(--border-color)', color: 'var(--text-main)' }} />
                      </label>
                      <label style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)' }}>
                        Project code
                        <input className="input" required value={projectForm.code} onChange={(event) => setProjectForm({ ...projectForm, code: event.target.value })} placeholder="e.g. DEMO" style={{ width: '100%', padding: '0.5rem 0.75rem', borderRadius: '6px', backgroundColor: 'var(--bg-input)', border: '1px solid var(--border-color)', color: 'var(--text-main)' }} />
                      </label>
                      <label style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)' }}>
                        Description
                        <input className="input" value={projectForm.description} onChange={(event) => setProjectForm({ ...projectForm, description: event.target.value })} placeholder="Optional description" style={{ width: '100%', padding: '0.5rem 0.75rem', borderRadius: '6px', backgroundColor: 'var(--bg-input)', border: '1px solid var(--border-color)', color: 'var(--text-main)' }} />
                      </label>
                    </form>
                  </div>
                  <button form="proj-form" className="btn btn-primary button button-primary" style={{ marginTop: '1.25rem', width: '100%', padding: '0.6rem 1rem', borderRadius: '6px', fontWeight: 600, cursor: 'pointer' }} disabled={submitting || projectForm.access_project_id === 0}>
                    Create Project
                  </button>
                </div>

                {/* Form 2: Create Module */}
                <div className="card" style={{ padding: '1.25rem', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                  <div>
                    <h4 style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                      <Layers size={18} style={{ color: 'var(--color-info)' }} />
                      Create Module
                    </h4>
                    <form id="mod-form" style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }} onSubmit={submitModule}>
                      <label style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)' }}>
                        Project
                        <select className="input select" value={moduleForm.project_id} onChange={(event) => setModuleForm({ ...moduleForm, project_id: Number(event.target.value) })} style={{ width: '100%', padding: '0.5rem 0.75rem', borderRadius: '6px', backgroundColor: 'var(--bg-input)', border: '1px solid var(--border-color)', color: 'var(--text-main)' }}>
                          {projects.map((project) => <option key={project.id} value={project.id}>{project.name}</option>)}
                        </select>
                      </label>
                      <label style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)' }}>
                        Module name
                        <input className="input" required value={moduleForm.name} onChange={(event) => setModuleForm({ ...moduleForm, name: event.target.value })} placeholder="e.g. HR Management" style={{ width: '100%', padding: '0.5rem 0.75rem', borderRadius: '6px', backgroundColor: 'var(--bg-input)', border: '1px solid var(--border-color)', color: 'var(--text-main)' }} />
                      </label>
                      <label style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)' }}>
                        Module code
                        <input className="input" required value={moduleForm.code} onChange={(event) => setModuleForm({ ...moduleForm, code: event.target.value })} placeholder="e.g. HR" style={{ width: '100%', padding: '0.5rem 0.75rem', borderRadius: '6px', backgroundColor: 'var(--bg-input)', border: '1px solid var(--border-color)', color: 'var(--text-main)' }} />
                      </label>
                    </form>
                  </div>
                  <button form="mod-form" className="btn btn-primary button button-primary" style={{ marginTop: '1.25rem', width: '100%', padding: '0.6rem 1rem', borderRadius: '6px', fontWeight: 600, cursor: 'pointer' }} disabled={submitting || projects.length === 0}>
                    Create Module
                  </button>
                </div>

                {/* Form 3: Create Suite */}
                <div className="card" style={{ padding: '1.25rem', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                  <div>
                    <h4 style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                      <PackagePlus size={18} style={{ color: 'var(--color-accent)' }} />
                      Create Suite
                    </h4>
                    <form id="suite-form" style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }} onSubmit={submitSuite}>
                      <label style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)' }}>
                        Project
                        <select className="input select" value={suiteForm.project_id} onChange={(event) => setSuiteForm({ ...suiteForm, project_id: Number(event.target.value) })} style={{ width: '100%', padding: '0.5rem 0.75rem', borderRadius: '6px', backgroundColor: 'var(--bg-input)', border: '1px solid var(--border-color)', color: 'var(--text-main)' }}>
                          {projects.map((project) => <option key={project.id} value={project.id}>{project.name}</option>)}
                        </select>
                      </label>
                      <label style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)' }}>
                        Module
                        <select className="input select" value={suiteForm.module_id} onChange={(event) => setSuiteForm({ ...suiteForm, module_id: Number(event.target.value) })} style={{ width: '100%', padding: '0.5rem 0.75rem', borderRadius: '6px', backgroundColor: 'var(--bg-input)', border: '1px solid var(--border-color)', color: 'var(--text-main)' }}>
                          {modules.filter((item) => item.project_id === suiteForm.project_id).map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}
                        </select>
                      </label>
                      <label style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)' }}>
                        Suite name
                        <input className="input" required value={suiteForm.name} onChange={(event) => setSuiteForm({ ...suiteForm, name: event.target.value })} placeholder="e.g. Employee Directory" style={{ width: '100%', padding: '0.5rem 0.75rem', borderRadius: '6px', backgroundColor: 'var(--bg-input)', border: '1px solid var(--border-color)', color: 'var(--text-main)' }} />
                      </label>
                      <label style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)' }}>
                        Suite code
                        <input className="input" required value={suiteForm.code} onChange={(event) => setSuiteForm({ ...suiteForm, code: event.target.value })} placeholder="e.g. EMP-SUITE" style={{ width: '100%', padding: '0.5rem 0.75rem', borderRadius: '6px', backgroundColor: 'var(--bg-input)', border: '1px solid var(--border-color)', color: 'var(--text-main)' }} />
                      </label>
                    </form>
                  </div>
                  <button form="suite-form" className="btn btn-primary button button-primary" style={{ marginTop: '1.25rem', width: '100%', padding: '0.6rem 1rem', borderRadius: '6px', fontWeight: 600, cursor: 'pointer' }} disabled={submitting || modules.length === 0}>
                    Create Suite
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* TAB 2: TEST CASES */}
      {!loading && tab === 'cases' && (
        <div className="card">
          <h3 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: '1rem' }}>Test Cases Directory</h3>
          <div className="tm-filters">
            <label>Search
              <input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Filter cases..." />
            </label>
            <label>State
              <select value={stateFilter} onChange={(event) => setStateFilter(event.target.value)}>
                <option value="">All States</option>
                <option value="DRAFT">DRAFT</option>
                <option value="IN_REVIEW">IN_REVIEW</option>
                <option value="APPROVED">APPROVED</option>
                <option value="REJECTED">REJECTED</option>
              </select>
            </label>
            <button className="button button-secondary" onClick={() => { setSearch(''); setStateFilter(''); void load(); }}>Clear</button>
            <button className="button button-primary" onClick={() => void load()}>Apply Filters</button>
          </div>

          {cases.length === 0 && <div className="state-panel">No test cases match the active filters.</div>}

          <div className="tm-table">
            {cases.map((item) => (
              <div className="tm-case-row" key={item.id}>
                <strong style={{ fontFamily: 'var(--font-mono)', color: 'var(--color-primary)' }}>{item.case_key}</strong>
                <span style={{ fontWeight: 500 }}>{item.title}</span>
                <span className={`badge badge-${item.lifecycle_state.toLowerCase()}`}>{item.lifecycle_state}</span>
                <span>{item.priority}</span>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>v{item.current_version}</span>
                <span className="table-actions">
                  {item.lifecycle_state === 'DRAFT' && item.created_by === operator.id && (
                    <button className="button button-secondary" onClick={() => void lifecycle('submit', item)}>Submit</button>
                  )}
                  {canReview && item.lifecycle_state === 'IN_REVIEW' && item.created_by !== operator.id && (
                    <button className="button button-primary" onClick={() => void lifecycle('approve', item)}>Approve</button>
                  )}
                  {canReview && item.lifecycle_state === 'IN_REVIEW' && item.created_by !== operator.id && (
                    <button className="button button-secondary" onClick={() => void lifecycle('reject', item)}>Reject</button>
                  )}
                  {canReview && item.lifecycle_state === 'IN_REVIEW' && item.created_by === operator.id && (
                    <button className="button button-secondary" disabled>Self Approval Blocked</button>
                  )}
                  <button className="button button-secondary" onClick={() => void openVersions(item)}>Versions</button>
                  <button className="button button-secondary" onClick={() => void lifecycle('archive', item)}>Archive</button>
                </span>
              </div>
            ))}
          </div>

          {/* Test Case Editor Form */}
          {canAuthor && (
            <form className="tm-editor" onSubmit={submitCase}>
              <h3 style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--text-main)' }}>Create Test Case Draft</h3>
              <div className="grid grid-cols-3">
                <label>Project
                  <select value={caseForm.project_id} onChange={(event) => { setCaseForm({ ...caseForm, project_id: Number(event.target.value) }); setDirty(true); }}>
                    {projects.map((project) => <option key={project.id} value={project.id}>{project.name}</option>)}
                  </select>
                </label>
                <label>Module
                  <select value={caseForm.module_id} onChange={(event) => { setCaseForm({ ...caseForm, module_id: Number(event.target.value) }); setDirty(true); }}>
                    {modules.filter((item) => item.project_id === caseForm.project_id).map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}
                  </select>
                </label>
                <label>Suite
                  <select value={caseForm.suite_id} onChange={(event) => { setCaseForm({ ...caseForm, suite_id: Number(event.target.value) }); setDirty(true); }}>
                    {suites.filter((item) => item.project_id === caseForm.project_id && item.module_id === caseForm.module_id).map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}
                  </select>
                </label>
              </div>

              <div className="grid grid-cols-2">
                <label>Case key
                  <input required value={caseForm.case_key} onChange={(event) => { setCaseForm({ ...caseForm, case_key: event.target.value }); setDirty(true); }} placeholder="e.g. TC-EMP-01" />
                </label>
                <label>Title
                  <input required value={caseForm.title} onChange={(event) => { setCaseForm({ ...caseForm, title: event.target.value }); setDirty(true); }} placeholder="e.g. Verify employee creation form" />
                </label>
              </div>

              <label>Objective
                <textarea value={caseForm.objective} onChange={(event) => { setCaseForm({ ...caseForm, objective: event.target.value }); setDirty(true); }} placeholder="Describe objective..." />
              </label>

              <div className="grid grid-cols-2">
                <label>Priority
                  <select value={caseForm.priority} onChange={(event) => setCaseForm({ ...caseForm, priority: event.target.value })}>
                    <option>LOW</option><option>MEDIUM</option><option>HIGH</option><option>CRITICAL</option>
                  </select>
                </label>
                <label>Tags
                  <input value={caseForm.tags} onChange={(event) => setCaseForm({ ...caseForm, tags: event.target.value })} placeholder="Comma separated tags" />
                </label>
              </div>

              <div className="tm-steps">
                <h4 style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-main)' }}>Ordered Test Steps</h4>
                {caseForm.steps.map((step, index) => (
                  <div className="tm-step" key={step.step_number}>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <strong style={{ fontSize: '0.8rem', color: 'var(--color-primary)' }}>Step {step.step_number}</strong>
                      <div className="table-actions">
                        <button type="button" className="button button-secondary" onClick={() => moveStep(index, -1)}><ArrowUp size={12} /></button>
                        <button type="button" className="button button-secondary" onClick={() => moveStep(index, 1)}><ArrowDown size={12} /></button>
                        <button type="button" className="button button-secondary" onClick={() => removeStep(index)}><Trash2 size={12} /></button>
                      </div>
                    </div>
                    <label>Action<input aria-label={`Action ${step.step_number}`} value={step.action} onChange={(event) => { const next = [...caseForm.steps]; next[index] = { ...step, action: event.target.value }; setCaseForm({ ...caseForm, steps: next }); setDirty(true); }} /></label>
                    <label>Expected result<input aria-label={`Expected result ${step.step_number}`} value={step.expected_result} onChange={(event) => { const next = [...caseForm.steps]; next[index] = { ...step, expected_result: event.target.value }; setCaseForm({ ...caseForm, steps: next }); setDirty(true); }} /></label>
                  </div>
                ))}
              </div>

              <div style={{ display: 'flex', gap: '0.75rem' }}>
                <button type="button" className="button button-secondary" onClick={addStep}><Plus size={14} /> Add Step</button>
                <button className="button button-primary" disabled={submitting}>Create Draft</button>
              </div>
            </form>
          )}
        </div>
      )}

      {/* TAB 3: AWAITING REVIEW */}
      {!loading && tab === 'review' && (
        <div className="card">
          <h3 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: '1rem' }}>Test Cases Awaiting Approval</h3>
          {reviewCases.length === 0 ? (
            <div className="state-panel">No test cases awaiting review.</div>
          ) : (
            reviewCases.map((item) => (
              <div className="tm-case-row" key={item.id}>
                <strong style={{ fontFamily: 'var(--font-mono)', color: 'var(--color-primary)' }}>{item.case_key}</strong>
                <span>{item.title}</span>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Creator #{item.created_by}</span>
                <span className="badge badge-in_review">{item.created_by === operator.id ? 'Self Approval Blocked' : 'Ready for Review'}</span>
                <span className="table-actions">
                  <button className="button button-primary" disabled={!canReview || item.created_by === operator.id} onClick={() => void lifecycle('approve', item)}>Approve</button>
                  <button className="button button-secondary" disabled={!canReview || item.created_by === operator.id} onClick={() => void lifecycle('reject', item)}>Reject</button>
                </span>
              </div>
            ))
          )}
        </div>
      )}

      {/* TAB 4: MANUAL RUNS */}
      {!loading && tab === 'runs' && (
        <div className="grid grid-cols-2">
          <div className="card">
            <h3 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: '1rem' }}>Manual Runs</h3>
            {runs.length === 0 ? (
              <div className="state-panel">No manual runs created yet.</div>
            ) : (
              runs.map((run) => (
                <div className="tm-row" key={run.id}>
                  <strong style={{ fontFamily: 'var(--font-mono)' }}>{run.run_key}</strong>
                  <span>{run.name}</span>
                  <span className={`badge badge-${run.status.toLowerCase()}`}>{run.status}</span>
                  <button className="button button-secondary" onClick={() => void openRun(run)}>Open</button>
                  {run.status === 'PLANNED' && <button className="button button-primary" onClick={() => void startManualRun(run.id).then(load)}>Start</button>}
                  {run.status === 'IN_PROGRESS' && <button className="button button-primary" onClick={() => void completeManualRun(run.id).then(load)}>Complete</button>}
                </div>
              ))
            )}

            {canAuthor && (
              <form className="admin-form" onSubmit={submitRun}>
                <h4 style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--text-main)' }}>Create Manual Run</h4>
                <label>Project
                  <select value={runForm.project_id} onChange={(event) => setRunForm({ ...runForm, project_id: Number(event.target.value) })}>
                    {projects.map((project) => <option key={project.id} value={project.id}>{project.name}</option>)}
                  </select>
                </label>
                <label>Suite
                  <select value={runForm.suite_id} onChange={(event) => setRunForm({ ...runForm, suite_id: Number(event.target.value) })}>
                    {suites.filter((suite) => suite.project_id === runForm.project_id).map((suite) => <option key={suite.id} value={suite.id}>{suite.name}</option>)}
                  </select>
                </label>
                <label>Run name
                  <input required value={runForm.name} onChange={(event) => setRunForm({ ...runForm, name: event.target.value })} placeholder="e.g. Sprint 24 Regression" />
                </label>
                <button className="button button-primary" disabled={submitting}>Create Manual Run</button>
              </form>
            )}
          </div>

          <div className="card">
            <h3 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: '1rem' }}>Manual Execution Panel</h3>
            {!selectedRun ? (
              <div className="state-panel">Open a manual run to record results.</div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
                <p><strong>{selectedRun.run_key}</strong> <span className="badge badge-info">{selectedRun.status}</span></p>
                <select aria-label="Run case" className="input" value={selectedRunCase?.id ?? ''} onChange={async (event) => { const next = runCases.find((item) => item.id === Number(event.target.value)) ?? null; setSelectedRunCase(next); if (next) setEvidence(await fetchManualEvidence(selectedRun.id, next.id)); }}>
                  {runCases.map((item) => <option key={item.id} value={item.id}>Case #{item.test_case_id} v{item.test_case_version} - {item.status}</option>)}
                </select>
                <button className="button button-primary" onClick={() => void saveResult()}>Save Progress</button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Version History Modal */}
      {selectedCase && (
        <div className="modal-backdrop">
          <div className="modal" role="dialog" aria-modal="true">
            <h3 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: '1rem' }}>Case Version History</h3>
            {versions.map((version) => (
              <div className="tm-row" key={version.id}>
                <strong>v{version.version_number}</strong>
                <span>{version.source_state}</span>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{version.change_summary}</span>
              </div>
            ))}
            <button className="button button-secondary" style={{ marginTop: '1rem' }} onClick={() => setSelectedCase(null)}>Close</button>
          </div>
        </div>
      )}
    </section>
  );
}

