/**
 * Phase 13 – Enterprise Cloud Platform frontend API service.
 * All typed API calls for Phase 13 modules.
 */

const BASE = '/api';

async function apiFetch<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    credentials: 'include',
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || res.statusText);
  }
  return res.json();
}

// ─── Module 1: Distributed Execution ────────────────────────────────────────
export const fetchWorkers = () => apiFetch('/execution/workers');
export const fetchWorkerHealth = () => apiFetch('/execution/workers/health');
export const registerWorker = (body: object) => apiFetch('/execution/workers/register', { method: 'POST', body: JSON.stringify(body) });
export const fetchQueue = (projectId?: number) => apiFetch(`/execution/queue${projectId ? `?project_id=${projectId}` : ''}`);
export const submitJob = (body: object) => apiFetch('/execution/queue/submit', { method: 'POST', body: JSON.stringify(body) });
export const fetchQueueAnalytics = () => apiFetch('/execution/analytics');
export const fetchCostReport = () => apiFetch('/execution/cost');
export const fetchScaleRecommendation = () => apiFetch('/execution/scale');
export const retryFailedJobs = () => apiFetch('/execution/queue/retry', { method: 'POST' });

// ─── Module 2: Cloud Browser Farm ────────────────────────────────────────────
export const fetchBrowserPool = () => apiFetch('/browser-farm/pool');
export const provisionBrowserPool = () => apiFetch('/browser-farm/provision', { method: 'POST' });
export const fetchLiveSessions = () => apiFetch('/browser-farm/sessions/live');
export const fetchBrowserFarmHealth = () => apiFetch('/browser-farm/health');
export const fetchFarmMetrics = () => apiFetch('/browser-farm/metrics');
export const reserveSession = (body: object) => apiFetch('/browser-farm/reserve', { method: 'POST', body: JSON.stringify(body) });
export const releaseSession = (sessionId: string) => apiFetch(`/browser-farm/sessions/${sessionId}/release`, { method: 'POST' });
export const autoCleanup = () => apiFetch('/browser-farm/cleanup', { method: 'POST' });

// ─── Module 3: Execution Stream ───────────────────────────────────────────────
export const fetchRecentEvents = (limit = 50) => apiFetch(`/stream/events?limit=${limit}`);
export const fetchExecutionEvents = (jobId: string, eventType?: string) =>
  apiFetch(`/stream/execution/${jobId}${eventType ? `?event_type=${eventType}` : ''}`);
export const emitEvent = (body: object) => apiFetch('/stream/events', { method: 'POST', body: JSON.stringify(body) });

// ─── Module 4: Observability ──────────────────────────────────────────────────
export const fetchObservabilityDashboard = () => apiFetch('/observability/dashboard');
export const fetchMetrics = (params?: Record<string, string | number>) => {
  const qs = params ? '?' + new URLSearchParams(params as Record<string, string>).toString() : '';
  return apiFetch(`/observability/metrics${qs}`);
};
export const fetchTraces = (traceId?: string) => apiFetch(`/observability/traces${traceId ? `?trace_id=${traceId}` : ''}`);
export const fetchFailureMetrics = () => apiFetch('/observability/failures');
export const ingestMetric = (body: object) => apiFetch('/observability/metrics', { method: 'POST', body: JSON.stringify(body) });

// ─── Module 5: Enterprise Analytics ──────────────────────────────────────────
export const fetchQualityTrends = (projectId?: number) => apiFetch(`/analytics/quality-trends${projectId ? `?project_id=${projectId}` : ''}`);
export const fetchReleaseTrends = (projectId?: number) => apiFetch(`/analytics/release-trends${projectId ? `?project_id=${projectId}` : ''}`);
export const fetchDeveloperQuality = (projectId?: number) => apiFetch(`/analytics/developer-quality${projectId ? `?project_id=${projectId}` : ''}`);
export const fetchFailureHeatmap = (projectId?: number) => apiFetch(`/analytics/failure-heatmap${projectId ? `?project_id=${projectId}` : ''}`);
export const fetchFlakyTests = (projectId?: number) => apiFetch(`/analytics/flaky-tests${projectId ? `?project_id=${projectId}` : ''}`);
export const fetchBrowserStats = () => apiFetch('/analytics/browser-stats');
export const fetchCostAnalytics = (projectId?: number) => apiFetch(`/analytics/cost${projectId ? `?project_id=${projectId}` : ''}`);
export const fetchAnalyticsKPIs = () => apiFetch('/analytics/kpis');

// ─── Module 6: Release Governance ─────────────────────────────────────────────
export const fetchGovernanceStages = (releaseVersion?: string) =>
  apiFetch(`/governance/stages${releaseVersion ? `?release_version=${releaseVersion}` : ''}`);
export const createGovernanceWorkflow = (body: object) => apiFetch('/governance/stages', { method: 'POST', body: JSON.stringify(body) });
export const submitApproval = (stageId: number, body: object) => apiFetch(`/governance/stages/${stageId}/approve`, { method: 'POST', body: JSON.stringify(body) });
export const fetchAuditTrail = (releaseVersion?: string) => apiFetch(`/governance/audit-trail${releaseVersion ? `?release_version=${releaseVersion}` : ''}`);
export const createRollback = (body: object) => apiFetch('/governance/rollback', { method: 'POST', body: JSON.stringify(body) });
export const fetchWorkflowStatus = (releaseVersion: string) => apiFetch(`/governance/status/${releaseVersion}`);

