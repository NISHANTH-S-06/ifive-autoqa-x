export type TargetLifecycle = 'DRAFT' | 'IN_REVIEW' | 'APPROVED' | 'REJECTED' | 'DISABLED' | 'ARCHIVED';
export type TargetEnvironment = 'LOCAL' | 'DEVELOPMENT' | 'QA' | 'STAGING';
export type CheckMethod = 'HEAD' | 'GET';

export interface Page { limit: number; offset: number; total: number }

export interface ConnectionTarget {
  id: number;
  target_key: string;
  name: string;
  description: string | null;
  environment_type: TargetEnvironment | string;
  base_url: string;
  normalized_scheme: string;
  normalized_host: string;
  normalized_port: number;
  normalized_origin: string;
  allowed_probe_paths: string[];
  tls_required: boolean;
  tls_verify: boolean;
  connection_timeout_seconds: number;
  lifecycle_state: TargetLifecycle;
  enabled: boolean;
  owner_operator_id: number | null;
  created_by: number;
  reviewed_by: number | null;
  approved_by: number | null;
  created_at: string;
  updated_at: string;
  submitted_at: string | null;
  approved_at: string | null;
  rejected_at: string | null;
  disabled_at: string | null;
  archived_at: string | null;
  rejection_reason: string | null;
  last_check_at: string | null;
  last_check_status: string | null;
  execution_enabled: boolean;
  execution_submitted_by: number | null;
  execution_submitted_at: string | null;
  execution_approved_by: number | null;
  execution_approved_at: string | null;
  version: number;
}

export interface ConnectionTargetList { items: ConnectionTarget[]; page: Page }

export interface ConnectionTargetVersion {
  id: number;
  target_id: number;
  version_number: number;
  snapshot_json: string;
  change_summary: string | null;
  created_by: number;
  created_at: string;
  source_state: string;
}

export interface ConnectionCheck {
  id: number;
  check_key: string;
  target_id: number;
  target_version: number;
  probe_path: string;
  method: CheckMethod;
  requested_origin: string;
  resolved_addresses: string[];
  started_at: string;
  completed_at: string | null;
  duration_ms: number | null;
  status: string;
  http_status: number | null;
  final_origin: string | null;
  redirect_count: number;
  tls_protocol: string | null;
  tls_certificate_summary: Record<string, unknown> | null;
  response_headers: Record<string, string>;
  response_size_bytes: number;
  error_category: string | null;
  safe_error_message: string | null;
  initiated_by: number;
  created_at: string;
}

export interface CredentialProfile {
  id: number;
  target_id: number;
  profile_name: string;
  username_hint: string | null;
  secret_source: 'PROMPT_AT_USE' | 'NONE';
  enabled: boolean;
  created_by: number;
  created_at: string;
  updated_at: string;
  last_used_at: string | null;
}
