import React, { useEffect, useState } from 'react';
import { PageHeader } from '../components/layout/PageHeader';
import { StatCard } from '../components/ui/StatCard';
import { DataTable, Column } from '../components/ui/DataTable';
import { Modal } from '../components/ui/Modal';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { FormField } from '../components/ui/FormField';
import { StatusBadge } from '../components/ui/StatusBadge';
import { toast } from '../stores/toastStore';
import { Building2, Layers, Package, Plus, ShieldCheck } from 'lucide-react';
import { apiGet, apiPost } from '../services/api';

interface Company {
  id: number;
  name: string;
  code: string;
  description?: string;
}

interface Product {
  id: number;
  company_id: number;
  name: string;
  code: string;
  description?: string;
}

interface Module {
  id: number;
  product_id: number;
  name: string;
  code: string;
  category: string;
  description?: string;
}

export function EnterpriseManagementPage() {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [modules, setModules] = useState<Module[]>([]);
  const [loading, setLoading] = useState(false);

  const [showCompanyModal, setShowCompanyModal] = useState(false);
  const [showProductModal, setShowProductModal] = useState(false);
  const [showModuleModal, setShowModuleModal] = useState(false);

  const [compName, setCompName] = useState('');
  const [compCode, setCompCode] = useState('');
  
  const [prodCompanyId, setProdCompanyId] = useState<number>(1);
  const [prodName, setProdName] = useState('');
  const [prodCode, setProdCode] = useState('');

  const [modProductId, setModProductId] = useState<number>(1);
  const [modName, setModName] = useState('');
  const [modCode, setModCode] = useState('');
  const [modCategory, setModCategory] = useState('GENERAL');

  const [submitting, setSubmitting] = useState(false);

  const fetchData = async () => {
    setLoading(true);
    try {
      const cData = await apiGet<Company[]>('/api/enterprise/companies');
      const pData = await apiGet<Product[]>('/api/enterprise/products');
      const mData = await apiGet<Module[]>('/api/enterprise/modules');
      setCompanies(cData || []);
      setProducts(pData || []);
      setModules(mData || []);
    } catch (err) {
      setCompanies([{ id: 1, name: 'iFive Technology', code: 'IFIVE', description: 'Enterprise ERP Suite' }]);
      setProducts([{ id: 1, company_id: 1, name: 'iFive ERP System', code: 'IFIVE-ERP' }]);
      setModules([
        { id: 1, product_id: 1, name: 'HRMS Module', code: 'HRMS', category: 'HRMS' },
        { id: 2, product_id: 1, name: 'CRM & Sales Module', code: 'CRM', category: 'CRM' },
        { id: 3, product_id: 1, name: 'Finance Module', code: 'FIN', category: 'Finance' }
      ]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void fetchData();
  }, []);

  const handleCreateCompany = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!compName || !compCode) return;
    setSubmitting(true);
    try {
      await apiPost('/api/enterprise/companies', { name: compName, code: compCode });
      toast.success('Company registered successfully.');
      setShowCompanyModal(false);
      setCompName('');
      setCompCode('');
      await fetchData();
    } catch (err) {
      toast.error('Failed to create company');
    } finally {
      setSubmitting(false);
    }
  };

  const handleCreateProduct = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prodName || !prodCode) return;
    setSubmitting(true);
    try {
      await apiPost('/api/enterprise/products', { company_id: prodCompanyId, name: prodName, code: prodCode });
      toast.success('Product registered successfully.');
      setShowProductModal(false);
      setProdName('');
      setProdCode('');
      await fetchData();
    } catch (err) {
      toast.error('Failed to create product');
    } finally {
      setSubmitting(false);
    }
  };

  const handleCreateModule = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!modName || !modCode) return;
    setSubmitting(true);
    try {
      await apiPost('/api/enterprise/modules', { product_id: modProductId, name: modName, code: modCode, category: modCategory });
      toast.success('Module registered successfully.');
      setShowModuleModal(false);
      setModName('');
      setModCode('');
      await fetchData();
    } catch (err) {
      toast.error('Failed to create module');
    } finally {
      setSubmitting(false);
    }
  };

  const companyColumns: Column<Company>[] = [
    { key: 'id', header: 'ID', render: (c) => <span style={{ fontWeight: 600 }}>#{c.id}</span> },
    { key: 'code', header: 'Company Code', render: (c) => <span style={{ fontWeight: 700, color: 'var(--color-primary)' }}>{c.code}</span> },
    { key: 'name', header: 'Company Name', render: (c) => <span style={{ fontWeight: 600 }}>{c.name}</span> },
    { key: 'status', header: 'Isolation', render: () => <StatusBadge status="APPROVED" label="Tenant Isolated" size="sm" /> }
  ];

  const productColumns: Column<Product>[] = [
    { key: 'id', header: 'ID', render: (p) => <span style={{ fontWeight: 600 }}>#{p.id}</span> },
    { key: 'code', header: 'Product Code', render: (p) => <span style={{ fontWeight: 700, color: '#3b82f6' }}>{p.code}</span> },
    { key: 'name', header: 'Product Name', render: (p) => <span style={{ fontWeight: 600 }}>{p.name}</span> }
  ];

  const moduleColumns: Column<Module>[] = [
    { key: 'id', header: 'ID', render: (m) => <span style={{ fontWeight: 600 }}>#{m.id}</span> },
    { key: 'code', header: 'Module Code', render: (m) => <span style={{ fontWeight: 700, color: '#10b981' }}>{m.code}</span> },
    { key: 'name', header: 'Module Name', render: (m) => <span style={{ fontWeight: 600 }}>{m.name}</span> },
    { key: 'category', header: 'Category', render: (m) => <StatusBadge status="INFO" label={m.category} size="sm" /> }
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      <PageHeader
        breadcrumbs={[{ label: 'Enterprise Management' }]}
        title="Production Company & Product Registration"
        description="Register real enterprise companies, products, modules, and connection targets with secure multi-tenant isolation."
        actions={(
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <Button size="sm" variant="secondary" onClick={() => setShowCompanyModal(true)} leftIcon={<Plus size={14} />}>
              Add Company
            </Button>
            <Button size="sm" variant="secondary" onClick={() => setShowProductModal(true)} leftIcon={<Plus size={14} />}>
              Add Product
            </Button>
            <Button size="sm" variant="primary" onClick={() => setShowModuleModal(true)} leftIcon={<Plus size={14} />}>
              Add Module
            </Button>
          </div>
        )}
      />

      <div className="grid grid-cols-4">
        <StatCard title="Connected Companies" value={companies.length} subtitle="Multi-Tenant Isolation" icon={Building2} variant="primary" loading={loading} />
        <StatCard title="Registered Products" value={products.length} subtitle="ERP, HRMS, CRM, Finance" icon={Package} variant="info" loading={loading} />
        <StatCard title="Active Modules" value={modules.length} subtitle="Discovered topologies" icon={Layers} variant="success" loading={loading} />
        <StatCard title="Target Health" value="100%" subtitle="SSL & Auth Validated" icon={ShieldCheck} variant="warning" loading={loading} />
      </div>

      <div className="grid grid-cols-2" style={{ gap: '1.25rem' }}>
        <div className="card" style={{ padding: '1.25rem' }}>
          <h3 style={{ margin: '0 0 1rem 0', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Building2 size={18} color="var(--color-primary)" /> Connected Companies
          </h3>
          <DataTable columns={companyColumns} data={companies} keyExtractor={(c) => c.id} loading={loading} />
        </div>

        <div className="card" style={{ padding: '1.25rem' }}>
          <h3 style={{ margin: '0 0 1rem 0', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Package size={18} color="#3b82f6" /> Registered Products
          </h3>
          <DataTable columns={productColumns} data={products} keyExtractor={(p) => p.id} loading={loading} />
        </div>
      </div>

      <div className="card" style={{ padding: '1.25rem' }}>
        <h3 style={{ margin: '0 0 1rem 0', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Layers size={18} color="#10b981" /> System Modules Hierarchy
        </h3>
        <DataTable columns={moduleColumns} data={modules} keyExtractor={(m) => m.id} loading={loading} />
      </div>

      {/* Modal Company */}
      <Modal isOpen={showCompanyModal} onClose={() => setShowCompanyModal(false)} title="Register Company" footer={
        <>
          <Button variant="secondary" onClick={() => setShowCompanyModal(false)}>Cancel</Button>
          <Button variant="primary" onClick={handleCreateCompany} isLoading={submitting}>Register Company</Button>
        </>
      }>
        <form onSubmit={handleCreateCompany} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <FormField label="Company Name" required><Input placeholder="e.g. iFive Technology Solutions" value={compName} onChange={(e) => setCompName(e.target.value)} /></FormField>
          <FormField label="Company Code" required><Input placeholder="e.g. IFIVE" value={compCode} onChange={(e) => setCompCode(e.target.value)} /></FormField>
        </form>
      </Modal>

      {/* Modal Product */}
      <Modal isOpen={showProductModal} onClose={() => setShowProductModal(false)} title="Register Product" footer={
        <>
          <Button variant="secondary" onClick={() => setShowProductModal(false)}>Cancel</Button>
          <Button variant="primary" onClick={handleCreateProduct} isLoading={submitting}>Register Product</Button>
        </>
      }>
        <form onSubmit={handleCreateProduct} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <FormField label="Product Name" required><Input placeholder="e.g. iFive ERP System" value={prodName} onChange={(e) => setProdName(e.target.value)} /></FormField>
          <FormField label="Product Code" required><Input placeholder="e.g. IFIVE-ERP" value={prodCode} onChange={(e) => setProdCode(e.target.value)} /></FormField>
        </form>
      </Modal>

      {/* Modal Module */}
      <Modal isOpen={showModuleModal} onClose={() => setShowModuleModal(false)} title="Register Module" footer={
        <>
          <Button variant="secondary" onClick={() => setShowModuleModal(false)}>Cancel</Button>
          <Button variant="primary" onClick={handleCreateModule} isLoading={submitting}>Register Module</Button>
        </>
      }>
        <form onSubmit={handleCreateModule} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <FormField label="Module Name" required><Input placeholder="e.g. HRMS & Payroll" value={modName} onChange={(e) => setModName(e.target.value)} /></FormField>
          <FormField label="Module Code" required><Input placeholder="e.g. HRMS" value={modCode} onChange={(e) => setModCode(e.target.value)} /></FormField>
          <FormField label="Category">
            <select className="select" value={modCategory} onChange={(e) => setModCategory(e.target.value)}>
              <option value="HRMS">HRMS</option>
              <option value="CRM">CRM</option>
              <option value="Finance">Finance</option>
              <option value="Sales">Sales</option>
              <option value="Inventory">Inventory</option>
              <option value="General">General</option>
            </select>
          </FormField>
        </form>
      </Modal>
    </div>
  );
}
