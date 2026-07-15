import type { PageMeta } from './testManagement';

export interface AutomatedRun {
  id: number;
  run_key: string;
  name: string;
  description: string | null;
  target_id: number;
  target_version: number;
  target_origin: string;
  status: string;
  risk_level: string;
  preflight_status: string;
  dns_pinning_status: string;
  runtime_secret_status: string;
  created_by: number;
  submitted_by: number | null;
  approved_by: number | null;
  queued_by: number | null;
  cancelled_by: number | null;
  worker_key: string | null;
  timeout_seconds: number;
  max_retries: number;
  attempt_count: number;
  total_steps: number;
  completed_steps: number;
  failed_steps: number;
  failure_classification: string | null;
  safe_error_message: string | null;
  created_at: string;
  updated_at: string;
  progress: string | null;
}

export interface AutomatedRunList { items: AutomatedRun[]; page: PageMeta; }

export interface AcceptanceReadiness {
  active_admin_count: number;
  admin_prerequisite_met: boolean;
  real_target_authorized: boolean;
  real_target_status: string;
  dns_pinning_status: string;
  runtime_secret_status: string;
  allowed_risk_levels: string[];
  blocked_risk_levels: string[];
}

export interface ExecutionPreflight {
  run_id: number;
  status: string;
  checks: Record<string, boolean>;
  risk_level: string;
  dns_pinning_status: string;
  runtime_secret_status: string;
  safe_message: string | null;
}

export interface AutomatedRunCase {
  id: number;
  run_id: number;
  test_case_id: number;
  test_case_version: number;
  status: string;
  failure_classification: string | null;
  safe_error_message: string | null;
}

export interface AutomatedStepResult {
  id: number;
  run_case_id: number;
  step_number: number;
  action_type: string;
  selector: string | null;
  value_redacted: string | null;
  expected_redacted: string | null;
  status: string;
  failure_classification: string | null;
  safe_error_message: string | null;
  duration_ms: number | null;
}

export interface ExecutionArtifact {
  id: number;
  run_id: number;
  run_case_id: number | null;
  step_result_id: number | null;
  artifact_type: string;
  original_filename: string;
  mime_type: string;
  size_bytes: number;
  sha256: string;
  safe: boolean;
  created_at: string;
}

export interface ExecutionWorker {
  id: number;
  worker_key: string;
  status: string;
  max_concurrency: number;
  current_run_id: number | null;
  heartbeat_at: string;
}
