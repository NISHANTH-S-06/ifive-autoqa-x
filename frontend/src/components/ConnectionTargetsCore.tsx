import { type FormEvent, useEffect, useMemo, useState } from 'react';
import { useAuth } from '../authContext';
import {
  approveConnectionTarget,
  approveExecutionTarget,
  archiveConnectionTarget,
  createConnectionTarget,
  createCredentialProfile,
  disableConnectionTarget,
  disableExecutionTarget,
  fetchConnectionChecks,
  fetchConnectionTargets,
  fetchCredentialProfiles,
  fetchTargetVersions,
  rejectConnectionTarget,
  runConnectionCheck,
  submitExecutionTarget,
  submitConnectionTarget,
} from '../services/connectionTargets';
import type { CheckMethod, ConnectionCheck, ConnectionTarget, ConnectionTargetVersion, CredentialProfile } from '../types/connectionTarget';
import { fetchProjects } from '../services/testRuns';
import type { Project } from '../types/product';

export function ConnectionTargetsCore() {
  const { operator } = useAuth();
  const [tab, setTab] = useState<'targets' | 'review' | 'checks' | 'credentials'>('targets');
  const [targets, setTargets] = useState<ConnectionTarget[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [checks, setChecks] = useState<ConnectionCheck[]>([]);
  const [versions, setVersions] = useState<ConnectionTargetVersion[]>([]);
  const [profiles, setProfiles] = useState<CredentialProfile[]>([]);
  const [selected, setSelected] = useState<ConnectionTarget | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  const [search, setSearch] = useState('');
  const [stateFilter, setStateFilter] = useState('');
  const [dirty, setDirty] = useState(false);
  const [form, setForm] = useState({ project_id: 0, target_key: '', name: '', description: '', environment_type: 'LOCAL', base_url: 'http://127.0.0.1:3300', allowed_probe_paths: '/\n/health', tls_required: false, tls_verify: true, connection_timeout_seconds: 3 });

  const [checkForm, setCheckForm] = useState({ method: 'HEAD' as CheckMethod, probe_path: '/' });
  const [profileForm, setProfileForm] = useState({ profile_name: '', username_hint: '', secret_source: 'NONE' });
  const canAuthor = ['TESTER', 'ADMIN'].includes(operator.role);
  const canReview = ['APPROVER', 'ADMIN'].includes(operator.role);
  const canAdmin = operator.role === 'ADMIN';
  const reviewTargets = useMemo(() => targets.filter((item) => item.lifecycle_state === 'IN_REVIEW'), [targets]);
  const approvedTargets = useMemo(() => targets.filter((item) => item.lifecycle_state === 'APPROVED' && item.enabled), [targets]);

  const load = async () => {
    setLoading(true); setError('');
    try {
      const query = `?search=${encodeURIComponent(search)}${stateFilter ? `&lifecycle_state=${stateFilter}` : ''}`;
      const [list, projectList] = await Promise.all([fetchConnectionTargets(query), fetchProjects()]);
      setProjects(projectList);
      setForm((current) => ({ ...current, project_id: current.project_id || projectList[0]?.id || 0 }));
      const items = Array.isArray(list.items) ? list.items : [];
      setTargets(items);
      const nextSelected = selected ? items.find((item) => item.id === selected.id) ?? null : items[0] ?? null;
      setSelected(nextSelected);
      if (nextSelected) {
        setChecks(await fetchConnectionChecks(nextSelected.id).catch(() => []));
        setProfiles(await fetchCredentialProfiles(nextSelected.id).catch(() => []));
      }
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Unable to load connection targets.');
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

  const paths = () => form.allowed_probe_paths.split('\n').map((item) => item.trim()).filter(Boolean);

  const submitTarget = async (event: FormEvent) => {
    event.preventDefault();
    if (submitting) return;
    setSubmitting(true); setError('');
    try {
      await createConnectionTarget({ ...form, allowed_probe_paths: paths() });
      setForm((current) => ({ ...current, target_key: '', name: '', description: '' }));
      setDirty(false); setMessage('Connection target draft created.'); await load();
    } catch (reason) { setError(reason instanceof Error ? reason.message : 'Target creation failed.'); }
    finally { setSubmitting(false); }
  };

  const lifecycle = async (action: 'submit' | 'approve' | 'reject' | 'disable' | 'archive', item: ConnectionTarget) => {
    try {
      if (action === 'submit') await submitConnectionTarget(item.id);
      if (action === 'approve') await approveConnectionTarget(item.id);
      if (action === 'reject') {
        const reason = window.prompt('Rejection reason');
        if (!reason) return;
        await rejectConnectionTarget(item.id, reason);
      }
      if (action === 'disable') await disableConnectionTarget(item.id);
      if (action === 'archive' && window.confirm('Archive this target?')) await archiveConnectionTarget(item.id);
      setMessage(`Target ${action} completed.`);
      await load();
    } catch (reason) { setError(reason instanceof Error ? reason.message : 'Target action failed.'); }
  };

  const executionApproval = async (action: 'submit' | 'approve' | 'disable', item: ConnectionTarget) => {
    try {
      if (action === 'submit') await submitExecutionTarget(item.id);
      if (action === 'approve') await approveExecutionTarget(item.id);
      if (action === 'disable') await disableExecutionTarget(item.id);
      setMessage(`Execution ${action} completed.`);
      await load();
    } catch (reason) { setError(reason instanceof Error ? reason.message : 'Execution approval action failed.'); }
  };

  const openTarget = async (item: ConnectionTarget) => {
    setSelected(item);
    setCheckForm((current) => ({ ...current, probe_path: item.allowed_probe_paths[0] ?? '/' }));
    setChecks(await fetchConnectionChecks(item.id));
    setProfiles(await fetchCredentialProfiles(item.id));
  };

  const showVersions = async (item: ConnectionTarget) => {
    setSelected(item);
    setVersions(await fetchTargetVersions(item.id));
  };

  const submitCheck = async (event: FormEvent) => {
    event.preventDefault();
    if (!selected || submitting) return;
    setSubmitting(true); setError('');
    try {
      const result = await runConnectionCheck(selected.id, checkForm.method, checkForm.probe_path);
      setMessage(`Connection check ${result.status}.`);
      await openTarget(selected);
    } catch (reason) { setError(reason instanceof Error ? reason.message : 'Connection check failed.'); }
    finally { setSubmitting(false); }
  };

  const submitProfile = async (event: FormEvent) => {
    event.preventDefault();
    if (!selected || submitting) return;
    setSubmitting(true); setError('');
    try {
      await createCredentialProfile(selected.id, { ...profileForm, username_hint: profileForm.username_hint || null });
      setProfileForm({ profile_name: '', username_hint: '', secret_source: 'NONE' });
      setMessage('Credential metadata saved. No password or token was stored.');
      setProfiles(await fetchCredentialProfiles(selected.id));
    } catch (reason) { setError(reason instanceof Error ? reason.message : 'Credential metadata failed.'); }
    finally { setSubmitting(false); }
  };

  const renderTargetRow = (item: ConnectionTarget) => <div className="ct-row" key={item.id}>
    <strong>{item.target_key}</strong><span>{item.name}</span><span className="origin-text">{item.normalized_origin}</span><span className="role-badge">{item.lifecycle_state}</span><span>{item.execution_enabled ? 'Execution Enabled' : 'Execution Disabled'}</span>
    <span className="table-actions"><button className="button button-secondary" onClick={() => void openTarget(item)}>Open</button><button className="button button-secondary" onClick={() => void showVersions(item)}>Versions</button>{item.lifecycle_state === 'DRAFT' && (canAdmin || item.created_by === operator.id) && <button className="button button-primary" onClick={() => void lifecycle('submit', item)}>Submit</button>}{canReview && item.lifecycle_state === 'IN_REVIEW' && item.created_by !== operator.id && <button className="button button-primary" onClick={() => void lifecycle('approve', item)}>Approve</button>}{canReview && item.lifecycle_state === 'IN_REVIEW' && item.created_by !== operator.id && <button className="button button-secondary" onClick={() => void lifecycle('reject', item)}>Reject</button>}{canReview && item.lifecycle_state === 'IN_REVIEW' && item.created_by === operator.id && <button className="button button-secondary" disabled>Self Approval Blocked</button>}{item.lifecycle_state === 'APPROVED' && item.enabled && (canAdmin || item.created_by === operator.id) && !item.execution_submitted_at && <button className="button button-secondary" onClick={() => void executionApproval('submit', item)}>Submit Execution</button>}{canReview && item.execution_submitted_at && !item.execution_enabled && item.created_by !== operator.id && item.execution_submitted_by !== operator.id && <button className="button button-primary" onClick={() => void executionApproval('approve', item)}>Approve Execution</button>}{canReview && item.execution_submitted_at && !item.execution_enabled && (item.created_by === operator.id || item.execution_submitted_by === operator.id) && <button className="button button-secondary" disabled>Execution Self Approval Blocked</button>}{canAdmin && item.execution_enabled && <button className="button button-secondary" onClick={() => void executionApproval('disable', item)}>Disable Execution</button>}{canAdmin && item.lifecycle_state === 'APPROVED' && <button className="button button-secondary" onClick={() => void lifecycle('disable', item)}>Disable</button>}{canAdmin && item.lifecycle_state !== 'ARCHIVED' && <button className="button button-secondary" onClick={() => void lifecycle('archive', item)}>Archive</button>}</span>
  </div>;

  return <section className="section" id="connection-targets"><div className="section-inner">
    <div className="section-title"><h2>Connection Targets</h2><p>Register and approve restricted read-only targets for safe connectivity checks.</p></div>
    <div className="tabbar" role="tablist" aria-label="Connection target views">{(['targets','review','checks','credentials'] as const).map((item) => <button key={item} className={`button ${tab === item ? 'button-primary' : 'button-secondary'}`} onClick={() => setTab(item)}>{item === 'targets' ? 'Targets' : item === 'review' ? 'Approval' : item === 'checks' ? 'Checks' : 'Credentials'}</button>)}</div>
    {loading && <div className="state-panel" role="status">Loading connection targets...</div>}
    {error && <div className="state-panel state-error" role="alert">{error}<button className="button button-secondary" onClick={() => void load()}>Retry</button></div>}
    {message && <div className="state-panel" role="status">{message}</div>}
    {!loading && tab === 'targets' && <div className="split">
      <div className="card"><h3>Approved Target Registry</h3><div className="tm-filters"><label>Find targets<input value={search} onChange={(event) => setSearch(event.target.value)} /></label><label>Target state<select value={stateFilter} onChange={(event) => setStateFilter(event.target.value)}><option value="">All</option><option>DRAFT</option><option>IN_REVIEW</option><option>APPROVED</option><option>REJECTED</option><option>DISABLED</option></select></label><button className="button button-secondary" onClick={() => { setSearch(''); setStateFilter(''); void load(); }}>Clear Target Filters</button><button className="button button-primary" onClick={() => void load()}>Filter Targets</button></div>{targets.length === 0 && <div className="state-panel">No connection targets registered.</div>}<div className="tm-table">{targets.map(renderTargetRow)}</div></div>
      {canAuthor && <div className="card"><h3>Create Target Draft</h3><form className="tm-editor" onSubmit={submitTarget}><label>Project<select required value={form.project_id} onChange={(event) => { setForm({ ...form, project_id: Number(event.target.value) }); setDirty(true); }}>{projects.map((project) => <option key={project.id} value={project.id}>{project.name}</option>)}</select></label><label>Target key<input required value={form.target_key} onChange={(event) => { setForm({ ...form, target_key: event.target.value }); setDirty(true); }} /></label><label>Name<input required value={form.name} onChange={(event) => { setForm({ ...form, name: event.target.value }); setDirty(true); }} /></label><label>Target tier<select value={form.environment_type} onChange={(event) => { setForm({ ...form, environment_type: event.target.value }); setDirty(true); }}><option>LOCAL</option><option>DEVELOPMENT</option><option>QA</option><option>STAGING</option></select></label><label>Base URL<input required value={form.base_url} onChange={(event) => { setForm({ ...form, base_url: event.target.value }); setDirty(true); }} /></label><label>Probe paths<textarea required value={form.allowed_probe_paths} onChange={(event) => { setForm({ ...form, allowed_probe_paths: event.target.value }); setDirty(true); }} /></label><label>Timeout seconds<input type="number" min={1} max={15} value={form.connection_timeout_seconds} onChange={(event) => setForm({ ...form, connection_timeout_seconds: Number(event.target.value) })} /></label><label><input type="checkbox" checked={form.tls_verify} onChange={(event) => setForm({ ...form, tls_verify: event.target.checked })} />Verify TLS certificates</label><button className="button button-primary" disabled={submitting || form.project_id === 0}>Create Target Draft</button></form></div>}
    </div>}
    {!loading && tab === 'review' && <div className="card"><h3>Target Approval</h3><div className="state-panel">Target Authorization allows only restricted HEAD/GET checks. Execution readiness requires a separate execution approval. Production remains blocked.</div>{reviewTargets.length === 0 && <div className="state-panel">No targets awaiting approval.</div>}{reviewTargets.map(renderTargetRow)}{targets.filter((item) => item.lifecycle_state === 'APPROVED' && item.execution_submitted_at && !item.execution_enabled).map(renderTargetRow)}</div>}
    {!loading && tab === 'checks' && <div className="split"><div className="card"><h3>Target Health</h3>{approvedTargets.length === 0 && <div className="state-panel">No approved enabled targets can be checked.</div>}{approvedTargets.map((item) => <button className="button button-secondary target-picker" key={item.id} onClick={() => void openTarget(item)}>{item.target_key} {item.last_check_status ?? 'NOT_CHECKED'}</button>)}</div><div className="card"><h3>Connection Check</h3>{!selected && <div className="state-panel">Select an approved target.</div>}{selected && <><p><strong>{selected.target_key}</strong> <span className="origin-text">{selected.normalized_origin}</span></p><form className="admin-form" onSubmit={submitCheck}><label>Probe path<select value={checkForm.probe_path} onChange={(event) => setCheckForm({ ...checkForm, probe_path: event.target.value })}>{selected.allowed_probe_paths.map((path) => <option key={path}>{path}</option>)}</select></label><label>Method<select value={checkForm.method} onChange={(event) => setCheckForm({ ...checkForm, method: event.target.value as CheckMethod })}><option>HEAD</option><option>GET</option></select></label><button className="button button-primary" disabled={submitting || selected.lifecycle_state !== 'APPROVED' || !selected.enabled}>Start Check</button></form><h3>Connection History</h3>{checks.length === 0 && <div className="state-panel">No checks recorded.</div>}{checks.map((check) => <div className="ct-check-row" key={check.id}><strong>{check.status}</strong><span>{check.method} {check.probe_path}</span><span>{check.http_status ?? '-'}</span><span>{check.duration_ms ?? 0} ms</span><span>{check.response_headers['content-type'] ?? 'no content type'}</span><span>{check.safe_error_message ?? 'sanitized'}</span></div>)}</>}</div></div>}
    {!loading && tab === 'credentials' && <div className="split"><div className="card"><h3>Credential Profile Metadata</h3>{!selected && <div className="state-panel">Open a target before adding metadata.</div>}{selected && <form className="admin-form" onSubmit={submitProfile}><label>Profile name<input required value={profileForm.profile_name} onChange={(event) => setProfileForm({ ...profileForm, profile_name: event.target.value })} /></label><label>Username hint<input value={profileForm.username_hint} onChange={(event) => setProfileForm({ ...profileForm, username_hint: event.target.value })} /></label><label>Secret source<select value={profileForm.secret_source} onChange={(event) => setProfileForm({ ...profileForm, secret_source: event.target.value })}><option>NONE</option><option>PROMPT_AT_USE</option></select></label><div className="state-panel">No password or token is stored in AutoQA. Authentication is not performed during Stage 9.</div><button className="button button-primary" disabled={submitting}>Save Metadata</button></form>}</div><div className="card"><h3>Profiles</h3>{profiles.length === 0 && <div className="state-panel">No credential metadata saved.</div>}{profiles.map((item) => <div className="tm-row" key={item.id}><strong>{item.profile_name}</strong><span>{item.username_hint ?? 'no username hint'}</span><span>{item.secret_source}</span><span>{item.enabled ? 'Enabled' : 'Disabled'}</span></div>)}</div></div>}
    {versions.length > 0 && selected && <div className="modal-backdrop"><div className="modal" role="dialog" aria-modal="true" aria-labelledby="target-versions-title"><h3 id="target-versions-title">Target Versions</h3>{versions.map((version) => <div className="tm-row" key={version.id}><strong>v{version.version_number}</strong><span>{version.source_state}</span><span>{version.change_summary}</span></div>)}<div className="modal-actions"><button className="button button-secondary" onClick={() => setVersions([])}>Close</button></div></div></div>}
  </div></section>;
}
