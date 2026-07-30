/**
 * Phase 15 – Autonomous Enterprise Software Quality Intelligence Platform (SQIP) frontend service.
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

// ─── Module 1: Enterprise Software Intelligence Graph ────────────────────────
export const seedSoftwareGraph = () => apiFetch('/software-graph/seed', { method: 'POST' });
export const fetchSoftwareGraph = (nodeType?: string) => apiFetch(`/software-graph/graph${nodeType ? `?node_type=${nodeType}` : ''}`);
export const analyzeSoftwareImpact = (nodeKey: string) => apiFetch(`/software-graph/impact/${nodeKey}`);

// ─── Module 2: AI Change Impact Intelligence ─────────────────────────────────
export const analyzeCommitImpact = (commitHash: string, author: string, changedFiles: string[]) =>
  apiFetch('/change-impact/analyze', { method: 'POST', body: JSON.stringify({ commit_hash: commitHash, author, changed_files: changedFiles }) });
export const fetchChangeImpactHistory = () => apiFetch('/change-impact/history');

// ─── Module 3: Enterprise AI Code Reviewer ───────────────────────────────────
export const reviewCodeFile = (filePath: string, language: string, codeSnippet?: string) =>
  apiFetch('/code-review/analyze', { method: 'POST', body: JSON.stringify({ file_path: filePath, language, code_snippet: codeSnippet || '' }) });
export const fetchCodeReviewHistory = () => apiFetch('/code-review/history');

// ─── Module 4: AI Test Coverage Intelligence ────────────────────────────────
export const computeCoverage = () => apiFetch('/coverage/compute', { method: 'POST' });
export const fetchCoverageMetrics = () => apiFetch('/coverage/metrics');
export const generateMissingTests = (dimensionType: string) => apiFetch(`/coverage/generate-missing/${dimensionType}`, { method: 'POST' });

// ─── Module 5: Enterprise Release Intelligence ───────────────────────────────
export const evaluateRelease = (releaseVersion: string) =>
  apiFetch('/release-intelligence/evaluate', { method: 'POST', body: JSON.stringify({ release_version: releaseVersion }) });
export const fetchReleaseEvaluations = () => apiFetch('/release-intelligence/evaluations');

// ─── Module 6: AI Defect Intelligence Hub ─────────────────────────────────────
export const seedDefectClusters = () => apiFetch('/defects-hub/seed', { method: 'POST' });
export const fetchDefectClusters = () => apiFetch('/defects-hub/clusters');
export const predictDuplicateDefect = (defectDescription: string) =>
  apiFetch('/defects-hub/predict-duplicate', { method: 'POST', body: JSON.stringify({ defect_description: defectDescription }) });

// ─── Module 7: Enterprise Engineering Analytics ─────────────────────────────
export const computeEngineeringMetrics = () => apiFetch('/engineering/compute', { method: 'POST' });
export const fetchEngineeringMetrics = () => apiFetch('/engineering/metrics');

// ─── Module 11: Enterprise Knowledge Lake ────────────────────────────────────
export const seedKnowledgeLake = () => apiFetch('/knowledge-lake/seed', { method: 'POST' });
export const searchKnowledgeLake = (query?: string) => apiFetch(`/knowledge-lake/search${query ? `?query=${encodeURIComponent(query)}` : ''}`);

// ─── Module 12: Executive Mission Control & Validator & Pair QA ─────────────
export const fetchMissionControlDashboard = () => apiFetch('/mission-control/dashboard');
export const assistPairQA = (intent: string, context?: any) =>
  apiFetch('/mission-control/pair-qa/assist', { method: 'POST', body: JSON.stringify({ intent, context: context || {} }) });
export const validateReleaseAutonomously = (releaseVersion: string) =>
  apiFetch('/mission-control/release-validator/validate', { method: 'POST', body: JSON.stringify({ release_version: releaseVersion }) });
export const triggerSelfEvolving = () => apiFetch('/mission-control/self-evolving/evolve', { method: 'POST' });
