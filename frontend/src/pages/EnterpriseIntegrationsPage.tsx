import React, { useEffect, useState } from 'react';
import { PageHeader } from '../components/layout/PageHeader';
import { StatCard } from '../components/ui/StatCard';
import { StatusBadge } from '../components/ui/StatusBadge';
import { Button } from '../components/ui/Button';
import { Globe, Plus, CheckCircle2, RefreshCw, MessageSquare, Zap } from 'lucide-react';
import { apiGet, apiPost } from '../services/api';
import { toast } from '../stores/toastStore';

interface Integration {
  id: number;
  integration_type: string;
  integration_name: string;
  is_active: boolean;
  last_sync_at: string | null;
}

const INTEGRATION_CATEGORIES = [
  { label: 'Issue Trackers', items: ['JIRA', 'AZURE_DEVOPS', 'GITHUB', 'GITLAB', 'CLICKUP', 'LINEAR'] },
  { label: 'Notifications', items: ['SLACK', 'TEAMS', 'EMAIL', 'WEBHOOK'] },
  { label: 'ITSM', items: ['SERVICENOW', 'FRESHSERVICE'] },
  { label: 'Enterprise Systems', items: ['SAP', 'SALESFORCE', 'ERP', 'CRM', 'HRMS'] },
];

const INTEGRATION_COLORS: Record<string, string> = {
  JIRA: '#0052CC', SLACK: '#4A154B', TEAMS: '#6264A7', GITHUB: '#333',
  GITLAB: '#FC6D26', AZURE_DEVOPS: '#0078D7', SAP: '#0FAAFF', SALESFORCE: '#00A1E0',
  SERVICENOW: '#81B5A1', FRESHSERVICE: '#0DB34F', EMAIL: '#f59e0b',
  WEBHOOK: '#6366f1', CLICKUP: '#7B68EE', LINEAR: '#5E6AD2',
  BITBUCKET: '#2684FF', ERP: '#ef4444', CRM: '#10b981', HRMS: '#8b5cf6',
};

