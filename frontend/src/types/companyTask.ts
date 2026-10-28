export type TaskStatus =
  | 'NEW'
  | 'ASSIGNED'
  | 'IN_PROGRESS'
  | 'DEVELOPER_COMPLETED'
  | 'TESTING_L2'
  | 'TEST_APPROVED'
  | 'AUTOQA_RUNNING'
  | 'PASSED'
  | 'FAILED'
  | 'BACK_TO_DEVELOPER'
  | 'DELIVERY_COMPLETED'
  | 'CLOSED';

export type TaskPriority = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
export type TaskSeverity = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
export type TaskBrowser = 'CHROMIUM' | 'FIREFOX' | 'WEBKIT';

export interface TaskOperatorSummary {
  id: number;
  username: string;
  display_name: string;
  role: string;
}

export interface CompanyTask {
  id: number;
  project_id: number | null;
  title: string;
  module: string | null;
  feature: string | null;
  description: string | null;
  
  target_url: string | null;
  expected_flow: string | null;
  acceptance_criteria: string | null;
  expected_result: string | null;
  api_endpoint: string | null;
  
  browser: TaskBrowser;
  environment: string;
  reference_screenshot_url: string | null;
  
  priority: TaskPriority;
  severity: TaskSeverity;
  estimated_hours: number | null;
  target_date: string | null;
  
  status: TaskStatus;
  retest_count: number;
  
  assigned_developer_id: number | null;
  assigned_developer: TaskOperatorSummary | null;
  assigned_tester_id: number | null;
  assigned_tester: TaskOperatorSummary | null;
  created_by: number;
  creator: TaskOperatorSummary | null;
  approved_by_tester_id: number | null;
  approver: TaskOperatorSummary | null;
  
  autoqa_run_id: number | null;
  autoqa_result: 'PASS' | 'FAIL' | null;
  autoqa_notes: string | null;
  
  created_at: string;
  updated_at: string;
  assigned_at: string | null;
  in_progress_at: string | null;
  developer_completed_at: string | null;
  testing_l2_at: string | null;
  test_approved_at: string | null;
  autoqa_started_at: string | null;
  autoqa_completed_at: string | null;
  back_to_developer_at: string | null;
  delivery_completed_at: string | null;
  closed_at: string | null;
}

export interface CompanyTaskListItem {
  id: number;
  project_id: number | null;
  title: string;
  module: string | null;
  feature: string | null;
  target_url?: string | null;
  priority: TaskPriority;
  severity: TaskSeverity;
  status: TaskStatus;
  browser: TaskBrowser;
  environment: string;
  retest_count: number;
  assigned_developer: TaskOperatorSummary | null;
  assigned_tester: TaskOperatorSummary | null;
  creator: TaskOperatorSummary | null;
  target_date: string | null;
  created_at: string;
  updated_at: string;
  autoqa_result: 'PASS' | 'FAIL' | null;
  autoqa_run_id: number | null;
}

export interface CompanyTaskCreate {
  title: string;
  module?: string;
  feature?: string;
  description?: string;
  target_url?: string;
  expected_flow?: string;
  acceptance_criteria?: string;
  expected_result?: string;
  api_endpoint?: string;
  browser?: TaskBrowser;
  environment?: string;
  reference_screenshot_url?: string;
  priority?: TaskPriority;
  severity?: TaskSeverity;
  estimated_hours?: number;
  target_date?: string;
  project_id?: number;
  assigned_developer_id?: number;
  assigned_tester_id?: number;
}

export interface CompanyTaskUpdate extends Partial<CompanyTaskCreate> {}

export interface TaskStatusTransition {
  status: TaskStatus;
  notes?: string;
}

export interface AutoQARunStatusRead {
  task_id: number;
  task_status: TaskStatus;
  autoqa_run_id: number | null;
  run_status: string | null;
  progress: string | null;
  completed_steps: number;
  failed_steps: number;
  total_steps: number;
  autoqa_result: 'PASS' | 'FAIL' | null;
  autoqa_notes: string | null;
  artifact_count: number;
}

export interface AutoQAPreviewStep {
  step_number: number;
  action_type: string;
  target: string;
  risk_level: string;
  expected_result: string;
}

export const TASK_STATUS_LABELS: Record<TaskStatus, string> = {
  NEW: 'New',
  ASSIGNED: 'Assigned',
  IN_PROGRESS: 'In Progress',
  DEVELOPER_COMPLETED: 'Dev Completed',
  TESTING_L2: 'Testing L2',
  TEST_APPROVED: 'Test Approved',
  AUTOQA_RUNNING: 'AutoQA Running',
  PASSED: 'Passed',
  FAILED: 'Failed',
  BACK_TO_DEVELOPER: 'Back to Dev',
  DELIVERY_COMPLETED: 'Delivered',
  CLOSED: 'Closed',
};

export const TASK_STATUS_COLORS: Record<TaskStatus, string> = {
  NEW: '#94a3b8',           // slate-400
  ASSIGNED: '#64748b',      // slate-500
  IN_PROGRESS: '#3b82f6',   // blue-500
  DEVELOPER_COMPLETED: '#0ea5e9', // sky-500
  TESTING_L2: '#f59e0b',    // amber-500
  TEST_APPROVED: '#8b5cf6', // violet-500
  AUTOQA_RUNNING: '#06b6d4',// cyan-500
  PASSED: '#10b981',        // emerald-500
  FAILED: '#ef4444',        // red-500
  BACK_TO_DEVELOPER: '#f43f5e', // rose-500
  DELIVERY_COMPLETED: '#059669',// emerald-600
  CLOSED: '#475569',        // slate-600
};

export const TASK_PRIORITY_COLORS: Record<TaskPriority, string> = {
  LOW: '#22c55e',
  MEDIUM: '#f59e0b',
  HIGH: '#f97316',
  CRITICAL: '#ef4444',
};

export const TASK_SEVERITY_COLORS: Record<TaskSeverity, string> = {
  LOW: '#22c55e',
  MEDIUM: '#eab308', // yellow-500
  HIGH: '#f97316',   // orange-500
  CRITICAL: '#dc2626',// red-600
};

/** Pipeline order for visual display */
export const TASK_STATUS_PIPELINE: TaskStatus[] = [
  'NEW', 'ASSIGNED', 'IN_PROGRESS', 'DEVELOPER_COMPLETED', 'TESTING_L2', 'TEST_APPROVED', 'AUTOQA_RUNNING', 'PASSED', 'DELIVERY_COMPLETED'
];
