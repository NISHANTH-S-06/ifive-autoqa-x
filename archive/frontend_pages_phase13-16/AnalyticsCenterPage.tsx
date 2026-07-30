import React, { useEffect, useState } from 'react';
import {
  fetchAnalyticsKPIs, fetchQualityTrends, fetchReleaseTrends, fetchDeveloperQuality,
  fetchFailureHeatmap, fetchFlakyTests, fetchBrowserStats, fetchCostAnalytics,
} from '../services/phase13Service';

const card = { background: '#1e293b', borderRadius: '12px', border: '1px solid #334155', padding: '20px' };
const BROWSER_COLORS: Record<string, string> = { CHROMIUM: '#38bdf8', FIREFOX: '#f97316', WEBKIT: '#8b5cf6', EDGE: '#3b82f6', CHROME: '#22c55e', MOBILE_CHROME: '#a78bfa', MOBILE_SAFARI: '#64748b' };

export const AnalyticsCenterPage: React.FC = () => {
  const [kpis, setKpis] = useState<any>({});
  const [qualityTrends, setQualityTrends] = useState<any[]>([]);
  const [releaseTrends, setReleaseTrends] = useState<any[]>([]);
  const [devQuality, setDevQuality] = useState<any[]>([]);
  const [heatmap, setHeatmap] = useState<any[]>([]);
  const [flaky, setFlaky] = useState<any[]>([]);
  const [browserStats, setBrowserStats] = useState<any[]>([]);
  const [costData, setCostData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('quality');

  const load = async () => {
    setLoading(true);
    try {
      const [k, qt, rt, dq, hm, fl, bs, ca] = await Promise.all([
        fetchAnalyticsKPIs(), fetchQualityTrends(), fetchReleaseTrends(),
        fetchDeveloperQuality(), fetchFailureHeatmap(), fetchFlakyTests(),
        fetchBrowserStats(), fetchCostAnalytics(),
      ]);
      setKpis(k); setQualityTrends(qt as any[]); setReleaseTrends(rt as any[]);
      setDevQuality(dq as any[]); setHeatmap(hm as any[]); setFlaky(fl as any[]);
      setBrowserStats(bs as any[]); setCostData(ca as any[]);
    } catch (e) { console.error(e); } finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const tabs = [
    { key: 'quality', label: '📈 Quality Trends' },
    { key: 'release', label: '🚀 Release Trends' },
    { key: 'developer', label: '👤 Developer Quality' },
    { key: 'heatmap', label: '🔥 Failure Heatmap' },
    { key: 'flaky', label: '⚡ Flaky Tests' },
    { key: 'browsers', label: '🌐 Browser Stats' },
    { key: 'cost', label: '💰 Cost Analytics' },
  ];

  const qSnap = qualityTrends[0];
  const qData = qSnap?.data || {};
  const rSnap = releaseTrends[0];
  const rData = rSnap?.data || {};
  const dSnap = devQuality[0];
  const hmSnap = heatmap[0];
  const flSnap = flaky[0];
  const bsSnap = browserStats[0];
  const caSnap = costData[0];

  const ScoreBar = ({ value, color }: { value: number; color: string }) => (
    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
      <div style={{ flex: 1, height: '6px', background: '#0f172a', borderRadius: '3px' }}>
        <div style={{ height: '100%', width: `${Math.min(value, 100)}%`, background: color, borderRadius: '3px', transition: 'width 0.5s ease' }} />
      </div>
      <span style={{ fontSize: '12px', color, fontWeight: 700, minWidth: '40px' }}>{value.toFixed(1)}%</span>
    </div>
  );

  return (
    <div style={{ padding: '24px', maxWidth: '1400px', margin: '0 auto', color: '#f8fafc' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '28px' }}>
        <div>
          <h1 style={{ fontSize: '28px', fontWeight: 800, margin: 0, background: 'linear-gradient(90deg, #6366f1, #a78bfa, #38bdf8)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            Analytics Center
          </h1>
          <p style={{ margin: '4px 0 0', color: '#64748b', fontSize: '14px' }}>Enterprise AI quality analytics — trends, heatmaps, developer quality</p>
        </div>
        <button onClick={load} style={{ padding: '10px 16px', borderRadius: '8px', border: '1px solid #334155', background: '#1e293b', color: '#94a3b8', cursor: 'pointer' }}>↻ Refresh</button>
      </div>

      {/* KPI Summary */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: '16px', marginBottom: '24px' }}>
        {Object.entries(kpis).slice(0, 6).map(([type, snap]: [string, any]) => (
          <div key={type} style={{ ...card, textAlign: 'center' }}>
            <div style={{ fontSize: '10px', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.04em', marginBottom: '6px' }}>{type.replace(/_/g, ' ')}</div>
            <div style={{ fontSize: '24px', fontWeight: 800, color: '#10b981' }}>{snap?.quality_score?.toFixed(1) ?? '—'}%</div>
          </div>
        ))}
      </div>

      {/* Tab navigation */}
      <div style={{ display: 'flex', gap: '8px', marginBottom: '20px', flexWrap: 'wrap' }}>
        {tabs.map(t => (
          <button key={t.key} onClick={() => setActiveTab(t.key)} style={{ padding: '8px 16px', borderRadius: '20px', border: `1px solid ${activeTab === t.key ? '#6366f1' : '#334155'}`, background: activeTab === t.key ? '#6366f122' : '#1e293b', color: activeTab === t.key ? '#a78bfa' : '#94a3b8', fontWeight: activeTab === t.key ? 700 : 400, cursor: 'pointer', fontSize: '13px' }}>
            {t.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div style={card}>
        {activeTab === 'quality' && qSnap && (
          <div>
            <h3 style={{ margin: '0 0 16px', color: '#10b981' }}>Quality Trend Analysis</h3>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
              <div>
                <div style={{ marginBottom: '12px' }}>
                  <div style={{ fontSize: '12px', color: '#64748b', marginBottom: '6px' }}>Quality Score</div>
                  <ScoreBar value={qSnap.quality_score} color="#10b981" />
                </div>
                <div style={{ marginBottom: '12px' }}>
                  <div style={{ fontSize: '12px', color: '#64748b', marginBottom: '6px' }}>Pass Rate</div>
                  <ScoreBar value={qSnap.pass_rate} color="#38bdf8" />
                </div>
                <div>
                  <div style={{ fontSize: '12px', color: '#64748b', marginBottom: '6px' }}>Coverage</div>
                  <ScoreBar value={qSnap.coverage_pct} color="#a78bfa" />
                </div>
              </div>
              {qData.weeks && (
                <div>
                  <div style={{ fontSize: '12px', color: '#64748b', marginBottom: '10px' }}>Weekly Trend ({qData.trend})</div>
                  <div style={{ display: 'flex', alignItems: 'flex-end', gap: '8px', height: '80px' }}>
                    {qData.scores?.map((score: number, i: number) => (
                      <div key={i} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '4px' }}>
                        <span style={{ fontSize: '10px', color: '#10b981' }}>{score}%</span>
                        <div style={{ width: '100%', height: `${(score / 100) * 60}px`, background: 'linear-gradient(180deg, #10b981, #064e3b)', borderRadius: '4px 4px 0 0' }} />
                        <span style={{ fontSize: '10px', color: '#64748b' }}>{qData.weeks[i]}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'developer' && dSnap && (
          <div>
            <h3 style={{ margin: '0 0 16px', color: '#a78bfa' }}>Developer Quality Scoreboard</h3>
            {(dSnap.data?.developers || []).map((dev: any, i: number) => (
              <div key={i} style={{ background: '#0f172a', borderRadius: '8px', padding: '14px', marginBottom: '10px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <div style={{ fontWeight: 700 }}>{dev.name}</div>
                  <div style={{ fontSize: '12px', color: '#64748b', marginTop: '2px' }}>Defects introduced: <span style={{ color: dev.defects_introduced > 5 ? '#ef4444' : '#10b981' }}>{dev.defects_introduced}</span></div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontSize: '24px', fontWeight: 800, color: dev.quality_score >= 90 ? '#10b981' : dev.quality_score >= 80 ? '#f59e0b' : '#ef4444' }}>{dev.quality_score}%</div>
                  <div style={{ fontSize: '11px', color: '#64748b' }}>quality score</div>
                </div>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'heatmap' && hmSnap && (
          <div>
            <h3 style={{ margin: '0 0 16px', color: '#ef4444' }}>Failure Heatmap</h3>
            {hmSnap.data?.modules && (
              <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                {hmSnap.data.modules.map((mod: string, i: number) => {
                  const cnt = hmSnap.data.failure_counts[i] || 0;
                  const intensity = Math.min(cnt / 15, 1);
                  const r = Math.round(30 + intensity * 225);
                  const g = Math.round(120 - intensity * 80);
                  const b = Math.round(80 - intensity * 60);
                  return (
                    <div key={mod} style={{ background: `rgb(${r},${g},${b})22`, border: `1px solid rgb(${r},${g},${b})44`, borderRadius: '10px', padding: '16px 24px', textAlign: 'center' }}>
                      <div style={{ fontWeight: 700, marginBottom: '6px' }}>{mod}</div>
                      <div style={{ fontSize: '28px', fontWeight: 800, color: `rgb(${r},${g},${b})` }}>{cnt}</div>
                      <div style={{ fontSize: '11px', color: '#64748b' }}>failures</div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}

        {activeTab === 'flaky' && flSnap && (
          <div>
            <h3 style={{ margin: '0 0 16px', color: '#f59e0b' }}>Flaky Test Detection</h3>
            <div style={{ marginBottom: '12px', fontSize: '13px', color: '#64748b' }}>Total flaky count: <span style={{ color: '#f59e0b', fontWeight: 700 }}>{flSnap.flaky_count}</span></div>
            {(flSnap.data?.tests || []).map((t: any, i: number) => (
              <div key={i} style={{ background: '#0f172a', borderRadius: '8px', padding: '12px 16px', marginBottom: '8px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontWeight: 600 }}>⚡ {t.test_name}</span>
                <div>
                  <span style={{ fontSize: '18px', fontWeight: 800, color: t.flakiness_pct > 12 ? '#ef4444' : '#f59e0b' }}>{t.flakiness_pct}%</span>
                  <span style={{ fontSize: '11px', color: '#64748b', marginLeft: '4px' }}>flaky</span>
                </div>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'browsers' && bsSnap && (
          <div>
            <h3 style={{ margin: '0 0 16px', color: '#38bdf8' }}>Browser Execution Stats</h3>
            {bsSnap.data?.browsers && Object.entries(bsSnap.data.browsers as Record<string, any>).map(([browser, stats]) => (
              <div key={browser} style={{ marginBottom: '16px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                  <span style={{ fontWeight: 700, color: BROWSER_COLORS[browser] || '#fff' }}>{browser}</span>
                  <span style={{ fontSize: '12px', color: '#64748b' }}>{stats.runs} runs · {stats.pass_rate}% pass</span>
                </div>
                <ScoreBar value={stats.pass_rate} color={BROWSER_COLORS[browser] || '#38bdf8'} />
              </div>
            ))}
          </div>
        )}

        {activeTab === 'cost' && caSnap && (
          <div>
            <h3 style={{ margin: '0 0 16px', color: '#fb923c' }}>Cost Analytics</h3>
            <div style={{ fontSize: '36px', fontWeight: 800, color: '#fb923c', marginBottom: '20px' }}>${caSnap.cost_usd.toFixed(2)} USD</div>
            {caSnap.data?.breakdown && Object.entries(caSnap.data.breakdown as Record<string, number>).map(([b, v]) => (
              <div key={b} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                <span style={{ color: BROWSER_COLORS[b] || '#94a3b8', fontWeight: 600 }}>{b}</span>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <div style={{ width: '120px', height: '6px', background: '#0f172a', borderRadius: '3px' }}>
                    <div style={{ height: '100%', width: `${(v / caSnap.cost_usd) * 100}%`, background: BROWSER_COLORS[b] || '#fb923c', borderRadius: '3px' }} />
                  </div>
                  <span style={{ color: '#fb923c', fontWeight: 700, minWidth: '60px', textAlign: 'right' }}>${v.toFixed(2)}</span>
                </div>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'release' && rSnap && (
          <div>
            <h3 style={{ margin: '0 0 16px', color: '#34d399' }}>Release Quality Trends</h3>
            <div style={{ marginBottom: '12px' }}><ScoreBar value={rSnap.pass_rate} color="#34d399" /></div>
            {rData.releases && (
              <div style={{ display: 'flex', gap: '8px', alignItems: 'flex-end', height: '100px', marginTop: '16px' }}>
                {rData.releases.map((rel: string, i: number) => (
                  <div key={rel} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '4px' }}>
                    <span style={{ fontSize: '10px', color: '#34d399' }}>{rData.pass_rates?.[i]}%</span>
                    <div style={{ width: '100%', height: `${(rData.pass_rates?.[i] / 100) * 70}px`, background: 'linear-gradient(180deg, #34d399, #064e3b)', borderRadius: '4px 4px 0 0' }} />
                    <span style={{ fontSize: '10px', color: '#64748b' }}>{rel}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
