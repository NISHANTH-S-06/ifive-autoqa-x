import { type FormEvent, useEffect, useRef, useState } from 'react';
import { AuthContext } from './authContext';
import { RequiredPasswordChange } from './components/PasswordControls';
import { login, logout, restoreSession } from './services/auth';
import type { Operator } from './types/auth';
import { HomePage } from './pages/HomePage';

export default function App() {
  const [operator, setOperator] = useState<Operator | null>(null);
  const [checking, setChecking] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const passwordRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    void restoreSession().then(setOperator).catch(() => undefined).finally(() => setChecking(false));
  }, []);

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    if (submitting) return;
    setSubmitting(true);
    setError('');
    try {
      setOperator(await login(username, password));
      setPassword('');
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Backend unavailable.');
      setPassword('');
      passwordRef.current?.focus();
    } finally {
      setSubmitting(false);
    }
  };

  const signOut = async () => {
    try {
      await logout();
    } finally {
      setOperator(null);
      setUsername('');
      setPassword('');
    }
  };

  const refreshOperator = async () => {
    setOperator(await restoreSession());
  };

  if (checking) return <main className="login-shell"><div className="state-panel" role="status">Loading dashboard...</div></main>;

  if (!operator) return <main className="login-shell"><div className="login-card"><div className="brand"><span className="brand-mark">i5</span><span>iFive AutoQA</span></div><h1>Local Operator Login</h1><p>Sign in with a locally created operator account.</p>{error && <div className="state-panel state-error" role="alert">{error}</div>}<form onSubmit={submit}><label>Username<input required autoComplete="username" value={username} onChange={(event) => setUsername(event.target.value)} /></label><label>Password<input ref={passwordRef} required type="password" autoComplete="current-password" value={password} onChange={(event) => setPassword(event.target.value)} /></label><button className="button button-primary" disabled={submitting}>{submitting ? 'Signing in...' : 'Sign In'}</button></form></div></main>;

  if (operator.must_change_password) return <RequiredPasswordChange username={operator.username} displayName={operator.display_name} onChanged={refreshOperator} onLogout={signOut} />;

  return <AuthContext.Provider value={{ operator, logout: signOut }}><HomePage /></AuthContext.Provider>;
}
