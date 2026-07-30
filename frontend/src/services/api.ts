const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? '';
export const apiUrl = (path: string) => `${apiBaseUrl}${path}`;
let csrfToken = '';
export const setCsrfToken = (value: string) => { csrfToken = value; };
export const getCsrfToken = () => csrfToken;

async function parseResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const body = await response.json().catch(() => null) as { detail?: any } | null;
    let errorMsg = `API request failed (${response.status}).`;
    if (body?.detail) {
      errorMsg = typeof body.detail === 'string' ? body.detail : JSON.stringify(body.detail);
    }
    throw new Error(errorMsg);
  }
  return response.json() as Promise<T>;
}

export async function apiGet<T>(path: string): Promise<T> {
  const response = await fetch(`${apiBaseUrl}${path}`, { credentials: 'include' });

  return parseResponse<T>(response);
}

export async function apiPost<T>(path: string, body: unknown): Promise<T> {
  return apiMutation<T>('POST', path, body);
}

export async function apiMutation<T>(method: 'POST' | 'PATCH' | 'DELETE', path: string, body: unknown): Promise<T> {
  const response = await fetch(`${apiBaseUrl}${path}`, { method, credentials: 'include', headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': csrfToken }, body: body !== undefined ? JSON.stringify(body) : undefined });
  if (response.status === 204) return undefined as T;
  return parseResponse<T>(response);
}
