import { type FormEvent, useRef, useState } from 'react';
import { changePassword, changeRequiredPassword } from '../services/auth';

function checks(password: string, username: string, displayName: string) {
  const lower = password.toLowerCase();
  const normalizedUser = username.toLowerCase();
  const displayTokens = displayName.toLowerCase().split(/[^a-z0-9]+/).filter((item) => item.length >= 3);
  return [
    ['At least 12 characters', password.length >= 12],
    ['Uppercase letter', /[A-Z]/.test(password)],
    ['Lowercase letter', /[a-z]/.test(password)],
    ['Number', /\d/.test(password)],
    ['Special character', /[^A-Za-z0-9]/.test(password)],
    ['Does not contain username', !normalizedUser || !lower.includes(normalizedUser)],
    ['Does not contain display name', !displayTokens.some((item) => lower.includes(item))],
  ] as const;
}

export function PasswordChecklist({ password, username, displayName }: { password: string; username: string; displayName: string }) {
  return <ul className="policy-list">{checks(password, username, displayName).map(([label, ok]) => <li key={label} className={ok ? 'policy-ok' : ''}>{label}</li>)}</ul>;
}

export function RequiredPasswordChange({ username, displayName, onChanged, onLogout }: { username: string; displayName: string; onChanged: () => Promise<void>; onLogout: () => Promise<void> }) {
  const [form, setForm] = useState({ current_password: '', new_password: '', confirm_password: '' });
  const [error, setError] = useState(''); const [submitting, setSubmitting] = useState(false);
  const currentRef = useRef<HTMLInputElement>(null);
  const confirmRef = useRef<HTMLInputElement>(null);
  const submit = async (event: FormEvent) => {
    event.preventDefault(); if (submitting) return; setError('');
    if (form.new_password !== form.confirm_password) { setError('New password and confirmation password do not match.'); confirmRef.current?.focus(); return; }
    setSubmitting(true);
    try { await changeRequiredPassword(form); setForm({ current_password: '', new_password: '', confirm_password: '' }); await onChanged(); }
    catch (reason) { setError(reason instanceof Error ? reason.message : 'Password change failed.'); setForm({ current_password: '', new_password: '', confirm_password: '' }); currentRef.current?.focus(); }
    finally { setSubmitting(false); }
  };
  return <main className="login-shell"><div className="login-card security-form-card"><div className="brand"><span className="brand-mark">i5</span><span>iFive AutoQA</span></div><h1>Password Change Required</h1><p>Your temporary or expired password must be changed before normal access is available.</p>{error && <div className="state-panel state-error" role="alert">{error}</div>}<form onSubmit={submit}><label>Current password<input ref={currentRef} required type="password" autoComplete="current-password" value={form.current_password} onChange={(e) => setForm({...form, current_password:e.target.value})}/></label><label>New password<input required type="password" autoComplete="new-password" value={form.new_password} onChange={(e) => setForm({...form, new_password:e.target.value})}/></label><label>Confirm password<input ref={confirmRef} required type="password" autoComplete="new-password" value={form.confirm_password} onChange={(e) => setForm({...form, confirm_password:e.target.value})}/></label><PasswordChecklist password={form.new_password} username={username} displayName={displayName}/><button className="button button-primary" disabled={submitting}>{submitting ? 'Changing Password' : 'Change Password'}</button><button type="button" className="button button-secondary" onClick={() => void onLogout()}>Logout</button></form></div></main>;
}

export function ChangePasswordPanel({ username, displayName }: { username: string; displayName: string }) {
  const [form, setForm] = useState({ current_password: '', new_password: '', confirm_password: '' });
  const [message, setMessage] = useState(''); const [error, setError] = useState(''); const [submitting, setSubmitting] = useState(false);
  const currentRef = useRef<HTMLInputElement>(null);
  const confirmRef = useRef<HTMLInputElement>(null);
  const submit = async (event: FormEvent) => {
    event.preventDefault(); if (submitting) return; setError(''); setMessage('');
    if (form.new_password !== form.confirm_password) { setError('New password and confirmation password do not match.'); confirmRef.current?.focus(); return; }
    setSubmitting(true);
    try { await changePassword(form); setForm({ current_password: '', new_password: '', confirm_password: '' }); setMessage('Password changed. Other sessions were revoked.'); }
    catch (reason) { setError(reason instanceof Error ? reason.message : 'Password change failed.'); setForm({ current_password: '', new_password: '', confirm_password: '' }); currentRef.current?.focus(); }
    finally { setSubmitting(false); }
  };
  return <div className="card"><h3>Change Password</h3>{message && <div className="state-panel" role="status">{message}</div>}{error && <div className="state-panel state-error" role="alert">{error}</div>}<form className="admin-form" onSubmit={submit}><input ref={currentRef} aria-label="Current password" required type="password" autoComplete="current-password" placeholder="Current password" value={form.current_password} onChange={(e)=>setForm({...form,current_password:e.target.value})}/><input aria-label="New password" required type="password" autoComplete="new-password" placeholder="New password" value={form.new_password} onChange={(e)=>setForm({...form,new_password:e.target.value})}/><input ref={confirmRef} aria-label="Confirm password" required type="password" autoComplete="new-password" placeholder="Confirm password" value={form.confirm_password} onChange={(e)=>setForm({...form,confirm_password:e.target.value})}/><PasswordChecklist password={form.new_password} username={username} displayName={displayName}/><button className="button button-primary" disabled={submitting}>{submitting ? 'Changing Password' : 'Change Password'}</button></form></div>;
}
