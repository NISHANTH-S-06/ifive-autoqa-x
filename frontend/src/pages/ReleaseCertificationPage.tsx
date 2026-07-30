import React, { useEffect, useState } from 'react';
import { certifyRelease, fetchCertificationsHistory } from '../services/phase16Service';

const card = { background: '#1e293b', borderRadius: '12px', border: '1px solid #334155', padding: '20px' };
const badge = (color: string) => ({ padding: '3px 10px', borderRadius: '20px', fontSize: '11px', fontWeight: 700 as const, background: `${color}22`, color, border: `1px solid ${color}44` });

export const ReleaseCertificationPage: React.FC = () => {
  const [certs, setCerts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    try {
      const data: any = await fetchCertificationsHistory();
      setCerts(data);
    } catch (e) { console.error(e); } finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const handleCertify = async () => {
    try {
      await certifyRelease('v5.1.0-RC1');
      load();
    } catch (e) { console.error(e); }
  };

  return (
    <div style={{ padding: '24px', maxWidth: '1600px', margin: '0 auto', color: '#f8fafc' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '28px' }}>
        <div>
          <h1 style={{ fontSize: '28px', fontWeight: 900, margin: 0, background: 'linear-gradient(90deg, #10b981, #34d399)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            🎓 Autonomous Release Certification
          </h1>
          <p style={{ margin: '4px 0 0', color: '#64748b', fontSize: '14px' }}>CERTIFIED · CONDITIONALLY_CERTIFIED · REJECTED Status Engine</p>
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button onClick={handleCertify} style={{ padding: '10px 18px', borderRadius: '8px', border: 'none', background: 'linear-gradient(135deg, #10b981, #059669)', color: '#fff', fontWeight: 700, cursor: 'pointer' }}>
            ⚡ Certify v5.1.0-RC1
          </button>
          <button onClick={load} style={{ padding: '10px 16px', borderRadius: '8px', border: '1px solid #334155', background: '#1e293b', color: '#94a3b8', cursor: 'pointer' }}>↻</button>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(380px, 1fr))', gap: '20px' }}>
        {certs.map((c: any) => {
          const color = c.certification_status === 'CERTIFIED' ? '#10b981' : c.certification_status === 'CONDITIONALLY_CERTIFIED' ? '#f59e0b' : '#ef4444';

          return (
            <div key={c.id} style={{ ...card, borderTop: `4px solid ${color}` }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
                <span style={{ fontSize: '18px', fontWeight: 900, color: '#fff' }}>{c.release_version}</span>
                <span style={badge(color)}>{c.certification_status}</span>
              </div>

              <div style={{ fontSize: '32px', fontWeight: 900, color, marginBottom: '12px' }}>{c.overall_quality_score}%</div>
              <p style={{ fontSize: '13px', color: '#94a3b8', marginBottom: '16px' }}>{c.report_summary}</p>

              {/* Breakdown */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', background: '#0f172a', padding: '12px', borderRadius: '8px', fontSize: '12px' }}>
                <div>QA Score: <strong style={{ color: '#fff' }}>{c.scores.qa}%</strong></div>
                <div>Security: <strong style={{ color: '#fff' }}>{c.scores.security}%</strong></div>
                <div>Performance: <strong style={{ color: '#fff' }}>{c.scores.performance}%</strong></div>
                <div>Compliance: <strong style={{ color: '#fff' }}>{c.scores.compliance}%</strong></div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
