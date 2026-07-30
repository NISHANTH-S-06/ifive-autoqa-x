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
      navigate('/');
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Login failed');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="login-page">
      <div className="login-box">
        <h1>Mock Task Portal</h1>
        <p className="login-subtitle">Local-only task workflow — no real company systems</p>

        {error && <div className="alert alert-error">{error}</div>}

        <form id="login-form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label" htmlFor="username">Username</label>
            <input
              id="username"
              className="form-control"
              type="text"
              value={username}
              onChange={e => setUsername(e.target.value)}
              placeholder="e.g. admin"
              autoFocus
              required
            />
          </div>
          <div className="form-group">
            <label className="form-label" htmlFor="password">Password</label>
            <input
              id="password"
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
            type="submit"
            className="btn btn-primary"
            style={{ width: '100%', justifyContent: 'center' }}
            disabled={loading}
          >
            {loading ? 'Signing in…' : 'Sign In'}
          </button>
        </form>

        <div className="demo-creds">
          <h4>Demo Credentials</h4>
          <table>
            <tbody>
              <tr><td>admin</td><td>Admin@Demo123</td><td>SUPERADMIN</td></tr>
              <tr><td>dev1</td><td>Dev@Demo123</td><td>DEVELOPER</td></tr>
              <tr><td>tester1</td><td>Test@Demo123</td><td>TESTER</td></tr>
              <tr><td>delivery1</td><td>Del@Demo123</td><td>DELIVERY</td></tr>
              <tr><td>viewer1</td><td>View@Demo123</td><td>VIEWER</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
