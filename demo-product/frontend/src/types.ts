export interface User {
  id: number;
  username: string;
  display_name: string;
  role: string;
  is_active: boolean;
}

export interface Department {
  id: number;
  name: string;
}

export interface Employee {
  id: number;
  employee_code: string;
  name: string;
  email: string;
  department_id: number;
  department_name?: string;
  joining_date: string;
  active: boolean;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface EmployeeCreate {
  name: string;
  email: string;
  department_id: number;
  joining_date: string;
  active: boolean;
  notes?: string;
}

export interface EmployeeUpdate {
  name?: string;
  email?: string;
  department_id?: number;
  joining_date?: string;
  active?: boolean;
  notes?: string;
}

export interface Product {
  id: number;
  product_code: string;
  name: string;
  current_quantity: number;
}

export interface StockCount {
  id: number;
  product_id: number;
  product_name?: string;
  previous_quantity: number;
  counted_quantity: number;
  difference: number;
  notes?: string;
  created_by: string;
  created_at: string;
}

export interface StockCountCreate {
  product_id: number;
  counted_quantity: number;
  notes?: string;
}

export interface DemoSetting {
  key: string;
  enabled: boolean;
  value?: string;
  updated_at: string;
}
