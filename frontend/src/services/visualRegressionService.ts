import { apiGet, apiPost, apiUrl, getCsrfToken } from './api';
import {
  ComparePayload,
  CreateBaselinePayload,
  VisualBaseline,
  VisualBaselineHistory,
  VisualComparisonRun,
  VisualHistoryFilter,
} from '../types/visualRegression';

export async function fetchBaselines(projectId?: number, module?: string, browser?: string): Promise<VisualBaseline[]> {
  const params = new URLSearchParams();
  if (projectId) params.append('project_id', projectId.toString());
  if (module) params.append('module', module);
  if (browser) params.append('browser', browser);
  const query = params.toString() ? `?${params.toString()}` : '';
  return apiGet<VisualBaseline[]>(`/api/visual/baselines${query}`);
}

export async function fetchBaselineHistory(baselineId: number): Promise<VisualBaselineHistory[]> {
  return apiGet<VisualBaselineHistory[]>(`/api/visual/baselines/${baselineId}/history`);
}

export async function createBaselineJson(payload: CreateBaselinePayload): Promise<VisualBaseline> {
  return apiPost<VisualBaseline>('/api/visual/baseline/json', payload);
}

export async function compareImagesJson(payload: ComparePayload): Promise<VisualComparisonRun> {
  return apiPost<VisualComparisonRun>('/api/visual/compare/json', payload);
}

export async function createBaselineFormData(formData: FormData): Promise<VisualBaseline> {
  const response = await fetch(apiUrl('/api/visual/baseline'), {
    method: 'POST',
    credentials: 'include',
    headers: {
      'X-CSRF-Token': getCsrfToken(),
    },
    body: formData,
  });
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(body?.detail || 'Failed to create baseline.');
  }
  return response.json();
}

export async function compareImagesFormData(formData: FormData): Promise<VisualComparisonRun> {
  const response = await fetch(apiUrl('/api/visual/compare'), {
    method: 'POST',
    credentials: 'include',
    headers: {
      'X-CSRF-Token': getCsrfToken(),
    },
    body: formData,
  });
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(body?.detail || 'Failed to compare images.');
  }
  return response.json();
}

export async function fetchVisualResults(runId: number): Promise<VisualComparisonRun[]> {
  return apiGet<VisualComparisonRun[]>(`/api/visual/results/${runId}`);
}

export async function fetchVisualHistory(filter?: VisualHistoryFilter): Promise<{ total: number; comparisons: VisualComparisonRun[] }> {
  const params = new URLSearchParams();
  if (filter?.project_id) params.append('project_id', filter.project_id.toString());
  if (filter?.module) params.append('module', filter.module);
  if (filter?.browser) params.append('browser', filter.browser);
  if (filter?.severity) params.append('severity', filter.severity);
  if (filter?.ai_classification) params.append('ai_classification', filter.ai_classification);
  if (filter?.status) params.append('status', filter.status);
  if (filter?.limit) params.append('limit', filter.limit.toString());
  if (filter?.offset) params.append('offset', filter.offset.toString());
  const query = params.toString() ? `?${params.toString()}` : '';
  return apiGet<{ total: number; comparisons: VisualComparisonRun[] }>(`/api/visual/history${query}`);
}

export function getArtifactImageUrl(comparisonId: number, artifactType: string): string {
  return apiUrl(`/api/visual/artifacts/${comparison_id_placeholder(comparisonId)}/${artifactType}`);
}

function comparison_id_placeholder(id: number): number {
  return id;
}
