// ── Auth Types ──
export interface User {
  id: number;
  username: string;
  display_name: string;
  role: string;
  is_active: boolean;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

// ── Task Types ──
export interface Task {
  id: number;
  task_code: string;
  project_name: string;
  module_name: string;
  title: string;
  description?: string;
  assigned_developer?: string;
  assigned_tester?: string;
  task_given_by?: string;
  target_date?: string;
  priority: string;
  application_url?: string;
  page_path?: string;
  environment: string;
  expected_result?: string;
  acceptance_criteria?: string;
  test_data?: string;
  developer_notes?: string;
  rework_remarks?: string;
  revision: number;
  status: string;
  created_at: string;
  updated_at: string;
  testing_l2_at?: string;
  completed_at?: string;
}

export interface TaskCreate {
  task_code: string;
  project_name: string;
  module_name: string;
  title: string;
  description?: string;
  assigned_developer?: string;
  assigned_tester?: string;
  task_given_by?: string;
  target_date?: string;
  priority?: string;
  application_url?: string;
  page_path?: string;
  environment?: string;
  expected_result?: string;
  acceptance_criteria?: string;
  test_data?: string;
}

export interface TaskUpdate {
  project_name?: string;
  module_name?: string;
  title?: string;
  description?: string;
  assigned_developer?: string;
  assigned_tester?: string;
  task_given_by?: string;
  target_date?: string;
  priority?: string;
  application_url?: string;
  page_path?: string;
  environment?: string;
  expected_result?: string;
  acceptance_criteria?: string;
  test_data?: string;
}

export interface HistoryRecord {
  id: number;
  task_id: number;
  previous_status: string | null;
  new_status: string;
  changed_by: string;
  reason: string | null;
  timestamp: string;
}

export interface DashboardSummary {
  counts: Record<string, number>;
  total: number;
}

export type QAResult = 'PASS' | 'FAIL' | 'BLOCKED';
