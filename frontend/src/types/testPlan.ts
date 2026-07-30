export interface TestStep {
  id?: number;
  scenario_id?: number;
  step_order: number;
  action: string;
  locator_json?: string | null;
  input_value_reference?: string | null;
  expected_value?: string | null;
  timeout_ms?: number;
  continue_on_failure?: boolean;
  metadata_json?: string | null;
}

export interface TestScenario {
  id?: number;
  test_plan_version_id?: number;
  scenario_type: 'PRIMARY' | 'NEGATIVE' | 'REGRESSION' | 'BOUNDARY';
  title: string;
  description?: string | null;
  priority: string;
  risk: string;
  enabled: boolean;
  mandatory: boolean;
  order_index: number;
  steps: TestStep[];
}

export interface TestPlanVersion {
  id: number;
  test_plan_id: number;
  version_number: number;
  source_revision: number;
  provider?: string | null;
  model?: string | null;
  prompt_version?: string | null;
  schema_version?: string | null;
  plan_hash: string;
  created_by: number;
  created_at: string;
  scenarios: TestScenario[];
}

export interface TestPlan {
  id: number;
  project_id: number;
  external_task_import_id: number;
  plan_code: string;
  current_version: number;
  source_task_id: string;
  source_revision: number;
  title: string;
  status: 'DRAFT' | 'IN_REVIEW' | 'APPROVED' | 'REJECTED';
  execution_enabled: boolean;
  optional_regression_enabled: boolean;
  
  created_by: number;
  submitted_by?: number | null;
  approved_by?: number | null;
  rejected_by?: number | null;
  
  created_at: string;
  updated_at: string;
  submitted_at?: string | null;
  approved_at?: string | null;
  rejected_at?: string | null;
  rejection_reason?: string | null;
  
  versions: TestPlanVersion[];
}

export interface TestPlanUpdatePayload {
  title?: string;
  optional_regression_enabled?: boolean;
  scenarios?: TestScenario[];
}

export interface TestPlanRejectPayload {
  reason: string;
}
