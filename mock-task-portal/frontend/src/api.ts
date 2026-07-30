/**
 * API client for Mock Task Portal.
 * All calls go through Vite proxy to http://localhost:8001
 */
import type {
  DashboardSummary,
  HistoryRecord,
  LoginResponse,
  QAResult,
  Task,
  TaskCreate,
  TaskUpdate,
  User,
} from './types';

const BASE = '/api';

function getToken(): string | null {
  return localStorage.getItem('mtp_token');
}

function authHeaders(): HeadersInit {
  const token = getToken();
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

async function request<T>(
  method: string,
  path: string,
  body?: unknown,
): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method,
    headers: authHeaders(),
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) {
    let detail = `HTTP ${res.status}`;
    try {
      const err = await res.json();
      detail = err.detail ?? JSON.stringify(err);
    } catch {
      // ignore parse error
    }
    throw new Error(detail);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

// ── Auth ──
export async function login(username: string, password: string): Promise<LoginResponse> {
  return request<LoginResponse>('POST', '/auth/login', { username, password });
}

export async function logout(): Promise<void> {
  return request<void>('POST', '/auth/logout');
}

export async function getMe(): Promise<User> {
  return request<User>('GET', '/auth/me');
}

// ── Users ──
export async function listUsers(): Promise<User[]> {
  return request<User[]>('GET', '/users');
}

// ── Tasks ──
export async function createTask(payload: TaskCreate): Promise<Task> {
  return request<Task>('POST', '/tasks', payload);
}

export interface TaskFilters {
  status?: string;
  project?: string;
  developer?: string;
  tester?: string;
  priority?: string;
}

export async function listTasks(filters: TaskFilters = {}): Promise<Task[]> {
  const params = new URLSearchParams();
  if (filters.status) params.set('status', filters.status);
  if (filters.project) params.set('project', filters.project);
  if (filters.developer) params.set('developer', filters.developer);
  if (filters.tester) params.set('tester', filters.tester);
  if (filters.priority) params.set('priority', filters.priority);
  const qs = params.toString();
  return request<Task[]>('GET', `/tasks${qs ? `?${qs}` : ''}`);
}

export async function getTask(taskId: number): Promise<Task> {
  return request<Task>('GET', `/tasks/${taskId}`);
}

export async function updateTask(taskId: number, payload: TaskUpdate): Promise<Task> {
  return request<Task>('PATCH', `/tasks/${taskId}`, payload);
}

export async function changeStatus(
  taskId: number,
  newStatus: string,
  reason?: string,
): Promise<Task> {
  return request<Task>('PATCH', `/tasks/${taskId}/status`, { new_status: newStatus, reason });
}

export async function addDeveloperNotes(taskId: number, notes: string): Promise<Task> {
  return request<Task>('POST', `/tasks/${taskId}/developer-notes`, { notes });
}

export async function addReworkRemarks(taskId: number, remarks: string): Promise<Task> {
  return request<Task>('POST', `/tasks/${taskId}/rework-remarks`, { remarks });
}

export async function recordQAResult(
  taskId: number,
  result: QAResult,
  reason?: string,
): Promise<Task> {
  return request<Task>('POST', `/tasks/${taskId}/qa-result`, { result, reason });
}

export async function getTaskHistory(taskId: number): Promise<HistoryRecord[]> {
  return request<HistoryRecord[]>('GET', `/tasks/${taskId}/history`);
}

// ── Dashboard ──
export async function getDashboardSummary(): Promise<DashboardSummary> {
  return request<DashboardSummary>('GET', '/dashboard/summary');
}