export function EnterpriseIntegrationsPage() {
  const [integrations, setIntegrations] = useState<Integration[]>([]);
  const [copilotInput, setCopilotInput] = useState('');
  const [copilotResponse, setCopilotResponse] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [copilotLoading, setCopilotLoading] = useState(false);

  const fetchIntegrations = async () => {
    setLoading(true);
    try {
      const res = await apiGet<Integration[]>('/api/integrations/?project_id=1');
      setIntegrations(res);
    } catch (err) {
      toast.error('Failed to load integrations');
    } finally {
      setLoading(false);
    }
  };

  const handleTestConnection = async (id: number, name: string) => {
    try {
      const res = await apiPost<any>(`/api/integrations/${id}/test`, {});
      toast.success(`${name}: ${res.message}`);
    } catch (err: any) {
      toast.error(err.message || 'Connection test failed');
    }
  };

  const handleCopilotCommand = async () => {
    if (!copilotInput.trim()) return;
    setCopilotLoading(true);
    try {
      const res = await apiPost<any>('/api/integrations/copilot-v4/command', { command: copilotInput });
      setCopilotResponse(res);
    } catch (err: any) {
      toast.error('Copilot V4 command failed');
    } finally {
      setCopilotLoading(false);
    }
  };

  useEffect(() => {
    void fetchIntegrations();
  }, []);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      <PageHeader
        breadcrumbs={[{ label: 'Zero-Code Ecosystem' }, { label: 'Enterprise Integrations' }]}
        title="Enterprise Integrations & AI Copilot V4"
        description="Connect to Jira, Azure DevOps, GitHub, Slack, Teams, ServiceNow, SAP, Salesforce, and 14 more enterprise platforms."
        actions={
          <Button size="sm" variant="secondary" onClick={() => void fetchIntegrations()} isLoading={loading} leftIcon={<RefreshCw size={14} />}>
            Refresh
          </Button>
        }
      />

      <div className="grid grid-cols-4">
        <StatCard title="Active Integrations" value={integrations.filter(i => i.is_active).length} subtitle="Connected Platforms" icon={Globe} variant="primary" />
        <StatCard title="Total Supported" value={18} subtitle="Enterprise Platforms" icon={CheckCircle2} variant="success" />
        <StatCard title="AI Copilot V4" value="Active" subtitle="Natural Language Commands" icon={MessageSquare} variant="info" />
        <StatCard title="Real-time Sync" value="Enabled" subtitle="Bi-directional" icon={Zap} variant="warning" />
      </div>

      {/* AI Copilot V4 Panel */}
      <div className="card" style={{ padding: '1.25rem', borderLeft: '4px solid var(--color-primary)' }}>
        <h3 style={{ margin: '0 0 0.75rem 0', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <MessageSquare size={18} color="var(--color-primary)" /> AI Executive Copilot V4
        </h3>
        <p style={{ margin: '0 0 1rem 0', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
          Natural language commands: "Connect my ERP", "Generate tests", "Run regression", "Explain failures", "Show release status", "Generate RCA"
        </p>
        <div style={{ display: 'flex', gap: '0.75rem' }}>
          <input
            value={copilotInput}
            onChange={e => setCopilotInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && void handleCopilotCommand()}
            placeholder='Try: "Generate tests" or "Show release status" or "Explain failures"'
            style={{
              flex: 1, padding: '0.7rem 1rem',
              background: 'var(--bg-muted)', border: '1px solid var(--border-color)',
              borderRadius: 8, color: 'var(--text-primary)', fontSize: '0.9rem',
            }}
          />
          <Button variant="primary" onClick={() => void handleCopilotCommand()} isLoading={copilotLoading}>
            Send
          </Button>
        </div>
        {copilotResponse && (
          <div style={{ marginTop: '1rem', background: 'var(--bg-muted)', padding: '1rem', borderRadius: 8 }}>
            <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center', marginBottom: '0.5rem' }}>
              <StatusBadge status="APPROVED" label={`Intent: ${copilotResponse.resolved_intent}`} size="sm" />
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Confidence: {(copilotResponse.confidence * 100).toFixed(0)}%</span>
            </div>
            <p style={{ margin: 0, fontSize: '0.9rem' }}>{copilotResponse.response}</p>
            {copilotResponse.suggestions && (
              <div style={{ marginTop: '0.75rem', display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                {copilotResponse.suggestions.map((s: string) => (
                  <span
                    key={s}
                    onClick={() => { setCopilotInput(s); }}
                    style={{
                      background: 'rgba(var(--color-primary-rgb,99,102,241),0.1)', color: 'var(--color-primary)',
                      borderRadius: 6, padding: '0.2rem 0.6rem', fontSize: '0.75rem', cursor: 'pointer',
                    }}
                  >
                    {s}
                  </span>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Integration Categories */}
      {INTEGRATION_CATEGORIES.map(category => (
        <div key={category.label} className="card" style={{ padding: '1.25rem' }}>
          <h4 style={{ margin: '0 0 0.75rem 0', color: 'var(--text-muted)', fontSize: '0.85rem', fontWeight: 700, textTransform: 'uppercase' }}>
            {category.label}
          </h4>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.6rem' }}>
            {category.items.map(item => {
              const config = integrations.find(i => i.integration_type === item);
              return (
                <div
                  key={item}
                  style={{
                    display: 'flex', alignItems: 'center', gap: '0.5rem',
                    padding: '0.6rem 1rem', borderRadius: 8,
                    border: `1px solid ${config?.is_active ? '#10b981' : 'var(--border-color)'}`,
                    background: config?.is_active ? 'rgba(16,185,129,0.06)' : 'var(--bg-muted)',
                  }}
                >
                  <div style={{ width: 10, height: 10, borderRadius: '50%', background: INTEGRATION_COLORS[item] || '#6366f1' }} />
                  <span style={{ fontWeight: 600, fontSize: '0.82rem' }}>{item.replace('_', ' ')}</span>
                  {config?.is_active && <CheckCircle2 size={14} color="#10b981" />}
                </div>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
}
