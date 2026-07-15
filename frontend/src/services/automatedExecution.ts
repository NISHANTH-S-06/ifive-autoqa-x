import { apiGet, apiMutation, apiUrl } from './api';
import type { AcceptanceReadiness, AutomatedRun, AutomatedRunCase, AutomatedRunList, AutomatedStepResult, ExecutionArtifact, ExecutionPreflight, ExecutionWorker } from '../types/automatedExecution';

export const fetchAutomatedRuns = (query = '') => apiGet<AutomatedRunList>(`/api/automated-runs${query}`);
export const fetchAcceptanceReadiness = () => apiGet<AcceptanceReadiness>('/api/automated-runs/readiness');
export const createAutomatedRun = (value: unknown) => apiMutation<AutomatedRun>('POST', '/api/automated-runs', value);
export const fetchAutomatedRunPreflight = (id: number) => apiGet<ExecutionPreflight>(`/api/automated-runs/${id}/preflight`);
export const submitAutomatedRun = (id: number) => apiMutation<AutomatedRun>('POST', `/api/automated-runs/${id}/submit`, {});
export const approveAutomatedRun = (id: number) => apiMutation<AutomatedRun>('POST', `/api/automated-runs/${id}/approve`, {});
export const queueAutomatedRun = (id: number) => apiMutation<AutomatedRun>('POST', `/api/automated-runs/${id}/queue`, {});
export const cancelAutomatedRun = (id: number) => apiMutation<AutomatedRun>('POST', `/api/automated-runs/${id}/cancel`, {});
export const retryAutomatedRun = (id: number) => apiMutation<AutomatedRun>('POST', `/api/automated-runs/${id}/retry`, {});
export const fetchAutomatedRunCases = (id: number) => apiGet<AutomatedRunCase[]>(`/api/automated-runs/${id}/cases`);
export const fetchAutomatedSteps = (id: number) => apiGet<AutomatedStepResult[]>(`/api/automated-runs/${id}/steps`);
export const fetchExecutionArtifacts = (id: number) => apiGet<ExecutionArtifact[]>(`/api/automated-runs/${id}/artifacts`);
export const fetchExecutionWorkers = () => apiGet<ExecutionWorker[]>('/api/execution-workers');
export const heartbeatWorker = (worker_key = 'local-stage10-worker') => apiMutation<ExecutionWorker>('POST', '/api/execution-workers/heartbeat', { worker_key });
export const runNextWorkerJob = (worker_key = 'local-stage10-worker') => apiMutation<AutomatedRun | null>('POST', '/api/execution-workers/run-next', { worker_key });
export const executionArtifactDownloadUrl = (id: number) => apiUrl(`/api/execution-artifacts/${id}/download`);
