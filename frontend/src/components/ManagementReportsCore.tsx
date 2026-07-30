import React, { type FormEvent, useEffect, useMemo, useState } from 'react';
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
import { StatCard } from './ui/StatCard';
import { DataTable, Column } from './ui/DataTable';
import { StatusBadge } from './ui/StatusBadge';
import { Button } from './ui/Button';
import { Input } from './ui/Input';
import { Select } from './ui/Select';
import { JSONViewer } from './ui/JSONViewer';
import {
  BarChart3, FileText, Download, RefreshCw,
  Layers, CheckCircle2, AlertTriangle, PlayCircle, ShieldCheck, Filter
} from 'lucide-react';

const reportTypes = ['dashboard', 'executions', 'defects', 'trends', 'quality', 'traceability', 'targets', 'workers'];
const dateRanges = ['today', 'last_7_days', 'last_30_days', 'custom'];

export function ManagementReportsCore() {
  const { operator } = useAuth();
  const [dashboard, setDashboard] = useState<ReportDashboard | null>(null);
  const [executions, setExecutions] = useState<ExecutionReport | null>(null);
  const [defects, setDefects] = useState<DefectReport | null>(null);
  const [quality, setQuality] = useState<QualityReport | null>(null);
  const [exports, setExports] = useState<ReportExport[]>([]);
  const [definitions, setDefinitions] = useState<ReportDefinition[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [projectId, setProjectId] = useState(0);
  const [filters, setFilters] = useState<ReportFilters>({ date_range: 'last_30_days', run_type: 'ALL' });
  const [exportType, setExportType] = useState('dashboard');
  const [exportFormat, setExportFormat] = useState('csv');

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');

  const canExport = operator.role === 'ADMIN';

  const load = async () => {
    setLoading(true); setError('');
    try {
      const [nextDashboard, nextExecutions, nextDefects, nextQuality, nextExports, nextDefinitions] = await Promise.all([
        fetchManagementDashboard(filters),
        fetchExecutionReport(filters),
        fetchDefectReport(filters),
        fetchQualityReport(filters),
        canExport ? fetchReportExports().catch(() => ({ items: [] })) : Promise.resolve({ items: [] }),
        canExport ? fetchReportDefinitions().catch(() => []) : Promise.resolve([]),
      ]);
      setDashboard(nextDashboard?.summary ? nextDashboard : null);
      setExecutions(nextExecutions?.manual && nextExecutions?.automated ? nextExecutions : null);
      setDefects(nextDefects?.by_status ? nextDefects : null);
      setQuality(nextQuality && 'pass_percentage' in nextQuality ? nextQuality : null);
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

  const exportReport = async () => {
    try {
      const created = await createReportExport(projectId, exportType, exportFormat, filters);
      setMessage(`Report export ${created.export_key} generated.`);
      setExports([created, ...exports]);
    } catch (reason) { setError(reason instanceof Error ? reason.message : 'Report export failed.'); }
  };

  const exportColumns: Column<ReportExport>[] = [
    { key: 'export_key', header: 'Export ID', render: (e) => <span style={{ fontWeight: 600, fontFamily: 'var(--font-mono)' }}>{e.export_key}</span> },
    { key: 'report_type', header: 'Report Type', render: (e) => <span style={{ fontWeight: 500 }}>{e.report_type.toUpperCase()}</span> },
    { key: 'export_format', header: 'Format', render: (e) => <span className="badge badge-draft">{e.export_format.toUpperCase()}</span> },
    { key: 'row_count', header: 'Rows', render: (e) => <span>{e.row_count} rows</span> },
    { key: 'sha256', header: 'Cryptographic Hash', render: (e) => <code style={{ fontSize: '0.75rem' }}>{e.sha256.slice(0, 14)}...</code> },
    { key: 'id', header: 'Actions', render: (e) => (
      <a href={reportExportDownloadUrl(e.id)} target="_blank" rel="noreferrer" className="btn btn-secondary btn-sm">
        <Download size={13} /> Download
      </a>
    )}
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      {/* Filters Bar Card */}
      <div className="card" style={{ padding: '1rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.75rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
            <Select
              value={filters.date_range ?? 'last_30_days'}
              onChange={(e) => setFilters({ ...filters, date_range: e.target.value })}
              style={{ width: '160px' }}
            >
              {dateRanges.map((item) => (
                <option key={item} value={item}>{item.replaceAll('_', ' ')}</option>
              ))}
            </Select>

            <Select
              value={filters.run_type ?? 'ALL'}
              onChange={(e) => setFilters({ ...filters, run_type: e.target.value })}
              style={{ width: '140px' }}
            >
              <option value="ALL">All Run Types</option>
              <option value="MANUAL">Manual Only</option>
              <option value="AUTOMATED">Automated Only</option>
            </Select>

            <Button size="sm" variant="primary" onClick={load} isLoading={loading} leftIcon={<Filter size={14} />}>
              Apply Filters
            </Button>
          </div>

          <Button size="sm" variant="secondary" onClick={load} isLoading={loading} leftIcon={<RefreshCw size={14} />}>
            Refresh Reports
          </Button>
        </div>
      </div>

      {error && <div className="state-panel state-error" role="alert">{error}</div>}
      {message && <div className="state-panel" role="status">{message}</div>}

      {/* KPI Cards Summary */}
      {dashboard && (
        <div className="grid grid-cols-4">
          <StatCard title="Test Projects" value={dashboard.summary.test_projects} subtitle="Configured projects" icon={Layers} variant="primary" loading={loading} />
          <StatCard title="Test Cases" value={dashboard.summary.test_cases} subtitle="Approved case definitions" icon={FileText} variant="info" loading={loading} />
          <StatCard title="Automated Runs" value={dashboard.summary.automated_runs} subtitle="Executed runs" icon={PlayCircle} variant="success" loading={loading} />
          <StatCard title="Defects Count" value={dashboard.summary.defects} subtitle="Open & closed defects" icon={AlertTriangle} variant="danger" loading={loading} />
        </div>
      )}

      {/* Quality Summary & Report Generator */}
      {canExport && (
        <div className="card" style={{ padding: '1.25rem' }}>
          <h4 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '1rem' }}>
            Report Export & Quality Engine
          </h4>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.25rem', flexWrap: 'wrap' }}>
            <Select value={projectId} onChange={(e) => setProjectId(Number(e.target.value))} style={{ width: '220px' }}>
              {projects.map((p) => (
                <option key={p.id} value={p.id}>{p.name}</option>
              ))}
            </Select>

            <Select value={exportType} onChange={(e) => setExportType(e.target.value)} style={{ width: '160px' }}>
              {reportTypes.map((t) => (
                <option key={t} value={t}>{t.toUpperCase()}</option>
              ))}
            </Select>

            <Select value={exportFormat} onChange={(e) => setExportFormat(e.target.value)} style={{ width: '120px' }}>
              <option value="csv">CSV</option>
              <option value="json">JSON</option>
            </Select>

            <Button size="sm" variant="primary" onClick={exportReport} disabled={projectId === 0} leftIcon={<Download size={14} />}>
              Generate Export File
            </Button>
          </div>

          <DataTable
            columns={exportColumns}
            data={exports}
            keyExtractor={(e) => e.id}
            loading={loading}
            emptyMessage="No report export files generated yet."
          />
        </div>
      )}
    </div>
  );
}
