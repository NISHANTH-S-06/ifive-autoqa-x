import { type FormEvent, useEffect, useMemo, useState } from 'react';
import { useAuth } from '../authContext';
import {
  createReportDefinition,
  createReportExport,
  disableReportDefinition,
  fetchDefectReport,
  fetchExecutionReport,
  fetchManagementDashboard,
  fetchQualityReport,
  fetchReportDefinitions,
  fetchReportExports,
  fetchTargetReport,
  fetchTraceabilityReport,
  fetchTrendReport,
  fetchWorkerReport,
  reportExportDownloadUrl,
  runReportDefinition,
} from '../services/reports';
import type { DefectReport, ExecutionReport, QualityReport, ReportDashboard, ReportDefinition, ReportExport, ReportFilters } from '../types/report';
import { fetchProjects } from '../services/testRuns';
import type { Project } from '../types/product';

const reportTypes = ['dashboard', 'executions', 'defects', 'trends', 'quality', 'traceability', 'targets', 'workers'];
const dateRanges = ['today', 'last_7_days', 'last_30_days', 'custom'];

function BarList({ title, values }: { title: string; values: Record<string, number> }) {
  const max = Math.max(1, ...Object.values(values));
  const entries = Object.entries(values);
  return <div><h3>{title}</h3>{entries.length === 0 && <div className="state-panel">No data.</div>}{entries.map(([key, value]) => <div className="report-bar" key={key}><span>{key}</span><div><i style={{ width: `${Math.max(4, (value / max) * 100)}%` }} /></div><strong>{value}</strong></div>)}</div>;
}

