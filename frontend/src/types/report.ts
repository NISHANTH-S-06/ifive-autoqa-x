export interface ReportMetric {
  label: string;
  value: string;
}

export interface EvidenceLink {
  type: 'screenshot' | 'trace' | 'video' | 'console' | 'network';
  label: string;
  path: string;
}

export interface ReportFilters {
  project_id?: number;
  module_id?: number;
  suite_id?: number;
  test_case_id?: number;
  run_type?: string;
  run_status?: string;
  defect_status?: string;
  severity?: string;
  priority?: string;
  assignee_id?: number;
  target_id?: number;
  environment?: string;
  date_range?: string;
  start_date?: string;
  end_date?: string;
}

export interface ReportDashboard {
  filters: Record<string, unknown>;
  summary: {
    test_projects: number;
    test_cases: number;
    approved_test_cases: number;
    manual_runs: number;
    automated_runs: number;
    result_counts: Record<string, number>;
    defects: number;
    open_defects: number;
    closed_defects: number;
    duplicate_defects: number;
    retest_results: Record<string, number>;
    target_health: Record<string, number>;
    worker_status: Record<string, number>;
  };
  recent_activity: Array<{ type: string; id: number; label: string; status: string; created_at: string }>;
}

export interface ExecutionReport {
  manual: { run_count: number; case_statuses: Record<string, number> };
  automated: { run_count: number; case_statuses: Record<string, number>; failure_categories: Record<string, number> };
  project_results: Array<Record<string, unknown>>;
  operator_execution: Array<Record<string, unknown>>;
  environment_results: Array<Record<string, unknown>>;
}

export interface DefectReport {
  by_status: Record<string, number>;
  by_severity: Record<string, number>;
  by_priority: Record<string, number>;
  by_project: Array<Record<string, unknown>>;
  ageing: Record<string, number>;
  reopened: number;
  duplicates: number;
  retest_results: Record<string, number>;
  average_time_to_close_hours: number;
  traceability: Array<Record<string, unknown>>;
}

export interface QualityReport {
  pass_percentage: number;
  failure_percentage: number;
  blocked_percentage: number;
  skipped_percentage: number;
  test_coverage_count: number;
  approved_test_case_percentage: number;
  automation_coverage: number;
  defect_density: number;
  defect_reopen_rate: number;
  retest_success_rate: number;
}

export interface ReportExport {
  id: number;
  project_id: number;
  export_key: string;
  report_type: string;
  export_format: string;
  original_filename: string;
  mime_type: string;
  size_bytes: number;
  sha256: string;
  row_count: number;
  created_by: number;
  created_at: string;
  expires_at: string | null;
}

export interface ReportDefinition {
  id: number;
  project_id: number;
  name: string;
  report_type: string;
  filters: ReportFilters;
  frequency: string;
  enabled: boolean;
  owner_operator_id: number;
  last_run_at: string | null;
  next_run_at: string | null;
  last_error: string | null;
}
