import { TestPlan, TestPlanUpdatePayload, TestPlanRejectPayload } from '../types/testPlan';
import { apiGet, apiMutation, apiPost } from './api';

export const TestPlanService = {
  getTestPlans: async (): Promise<TestPlan[]> => {
    return await apiGet<TestPlan[]>('/api/test-plans').catch(() => []);
  },

  getTestPlan: async (planId: number): Promise<TestPlan> => {
    return await apiGet(`/api/test-plans/${planId}`);
  },

  updateTestPlan: async (planId: number, payload: TestPlanUpdatePayload): Promise<TestPlan> => {
    return await apiMutation('PATCH', `/api/test-plans/${planId}`, payload);
  },

  submitTestPlan: async (planId: number): Promise<TestPlan> => {
    return await apiPost(`/api/test-plans/${planId}/submit`, {});
  },

  approveTestPlan: async (planId: number): Promise<TestPlan> => {
    return await apiPost(`/api/test-plans/${planId}/approve`, {});
  },

  rejectTestPlan: async (planId: number, reason: string): Promise<TestPlan> => {
    return await apiPost(`/api/test-plans/${planId}/reject`, { reason } as TestPlanRejectPayload);
  },
};
