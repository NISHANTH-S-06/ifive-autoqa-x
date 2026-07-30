import React, { useEffect, useState } from 'react';
import { Button } from './ui/Button';
import { Input } from './ui/Input';
import { Select } from './ui/Select';
import { FormField } from './ui/FormField';
import { StatusBadge } from './ui/StatusBadge';
import { DataTable, Column } from './ui/DataTable';
import { JSONViewer } from './ui/JSONViewer';
import { 
  ShieldCheck, Plus, Database, Globe, CheckCircle2, 
  AlertTriangle, FileText, Download, Code 
} from 'lucide-react';
import { apiGet, apiPost } from '../services/api';

export function AdvancedValidationCore() {
  const [profiles, setProfiles] = useState<any[]>([]);
  const [activeProfile, setActiveProfile] = useState<any | null>(null);
  const [selectedRun, setSelectedRun] = useState<any | null>(null);
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');

  // Form states
  const [profileName, setProfileName] = useState('');
  const [apiName, setApiName] = useState('');
  const [apiPath, setApiPath] = useState('');
  const [apiMethod, setApiMethod] = useState('GET');
  const [dbName, setDbName] = useState('');
  const [dbProfileRef, setDbProfileRef] = useState('autoqa');
  const [dbQuery, setDbQuery] = useState('SELECT * FROM test_projects LIMIT 5');

  useEffect(() => {
    void fetchProfiles();
  }, []);

  const fetchProfiles = async () => {
    try {
      setLoading(true);
      setError('');
      const data = await apiGet<any[]>('/api/projects/1/advanced-profiles').catch(() => []);
      setProfiles(data);
      if (data.length > 0) {
        await fetchProfileDetail(data[0].id);
      }
    } catch (e: any) {
      setError(e.message || 'Failed to fetch validation profiles');
    } finally {
      setLoading(false);
    }
  };

  const fetchProfileDetail = async (id: number) => {
    try {
      const data = await apiGet<any>(`/api/projects/1/advanced-profiles/${id}`);
      setActiveProfile(data);
    } catch (e) {
      /* ignore */
    }
  };

  const createProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!profileName.trim()) return;
    try {
      await apiPost('/api/projects/1/advanced-profiles', { name: profileName, enabled: true });
      setProfileName('');
      setMessage('Validation profile created.');
      await fetchProfiles();
    } catch (e: any) {
      setError(e.message || 'Failed to create profile');
    }
  };

  const addApiDef = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeProfile || !apiName.trim() || !apiPath.trim()) return;
    try {
      await apiPost(`/api/projects/1/advanced-profiles/${activeProfile.profile.id}/api-definitions`, {
        name: apiName,
        method: apiMethod,
        path: apiPath,
        expected_status: 200,
      });
      setApiName('');
      setApiPath('');
      setMessage('API validation rule added.');
      await fetchProfileDetail(activeProfile.profile.id);
    } catch (e: any) {
      setError(e.message || 'Failed to add API definition');
    }
  };

  const addDbDef = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeProfile || !dbName.trim() || !dbQuery.trim()) return;
    try {
      await apiPost(`/api/projects/1/advanced-profiles/${activeProfile.profile.id}/db-definitions`, {
        name: dbName,
        connection_profile_reference: dbProfileRef,
        query_template: dbQuery,
        max_rows: 50,
      });
      setDbName('');
      setMessage('Read-only DB validation rule added.');
      await fetchProfileDetail(activeProfile.profile.id);
    } catch (e: any) {
      setError(e.message || 'Failed to add DB definition');
    }
  };

  const resultColumns: Column<any>[] = [
    { key: 'validator_type', header: 'Validation Layer', render: (r) => <span style={{ fontWeight: 600, color: 'var(--color-primary)' }}>{r.validator_type}</span> },
    { key: 'status', header: 'Status', render: (r) => <StatusBadge status={r.status} size="sm" /> },
    { key: 'severity', header: 'Severity', render: (r) => <span className="badge badge-draft">{r.severity}</span> },
    { key: 'message', header: 'Details / Assertion Result', render: (r) => <span>{r.message}</span> },
    { key: 'duration_ms', header: 'Duration', render: (r) => <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{r.duration_ms}ms</span> },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      <div>
        <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '0.35rem' }}>
          Advanced Validation Engine & Multi-Layer Assertions
        </h3>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
          Configure API contracts, read-only DB queries, WCAG 2.1 accessibility scans, performance thresholds, and evidence rules.
        </p>
      </div>

      {error && <div className="state-panel state-error" role="alert">{error}</div>}
      {message && <div className="state-panel" role="status">{message}</div>}

      <div className="grid grid-cols-3">
        {/* Left Column: Validation Profiles */}
        <div className="card" style={{ gridColumn: 'span 1' }}>
          <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '1rem' }}>
            Validation Profiles
          </h4>

          <form onSubmit={createProfile} style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginBottom: '1rem' }}>
            <Input
              placeholder="New profile name..."
              value={profileName}
              onChange={(e) => setProfileName(e.target.value)}
            />
            <Button size="sm" variant="primary" type="submit" leftIcon={<Plus size={14} />}>
              Create Profile
            </Button>
          </form>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            {profiles.length === 0 ? (
              <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>No validation profiles registered.</p>
            ) : (
              profiles.map((p) => (
                <div
                  key={p.id}
                  onClick={() => fetchProfileDetail(p.id)}
                  style={{
                    padding: '0.6rem 0.8rem',
                    borderRadius: 'var(--radius-md)',
                    background: activeProfile?.profile.id === p.id ? 'var(--color-primary-light)' : 'var(--bg-card-subtle)',
                    border: '1px solid var(--border-color)',
                    color: 'var(--text-main)',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                  }}
                >
                  <span style={{ fontSize: '0.85rem', fontWeight: 600 }}>{p.name}</span>
                  <StatusBadge status={p.enabled ? 'APPROVED' : 'DRAFT'} label={p.enabled ? 'Active' : 'Disabled'} size="sm" />
                </div>
              ))
            )}
          </div>
        </div>

        {/* Right Column: Active Profile Rules & Definitions */}
        <div className="card" style={{ gridColumn: 'span 2' }}>
          {activeProfile ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
              <div>
                <h4 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-main)' }}>
                  Profile Rules: {activeProfile.profile.name}
                </h4>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                  Project ID: #{activeProfile.profile.project_id}
                </p>
              </div>

              {/* API Validation Rules */}
              <div style={{ padding: '1rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)', background: 'var(--bg-card-subtle)' }}>
                <h5 style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <Globe size={16} style={{ color: 'var(--color-primary)' }} />
                  API Validation Definitions ({activeProfile.api_definitions.length})
                </h5>

                <form onSubmit={addApiDef} className="grid grid-cols-4" style={{ gap: '0.5rem', marginBottom: '0.75rem' }}>
                  <Input placeholder="Rule Name" value={apiName} onChange={(e) => setApiName(e.target.value)} />
                  <Select value={apiMethod} onChange={(e) => setApiMethod(e.target.value)}>
                    <option value="GET">GET</option>
                    <option value="POST">POST</option>
                    <option value="PUT">PUT</option>
                    <option value="DELETE">DELETE</option>
                  </Select>
                  <Input placeholder="/api/health" value={apiPath} onChange={(e) => setApiPath(e.target.value)} />
                  <Button size="sm" variant="primary" type="submit">Add Rule</Button>
                </form>

                {activeProfile.api_definitions.map((d: any) => (
                  <div key={d.id} style={{ fontSize: '0.8rem', padding: '0.35rem 0', borderBottom: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'space-between' }}>
                    <span><strong>{d.method}</strong> {d.path}</span>
                    <span style={{ color: 'var(--text-muted)' }}>Expected: Status {d.expected_status}</span>
                  </div>
                ))}
              </div>

              {/* Read-Only DB Validation Rules */}
              <div style={{ padding: '1rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)', background: 'var(--bg-card-subtle)' }}>
                <h5 style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <Database size={16} style={{ color: 'var(--color-warning)' }} />
                  Read-Only DB Validation Definitions ({activeProfile.db_definitions.length})
                </h5>
                <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.75rem' }}>
                  ⚠️ Security Policy: DB queries are strictly parsed and limited to SELECT / WITH...SELECT statements only.
                </p>

                <form onSubmit={addDbDef} style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', marginBottom: '0.75rem' }}>
                  <div className="grid grid-cols-3" style={{ gap: '0.5rem' }}>
                    <Input placeholder="Check Name" value={dbName} onChange={(e) => setDbName(e.target.value)} />
                    <Select value={dbProfileRef} onChange={(e) => setDbProfileRef(e.target.value)}>
                      <option value="autoqa">autoqa (data/autoqa.db)</option>
                      <option value="demo_product">demo_product</option>
                      <option value="mock_task_portal">mock_task_portal</option>
                    </Select>
                    <Button size="sm" variant="primary" type="submit">Add DB Check</Button>
                  </div>
                  <textarea
                    className="textarea"
                    placeholder="SELECT * FROM table WHERE condition..."
                    value={dbQuery}
                    onChange={(e) => setDbQuery(e.target.value)}
                    style={{ height: '60px', fontFamily: 'var(--font-mono)', fontSize: '0.8rem' }}
                  />
                </form>

                {activeProfile.db_definitions.map((d: any) => (
                  <div key={d.id} style={{ fontSize: '0.8rem', padding: '0.35rem 0', borderBottom: '1px solid var(--border-subtle)' }}>
                    <strong>[{d.connection_profile_reference}]</strong> <code style={{ fontSize: '0.75rem' }}>{d.query_template}</code>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div style={{ textAlign: 'center', padding: '3rem 1rem', color: 'var(--text-muted)' }}>
              Select or create a validation profile to configure rules.
            </div>
          )}
        </div>
      </div>

      {/* Results Detail Table */}
      {selectedRun && (
        <div className="card" style={{ padding: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
            <div>
              <h4 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-main)' }}>
                Validation Results — Run #{selectedRun.id}
              </h4>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                Result Hash: {selectedRun.result_hash || '—'}
              </p>
            </div>
            <StatusBadge status={selectedRun.status} />
          </div>

          <DataTable
            columns={resultColumns}
            data={results}
            keyExtractor={(r) => r.id}
            loading={loading}
            emptyMessage="No validation layer results recorded."
          />
        </div>
      )}
    </div>
  );
}