export function ManagementReportsCore() {
  const { operator } = useAuth();
  const [dashboard, setDashboard] = useState<ReportDashboard | null>(null);
  const [executions, setExecutions] = useState<ExecutionReport | null>(null);
  const [defects, setDefects] = useState<DefectReport | null>(null);
  const [quality, setQuality] = useState<QualityReport | null>(null);
  const [trends, setTrends] = useState<Record<string, unknown> | null>(null);
  const [traceability, setTraceability] = useState<Array<Record<string, unknown>>>([]);
  const [targets, setTargets] = useState<Record<string, unknown> | null>(null);
  const [workers, setWorkers] = useState<Record<string, unknown> | null>(null);
  const [exports, setExports] = useState<ReportExport[]>([]);
  const [definitions, setDefinitions] = useState<ReportDefinition[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [projectId, setProjectId] = useState(0);
  const [filters, setFilters] = useState<ReportFilters>({ date_range: 'last_30_days', run_type: 'ALL' });
  const [exportType, setExportType] = useState('dashboard');
  const [exportFormat, setExportFormat] = useState('csv');
  const [definition, setDefinition] = useState({ name: '', report_type: 'quality', frequency: 'DAILY' });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  const canExport = operator.role === 'ADMIN';
  const safeTrendKeys = useMemo(() => Object.keys(trends ?? {}).filter((key) => key !== 'filters'), [trends]);

  const load = async () => {
    setLoading(true); setError('');
    try {
      const [nextDashboard, nextExecutions, nextDefects, nextQuality, nextTrends, nextTraceability, nextTargets, nextWorkers, nextExports, nextDefinitions] = await Promise.all([
        fetchManagementDashboard(filters),
        fetchExecutionReport(filters),
        fetchDefectReport(filters),
        fetchQualityReport(filters),
        fetchTrendReport(filters),
        fetchTraceabilityReport(filters),
        fetchTargetReport(filters),
        fetchWorkerReport(),
        canExport ? fetchReportExports().catch(() => ({ items: [] })) : Promise.resolve({ items: [] }),
        canExport ? fetchReportDefinitions().catch(() => []) : Promise.resolve([]),
      ]);
      setDashboard(nextDashboard?.summary ? nextDashboard : null);
      setExecutions(nextExecutions?.manual && nextExecutions?.automated ? nextExecutions : null);
      setDefects(nextDefects?.by_status ? nextDefects : null);
      setQuality(nextQuality && 'pass_percentage' in nextQuality ? nextQuality : null);
      setTrends(nextTrends ?? null);
      setTraceability(Array.isArray(nextTraceability?.items) ? nextTraceability.items : []);
      setTargets(nextTargets ?? null);
      setWorkers(nextWorkers ?? null);
      setExports(nextExports.items ?? []);
      setDefinitions(Array.isArray(nextDefinitions) ? nextDefinitions : []);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Unable to load management reports.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { void load(); }, []);
  useEffect(() => {
    void fetchProjects().then((items) => {
      setProjects(items);
      setProjectId((current) => current || items[0]?.id || 0);
    }).catch(() => setProjects([]));
  }, []);

  const applyFilters = (event: FormEvent) => {
    event.preventDefault();
    void load();
  };

  const exportReport = async () => {
    try {
      const created = await createReportExport(projectId, exportType, exportFormat, filters);
      setMessage(`Report export ${created.export_key} created.`);
      setExports([created, ...exports]);
    } catch (reason) { setError(reason instanceof Error ? reason.message : 'Report export failed.'); }
  };

  const saveDefinition = async (event: FormEvent) => {
    event.preventDefault();
    try {
      const created = await createReportDefinition({ project_id: projectId, ...definition, filters });
      setDefinitions([created, ...definitions]);
      setDefinition({ ...definition, name: '' });
      setMessage('Saved report definition created.');
    } catch (reason) { setError(reason instanceof Error ? reason.message : 'Saved report creation failed.'); }
  };

  const runDefinition = async (id: number) => {
    try {
      const created = await runReportDefinition(id);
      setExports([created, ...exports]);
      setMessage(`Saved report generated ${created.export_key}.`);
      const nextDefinitions = await fetchReportDefinitions().catch(() => definitions);
      setDefinitions(Array.isArray(nextDefinitions) ? nextDefinitions : definitions);
    } catch (reason) { setError(reason instanceof Error ? reason.message : 'Saved report run failed.'); }
  };

  const disableDefinition = async (id: number) => {
    try {
      const updated = await disableReportDefinition(id);
      setDefinitions(definitions.map((item) => item.id === id ? updated : item));
      setMessage('Saved report disabled.');
    } catch (reason) { setError(reason instanceof Error ? reason.message : 'Saved report disable failed.'); }
  };

  return <section className="section" id="management-reports"><div className="section-inner">
    <div className="section-title"><h2>Management Reports</h2><p>Server-calculated execution, defect, quality, target, worker, and traceability reporting.</p></div>
    {loading && <div className="state-panel" role="status">Loading management reports...</div>}
    {error && <div className="state-panel state-error" role="alert">{error}<button className="button button-secondary" onClick={() => void load()}>Retry Reports</button></div>}
    {message && <div className="state-panel" role="status">{message}</div>}
    <form className="card admin-form" onSubmit={applyFilters}><h3>Report Filters</h3><label>Report date range<select value={filters.date_range ?? 'last_30_days'} onChange={(event) => setFilters({ ...filters, date_range: event.target.value })}>{dateRanges.map((item) => <option key={item} value={item}>{item}</option>)}</select></label><label>Report start date<input type="date" value={filters.start_date ?? ''} onChange={(event) => setFilters({ ...filters, start_date: event.target.value })} /></label><label>Report end date<input type="date" value={filters.end_date ?? ''} onChange={(event) => setFilters({ ...filters, end_date: event.target.value })} /></label><label>Report project id<input type="number" min={1} value={filters.project_id ?? ''} onChange={(event) => setFilters({ ...filters, project_id: event.target.value ? Number(event.target.value) : undefined })} /></label><label>Report run type<select value={filters.run_type ?? 'ALL'} onChange={(event) => setFilters({ ...filters, run_type: event.target.value })}><option value="ALL">All</option><option value="MANUAL">Manual</option><option value="AUTOMATED">Automated</option></select></label><label>Report defect status<input value={filters.defect_status ?? ''} onChange={(event) => setFilters({ ...filters, defect_status: event.target.value })} /></label><button className="button button-primary">Refresh Reports</button></form>
    {!loading && dashboard && <div className="report-grid">
      {Object.entries({ Projects: dashboard.summary.test_projects, Cases: dashboard.summary.test_cases, Approved: dashboard.summary.approved_test_cases, Manual: dashboard.summary.manual_runs, Automated: dashboard.summary.automated_runs, Defects: dashboard.summary.defects, Open: dashboard.summary.open_defects, Closed: dashboard.summary.closed_defects }).map(([label, value]) => <div className="metric-card" key={label}><span>{label}</span><strong>{value}</strong></div>)}
    </div>}
    {!loading && dashboard && <div className="split"><div className="card"><BarList title="Execution Results" values={dashboard.summary.result_counts} /></div><div className="card"><BarList title="Defect Status" values={defects?.by_status ?? {}} /></div></div>}
    {!loading && quality && <div className="card"><h3>Quality Metrics</h3><div className="report-grid">{Object.entries(quality).map(([key, value]) => <div className="metric-card" key={key}><span>{key.replaceAll('_', ' ')}</span><strong>{String(value)}</strong></div>)}</div></div>}
    {!loading && executions && <div className="split"><div className="card"><BarList title="Manual Case Results" values={executions.manual.case_statuses} /></div><div className="card"><BarList title="Automated Case Results" values={executions.automated.case_statuses} /></div></div>}
    {!loading && defects && <div className="split"><div className="card"><BarList title="Defect Severity" values={defects.by_severity} /></div><div className="card"><BarList title="Defect Priority" values={defects.by_priority} /></div></div>}
    {!loading && <div className="split"><div className="card"><h3>Trends</h3>{safeTrendKeys.length === 0 && <div className="state-panel">No trend data.</div>}{safeTrendKeys.map((key) => <div className="tm-row" key={key}><strong>{key}</strong><span>{JSON.stringify(trends?.[key]).slice(0, 140)}</span><span /><span /><span /></div>)}</div><div className="card"><h3>Target and Worker Health</h3><div className="tm-row"><strong>Targets</strong><span>{JSON.stringify(targets?.['target_health'] ?? {})}</span><span /><span /><span /></div><div className="tm-row"><strong>Workers</strong><span>{JSON.stringify(workers?.['status_counts'] ?? {})}</span><span /><span /><span /></div></div></div>}
    {!loading && <div className="card"><h3>Traceability</h3>{traceability.length === 0 && <div className="state-panel">No traceability rows.</div>}{traceability.slice(0, 20).map((item, index) => <div className="tm-row" key={`${item.defect_key}-${index}`}><strong>{String(item.defect_key ?? item.defect_id)}</strong><span>{String(item.status ?? '-')}</span><span>Case {String(item.test_case_id ?? '-')} v{String(item.test_case_version ?? '-')}</span><span>{item.automated_run_id ? `Auto ${item.automated_run_id}` : item.manual_run_id ? `Manual ${item.manual_run_id}` : 'No run'}</span><span /></div>)}</div>}
    {!loading && canExport && <div className="split"><div className="card"><h3>Exports</h3><div className="admin-form"><label>Access project<select required value={projectId} onChange={(event) => setProjectId(Number(event.target.value))}>{projects.map((project) => <option key={project.id} value={project.id}>{project.name}</option>)}</select></label><label>Export report type<select value={exportType} onChange={(event) => setExportType(event.target.value)}>{reportTypes.map((item) => <option key={item}>{item}</option>)}</select></label><label>Export format<select value={exportFormat} onChange={(event) => setExportFormat(event.target.value)}><option value="csv">csv</option><option value="json">json</option></select></label><button className="button button-primary" disabled={projectId === 0} onClick={() => void exportReport()}>Create Report Export</button></div>{exports.length === 0 && <div className="state-panel">No exports yet.</div>}{exports.map((item) => <div className="tm-row" key={item.id}><strong>{item.export_key}</strong><span>{item.report_type} {item.export_format}</span><span>{item.row_count} rows</span><span>{item.sha256.slice(0, 12)}</span><a className="button button-secondary" href={reportExportDownloadUrl(item.id)} target="_blank" rel="noreferrer">Download</a></div>)}</div><div className="card"><h3>Saved Reports</h3><form className="admin-form" onSubmit={saveDefinition}><label>Saved report name<input required value={definition.name} onChange={(event) => setDefinition({ ...definition, name: event.target.value })} /></label><label>Saved report type<select value={definition.report_type} onChange={(event) => setDefinition({ ...definition, report_type: event.target.value })}>{reportTypes.map((item) => <option key={item}>{item}</option>)}</select></label><label>Saved report frequency<select value={definition.frequency} onChange={(event) => setDefinition({ ...definition, frequency: event.target.value })}><option>DAILY</option><option>WEEKLY</option><option>MONTHLY</option></select></label><button className="button button-primary" disabled={projectId === 0}>Save Report Definition</button></form>{definitions.map((item) => <div className="tm-row" key={item.id}><strong>{item.name}</strong><span>{item.report_type}</span><span>{item.enabled ? item.frequency : 'DISABLED'}</span><button className="button button-secondary" disabled={!item.enabled} onClick={() => void runDefinition(item.id)}>Run Now</button><button className="button button-secondary" disabled={!item.enabled} onClick={() => void disableDefinition(item.id)}>Disable</button></div>)}</div></div>}
    {!loading && !canExport && <div className="state-panel">Report exports and saved definitions require ADMIN.</div>}
  </div></section>;
}
