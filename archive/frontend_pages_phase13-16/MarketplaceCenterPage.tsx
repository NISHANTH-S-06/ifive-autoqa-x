import React, { useEffect, useState } from 'react';
import { fetchMarketplacePlugins, seedMarketplace, installPlugin, uninstallPlugin, fetchMarketplaceCategories, fetchSDKInfo } from '../services/phase13Service';

const card = { background: '#1e293b', borderRadius: '12px', border: '1px solid #334155', padding: '20px' };
const CATEGORY_COLORS: Record<string, string> = { PLUGIN: '#38bdf8', AI_AGENT: '#a78bfa', REPORT: '#10b981', THEME: '#f59e0b', CONNECTOR: '#fb923c', VALIDATOR: '#34d399', EXECUTOR: '#6366f1', EXTENSION: '#f472b6' };
const CATEGORY_ICONS: Record<string, string> = { PLUGIN: '🔌', AI_AGENT: '🤖', REPORT: '📊', THEME: '🎨', CONNECTOR: '🔗', VALIDATOR: '✅', EXECUTOR: '⚡', EXTENSION: '🧩' };

function StarRating({ rating }: { rating: number }) {
  return (
    <span style={{ color: '#f59e0b', fontSize: '12px' }}>
      {'★'.repeat(Math.round(rating))}{'☆'.repeat(5 - Math.round(rating))}
      <span style={{ color: '#64748b', marginLeft: '4px' }}>{rating.toFixed(1)}</span>
    </span>
  );
}

