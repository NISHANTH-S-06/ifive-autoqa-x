import type { Product } from '../types/product';

export const products: Product[] = [
  {
    id: 'erp',
    name: 'iFive ERP',
    shortName: 'ERP',
    modules: ['Login', 'Customer', 'Vendor', 'Inventory', 'Purchase', 'Sales', 'Finance', 'Production', 'Reports', 'Export', 'Permissions'],
  },
  {
    id: 'hrms',
    name: 'iFive HRMS',
    shortName: 'HRMS',
    modules: ['Employee', 'Attendance', 'Leave', 'Shift', 'Payroll Preview', 'Recruitment', 'Self Service', 'Permissions'],
  },
  {
    id: 'crm',
    name: 'iFive CRM',
    shortName: 'CRM',
    modules: ['Lead', 'Opportunity', 'Follow-up', 'Quotation', 'Customer', 'Reports', 'Permissions'],
  },
  {
    id: 'iiot',
    name: 'iFive IIoT',
    shortName: 'IIoT',
    modules: ['Dashboard', 'Device Status', 'Telemetry', 'Alerts', 'Charts', 'Filters', 'Data Freshness'],
  },
  {
    id: 'integration',
    name: 'Application Integration',
    shortName: 'Integration',
    modules: ['Authentication', 'API Mapping', 'Schema', 'Retry', 'Duplicate Handling', 'Webhooks', 'Error Logs'],
  },
];