// ─── Module 7: Compliance Center ──────────────────────────────────────────────
export const fetchComplianceStandards = () => apiFetch('/compliance/standards');
export const fetchComplianceReports = () => apiFetch('/compliance/reports');
export const generateComplianceReport = (body: object) => apiFetch('/compliance/reports/generate', { method: 'POST', body: JSON.stringify(body) });
export const fetchComplianceDashboard = () => apiFetch('/compliance/dashboard');

// ─── Module 8: API Hub ────────────────────────────────────────────────────────
export const fetchAPIKeys = () => apiFetch('/hub/keys');
export const createAPIKey = (body: object) => apiFetch('/hub/keys', { method: 'POST', body: JSON.stringify(body) });
export const revokeAPIKey = (keyId: number) => apiFetch(`/hub/keys/${keyId}`, { method: 'DELETE' });
export const fetchWebhooks = () => apiFetch('/hub/webhooks');
export const registerWebhook = (body: object) => apiFetch('/hub/webhooks', { method: 'POST', body: JSON.stringify(body) });
export const deleteWebhook = (webhookId: number) => apiFetch(`/hub/webhooks/${webhookId}`, { method: 'DELETE' });
export const fetchSDKInfo = () => apiFetch('/hub/sdks');

// ─── Module 9: Marketplace ────────────────────────────────────────────────────
export const fetchMarketplacePlugins = (category?: string, search?: string) => {
  const params = new URLSearchParams();
  if (category) params.set('category', category);
  if (search) params.set('search', search);
  const qs = params.toString() ? `?${params.toString()}` : '';
  return apiFetch(`/marketplace/plugins${qs}`);
};
export const seedMarketplace = () => apiFetch('/marketplace/seed', { method: 'POST' });
export const installPlugin = (pluginId: number) => apiFetch(`/marketplace/plugins/${pluginId}/install`, { method: 'POST' });
export const uninstallPlugin = (pluginId: number) => apiFetch(`/marketplace/plugins/${pluginId}/uninstall`, { method: 'POST' });
export const fetchMarketplaceCategories = () => apiFetch('/marketplace/categories');

// ─── Module 10: DevOps ────────────────────────────────────────────────────────
export const fetchDevOpsTools = () => apiFetch('/devops/tools');
export const fetchPipelines = (projectId?: number) => apiFetch(`/devops/pipelines${projectId ? `?project_id=${projectId}` : ''}`);
export const createPipeline = (body: object) => apiFetch('/devops/pipelines', { method: 'POST', body: JSON.stringify(body) });
export const triggerPipeline = (pipelineId: number) => apiFetch(`/devops/pipelines/${pipelineId}/trigger`, { method: 'POST' });
export const fetchPipelineStatus = (pipelineId: number) => apiFetch(`/devops/pipelines/${pipelineId}/status`);
export const deletePipeline = (pipelineId: number) => apiFetch(`/devops/pipelines/${pipelineId}`, { method: 'DELETE' });

// ─── Module 11: Multi-Region Cloud ────────────────────────────────────────────
export const fetchCloudRegions = () => apiFetch('/cloud/regions');
export const seedCloudRegions = () => apiFetch('/cloud/regions/seed', { method: 'POST' });
export const fetchCloudHealth = () => apiFetch('/cloud/health');
export const triggerFailover = (body: object) => apiFetch('/cloud/failover', { method: 'POST', body: JSON.stringify(body) });
export const fetchBackupStatus = () => apiFetch('/cloud/backup');

// ─── Module 12: Security Center ───────────────────────────────────────────────
export const fetchVaultSecrets = () => apiFetch('/security-center/vault');
export const addSecret = (body: object) => apiFetch('/security-center/vault', { method: 'POST', body: JSON.stringify(body) });
export const rotateSecret = (entryId: number, body: object) => apiFetch(`/security-center/vault/${entryId}/rotate`, { method: 'POST', body: JSON.stringify(body) });
export const deleteSecret = (entryId: number) => apiFetch(`/security-center/vault/${entryId}`, { method: 'DELETE' });
export const fetchSecurityDashboard = () => apiFetch('/security-center/dashboard');
export const fetchSSOConfig = () => apiFetch('/security-center/sso-config');

// ─── Module 13: AI Optimizer ──────────────────────────────────────────────────
export const fetchOptimizerLogs = (projectId?: number) => apiFetch(`/ai-optimizer/logs${projectId ? `?project_id=${projectId}` : ''}`);
export const triggerOptimization = (projectId?: number) => apiFetch(`/ai-optimizer/optimize${projectId ? `?project_id=${projectId}` : ''}`, { method: 'POST' });
export const fetchOptimizerRecommendations = (projectId?: number) => apiFetch(`/ai-optimizer/recommendations${projectId ? `?project_id=${projectId}` : ''}`);

// ─── Module 14: Executive Command Center ──────────────────────────────────────
export const fetchExecutiveKPIs = () => apiFetch('/executive/kpis');
export const fetchCompanyOverview = () => apiFetch('/executive/companies');
export const fetchPlatformHealth = () => apiFetch('/executive/health');
export const fetchActiveAlerts = () => apiFetch('/executive/alerts');
export const fetchKPIHistory = (limit = 20) => apiFetch(`/executive/history?limit=${limit}`);
