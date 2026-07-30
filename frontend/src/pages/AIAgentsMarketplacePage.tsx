import React, { useEffect, useState } from 'react';
import { fetchAgentPackages, seedAIAgents, installAgentPackage } from '../services/phase14Service';

const card = { background: '#1e293b', borderRadius: '12px', border: '1px solid #334155', padding: '20px' };
const badge = (color: string) => ({ padding: '3px 10px', borderRadius: '20px', fontSize: '11px', fontWeight: 700 as const, background: `${color}22`, color, border: `1px solid ${color}44` });
const CATEGORY_COLORS: Record<string, string> = { SECURITY: '#ef4444', ACCESSIBILITY: '#10b981', SAP: '#0078d4', CRM: '#3b82f6', FINANCE: '#fb923c', PERFORMANCE: '#f59e0b', BROWSER: '#a78bfa', DATABASE: '#38bdf8', API: '#818cf8', COMPLIANCE: '#f472b6' };
const CATEGORY_ICONS: Record<string, string> = { SECURITY: '🔒', ACCESSIBILITY: '♿', SAP: '🏢', CRM: '🤝', FINANCE: '💰', PERFORMANCE: '⚡', BROWSER: '🌐', DATABASE: '🗄️', API: '🔗', COMPLIANCE: '🛡️' };

export const AIAgentsMarketplacePage: React.FC = () => {
  const [agents, setAgents] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    try {
      let data: any = await fetchAgentPackages();
      if (data.length === 0) data = await seedAIAgents();
      setAgents(data);
    } catch (e) { console.error(e); } finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const handleInstall = async (id: number) => {
    try {
      await installAgentPackage(id);
      load();
    } catch (err: any) { alert(err.message); }
  };

  return (
    <div style={{ padding: '24px', maxWidth: '1600px', margin: '0 auto', color: '#f8fafc' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '28px' }}>
        <div>
          <h1 style={{ fontSize: '28px', fontWeight: 900, margin: 0, background: 'linear-gradient(90deg, #a78bfa, #f472b6)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            🤖 Enterprise AI Agents Marketplace
          </h1>
          <p style={{ margin: '4px 0 0', color: '#64748b', fontSize: '14px' }}>Install specialized AI agents — Security · A11y · SAP · CRM · Finance · Performance · Browser · DB · API · Compliance</p>
        </div>
        <button onClick={load} style={{ padding: '10px 16px', borderRadius: '8px', border: '1px solid #334155', background: '#1e293b', color: '#94a3b8', cursor: 'pointer' }}>↻</button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))', gap: '20px' }}>
        {agents.map((a: any) => {
          const color = CATEGORY_COLORS[a.agent_category] || '#64748b';
          const icon = CATEGORY_ICONS[a.agent_category] || '🤖';
          const isInstalled = a.install_status === 'INSTALLED';

          return (
            <div key={a.id} style={{ ...card, borderLeft: `4px solid ${color}` }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
                <div>
                  <div style={{ fontSize: '20px', marginBottom: '4px' }}>{icon}</div>
                  <h3 style={{ margin: 0, fontSize: '16px', fontWeight: 700 }}>{a.agent_name}</h3>
                  <div style={{ fontSize: '11px', color: '#64748b', marginTop: '2px' }}>Key: {a.agent_key} · v{a.version}</div>
                </div>
                <span style={badge(color)}>{a.agent_category}</span>
              </div>

              <p style={{ fontSize: '13px', color: '#94a3b8', margin: '0 0 14px', lineHeight: '1.5' }}>{a.description}</p>

              <div style={{ marginBottom: '14px' }}>
                <div style={{ fontSize: '11px', color: '#64748b', textTransform: 'uppercase', marginBottom: '6px' }}>Granted Permissions</div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                  {a.permissions?.map((p: string) => (
                    <span key={p} style={{ fontSize: '10px', background: '#0f172a', color: '#94a3b8', borderRadius: '4px', padding: '2px 6px' }}>{p}</span>
                  ))}
                </div>
              </div>

              <button onClick={() => handleInstall(a.id)}
                style={{ width: '100%', padding: '9px', borderRadius: '8px', border: 'none', background: isInstalled ? '#334155' : `linear-gradient(135deg, ${color}, ${color}dd)`, color: isInstalled ? '#94a3b8' : '#fff', fontWeight: 700, fontSize: '13px', cursor: 'pointer' }}>
                {isInstalled ? '✓ Agent Active' : '⬇️ Install Agent'}
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
};
