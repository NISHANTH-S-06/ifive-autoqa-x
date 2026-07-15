export type LifecycleState = 'DRAFT' | 'IN_REVIEW' | 'APPROVED' | 'REJECTED' | 'ARCHIVED';
export type Priority = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
export type ManualRunStatus = 'PLANNED' | 'IN_PROGRESS' | 'COMPLETED' | 'CANCELLED';
export type ManualResultStatus = 'NOT_RUN' | 'IN_PROGRESS' | 'PASSED' | 'FAILED' | 'BLOCKED' | 'SKIPPED';

export interface PageMeta { limit: number; offset: number; total: number; }
export interface TestProject { id: number; name: string; code: string; description: string | null; status: string; owner_operator_id: number | null; created_by: number; created_at: string; updated_at: string; archived_at: string | null; version: number; }
export interface TestModule { id: number; project_id: number; name: string; code: string; description: string | null; sort_order: number; status: string; }
export interface TestSuite { id: number; project_id: number; module_id: number; name: string; code: string; description: string | null; suite_type: string; status: string; owner_operator_id: number | null; }
export interface TestCaseStep { id?: number; step_number: number; action: string; expected_result: string; test_data?: string | null; }
export interface TestCase {
  id: number; project_id: number; module_id: number; suite_id: number; case_key: string; title: string;
  objective: string | null; preconditions: string | null; test_type: string; priority: Priority; severity: Priority;
  status: string; lifecycle_state: LifecycleState; owner_operator_id: number | null; created_by: number;
  reviewed_by: number | null; approved_by: number | null; created_at: string; updated_at: string;
  reviewed_at: string | null; approved_at: string | null; archived_at: string | null; current_version: number;
  steps: TestCaseStep[]; tags: string[];
}
export interface TestCaseList { items: TestCase[]; page: PageMeta; }
export interface TestProjectList { items: TestProject[]; page: PageMeta; }
export interface TestCaseVersion { id: number; test_case_id: number; version_number: number; snapshot_json: string; change_summary: string | null; created_by: number; created_at: string; source_state: string; }
export interface ManualRun { id: number; run_key: string; project_id: number; suite_id: number; name: string; description: string | null; status: ManualRunStatus; created_by: number; assigned_to: number | null; started_at: string | null; completed_at: string | null; created_at: string; updated_at: string; progress?: string | null; }
export interface ManualRunCase { id: number; run_id: number; test_case_id: number; test_case_version: number; status: ManualResultStatus; assigned_to: number | null; started_at: string | null; completed_at: string | null; actual_result: string | null; notes: string | null; executed_by: number | null; }
export interface ManualEvidence { id: number; run_case_id: number; step_result_id: number | null; evidence_type: string; original_filename: string; mime_type: string; size_bytes: number; sha256: string; uploaded_by: number; created_at: string; }
