import React, { useEffect, useState } from 'react';
import { PageHeader } from '../components/layout/PageHeader';
import { StatCard } from '../components/ui/StatCard';
import { StatusBadge } from '../components/ui/StatusBadge';
import { Button } from '../components/ui/Button';
import { Package, Download, Trash2, RefreshCw, ShieldCheck, BarChart3, Zap, Globe } from 'lucide-react';
import { apiGet, apiPost } from '../services/api';
import { toast } from '../stores/toastStore';

interface Plugin {
  id: number;
  package_name: string;
  version: string;
  plugin_type: string;
  author: string;
  description: string;
  is_installed: boolean;
}

const TYPE_COLORS: Record<string, string> = {
  INTEGRATION: '#6366f1', VALIDATOR: '#10b981', REPORT: '#f59e0b',
  BROWSER_ACTION: '#3b82f6', AI_AGENT: '#8b5cf6', EXTENSION: '#ec4899',
};

export function PluginMarketplacePage() {
  const [plugins, setPlugins] = useState<Plugin[]>([]);
  const [loading, setLoading] = useState(false);
  const [actionId, setActionId] = useState<number | null>(null);

  const fetchPlugins = async () => {
    setLoading(true);
    try {
      const res = await apiGet<Plugin[]>('/api/plugins/');
      setPlugins(res);
    } catch (err) {
      toast.error('Failed to load Plugin Marketplace');
    } finally {
      setLoading(false);
    }
  };

  const handleInstall = async (id: number, name: string) => {
    setActionId(id);
    try {
      await apiPost(`/api/plugins/${id}/install`, {});
      toast.success(`${name} installed successfully!`);
      void fetchPlugins();
    } catch (err: any) {
      toast.error(err.message || 'Install failed');
    } finally {
      setActionId(null);
    }
  };

  const handleUninstall = async (id: number, name: string) => {
    setActionId(id);
    try {
      await apiPost(`/api/plugins/${id}/uninstall`, {});
      toast.success(`${name} uninstalled.`);
      void fetchPlugins();
    } catch (err: any) {
      toast.error(err.message || 'Uninstall failed');
    } finally {
      setActionId(null);
    }
  };

  useEffect(() => {
    void fetchPlugins();
  }, []);

  const installedCount = plugins.filter(p => p.is_installed).length;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      <PageHeader
        breadcrumbs={[{ label: 'Zero-Code Ecosystem' }, { label: 'Plugin Marketplace' }]}
        title="Enterprise Plugin Marketplace"
        description="SDK extensions for custom validators, AI agents, reports, browser actions, integrations, and company-specific enterprise extensions."
        actions={
          <Button size="sm" variant="secondary" onClick={() => void fetchPlugins()} isLoading={loading} leftIcon={<RefreshCw size={14} />}>
            Refresh
          </Button>
        }
      />

      <div className="grid grid-cols-4">
        <StatCard title="Available Plugins" value={plugins.length} subtitle="Marketplace Packages" icon={Package} variant="primary" />
        <StatCard title="Installed" value={installedCount} subtitle="Active Extensions" icon={ShieldCheck} variant="success" />
        <StatCard title="Plugin Types" value={6} subtitle="Categories" icon={BarChart3} variant="info" />
        <StatCard title="Enterprise SDK" value="Open" subtitle="Custom Extension Support" icon={Zap} variant="warning" />
      </div>

      <div className="card" style={{ padding: '1.25rem' }}>
        <h3 style={{ margin: '0 0 1rem 0' }}>Plugin Registry</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '0.75rem' }}>
          {plugins.map(plugin => (
            <div
              key={plugin.id}
              style={{
                background: 'var(--bg-muted)', padding: '1.25rem', borderRadius: 10,
                border: `1px solid ${plugin.is_installed ? '#10b981' : 'var(--border-color)'}`,
                display: 'flex', flexDirection: 'column', gap: '0.5rem',
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <div style={{ fontWeight: 700, fontSize: '0.9rem' }}>{plugin.package_name}</div>
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>v{plugin.version} · by {plugin.author}</div>
                </div>
                <div style={{ display: 'flex', gap: '0.4rem', flexShrink: 0 }}>
                  <span style={{
                    background: `${TYPE_COLORS[plugin.plugin_type] || '#6366f1'}1A`,
                    color: TYPE_COLORS[plugin.plugin_type] || '#6366f1',
                    borderRadius: 6, padding: '0.2rem 0.6rem', fontSize: '0.7rem', fontWeight: 700,
                  }}>
                    {plugin.plugin_type}
                  </span>
                </div>
              </div>
              <p style={{ margin: 0, fontSize: '0.8rem', color: 'var(--text-muted)' }}>{plugin.description}</p>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <StatusBadge status={plugin.is_installed ? 'APPROVED' : 'WARNING'} label={plugin.is_installed ? 'Installed' : 'Available'} size="sm" />
                {plugin.is_installed ? (
                  <Button size="sm" variant="secondary" onClick={() => void handleUninstall(plugin.id, plugin.package_name)} isLoading={actionId === plugin.id} leftIcon={<Trash2 size={12} />}>
                    Uninstall
                  </Button>
                ) : (
                  <Button size="sm" variant="primary" onClick={() => void handleInstall(plugin.id, plugin.package_name)} isLoading={actionId === plugin.id} leftIcon={<Download size={12} />}>
                    Install
                  </Button>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
