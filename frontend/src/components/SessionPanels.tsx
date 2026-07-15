import { useEffect, useState } from 'react';
import { useAuth } from '../authContext';
import { listSessions, revokeOtherSessions, revokeSession } from '../services/auth';
import type { OperatorSession } from '../types/auth';

const formatDate = (value: string | null) => value ? new Date(value).toLocaleString() : 'Never';

export function MySessionsPanel() {
  const { logout } = useAuth();
  const [sessions, setSessions] = useState<OperatorSession[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  const load = async () => {
    setLoading(true);
    setError('');
    try {
      setSessions(await listSessions());
    } catch (reason) {
      setSessions([]);
      setError(reason instanceof Error ? reason.message : 'Unable to load sessions.');
    } finally {
      setLoading(false);
    }
  };
  useEffect(() => { void load(); }, []);
  const revoke = async (session: OperatorSession) => {
    if (!window.confirm(session.is_current ? 'Revoke your current session and return to login?' : 'Revoke this saved session?')) return;
    setError(''); setMessage('');
    try {
      await revokeSession(session.session_id, 'Owner requested revocation');
      if (session.is_current) {
        await logout();
        return;
      }
      setMessage('Session revoked.');
      await load();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Session revocation failed.');
    }
  };
  const revokeOthers = async () => {
    if (!window.confirm('Revoke every other active session for your account? Your current session will remain signed in.')) return;
    setError(''); setMessage('');
    try {
      const result = await revokeOtherSessions();
      setMessage(`${result.revoked_count} session(s) revoked.`);
      await load();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Session revocation failed.');
    }
  };
  return <div className="card"><h3>My Sessions</h3>{error && <div className="state-panel state-error" role="alert">{error}<button className="button button-secondary" onClick={() => void load()}>Retry</button></div>}{message && <div className="state-panel" role="status">{message}</div>}<div className="session-actions"><button className="button button-secondary" disabled={loading || sessions.filter((session) => session.is_active && !session.is_current).length === 0} onClick={() => void revokeOthers()}>Revoke Other Sessions</button></div>{loading && <div className="state-panel" role="status">Loading sessions...</div>}{!loading && !error && sessions.length === 0 && <div className="state-panel">No sessions to display.</div>}{!loading && !error && sessions.length > 0 && <div className="session-list">{sessions.map((session) => <div className="session-row" key={session.session_id}><div><strong>{session.user_agent ?? 'Unknown browser'}</strong><span>{session.ip_address ?? 'Masked IP'}{session.is_current ? ' - Current session' : ''}</span></div><span>Created {formatDate(session.created_at)}</span><span>Activity {formatDate(session.last_activity_at ?? session.last_seen_at)}</span><span>Expires {formatDate(session.expires_at)}</span><span className={session.is_active ? 'status-pass' : 'status-fail'}>{session.is_active ? 'Active' : 'Revoked'}</span><button className="button button-secondary" disabled={!session.is_active} onClick={() => void revoke(session)}>{session.is_current ? 'Revoke Current' : 'Revoke'}</button></div>)}</div>}</div>;
}
