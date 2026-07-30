import React, { useEffect, useState } from 'react';
import { PageHeader } from '../components/layout/PageHeader';
import { StatCard } from '../components/ui/StatCard';
import { StatusBadge } from '../components/ui/StatusBadge';
import { Button } from '../components/ui/Button';
import { Monitor, Cpu, RefreshCw, HeartPulse, Play, Zap } from 'lucide-react';
import { apiGet, apiPost } from '../services/api';
import { toast } from '../stores/toastStore';

interface Worker {
  id: number;
  worker_name: string;
  browser_type: string;
  status: string;
  jobs_completed: number;
  jobs_failed: number;
}

interface FarmStatus {
  total_workers: number;
  idle: number;
  busy: number;
  unhealthy: number;
  workers: Worker[];
}

const BROWSER_COLORS: Record<string, string> = {
  CHROMIUM: '#4f46e5', CHROME: '#2563eb', FIREFOX: '#ea580c',
  EDGE: '#0ea5e9', WEBKIT: '#8b5cf6', MOBILE_CHROME: '#10b981',
  MOBILE_SAFARI: '#ec4899', TABLET: '#f59e0b', DESKTOP: '#6366f1',
};

export function AutonomousTestLabPage() {
  const [farmStatus, setFarmStatus] = useState<FarmStatus | null>(null);
  const [loading, setLoading] = useState(false);
  const [healing, setHealing] = useState(false);
  const [provisioning, setProvisioning] = useState(false);

  const fetchStatus = async () => {
    setLoading(true);
    try {
      const res = await apiGet<FarmStatus>('/api/test-lab/farm-status');
      setFarmStatus(res);
    } catch (err) {
      toast.error('Failed to load browser farm status');
    } finally {
      setLoading(false);
    }
  };

  const handleProvision = async () => {
    setProvisioning(true);
    try {
      await apiPost('/api/test-lab/provision', {});
      toast.success('Browser farm workers provisioned!');
      void fetchStatus();
    } catch (err: any) {
      toast.error(err.message || 'Provisioning failed');
    } finally {
      setProvisioning(false);
    }
  };

  const handleHeal = async () => {
    setHealing(true);
    try {
      const res = await apiPost<any>('/api/test-lab/self-heal', {});
      toast.success(`Self-heal complete. ${res.healed_count} workers restored.`);
      void fetchStatus();
    } catch (err: any) {
      toast.error(err.message || 'Self-heal failed');
    } finally {
      setHealing(false);
    }
  };

  useEffect(() => {
    void fetchStatus();
  }, []);

  const statusColor = (s: string) =>
    s === 'IDLE' ? '#10b981' : s === 'BUSY' ? '#f59e0b' : '#ef4444';

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      <PageHeader
        breadcrumbs={[{ label: 'Zero-Code Ecosystem' }, { label: 'Autonomous Test Lab' }]}
        title="Autonomous Browser Farm & Test Lab"
        description="Multi-browser parallel execution farm: Chromium, Chrome, Firefox, Edge, WebKit, Mobile Chrome, Mobile Safari, Tablet, Desktop."
        actions={
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <Button size="sm" variant="secondary" onClick={() => void handleProvision()} isLoading={provisioning} leftIcon={<Play size={14} />}>
              Provision Workers
            </Button>
            <Button size="sm" variant="secondary" onClick={() => void handleHeal()} isLoading={healing} leftIcon={<HeartPulse size={14} />}>
              Self-Heal
            </Button>
            <Button size="sm" variant="secondary" onClick={() => void fetchStatus()} isLoading={loading} leftIcon={<RefreshCw size={14} />}>
              Refresh
            </Button>
          </div>
        }
      />

      {farmStatus && (
        <>
          <div className="grid grid-cols-4">
            <StatCard title="Total Workers" value={farmStatus.total_workers} subtitle="Browser Farm Nodes" icon={Monitor} variant="primary" />
            <StatCard title="Idle Workers" value={farmStatus.idle} subtitle="Ready for Execution" icon={Cpu} variant="success" />
            <StatCard title="Busy Workers" value={farmStatus.busy} subtitle="Actively Running" icon={Zap} variant="warning" />
            <StatCard title="Unhealthy" value={farmStatus.unhealthy} subtitle="Needs Self-Heal" icon={HeartPulse} variant={farmStatus.unhealthy > 0 ? 'danger' : 'success'} />
          </div>

          <div className="card" style={{ padding: '1.25rem' }}>
            <h3 style={{ margin: '0 0 1rem 0' }}>Browser Farm Worker Registry</h3>
            {farmStatus.workers.length === 0 ? (
              <p style={{ color: 'var(--text-muted)' }}>No workers provisioned. Click "Provision Workers" to initialize the browser farm.</p>
            ) : (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '0.75rem' }}>
                {farmStatus.workers.map(w => (
                  <div
                    key={w.id}
                    style={{
                      background: 'var(--bg-muted)', padding: '1rem', borderRadius: 8,
                      borderLeft: `4px solid ${BROWSER_COLORS[w.browser_type] || '#6366f1'}`,
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                      <span style={{ fontWeight: 700, fontSize: '0.85rem' }}>{w.worker_name}</span>
                      <div style={{ width: 10, height: 10, borderRadius: '50%', background: statusColor(w.status) }} title={w.status} />
                    </div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>{w.browser_type}</div>
                    <div style={{ display: 'flex', gap: '1rem', fontSize: '0.75rem' }}>
                      <span>✅ {w.jobs_completed}</span>
                      <span>❌ {w.jobs_failed}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
