import { apiGet, apiMutation } from './api';
import type {
  CompanyTask,
  CompanyTaskCreate,
  CompanyTaskListItem,
  CompanyTaskUpdate,
  TaskStatusTransition,
  AutoQARunStatusRead,
  AutoQAPreviewStep,
} from '../types/companyTask';

export const listTasks = (params?: {
  status?: string;
  priority?: string;
  project_id?: number;
  assigned_to_me?: boolean;
}) => {
  const query = new URLSearchParams();
  if (params?.status) query.set('status', params.status);
  if (params?.priority) query.set('priority', params.priority);
  if (params?.project_id) query.set('project_id', String(params.project_id));
  if (params?.assigned_to_me) query.set('assigned_to_me', 'true');
  const qs = query.toString();
  return apiGet<CompanyTaskListItem[]>(`/api/company-tasks${qs ? '?' + qs : ''}`);
};

export const getMyTasks = () =>
  apiGet<CompanyTaskListItem[]>('/api/company-tasks/my-tasks');

export const getPendingApproval = () =>
  apiGet<CompanyTaskListItem[]>('/api/company-tasks/pending-approval');

export const getTask = (id: number) =>
  apiGet<CompanyTask>(`/api/company-tasks/${id}`);

export const createTask = (payload: CompanyTaskCreate) =>
  apiMutation<CompanyTask>('POST', '/api/company-tasks', payload);

export const updateTask = (id: number, payload: CompanyTaskUpdate) =>
  apiMutation<CompanyTask>('PATCH', `/api/company-tasks/${id}`, payload);

export const assignDeveloper = (id: number, developer_id: number) =>
  apiMutation<CompanyTask>('POST', `/api/company-tasks/${id}/assign`, { developer_id });

export const transitionStatus = (id: number, payload: TaskStatusTransition) =>
  apiMutation<CompanyTask>('POST', `/api/company-tasks/${id}/status`, payload);

export const previewAutoQAPlan = (id: number) =>
  apiMutation<AutoQAPreviewStep[]>('POST', `/api/company-tasks/${id}/preview-autoqa`, {});

export const approveAndRunAutoQA = (id: number, steps?: AutoQAPreviewStep[]) =>
  apiMutation<CompanyTask>('POST', `/api/company-tasks/${id}/approve-autoqa`, { steps });

export const getTaskRunStatus = (id: number) =>
  apiGet<AutoQARunStatusRead>(`/api/company-tasks/${id}/run-status`);

export const assignTester = (id: number, tester_id: number) =>
  apiMutation<CompanyTask>('POST', `/api/company-tasks/${id}/assign-tester`, { tester_id });

export const markDeliveryComplete = (id: number) =>
  apiMutation<CompanyTask>('POST', `/api/company-tasks/${id}/delivery-complete`, {});

export const deleteTask = (id: number) =>
  apiMutation<void>('DELETE', `/api/company-tasks/${id}`, undefined);
