import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../AuthContext';

export default function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(username, password);
      navigate('/dashboard');
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Login failed');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="login-page">
      <div className="login-box">
        <h1 style={{ fontSize: 20, color: 'var(--primary)', marginBottom: 6 }}>Demo ERP System</h1>
        <p style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 20 }}>
          Local target website for AutoQA testing
        </p>

        {error && <div className="alert alert-error">{error}</div>}

        <form id="login-form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label" htmlFor="username">Username</label>
            <input
              id="username"
              data-testid="login-username"
              className="form-control"
              type="text"
              value={username}
              onChange={e => setUsername(e.target.value)}
              placeholder="e.g. demo_admin"
              autoFocus
              required
            />
          </div>
          <div className="form-group">
            <label className="form-label" htmlFor="password">Password</label>
            <input
              id="password"
              data-testid="login-password"
              className="form-control"
              type="password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              placeholder="Password"
              required
            />
          </div>
          <button
            id="login-submit"
            data-testid="login-submit"
            type="submit"
            className="btn btn-primary"
            style={{ width: '100%' }}
            disabled={loading}
          >
            {loading ? 'Signing in…' : 'Sign In'}
          </button>
        </form>

        <div style={{ marginTop: 24, paddingTop: 16, borderTop: '1px solid var(--border)', fontSize: 11, color: 'var(--text-muted)' }}>
          <strong style={{ color: 'var(--text)', display: 'block', marginBottom: 6 }}>Demo Fixture Accounts:</strong>
          <table style={{ width: '100%', fontSize: 11 }}>
            <tbody>
              <tr><td>demo_admin</td><td>Admin@Demo123</td><td>ADMIN</td></tr>
              <tr><td>demo_hr_user</td><td>Hr@Demo123</td><td>HR</td></tr>
              <tr><td>demo_inventory_user</td><td>Inv@Demo123</td><td>Inventory</td></tr>
              <tr><td>demo_viewer</td><td>View@Demo123</td><td>Viewer</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
