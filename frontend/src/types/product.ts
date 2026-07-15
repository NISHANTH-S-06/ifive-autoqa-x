export type ProductCode = 'ERP' | 'HRMS' | 'CRM' | 'IIOT' | 'INTEGRATION' | 'AUTOQA';
export type ProductKey = 'erp' | 'hrms' | 'crm' | 'iiot' | 'integration';

export interface Product {
  id: ProductKey;
  name: string;
  shortName: string;
  modules: string[];
}

export interface Project {
  id: number;
  name: string;
  product_code: ProductCode;
  description: string | null;
  base_url: string | null;
  environment: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}
