import React, { useEffect, useState } from 'react';
import { PageHeader } from '../components/layout/PageHeader';
import { DataTable, Column } from '../components/ui/DataTable';
import { StatusBadge } from '../components/ui/StatusBadge';
import { StatCard } from '../components/ui/StatCard';
import { ErrorState } from '../components/ui/ErrorState';
import { Button } from '../components/ui/Button';
import { Drawer } from '../components/ui/Drawer';
import { JSONViewer } from '../components/ui/JSONViewer';
import { listAuditEvents, verifyAudit } from '../services/auth';
import type { AuditEvent } from '../types/auth';
import { toast } from '../stores/toastStore';
import { ShieldCheck, ShieldAlert, RefreshCw, Eye, FileCheck2, Lock } from 'lucide-react';

export function AuditLogsPage() {
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [selectedEvent, setSelectedEvent] = useState<AuditEvent | null>(null);
  const [verification, setVerification] = useState<{ valid: boolean; total_events: number; first_invalid_event_id: number | null } | null>(null);
  const [loading, setLoading] = useState(true);
  const [verifying, setVerifying] = useState(false);
  const [error, setError] = useState('');

  const loadLogs = async () => {
    setLoading(true);
    setError('');
    try {
      const [evRes, verRes] = await Promise.all([
        listAuditEvents(),
        verifyAudit()
      ]);
      setEvents(evRes || []);
      setVerification(verRes);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch audit events.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadLogs();
  }, []);

  const handleVerify = async () => {
    setVerifying(true);
    try {
      const res = await verifyAudit();
      setVerification(res);
      if (res.valid) {
        toast.success(`Audit hash chain verified valid (${res.total_events} events).`);
      } else {
        toast.error(`Audit hash chain mismatch at event ID: ${res.first_invalid_event_id}`);
      }
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Audit verification failed.');
    } finally {
      setVerifying(false);
    }
  };

  const columns: Column<AuditEvent>[] = [
    { key: 'id', header: 'Event ID', render: (e) => <span style={{ fontWeight: 600, fontFamily: 'var(--font-mono)' }}>#{e.id}</span> },
    { key: 'action', header: 'Action', render: (e) => <span style={{ fontWeight: 600, color: 'var(--color-primary)' }}>{e.action}</span> },
    { key: 'operator_id', header: 'Operator', render: (e) => <span style={{ fontSize: '0.8rem' }}>Operator #{e.operator_id || 'System'}</span> },
    { key: 'resource_type', header: 'Resource', render: (e) => <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{e.resource_type || 'system'} #{e.resource_id || ''}</span> },
    { key: 'outcome', header: 'Outcome', render: (e) => <StatusBadge status={e.outcome === 'SUCCESS' ? 'PASS' : 'FAIL'} label={e.outcome} size="sm" /> },
    { key: 'occurred_at', header: 'Timestamp', render: (e) => <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{e.occurred_at ? new Date(e.occurred_at).toLocaleString() : '-'}</span> },
    { key: 'request_id', header: 'Request ID', render: (e) => <span style={{ fontSize: '0.7rem', fontFamily: 'var(--font-mono)', color: 'var(--text-subtle)' }}>{e.request_id ? e.request_id.substring(0, 12) + '...' : '-'}</span> },
    { key: 'id', header: 'Actions', render: (e) => (
      <Button size="sm" variant="secondary" onClick={() => setSelectedEvent(e)} leftIcon={<Eye size={13} />}>
        Inspect
      </Button>
    )}
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      <PageHeader
        breadcrumbs={[{ label: 'Audit Logs' }]}
        title="Cryptographic Audit Trail & Integrity Logs"
        description="Append-only audit ledger tracking system operations, security events, and approval actions."
        actions={(
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <Button size="sm" variant="secondary" onClick={handleVerify} isLoading={verifying} leftIcon={<ShieldCheck size={14} style={{ color: 'var(--color-success)' }} />}>
              Verify Audit Chain
            </Button>
            <Button size="sm" variant="secondary" onClick={loadLogs} isLoading={loading} leftIcon={<RefreshCw size={14} />}>
              Refresh
            </Button>
          </div>
        )}
      />

      <div className="grid grid-cols-3">
        <StatCard title="Total Audit Events" value={verification?.total_events || events.length} subtitle="Recorded ledger events" icon={FileCheck2} variant="primary" loading={loading} />
        <StatCard title="Ledger Integrity" value={verification?.valid ? 'INTACT' : 'VERIFIED'} subtitle="Sequential hash verification" icon={ShieldCheck} variant="success" loading={loading} />
        <StatCard title="Storage Security" value="APPEND-ONLY" subtitle="Immutable trigger protection" icon={Lock} variant="info" loading={loading} />
      </div>

      {/* Verification Status Banner */}
      {verification && (
        <div className="card" style={{ padding: '1rem', borderLeft: `4px solid ${verification.valid ? 'var(--color-success)' : 'var(--color-danger)'}` }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              {verification.valid ? (
                <ShieldCheck size={24} style={{ color: 'var(--color-success)' }} />
              ) : (
                <ShieldAlert size={24} style={{ color: 'var(--color-danger)' }} />
              )}
              <div>
                <h4 style={{ fontWeight: 600, fontSize: '0.95rem', color: 'var(--text-main)' }}>
                  Audit Ledger Integrity: {verification.valid ? 'VERIFIED INTACT' : 'TAMPER DETECTED'}
                </h4>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                  Validated {verification.total_events} sequential cryptographic hashes against database state.
                </p>
              </div>
            </div>
            <StatusBadge status={verification.valid ? 'APPROVED' : 'REJECTED'} label={verification.valid ? 'VALID HASH CHAIN' : 'CORRUPTED'} />
          </div>
        </div>
      )}

      {error && <ErrorState message={error} onRetry={loadLogs} />}

      <div className="card" style={{ padding: '1.25rem' }}>
        <DataTable
          columns={columns}
          data={events}
          keyExtractor={(e) => e.id}
          loading={loading}
          emptyMessage="No audit log events recorded."
        />
      </div>

      {selectedEvent && (
        <Drawer
          isOpen={true}
          onClose={() => setSelectedEvent(null)}
          title={`Audit Event #${selectedEvent.id}: ${selectedEvent.action}`}
          subtitle={`Resource: ${selectedEvent.resource_type || 'system'} #${selectedEvent.resource_id || ''}`}
          width="650px"
        >
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <JSONViewer data={selectedEvent} title="Complete Audit Record JSON" maxHeight="450px" />
          </div>
        </Drawer>
      )}
    </div>
  );
}
