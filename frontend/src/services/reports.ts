import { apiGet, apiMutation, apiUrl } from './api';
import type { DefectReport, ExecutionReport, QualityReport, ReportDashboard, ReportDefinition, ReportExport, ReportFilters, ReportMetric } from '../types/report';

export function fetchReportMetrics() {
  return apiGet<ReportMetric[]>('/api/reports/summary');
}

const query = (filters: ReportFilters) => {
  const params = new URLSearchParams();
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') params.set(key, String(value));
  });
  return params.toString() ? `?${params.toString()}` : '';
};

export const fetchManagementDashboard = (filters: ReportFilters = {}) => apiGet<ReportDashboard>(`/api/reports/dashboard${query(filters)}`);
export const fetchExecutionReport = (filters: ReportFilters = {}) => apiGet<ExecutionReport>(`/api/reports/executions${query(filters)}`);
export const fetchDefectReport = (filters: ReportFilters = {}) => apiGet<DefectReport>(`/api/reports/defects${query(filters)}`);
export const fetchTrendReport = (filters: ReportFilters = {}) => apiGet<Record<string, unknown>>(`/api/reports/trends${query(filters)}`);
export const fetchQualityReport = (filters: ReportFilters = {}) => apiGet<QualityReport>(`/api/reports/quality${query(filters)}`);
export const fetchTraceabilityReport = (filters: ReportFilters = {}) => apiGet<{ items: Array<Record<string, unknown>> }>(`/api/reports/traceability${query(filters)}`);
export const fetchTargetReport = (filters: ReportFilters = {}) => apiGet<Record<string, unknown>>(`/api/reports/targets${query(filters)}`);
export const fetchWorkerReport = () => apiGet<Record<string, unknown>>('/api/reports/workers');
export const createReportExport = (project_id: number, report_type: string, export_format: string, filters: ReportFilters) => apiMutation<ReportExport>('POST', '/api/reports/export', { project_id, report_type, export_format, filters });
export const fetchReportExports = () => apiGet<{ items: ReportExport[] }>('/api/reports/exports');
export const reportExportDownloadUrl = (id: number) => apiUrl(`/api/reports/exports/${id}/download`);
export const fetchReportDefinitions = () => apiGet<ReportDefinition[]>('/api/report-definitions');
export const createReportDefinition = (value: { project_id: number; name: string; report_type: string; frequency: string; filters: ReportFilters }) => apiMutation<ReportDefinition>('POST', '/api/report-definitions', value);
export const runReportDefinition = (id: number) => apiMutation<ReportExport>('POST', `/api/report-definitions/${id}/run`, {});
export const disableReportDefinition = (id: number) => apiMutation<ReportDefinition>('POST', `/api/report-definitions/${id}/disable`, {});
