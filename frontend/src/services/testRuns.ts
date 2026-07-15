import { apiGet, apiPost, apiUrl } from './api';
import type { DashboardSummary, TestRun, TestRunRequest } from '../types/testRun';
import type { Project } from '../types/product';

export const fetchProjects = () => apiGet<Project[]>('/api/projects');
export const fetchRecentTestRuns = () => apiGet<TestRun[]>('/api/test-runs?limit=10');
export const fetchDashboardSummary = () => apiGet<DashboardSummary>('/api/dashboard/summary');
export const createTestRun = (request: TestRunRequest) => apiPost<TestRun>('/api/test-runs', request);
export const fetchTestRun = (runId: number) => apiGet<TestRun>(`/api/test-runs/${runId}`);
export const approveTestRun = (runId: number, confirmation: string) => apiPost<TestRun>(`/api/test-runs/${runId}/approve`, { confirmation });
export const executeTestRun = (runId: number) => apiPost<{ run_id: number; status: string }>(`/api/test-runs/${runId}/execute`, { confirm_local_execution: true });
export const cancelTestRun = (runId: number) => apiPost<TestRun>(`/api/test-runs/${runId}/cancel`, {});
export const evidenceUrl = (runId: number, evidenceId: number) => apiUrl(`/api/test-runs/${runId}/evidence/${evidenceId}`);
