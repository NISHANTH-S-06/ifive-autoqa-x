import type {
  User, Department, Employee, EmployeeCreate, EmployeeUpdate,
  Product, StockCount, StockCountCreate, DemoSetting,
} from './types';

const BASE = '/api';

function getToken(): string | null {
  return localStorage.getItem('demo_token');
}

function authHeaders(): HeadersInit {
  const token = getToken();
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

async function request<T>(method: string, path: string, body?: unknown): Promise<T> {
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
    } catch {}
    throw new Error(detail);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

// ── Auth ──
export async function login(username: string, password: string) {
  return request<{ access_token: string; user: User }>('POST', '/auth/login', { username, password });
}

export async function logout(): Promise<void> {
  return request<void>('POST', '/auth/logout');
}

export async function getMe(): Promise<User> {
  return request<User>('GET', '/auth/me');
}

// ── Departments ──
export async function listDepartments(): Promise<Department[]> {
  return request<Department[]>('GET', '/departments');
}

// ── Employees ──
export async function listEmployees(): Promise<Employee[]> {
  return request<Employee[]>('GET', '/employees');
}

export async function getEmployee(id: number): Promise<Employee> {
  return request<Employee>('GET', `/employees/${id}`);
}

export async function createEmployee(payload: EmployeeCreate): Promise<Employee> {
  return request<Employee>('POST', '/employees', payload);
}

export async function updateEmployee(id: number, payload: EmployeeUpdate): Promise<Employee> {
  return request<Employee>('PATCH', `/employees/${id}`, payload);
}

// ── Products & Inventory ──
export async function listProducts(): Promise<Product[]> {
  return request<Product[]>('GET', '/products');
}

export async function listStockCounts(): Promise<StockCount[]> {
  return request<StockCount[]>('GET', '/stock-counts');
}

export async function createStockCount(payload: StockCountCreate): Promise<StockCount> {
  return request<StockCount>('POST', '/stock-counts', payload);
}

// ── Demo Settings ──
export async function listDemoSettings(): Promise<DemoSetting[]> {
  return request<DemoSetting[]>('GET', '/demo-settings');
}

export async function updateDemoSetting(key: string, enabled: boolean, value?: string): Promise<DemoSetting> {
  return request<DemoSetting>('PATCH', `/demo-settings/${key}`, { enabled, value });
}
