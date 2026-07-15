import type { PageMeta } from './testManagement';

export type DefectStatus = 'NEW' | 'TRIAGED' | 'ASSIGNED' | 'IN_PROGRESS' | 'FIXED' | 'READY_FOR_RETEST' | 'RETEST_PASSED' | 'REOPENED' | 'CLOSED' | 'REJECTED' | 'DUPLICATE';
export type DefectLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
export type DefectSourceType = 'MANUAL_RUN_CASE' | 'MANUAL_STEP' | 'AUTOMATED_RUN' | 'AUTOMATED_RUN_CASE' | 'AUTOMATED_STEP';

export interface Defect {
  id: number;
  defect_key: string;
  title: string;
  description: string | null;
  project_id: number;
  module_id: number | null;
  suite_id: number | null;
  test_case_id: number | null;
  test_case_version: number | null;
  manual_run_id: number | null;
  manual_run_case_id: number | null;
  manual_step_result_id: number | null;
  automated_run_id: number | null;
  automated_run_case_id: number | null;
  automated_step_result_id: number | null;
  severity: DefectLevel;
  priority: DefectLevel;
  status: DefectStatus;
  assigned_to: number | null;
  reporter_id: number;
  environment: string | null;
  target_id: number | null;
  target_version: number | null;
  failure_category: string | null;
  expected_result: string | null;
  actual_result: string | null;
  reproduction_steps: string | null;
  resolution: string | null;
  duplicate_of_defect_id: number | null;
  created_by: number;
  created_at: string;
  updated_at: string;
  closed_at: string | null;
  archived_at: string | null;
}

export interface DefectList { items: Defect[]; page: PageMeta; }
export interface DefectComment { id: number; defect_id: number; body: string; created_by: number; created_at: string; }
export interface DefectHistory { id: number; defect_id: number; event_type: string; old_value: string | null; new_value: string | null; safe_message: string | null; created_by: number; created_at: string; }
export interface DefectEvidenceLink { id: number; defect_id: number; manual_evidence_id: number | null; execution_artifact_id: number | null; link_type: string; created_by: number; created_at: string; }
export interface DefectRetest { id: number; defect_id: number; manual_run_id: number | null; automated_run_id: number | null; test_case_id: number | null; test_case_version: number | null; target_id: number | null; target_version: number | null; result_status: string; safe_notes: string | null; created_by: number; created_at: string; }
export interface DefectConfirmation { requires_confirmation: true; possible_existing: Defect[]; }
export interface DefectTraceability {
  defect: { id: number; defect_key: string; status: string };
  project: Record<string, unknown> | null;
  module: Record<string, unknown> | null;
  suite: Record<string, unknown> | null;
  test_case: Record<string, unknown> | null;
  test_case_version: number | null;
  manual_run_id: number | null;
  automated_run_id: number | null;
  evidence_links: Array<{ manual_evidence_id: number | null; execution_artifact_id: number | null }>;
  retests: Array<{ manual_run_id: number | null; result_status: string; test_case_version: number | null }>;
}
