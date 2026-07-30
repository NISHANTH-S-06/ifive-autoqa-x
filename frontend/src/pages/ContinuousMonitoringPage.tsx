import React, { useEffect, useState } from 'react';
import { PageHeader } from '../components/layout/PageHeader';
import { StatusBadge } from '../components/ui/StatusBadge';
import { Button } from '../components/ui/Button';
import { DataTable, Column } from '../components/ui/DataTable';
import { Activity, ShieldAlert, Globe, RefreshCw, Bell } from 'lucide-react';
import { apiGet } from '../services/api';
import { toast } from '../stores/toastStore';

interface MonitorAlert {
  id: number;
  target_url: string;
  alert_type: string;
  severity: string;
  details: Record<string, any>;
  created_at: string;
}

export function ContinuousMonitoringPage() {
  const [alerts, setAlerts] = useState<MonitorAlert[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchAlerts = async () => {
    setLoading(true);
    try {
      const data = await apiGet<MonitorAlert[]>('/api/monitoring/alerts?company_id=1');
      setAlerts(data);
    } catch (err) {
      toast.error('Failed to load continuous monitoring alerts');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void fetchAlerts();
  }, []);

  const columns: Column<MonitorAlert>[] = [
    { key: 'id', header: 'Alert ID', render: (a) => <span style={{ fontWeight: 700, fontFamily: 'var(--font-mono)' }}>#{a.id}</span> },
    { key: 'target_url', header: 'Target URL', render: (a) => <span style={{ fontWeight: 600 }}>{a.target_url}</span> },
    { key: 'alert_type', header: 'Alert Type', render: (a) => <StatusBadge status="WARNING" label={a.alert_type} size="sm" /> },
    { key: 'severity', header: 'Severity', render: (a) => <StatusBadge status={a.severity === 'HIGH' ? 'CRITICAL' : 'INFO'} label={a.severity} size="sm" /> },
    { key: 'created_at', header: 'Detected At', render: (a) => new Date(a.created_at).toLocaleString() }
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      <PageHeader
        breadcrumbs={[{ label: 'Autonomous Monitoring' }, { label: 'Continuous Alerts' }]}
        title="Continuous Autonomous Monitoring Feed"
        description="Real-time monitoring feed tracking live connected company products for UI drift, broken links, perf degradation, API errors, cert expiry, and security header changes."
        actions={(
          <Button size="sm" variant="secondary" onClick={() => void fetchAlerts()} isLoading={loading} leftIcon={<RefreshCw size={14} />}>
            Refresh Alerts Feed
          </Button>
        )}
      />

      <div className="card" style={{ padding: '1.25rem' }}>
        <h3 style={{ margin: '0 0 1rem 0', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Activity size={18} color="var(--color-primary)" /> Active Monitoring Alerts ({alerts.length})
        </h3>
        <DataTable columns={columns} data={alerts} keyExtractor={(a) => a.id.toString()} />
      </div>
    </div>
  );
}
