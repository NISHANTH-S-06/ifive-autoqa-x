import React from 'react';
import { PageHeader } from '../components/layout/PageHeader';
import { StatCard } from '../components/ui/StatCard';
import { StatusBadge } from '../components/ui/StatusBadge';
import { Brain, Sparkles, TrendingUp, CheckCircle, Zap } from 'lucide-react';

export function SelfEvolutionDashboardPage() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      <PageHeader
        breadcrumbs={[{ label: 'AI QA Brain' }, { label: 'Self Evolution Dashboard' }]}
        title="Self-Evolving AI QA Brain Dashboard"
        description="Tracks continuous AI evolution progress, locator healing accuracy %, test suite deduplication, and multi-tenant global learning timelines."
      />

      <div className="grid grid-cols-4">
        <StatCard title="AI Evolution Score" value="98.5%" subtitle="Self-Tuned Maturity" icon={Brain} variant="primary" />
        <StatCard title="Self-Healing Accuracy" value="99.4%" subtitle="Zero Human Healing Needed" icon={Sparkles} variant="success" />
        <StatCard title="Locator Success Rate" value="99.8%" subtitle="Adaptive DOM Selectors" icon={CheckCircle} variant="info" />
        <StatCard title="Learning Timeline" value="Continuous" subtitle="Real-time Feedback Loops" icon={TrendingUp} variant="warning" />
      </div>

      <div className="card" style={{ padding: '1.25rem' }}>
        <h3 style={{ margin: '0 0 1rem 0' }}>AI Self-Evolution Learning Milestones</h3>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {[
            { title: 'Global Multi-Tenant Healed Selectors', desc: 'Promoted data-testid patterns across 100 anonymized tenants.', badge: 'EVOLVED' },
            { title: 'Dynamic NetworkIdle Waiting', desc: 'Replaced static 500ms sleep with dynamic networkidle event listeners.', badge: 'OPTIMIZED' },
            { title: 'Automatic Step Deduplication', desc: 'Identified and merged 14 duplicate authorization checks.', badge: 'DEDUPLICATED' }
          ].map((m, idx) => (
            <div key={idx} style={{ background: 'var(--bg-muted)', padding: '1rem', borderRadius: '8px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <div style={{ fontWeight: 700, fontSize: '0.9rem' }}>{m.title}</div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{m.desc}</div>
              </div>
              <StatusBadge status="APPROVED" label={m.badge} size="sm" />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
