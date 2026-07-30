import React, { useEffect, useState } from 'react';
import { Button } from './ui/Button';
import { Input } from './ui/Input';
import { Select } from './ui/Select';
import { FormField } from './ui/FormField';
import { StatusBadge } from './ui/StatusBadge';
import { StatCard } from './ui/StatCard';
import { DataTable, Column } from './ui/DataTable';
import { Modal } from './ui/Modal';
import { Drawer } from './ui/Drawer';
import { CalendarClock, Play, Plus, RefreshCw, History, Lock } from 'lucide-react';
import { apiGet, apiPost } from '../services/api';

export function LocalSchedulesCore() {
  const [schedules, setSchedules] = useState<any[]>([]);
  const [history, setHistory] = useState<any[]>([]);
  const [selectedScheduleId, setSelectedScheduleId] = useState<number | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);

  const [name, setName] = useState('');
  const [cron, setCron] = useState('0 0 * * *');
  const [planId, setPlanId] = useState('1');
  const [profileId, setProfileId] = useState('1');
  const [browser, setBrowser] = useState('chromium');

  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');

  useEffect(() => {
    void fetchSchedules();
  }, []);

  const fetchSchedules = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await apiGet<any[]>('/api/local-schedules?project_id=1').catch(() => []);
      setSchedules(data);
    } catch (e: any) {
      setError(e.message || 'Failed to load local schedules');
    } finally {
      setLoading(false);
    }
  };

  const createSchedule = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim() || !planId || !profileId) {
      setError('Name, Approved Test Plan ID, and Validation Profile ID are required.');
      return;
    }
    setSubmitting(true);
    setError('');
    try {
      await apiPost('/api/local-schedules', {
        project_id: 1,
        name: name.trim(),
        cron_expression: cron.trim(),
        approved_test_plan_id: parseInt(planId),
        validation_profile_id: parseInt(profileId),
        browser: browser,
      });
      setName('');
      setMessage('Schedule created successfully.');
      setShowCreateModal(false);
      await fetchSchedules();
    } catch (e: any) {
      setError(e.message || 'Failed to create schedule');
    } finally {
      setSubmitting(false);
    }
  };

  const toggleSchedule = async (id: number, currentEnabled: boolean) => {
    try {
      const action = currentEnabled ? 'disable' : 'enable';
      await apiPost(`/api/local-schedules/${id}/${action}`, {});
      setMessage(`Schedule ${action}d.`);
      await fetchSchedules();
    } catch (e: any) {
      setError(e.message || 'Toggle schedule failed');
    }
  };

  const runNow = async (id: number) => {
    try {
      await apiPost(`/api/local-schedules/${id}/run-now`, {});
      setMessage('Schedule execution triggered.');
      await fetchHistory(id);
      await fetchSchedules();
    } catch (e: any) {
      setError(e.message || 'Run now failed');
    }
  };

  const fetchHistory = async (id: number) => {
    setSelectedScheduleId(id);
    try {
      const data = await apiGet<any[]>(`/api/local-schedules/${id}/history`).catch(() => []);
      setHistory(data);
    } catch (e) {
      /* ignore */
    }
  };

  const columns: Column<any>[] = [
    { key: 'name', header: 'Schedule Name', render: (s) => <span style={{ fontWeight: 600 }}>{s.name}</span> },
    { key: 'cron_expression', header: 'Cron Schedule', render: (s) => <code style={{ fontSize: '0.8rem' }}>{s.cron_expression}</code> },
    { key: 'approved_test_plan_id', header: 'Approved Plan Version', render: (s) => <span style={{ fontSize: '0.825rem', color: 'var(--color-primary)' }}>Plan #{s.approved_test_plan_id} (v{s.approved_version_number || 1})</span> },
    { key: 'browser', header: 'Browser', render: (s) => <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{s.browser}</span> },
    { key: 'next_run_at', header: 'Next Run', render: (s) => <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{s.next_run_at ? new Date(s.next_run_at).toLocaleString() : '—'}</span> },
    { key: 'enabled', header: 'Status', render: (s) => <StatusBadge status={s.enabled ? 'APPROVED' : 'DRAFT'} label={s.enabled ? 'Enabled' : 'Disabled'} size="sm" /> },
    { key: 'id', header: 'Actions', render: (s) => (
      <div style={{ display: 'flex', gap: '0.35rem' }}>
        <Button size="sm" variant={s.enabled ? 'danger' : 'secondary'} onClick={() => void toggleSchedule(s.id, s.enabled)}>
          {s.enabled ? 'Disable' : 'Enable'}
        </Button>
        <Button size="sm" variant="primary" onClick={() => void runNow(s.id)} leftIcon={<Play size={12} />}>
          Run Now
        </Button>
        <Button size="sm" variant="secondary" onClick={() => void fetchHistory(s.id)} leftIcon={<History size={12} />}>
          History
        </Button>
      </div>
    )}
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      {/* KPI Stat Cards */}
      <div className="grid grid-cols-3">
        <StatCard title="Active Schedules" value={schedules.filter(s => s.enabled).length} subtitle="Periodic test triggers" icon={CalendarClock} variant="primary" loading={loading} />
        <StatCard title="Total Schedules" value={schedules.length} subtitle="Configured schedules" icon={CalendarClock} variant="info" loading={loading} />
        <StatCard title="Security & Scope" value="ADMIN / LOCAL" subtitle="Local target lock enabled" icon={Lock} variant="warning" loading={loading} />
      </div>

      {error && <div className="state-panel state-error" role="alert">{error}</div>}
      {message && <div className="state-panel" role="status">{message}</div>}

      {/* Main Table Card */}
      <div className="card" style={{ padding: '1.25rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
          <div>
            <h3 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-main)' }}>
              Local Schedules Registry
            </h3>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              Periodic background execution of approved test plans on local target environments.
            </p>
          </div>

          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <Button size="sm" variant="secondary" onClick={fetchSchedules} isLoading={loading} leftIcon={<RefreshCw size={14} />}>
              Refresh
            </Button>
            <Button size="sm" variant="primary" onClick={() => setShowCreateModal(true)} leftIcon={<Plus size={14} />}>
              New Schedule
            </Button>
          </div>
        </div>

        <DataTable
          columns={columns}
          data={schedules}
          keyExtractor={(s) => s.id}
          loading={loading}
          emptyMessage="No local schedules configured yet."
        />
      </div>

      {/* Create Schedule Modal */}
      <Modal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        title="Create Local Schedule"
        subtitle="Configure cron expression and approved test plan parameters"
        footer={(
          <>
            <Button variant="secondary" onClick={() => setShowCreateModal(false)}>Cancel</Button>
            <Button variant="primary" onClick={createSchedule} isLoading={submitting} disabled={!name.trim() || !planId}>
              Create Schedule
            </Button>
          </>
        )}
      >
        <form onSubmit={createSchedule} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <FormField label="Schedule Name" required>
            <Input
              required
              placeholder="e.g. Daily Nightly Acceptance Audit"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </FormField>

          <div className="grid grid-cols-2" style={{ gap: '0.75rem' }}>
            <FormField label="Cron Expression" required hint="Standard 5-field cron (min hour day month weekday)">
              <Input
                required
                value={cron}
                onChange={(e) => setCron(e.target.value)}
              />
            </FormField>

            <FormField label="Browser Environment">
              <Select value={browser} onChange={(e) => setBrowser(e.target.value)}>
                <option value="chromium">Chromium</option>
              </Select>
            </FormField>
          </div>

          <div className="grid grid-cols-2" style={{ gap: '0.75rem' }}>
            <FormField label="Approved Test Plan ID" required>
              <Input
                type="number"
                required
                value={planId}
                onChange={(e) => setPlanId(e.target.value)}
              />
            </FormField>

            <FormField label="Validation Profile ID" required>
              <Input
                type="number"
                required
                value={profileId}
                onChange={(e) => setProfileId(e.target.value)}
              />
            </FormField>
          </div>
        </form>
      </Modal>

      {/* History Drawer */}
      {selectedScheduleId && (
        <Drawer
          isOpen={true}
          onClose={() => setSelectedScheduleId(null)}
          title={`Execution History — Schedule #${selectedScheduleId}`}
          subtitle="Timestamped local execution run logs"
          width="650px"
        >
          {history.length === 0 ? (
            <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>
              No execution history recorded for this schedule yet.
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              {history.map((h) => (
                <div key={h.id} style={{ padding: '0.65rem 0.85rem', borderRadius: 'var(--radius-md)', background: 'var(--bg-card-subtle)', border: '1px solid var(--border-color)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <div>
                    <span style={{ fontWeight: 600, fontSize: '0.85rem' }}>Run #{h.id}</span>
                    <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{new Date(h.started_at).toLocaleString()}</p>
                  </div>
                  <StatusBadge status={h.status} size="sm" />
                </div>
              ))}
            </div>
          )}
        </Drawer>
      )}
    </div>
  );
}
