const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? '';
export const apiUrl = (path: string) => `${apiBaseUrl}${path}`;
let csrfToken = '';
export const setCsrfToken = (value: string) => { csrfToken = value; };
export const getCsrfToken = () => csrfToken;

async function parseResponse<T>(response: Response): Promise<T> {
  const text = await response.text();
  let body: any = null;
  try {
    body = text ? JSON.parse(text) : null;
  } catch {
    if (!response.ok) {
      throw new Error(`API request failed with status ${response.status}.`);
    }
    throw new Error('Server returned invalid JSON response.');
  }

  if (!response.ok) {
    let errorMsg = `API request failed (${response.status}).`;
    if (body?.detail) {
      errorMsg = typeof body.detail === 'string' ? body.detail : JSON.stringify(body.detail);
    }
    throw new Error(errorMsg);
  }
  return body as T;
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
