/**
 * Phase 14 – Enterprise Autonomous AI QA Operating System (AI QA OS) frontend service.
 * All typed API calls for Phase 14 modules.
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

// ─── Module 1: Enterprise Command Brain ─────────────────────────────────────
export const orchestrateGoal = (body: object) => apiFetch('/enterprise-brain/orchestrate', { method: 'POST', body: JSON.stringify(body) });
export const fetchBrainRuns = (limit = 20) => apiFetch(`/enterprise-brain/runs?limit=${limit}`);
export const fetchBrainRunStatus = (runId: string) => apiFetch(`/enterprise-brain/runs/${runId}`);

// ─── Module 2: Autonomous Workflow Composer ────────────────────────────────
export const seedWorkflowTemplates = () => apiFetch('/workflows/templates/seed', { method: 'POST' });
export const fetchWorkflowTemplates = () => apiFetch('/workflows/templates');
export const createWorkflowTemplate = (body: object) => apiFetch('/workflows/templates', { method: 'POST', body: JSON.stringify(body) });
export const executeWorkflow = (body: object) => apiFetch('/workflows/execute', { method: 'POST', body: JSON.stringify(body) });
export const fetchWorkflowExecutions = () => apiFetch('/workflows/executions');

// ─── Module 3: AI Agents Marketplace ────────────────────────────────────────
export const seedAIAgents = () => apiFetch('/marketplace/plugins/seed', { method: 'POST' }).catch(() => apiFetch('/marketplace/plugins'));
export const fetchAgentPackages = (category?: string) => apiFetch(`/marketplace/plugins${category ? `?category=${category}` : ''}`);
export const installAgentPackage = (id: number) => apiFetch(`/marketplace/plugins/${id}/install`, { method: 'POST' });

// ─── Module 4: Business Process Understanding ───────────────────────────────
export const seedBusinessProcesses = () => apiFetch('/business-process/seed', { method: 'POST' });
export const fetchBusinessProcesses = (domainType?: string) => apiFetch(`/business-process/processes${domainType ? `?domain_type=${domainType}` : ''}`);
export const createBusinessProcess = (body: object) => apiFetch('/business-process/processes', { method: 'POST', body: JSON.stringify(body) });

// ─── Module 5 & 10: Release Simulation & Optimization V2 ─────────────────────
export const runReleaseSimulation = (releaseVersion: string) => apiFetch('/optimization-v2/simulation/run', { method: 'POST', body: JSON.stringify({ release_version: releaseVersion }) });
export const fetchSimulationHistory = () => apiFetch('/optimization-v2/simulation/history');
export const tuneOptimizationV2 = () => apiFetch('/optimization-v2/tune', { method: 'POST' });
export const fetchOptimizationV2History = () => apiFetch('/optimization-v2/history');

// ─── Module 7: Autonomous Incident Commander ───────────────────────────────
export const triggerIncident = (body: object) => apiFetch('/incidents/trigger', { method: 'POST', body: JSON.stringify(body) });
export const fetchIncidents = (status?: string) => apiFetch(`/incidents${status ? `?status=${status}` : ''}`);
export const fetchIncidentDetails = (id: number) => apiFetch(`/incidents/${id}`);
export const resolveIncident = (id: number, summary: string) => apiFetch(`/incidents/${id}/resolve`, { method: 'POST', body: JSON.stringify({ summary }) });

// ─── Module 8: Knowledge Universe ───────────────────────────────────────────
export const seedKnowledgeUniverse = () => apiFetch('/knowledge-universe/seed', { method: 'POST' });
export const fetchKnowledgeUniverseGraph = (nodeType?: string) => apiFetch(`/knowledge-universe/graph${nodeType ? `?node_type=${nodeType}` : ''}`);
export const addKnowledgeUniverseNode = (body: object) => apiFetch('/knowledge-universe/nodes', { method: 'POST', body: JSON.stringify(body) });

// ─── Module 9: AI Executive Advisor ────────────────────────────────────────
export const askExecutiveAdvisor = (query: string) => apiFetch('/executive-advisor/ask', { method: 'POST', body: JSON.stringify({ query }) });
export const fetchExecutiveInsights = () => apiFetch('/executive-advisor/history');

// ─── Module 11: Governance Center ───────────────────────────────────────────
export const seedGovernancePolicies = () => apiFetch('/governance-v2/policies/seed', { method: 'POST' });
export const fetchGovernancePolicies = () => apiFetch('/governance-v2/policies');
export const createGovernancePolicy = (body: object) => apiFetch('/governance-v2/policies', { method: 'POST', body: JSON.stringify(body) });
export const toggleGovernancePolicy = (id: number) => apiFetch(`/governance-v2/policies/${id}/toggle`, { method: 'POST' });

// ─── Module 12: Forecast Center ────────────────────────────────────────────
export const generateForecasts = (horizonDays = 30) => apiFetch(`/forecast/generate?horizon_days=${horizonDays}`, { method: 'POST' });
export const fetchForecastMetrics = () => apiFetch('/forecast/metrics');

// ─── Module 13: Report Factory V2 ───────────────────────────────────────────
export const generateReportV2 = (body: object) => apiFetch('/report-factory/generate', { method: 'POST', body: JSON.stringify(body) });
export const fetchReportsV2 = (persona?: string) => apiFetch(`/report-factory/reports${persona ? `?persona=${persona}` : ''}`);
