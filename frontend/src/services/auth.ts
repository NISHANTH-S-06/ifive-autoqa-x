import { apiGet, apiMutation, apiUrl, setCsrfToken } from './api';
import type { AuditEvent, Operator, OperatorRole, OperatorSecurity, OperatorSession, SecuritySummary } from '../types/auth';

export async function login(username: string, password: string) {
  const response = await fetch(apiUrl('/api/auth/login'), { method: 'POST', credentials: 'include', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ username, password }) });
  const text = await response.text();
  let body: { operator?: Operator; csrf_token?: string; detail?: string } = {};
  try {
    body = JSON.parse(text);
  } catch {
    throw new Error(`Server returned invalid response (${response.status}). Ensure Vite dev server is proxying to backend.`);
  }
  if (!response.ok || !body.operator || !body.csrf_token) throw new Error(body.detail ?? 'Login failed.');
  setCsrfToken(body.csrf_token); return body.operator;
}
export async function restoreSession() { const operator = await apiGet<Operator>('/api/auth/me'); const csrf = await apiGet<{ csrf_token: string }>('/api/auth/csrf'); setCsrfToken(csrf.csrf_token); return operator; }
export const logout = () => apiMutation<{ status: string }>('POST', '/api/auth/logout', {});
export const listOperators = () => apiGet<Operator[]>('/api/operators');
export const createOperator = (value: { username: string; display_name: string; role: OperatorRole; temporary_password: string }) => apiMutation<Operator>('POST', '/api/operators', value);
export const setOperatorStatus = (id: number, is_active: boolean) => apiMutation<Operator>('PATCH', `/api/operators/${id}/status`, { is_active });
export const setOperatorRole = (id: number, role: OperatorRole) => apiMutation<Operator>('PATCH', `/api/operators/${id}/role`, { role });
export const changeRequiredPassword = (value: { current_password: string; new_password: string; confirm_password: string }) => apiMutation<{ status: string }>('POST', '/api/auth/change-required-password', value);
export const changePassword = (value: { current_password: string; new_password: string; confirm_password: string }) => apiMutation<{ status: string }>('POST', '/api/auth/change-password', value);
export const listSessions = () => apiGet<OperatorSession[]>('/api/auth/sessions');
export const revokeSession = (id: number, reason: string) => apiMutation<{ status: string }>('POST', `/api/auth/sessions/${id}/revoke`, { reason });
export const revokeOtherSessions = () => apiMutation<{ revoked_count: number }>('POST', '/api/auth/sessions/revoke-others', {});
export const listAuditEvents = () => apiGet<AuditEvent[]>('/api/audit/events?limit=50');
export const verifyAudit = () => apiGet<{ valid: boolean; total_events: number; first_invalid_event_id: number | null }>('/api/audit/verify');
export const getSecuritySummary = () => apiGet<SecuritySummary>('/api/security/summary');
export const listSecurityOperators = () => apiGet<OperatorSecurity[]>('/api/security/operators?limit=100');
export const resetOperatorPassword = (id: number, value: { temporary_password: string; confirm_temporary_password: string; reason: string }) => apiMutation<{ message: string }>('POST', `/api/operators/${id}/reset-password`, value);
export const listOperatorSessions = (id: number) => apiGet<OperatorSession[]>(`/api/operators/${id}/sessions`);
export const revokeOperatorSessions = (id: number, reason: string) => apiMutation<{ revoked_count: number }>('POST', `/api/operators/${id}/sessions/revoke-all`, { reason });
