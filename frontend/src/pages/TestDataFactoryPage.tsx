import React, { useState } from 'react';
import { PageHeader } from '../components/layout/PageHeader';
import { StatCard } from '../components/ui/StatCard';
import { StatusBadge } from '../components/ui/StatusBadge';
import { Button } from '../components/ui/Button';
import { Database, FlaskConical, Shield, Layers, Shuffle, Zap } from 'lucide-react';
import { apiGet, apiPost } from '../services/api';
import { toast } from '../stores/toastStore';

const CATEGORIES = [
  'CUSTOMERS', 'PRODUCTS', 'INVOICES', 'ORDERS', 'USERS',
  'ROLES', 'PERMISSIONS', 'RANDOM', 'BOUNDARY', 'NEGATIVE', 'SYNTHETIC',
];

const CATEGORY_COLORS: Record<string, string> = {
  CUSTOMERS: '#6366f1', PRODUCTS: '#10b981', INVOICES: '#f59e0b',
  ORDERS: '#3b82f6', USERS: '#8b5cf6', ROLES: '#ec4899',
  PERMISSIONS: '#14b8a6', RANDOM: '#f97316', BOUNDARY: '#a855f7',
  NEGATIVE: '#ef4444', SYNTHETIC: '#06b6d4',
};

export function TestDataFactoryPage() {
  const [selectedCategory, setSelectedCategory] = useState('CUSTOMERS');
  const [recordCount, setRecordCount] = useState(10);
  const [masked, setMasked] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleGenerate = async () => {
    setGenerating(true);
    try {
      const res = await apiPost<any>(
        `/api/data-factory/generate?project_id=1&category=${selectedCategory}&record_count=${recordCount}&masked=${masked}`,
        {}
      );
      setResult(res);
      toast.success(`Generated ${res.record_count} ${selectedCategory} records!`);
    } catch (err: any) {
      toast.error(err.message || 'Data generation failed');
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      <PageHeader
        breadcrumbs={[{ label: 'Zero-Code Ecosystem' }, { label: 'Test Data Factory' }]}
        title="Smart Test Data Factory"
        description="AI-generates synthetic enterprise datasets: Customers, Products, Invoices, Orders, Users, Boundary, Negative, and Masked Sensitive data."
      />

      <div className="grid grid-cols-4">
        <StatCard title="Data Categories" value={11} subtitle="Enterprise Datasets" icon={Database} variant="primary" />
        <StatCard title="Synthetic Datasets" value="Unlimited" subtitle="AI-Generated Records" icon={FlaskConical} variant="success" />
        <StatCard title="Sensitive Masking" value="AES-256" subtitle="PII Auto-Masked" icon={Shield} variant="warning" />
        <StatCard title="Boundary Testing" value="Auto" subtitle="Min/Max/Edge Cases" icon={Zap} variant="info" />
      </div>

      <div className="card" style={{ padding: '1.5rem' }}>
        <h3 style={{ margin: '0 0 1.25rem 0' }}>Dataset Generator</h3>

        {/* Category Selection */}
        <div style={{ marginBottom: '1.25rem' }}>
          <div style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-muted)', marginBottom: '0.6rem', textTransform: 'uppercase' }}>Data Category</div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
            {CATEGORIES.map(cat => (
              <div
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                style={{
                  padding: '0.5rem 1rem', borderRadius: 8, cursor: 'pointer', fontSize: '0.82rem', fontWeight: 600,
                  border: `2px solid ${selectedCategory === cat ? (CATEGORY_COLORS[cat] || 'var(--color-primary)') : 'var(--border-color)'}`,
                  background: selectedCategory === cat ? `${CATEGORY_COLORS[cat] || 'var(--color-primary)'}1A` : 'var(--bg-muted)',
                  color: selectedCategory === cat ? (CATEGORY_COLORS[cat] || 'var(--color-primary)') : 'var(--text-primary)',
                  transition: 'all 0.2s',
                }}
              >
                {cat}
              </div>
            ))}
          </div>
        </div>

        {/* Controls */}
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', marginBottom: '1.25rem', flexWrap: 'wrap' }}>
          <div>
            <div style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-muted)', marginBottom: '0.4rem', textTransform: 'uppercase' }}>Record Count</div>
            <input
              type="number"
              value={recordCount}
              min={1}
              max={1000}
              onChange={e => setRecordCount(parseInt(e.target.value) || 10)}
              style={{
                width: 100, padding: '0.6rem 0.9rem',
                background: 'var(--bg-muted)', border: '1px solid var(--border-color)',
                borderRadius: 8, color: 'var(--text-primary)', fontSize: '0.9rem',
              }}
            />
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
            <div style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Mask PII Data</div>
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
              <input type="checkbox" checked={masked} onChange={e => setMasked(e.target.checked)} />
              <span style={{ fontSize: '0.85rem' }}>Enable Sensitive Data Masking</span>
            </label>
          </div>
          <Button variant="primary" onClick={() => void handleGenerate()} isLoading={generating} leftIcon={<Shuffle size={16} />} style={{ alignSelf: 'flex-end' }}>
            Generate Dataset
          </Button>
        </div>

        {/* Preview */}
        {result && (
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem' }}>
              <StatusBadge status="APPROVED" label={`${result.record_count} Records Generated`} />
              {result.masked && <StatusBadge status="WARNING" label="PII Masked" size="sm" />}
            </div>
            <div style={{ background: 'var(--bg-muted)', borderRadius: 8, padding: '1rem', fontFamily: 'var(--font-mono)', fontSize: '0.78rem', overflowX: 'auto' }}>
              <pre style={{ margin: 0 }}>{JSON.stringify(result.sample_preview, null, 2)}</pre>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
