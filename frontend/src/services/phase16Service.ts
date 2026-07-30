/**
 * Phase 16 – Enterprise Autonomous Software Engineering Intelligence Platform (ASEIP) service.
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

// ─── Module 1: Knowledge Lake V2 ──────────────────────────────────────────────
export const seedKnowledgeLakeV2 = () => apiFetch('/knowledge-lake-v2/seed', { method: 'POST' });
export const searchKnowledgeLakeV2 = (query?: string, sourceType?: string) =>
  apiFetch(`/knowledge-lake-v2/search?query=${encodeURIComponent(query || '')}${sourceType ? `&source_type=${sourceType}` : ''}`);

// ─── Module 2: AI Requirement Intelligence ────────────────────────────────────
export const seedRequirements = () => apiFetch('/requirements/seed', { method: 'POST' });
export const fetchRequirements = (type?: string) => apiFetch(`/requirements/list${type ? `?req_type=${type}` : ''}`);
export const analyzeRequirement = (code: string, title: string, desc: string) =>
  apiFetch('/requirements/analyze', { method: 'POST', body: JSON.stringify({ requirement_code: code, title, description: desc }) });

// ─── Module 3: Autonomous Traceability Matrix ─────────────────────────────────
export const seedTraceability = () => apiFetch('/traceability/seed', { method: 'POST' });
export const fetchTraceabilityMatrix = (ver?: string) => apiFetch(`/traceability/matrix${ver ? `?release_version=${ver}` : ''}`);
export const fetchTraceabilityGapReport = () => apiFetch('/traceability/gap-report');

// ─── Module 4: Architecture Intelligence ──────────────────────────────────────
export const fetchArchitectureGraph = () => apiFetch('/architecture/graph');

// ─── Module 5: AI Code Quality Governor ───────────────────────────────────────
export const fetchCodeQualityViolations = (lang?: string, cat?: string) =>
  apiFetch(`/code-quality/violations?${lang ? `language=${lang}&` : ''}${cat ? `category=${cat}` : ''}`);
export const scanCodeSnippet = (path: string, lang: string, snippet: string) =>
  apiFetch('/code-quality/scan', { method: 'POST', body: JSON.stringify({ file_path: path, language: lang, code_snippet: snippet }) });

// ─── Module 6: Autonomous Release Certification ───────────────────────────────
export const certifyRelease = (ver: string) =>
  apiFetch('/release-certification/certify', { method: 'POST', body: JSON.stringify({ release_version: ver }) });
export const fetchCertificationsHistory = () => apiFetch('/release-certification/history');

// ─── Module 7: Production Observability AI ───────────────────────────────────
export const fetchObservabilityMetrics = () => apiFetch('/observability-ai/metrics');

// ─── Module 8: Customer Experience Intelligence ──────────────────────────────
export const fetchCustomerFeedback = () => apiFetch('/customer-intelligence/feedback');

// ─── Module 9 & 10: Digital Twin V2 & Enterprise Policy Engine ───────────────
export const fetchDigitalTwinV2 = () => apiFetch('/policies/digital-twin-v2');
export const fetchPolicies = (category?: string) => apiFetch(`/policies/list${category ? `?category=${category}` : ''}`);
export const evaluatePolicies = (context: object) => apiFetch('/policies/evaluate', { method: 'POST', body: JSON.stringify(context) });

// ─── Module 11 & 12: Executive Decision Engine & SDLC Orchestrator ────────────
export const fetchSDLCStatus = () => apiFetch('/sdlc-orchestrator/status');
export const fetchExecutiveDecisions = () => apiFetch('/sdlc-orchestrator/executive-decisions');
