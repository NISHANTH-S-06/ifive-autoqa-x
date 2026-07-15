export type TestRunStatus = 'QUEUED' | 'APPROVED' | 'RUNNING' | 'PASSED' | 'FAILED' | 'CANCELLED';

export interface TestResult {
  id: number; test_name: string; test_file: string; status: 'PASSED' | 'FAILED' | 'SKIPPED' | 'TIMED_OUT';
  duration_seconds: number; error_message: string | null;
}

export interface Evidence {
  id: number; evidence_type: 'HTML_REPORT' | 'JSON_RESULT' | 'SCREENSHOT' | 'TRACE' | 'VIDEO' | 'STDOUT' | 'STDERR';
  relative_path: string; file_size_bytes: number;
}

export interface TestRun {
  id: number;
  run_code: string;
  project_id: number;
  created_by_operator_id: number | null;
  approved_by_operator_id: number | null;
  executed_by_operator_id: number | null;
  cancelled_by_operator_id: number | null;
  suite_name: string;
  browser: string;
  environment: string;
  status: TestRunStatus;
  total_tests: number;
  passed_tests: number;
  failed_tests: number;
  skipped_tests: number;
  duration_seconds: number;
  approved_at: string | null;
  started_at: string | null;
  completed_at: string | null;
  exit_code: number | null;
  error_summary: string | null;
  result_json_path: string | null;
  html_report_path: string | null;
  stdout_log_path: string | null;
  stderr_log_path: string | null;
  created_at: string;
  results?: TestResult[];
  evidence?: Evidence[];
}

export interface TestRunRequest {
  project_id: number;
  suite_name: string;
  browser: 'chromium';
  environment: 'local' | 'qa' | 'staging';
}

export interface DashboardSummary {
  total_projects: number;
  active_projects: number;
  total_runs: number;
  passed_runs: number;
  failed_runs: number;
  queued_runs: number;
  running_runs: number;
  pass_rate: number;
  total_tests: number;
  average_duration_seconds: number;
  recent_runs: TestRun[];
}
