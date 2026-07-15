import { type FormEvent, useCallback, useEffect, useState } from 'react';
import { useAuth } from '../authContext';
import { applyCleanup, createBackup, fetchBackups, fetchSystemHealth, previewCleanup } from '../services/system';
import type { BackupSummary, CleanupSummary, SystemHealth } from '../types/system';

const statusLabel = (ready: boolean) => ready ? 'Ready' : 'Attention';
const formatBytes = (value: number) => value < 1024 ? `${value} B` : value < 1024 * 1024 ? `${(value / 1024).toFixed(1)} KB` : `${(value / 1024 / 1024).toFixed(1)} MB`;

export function FinalReleaseCore() {
  const { operator } = useAuth();
  const isAdmin = operator.role === 'ADMIN';
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [backups, setBackups] = useState<BackupSummary[]>([]);
  const [cleanup, setCleanup] = useState<CleanupSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const [backupConfirmation, setBackupConfirmation] = useState('');
  const [cleanupConfirmation, setCleanupConfirmation] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const nextHealth = await fetchSystemHealth();
      if (!nextHealth?.database || !nextHealth?.worker || !nextHealth?.queue || !nextHealth?.playwright || !nextHealth?.disk) throw new Error('Release diagnostics response is incomplete.');
      setHealth(nextHealth);
      if (isAdmin) {
        const [nextBackups, nextCleanup] = await Promise.all([fetchBackups(), previewCleanup()]);
        setBackups(Array.isArray(nextBackups) ? nextBackups : []);
        setCleanup(nextCleanup);
      }
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Release diagnostics are unavailable.');
    } finally { setLoading(false); }
  }, [isAdmin]);

  useEffect(() => { void load(); }, [load]);

  const submitBackup = async (event: FormEvent) => {
    event.preventDefault();
    if (backupConfirmation !== 'CREATE LOCAL BACKUP') return;
    setSubmitting(true); setNotice('');
    try {
      const result = await createBackup(backupConfirmation);
      setNotice(`Backup ${result.backup_id} created and checksummed.`);
      setBackupConfirmation('');
      setBackups(await fetchBackups());
    } catch (reason) { setError(reason instanceof Error ? reason.message : 'Backup failed safely.'); }
    finally { setSubmitting(false); }
  };

  const submitCleanup = async (event: FormEvent) => {
    event.preventDefault();
    if (cleanupConfirmation !== 'DELETE RETAINED FILES') return;
    setSubmitting(true); setNotice('');
    try {
      const result = await applyCleanup(cleanupConfirmation);
      setNotice(`Cleanup completed: ${result.deleted_files} files removed.`);
      setCleanupConfirmation('');
      setCleanup(await previewCleanup());
    } catch (reason) { setError(reason instanceof Error ? reason.message : 'Cleanup failed safely.'); }
    finally { setSubmitting(false); }
  };

  return <section className="section section-muted" id="system-health"><div className="section-inner">
    <div className="section-title"><h2>Final Release Readiness</h2><p>Local runtime health, queue status, protected storage, and maintenance controls.</p></div>
    {loading && <div className="state-panel" role="status">Loading system health...</div>}
    {error && <div className="state-panel state-error" role="alert">{error}<button className="button button-secondary" onClick={() => void load()}>Retry</button></div>}
    {notice && <div className="state-panel" role="status">{notice}</div>}
    {!loading && health && <><div className="release-status-grid">
      <div className="metric-card"><span>Backend</span><strong>{health.status === 'ok' ? 'Ready' : 'Degraded'}</strong><small>{health.environment}</small></div>
      <div className="metric-card"><span>Database</span><strong>{statusLabel(health.database.ready && health.database.migrations_current)}</strong><small>Migrations {health.database.migrations_current ? 'current' : 'pending'}</small></div>
      <div className="metric-card"><span>Worker</span><strong>{health.worker.heartbeat_ok ? 'Online' : 'Offline'}</strong><small>{health.worker.active_count} active</small></div>
      <div className="metric-card"><span>Queue</span><strong>{health.queue.queued} queued</strong><small>{health.queue.running} running</small></div>
      <div className="metric-card"><span>Chromium</span><strong>{statusLabel(health.playwright.installed && health.playwright.chromium_available)}</strong><small>Local runner</small></div>
      <div className="metric-card"><span>Disk</span><strong>{health.disk.warning ? 'Warning' : 'Ready'}</strong><small>{health.disk.free_mb} MB free</small></div>
    </div><div className="release-safety-band" aria-label="Release safety status">
      <span>Safe mode <strong>{health.safe_mode ? 'On' : 'Off'}</strong></span><span>TLS verification <strong>{health.tls_verification_enabled ? 'On' : 'Off'}</strong></span><span>Production execution <strong>{health.production_execution_enabled ? 'Enabled' : 'Blocked'}</strong></span><span>Real target execution <strong>{health.real_target_execution_enabled ? 'Enabled' : 'Disabled'}</strong></span><span>Immutable triggers <strong>{health.database.immutable_triggers_installed ? 'Installed' : 'Attention'}</strong></span>
    </div></>}
    {!loading && health && isAdmin && <div className="maintenance-grid"><div className="card maintenance-panel"><h3>Local Backup</h3><p>{backups.length ? `${backups.length} validated backup records available.` : 'No validated backups recorded yet.'}</p><form onSubmit={submitBackup}><label>Type CREATE LOCAL BACKUP<input value={backupConfirmation} onChange={(event) => setBackupConfirmation(event.target.value)} /></label><button className="button button-primary" disabled={submitting || backupConfirmation !== 'CREATE LOCAL BACKUP'}>Create Backup</button></form></div><div className="card maintenance-panel"><h3>Retention Cleanup</h3><p>{cleanup ? `${cleanup.candidate_files} files (${formatBytes(cleanup.candidate_bytes)}) in the current dry-run.` : 'Cleanup preview is unavailable.'}</p><form onSubmit={submitCleanup}><label>Type DELETE RETAINED FILES<input value={cleanupConfirmation} onChange={(event) => setCleanupConfirmation(event.target.value)} /></label><button className="button button-danger" disabled={submitting || cleanupConfirmation !== 'DELETE RETAINED FILES'}>Apply Cleanup</button></form></div></div>}
    {!loading && health && !isAdmin && <div className="state-panel">Backup and cleanup controls require ADMIN access.</div>}
  </div></section>;
}
