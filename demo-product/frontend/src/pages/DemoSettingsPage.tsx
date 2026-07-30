import React, { useEffect, useState } from 'react';
import { listDemoSettings, updateDemoSetting } from '../api';
import type { DemoSetting } from '../types';

const BUG_LABELS: Record<string, { label: string; desc: string }> = {
  employee_save_failure: {
    label: '1. Employee Save Failure (HTTP 500)',
    desc: 'Saving an employee returns HTTP 500 error and the employee record is NOT created in DB.',
  },
  employee_success_message_missing: {
    label: '2. Employee Success Message Missing',
    desc: 'Employee is created in DB, but the success notification banner is hidden from the UI.',
  },
  employee_table_refresh_failure: {
    label: '3. Employee Table Refresh Failure',
    desc: 'Employee is created in DB, but GET /api/employees omits the newly created record from the table.',
  },
  stock_difference_error: {
    label: '4. Stock Difference Calculation Error',
    desc: 'Submitting a stock count calculates an deliberately incorrect difference formula.',
  },
  api_delay: {
    label: '5. Configurable API Response Delay (3s)',
    desc: 'Introduces a 3-second delay on API requests to simulate slow network responses.',
  },
  login_failure_mode: {
    label: '6. Login Failure Mode (HTTP 503)',
    desc: 'Login attempts fail with HTTP 503 Service Unavailable, blocking access to the application.',
  },
};

export default function DemoSettingsPage() {
  const [settings, setSettings] = useState<DemoSetting[]>([]);
  const [loading, setLoading] = useState(true);
  const [updatingKey, setUpdatingKey] = useState<string | null>(null);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  function fetchSettings() {
    return listDemoSettings().then(setSettings).catch(err => setError(err.message));
  }

  useEffect(() => {
    fetchSettings().finally(() => setLoading(false));
  }, []);

  async function handleToggle(key: string, currentEnabled: boolean) {
    setUpdatingKey(key);
    setError('');
    setSuccess('');
    try {
      await updateDemoSetting(key, !currentEnabled);
      await fetchSettings();
      setSuccess(`Bug toggle ${key} updated to ${!currentEnabled ? 'ENABLED' : 'DISABLED'}.`);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to update setting');
    } finally {
      setUpdatingKey(null);
    }
  }

  const anyBugEnabled = settings.some(s => s.enabled);

  return (
    <>
      <div className="page-header">
        <h1>Demo Bug Toggles Settings</h1>
        <p>Admin Control Panel for Intentional Observability Bugs</p>
      </div>

      <div className="page-body">
        {error && <div className="alert alert-error">{error}</div>}
        {success && <div className="alert alert-success">{success}</div>}

        {anyBugEnabled && (
          <div data-testid="bug-warning-banner" className="alert" style={{ background: '#341a00', border: '1px solid var(--warning)', color: 'var(--warning)', fontWeight: 600 }}>
            ⚠ WARNING: One or more intentional bug toggles are currently ENABLED. Application behavior may demonstrate observable defects.
          </div>
        )}

        <div className="card">
          <div className="card-title">Configurable Bug Toggles</div>
          {loading ? (
            <p style={{ color: 'var(--text-muted)' }}>Loading bug settings…</p>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              {settings.map(s => {
                const info = BUG_LABELS[s.key] || { label: s.key, desc: '' };
                return (
                  <div
                    key={s.key}
                    style={{
                      padding: 16,
                      background: 'var(--surface-2)',
                      borderRadius: 'var(--radius)',
                      border: s.enabled ? '1px solid var(--warning)' : '1px solid var(--border)',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                    }}
                  >
                    <div style={{ maxWidth: '80%' }}>
                      <div style={{ fontWeight: 600, fontSize: 14, color: s.enabled ? 'var(--warning)' : 'var(--text)' }}>
                        {info.label}
                      </div>
                      <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 4 }}>
                        {info.desc}
                      </div>
                    </div>
                    <div>
                      <button
                        data-testid={`toggle-${s.key}`}
                        className={`btn ${s.enabled ? 'btn-danger' : 'btn-ghost'}`}
                        style={{ minWidth: 100 }}
                        disabled={updatingKey === s.key}
                        onClick={() => handleToggle(s.key, s.enabled)}
                      >
                        {updatingKey === s.key ? 'Updating…' : s.enabled ? 'ON (Bug Active)' : 'OFF (Normal)'}
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </>
  );
}