export const MarketplaceCenterPage: React.FC = () => {
  const [plugins, setPlugins] = useState<any[]>([]);
  const [categories, setCategories] = useState<any[]>([]);
  const [sdkInfo, setSdkInfo] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeCategory, setActiveCategory] = useState<string | null>(null);
  const [search, setSearch] = useState('');
  const [activeTab, setActiveTab] = useState<'plugins' | 'sdks'>('plugins');

  const load = async () => {
    setLoading(true);
    try {
      const [p, c, s] = await Promise.all([fetchMarketplacePlugins(activeCategory || undefined, search || undefined), fetchMarketplaceCategories(), fetchSDKInfo()]);
      setPlugins(p as any[]); setCategories(c as any[]); setSdkInfo(s as any[]);
    } catch (e) { console.error(e); } finally { setLoading(false); }
  };

  useEffect(() => { load(); }, [activeCategory, search]);

  const handleSeed = async () => { await seedMarketplace(); load(); };
  const handleInstall = async (pluginId: number) => { await installPlugin(pluginId); load(); };
  const handleUninstall = async (pluginId: number) => { await uninstallPlugin(pluginId); load(); };

  return (
    <div style={{ padding: '24px', maxWidth: '1400px', margin: '0 auto', color: '#f8fafc' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '28px' }}>
        <div>
          <h1 style={{ fontSize: '28px', fontWeight: 800, margin: 0, background: 'linear-gradient(90deg, #a78bfa, #f472b6)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            Marketplace
          </h1>
          <p style={{ margin: '4px 0 0', color: '#64748b', fontSize: '14px' }}>Plugins · AI Agents · Reports · Themes · Connectors · SDKs</p>
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search marketplace..." style={{ padding: '9px 12px', borderRadius: '8px', border: '1px solid #334155', background: '#1e293b', color: '#fff', width: '220px' }} />
          <button onClick={handleSeed} style={{ padding: '10px 18px', borderRadius: '8px', border: 'none', background: 'linear-gradient(135deg, #a78bfa, #7c3aed)', color: '#fff', fontWeight: 700, cursor: 'pointer' }}>⚡ Seed Marketplace</button>
        </div>
      </div>

      {/* Tab Navigation */}
      <div style={{ display: 'flex', gap: '8px', marginBottom: '20px' }}>
        {([['plugins', '🔌 Plugins & Extensions'], ['sdks', '📦 SDKs & APIs']] as [string, string][]).map(([key, label]) => (
          <button key={key} onClick={() => setActiveTab(key as any)} style={{ padding: '8px 18px', borderRadius: '20px', border: `1px solid ${activeTab === key ? '#a78bfa' : '#334155'}`, background: activeTab === key ? '#a78bfa22' : '#1e293b', color: activeTab === key ? '#a78bfa' : '#94a3b8', fontWeight: activeTab === key ? 700 : 400, cursor: 'pointer' }}>
            {label}
          </button>
        ))}
      </div>

      {activeTab === 'plugins' && (
        <>
          {/* Category Filters */}
          <div style={{ display: 'flex', gap: '8px', marginBottom: '20px', flexWrap: 'wrap' }}>
            <button onClick={() => setActiveCategory(null)} style={{ padding: '7px 14px', borderRadius: '20px', border: `1px solid ${!activeCategory ? '#a78bfa' : '#334155'}`, background: !activeCategory ? '#a78bfa22' : '#1e293b', color: !activeCategory ? '#a78bfa' : '#94a3b8', cursor: 'pointer', fontSize: '13px' }}>
              All ({plugins.length})
            </button>
            {categories.map((cat: any) => (
              <button key={cat.category} onClick={() => setActiveCategory(activeCategory === cat.category ? null : cat.category)}
                style={{ padding: '7px 14px', borderRadius: '20px', border: `1px solid ${activeCategory === cat.category ? CATEGORY_COLORS[cat.category] || '#64748b' : '#334155'}`, background: activeCategory === cat.category ? `${CATEGORY_COLORS[cat.category] || '#64748b'}22` : '#1e293b', color: activeCategory === cat.category ? CATEGORY_COLORS[cat.category] || '#fff' : '#94a3b8', cursor: 'pointer', fontSize: '12px' }}>
                {CATEGORY_ICONS[cat.category] || '📦'} {cat.category} ({cat.count})
              </button>
            ))}
          </div>

          {/* Plugin Grid */}
          {loading ? (
            <div style={{ color: '#64748b', textAlign: 'center', padding: '40px' }}>Loading marketplace...</div>
          ) : plugins.length === 0 ? (
            <div style={{ color: '#64748b', textAlign: 'center', padding: '40px' }}>No plugins found. Click "Seed Marketplace" to populate.</div>
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '16px' }}>
              {plugins.map((p: any) => (
                <div key={p.id} style={{ ...card, borderLeft: `3px solid ${CATEGORY_COLORS[p.plugin_category] || '#64748b'}`, transition: 'transform 0.2s ease', cursor: 'default' }}
                  onMouseEnter={e => (e.currentTarget.style.transform = 'translateY(-2px)')}
                  onMouseLeave={e => (e.currentTarget.style.transform = 'translateY(0)')}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '10px' }}>
                    <div>
                      <span style={{ fontSize: '20px', marginRight: '8px' }}>{CATEGORY_ICONS[p.plugin_category] || '📦'}</span>
                      <span style={{ fontWeight: 700, fontSize: '14px' }}>{p.plugin_name}</span>
                    </div>
                    <span style={{ fontSize: '11px', color: CATEGORY_COLORS[p.plugin_category] || '#64748b', background: `${CATEGORY_COLORS[p.plugin_category]}22`, padding: '2px 8px', borderRadius: '4px', fontWeight: 600 }}>{p.plugin_category}</span>
                  </div>
                  <p style={{ fontSize: '12px', color: '#94a3b8', margin: '0 0 10px', lineHeight: '1.5' }}>{p.description}</p>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                    <div>
                      <StarRating rating={p.rating} />
                      <div style={{ fontSize: '11px', color: '#64748b', marginTop: '2px' }}>by {p.author} · v{p.plugin_version} · {p.install_count.toLocaleString()} installs</div>
                    </div>
                  </div>
                  <button
                    onClick={() => p.install_status === 'INSTALLED' ? handleUninstall(p.id) : handleInstall(p.id)}
                    style={{ width: '100%', padding: '8px', borderRadius: '7px', border: 'none', background: p.install_status === 'INSTALLED' ? '#334155' : `linear-gradient(135deg, ${CATEGORY_COLORS[p.plugin_category] || '#6366f1'}, ${CATEGORY_COLORS[p.plugin_category] || '#4f46e5'})`, color: p.install_status === 'INSTALLED' ? '#94a3b8' : '#fff', fontWeight: 700, cursor: 'pointer', fontSize: '13px' }}>
                    {p.install_status === 'INSTALLED' ? '✓ Installed — Uninstall' : '⬇️ Install'}
                  </button>
                </div>
              ))}
            </div>
          )}
        </>
      )}

      {activeTab === 'sdks' && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '16px' }}>
          {sdkInfo.map((sdk: any) => (
            <div key={sdk.language} style={card}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                <h3 style={{ margin: 0, fontSize: '16px', color: '#38bdf8' }}>{sdk.language} SDK</h3>
                <span style={{ fontSize: '12px', color: '#64748b' }}>v{sdk.version}</span>
              </div>
              <div style={{ background: '#0f172a', borderRadius: '6px', padding: '10px 14px', marginBottom: '12px', fontFamily: 'monospace', fontSize: '12px', color: '#10b981' }}>
                $ {sdk.install_command}
              </div>
              <div style={{ background: '#0f172a', borderRadius: '6px', padding: '10px 14px', marginBottom: '12px', fontFamily: 'monospace', fontSize: '11px', color: '#94a3b8', whiteSpace: 'pre' }}>
                {sdk.example_snippet}
              </div>
              <a href={sdk.documentation_url} target="_blank" rel="noopener noreferrer" style={{ color: '#38bdf8', fontSize: '12px', textDecoration: 'none' }}>
                📖 View Documentation →
              </a>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
