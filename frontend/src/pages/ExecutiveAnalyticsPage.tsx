import React from 'react';
import { PageHeader } from '../components/layout/PageHeader';
import { StatCard } from '../components/ui/StatCard';
import { StatusBadge } from '../components/ui/StatusBadge';
import { BarChart3, TrendingUp, Activity, Zap, ShieldCheck } from 'lucide-react';

export function ExecutiveAnalyticsPage() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      <PageHeader
        breadcrumbs={[{ label: 'Executive' }, { label: 'Enterprise Analytics' }]}
        title="Enterprise Analytics & Risk Heatmaps"
        description="Interactive heatmaps, trend graphs, bug density analytics, execution speed trends, pass/fail ratios, and AI confidence tracking."
      />

      <div className="grid grid-cols-4">
        <StatCard title="Overall Pass Rate" value="98.4%" subtitle="Suite Execution" icon={ShieldCheck} variant="success" />
        <StatCard title="Average Execution Speed" value="1.16s" subtitle="Per Test Case" icon={Zap} variant="primary" />
        <StatCard title="AI Healing Rate" value="99.4%" subtitle="Zero Flakiness" icon={TrendingUp} variant="info" />
        <StatCard title="Predictive Bug Density" value="0.12 / KLOC" subtitle="Codebase Health" icon={Activity} variant="warning" />
      </div>

      <div className="card" style={{ padding: '1.25rem' }}>
        <h3 style={{ margin: '0 0 1rem 0', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <BarChart3 size={18} color="var(--color-primary)" /> Enterprise Module Risk Heatmap
        </h3>

        <div className="grid grid-cols-4" style={{ gap: '1rem' }}>
          {[
            { module: 'HRMS Payroll', risk: 'MODERATE (18.5%)', color: '#f59e0b' },
            { module: 'Sales Orders', risk: 'LOW (8.2%)', color: '#10b981' },
            { module: 'Checkout Portal', risk: 'LOW (6.4%)', color: '#10b981' },
            { module: 'Inventory Mgmt', risk: 'LOW (9.1%)', color: '#10b981' }
          ].map((m, idx) => (
            <div key={idx} style={{ background: 'var(--bg-muted)', padding: '1rem', borderRadius: '8px', borderLeft: `5px solid ${m.color}` }}>
              <div style={{ fontWeight: 700, fontSize: '0.9rem', marginBottom: '0.2rem' }}>{m.module}</div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Risk Index: {m.risk}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
