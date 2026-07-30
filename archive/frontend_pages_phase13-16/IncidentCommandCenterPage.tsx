import React, { useEffect, useState } from 'react';
import { fetchIncidents, triggerIncident, resolveIncident } from '../services/phase14Service';

const card = { background: '#1e293b', borderRadius: '12px', border: '1px solid #334155', padding: '20px' };
const badge = (color: string) => ({ padding: '3px 10px', borderRadius: '20px', fontSize: '11px', fontWeight: 700 as const, background: `${color}22`, color, border: `1px solid ${color}44` });
const SEV_COLORS: Record<string, string> = { 'SEV-1': '#ef4444', 'SEV-2': '#f97316', 'SEV-3': '#f59e0b', 'SEV-4': '#38bdf8' };

export const IncidentCommandCenterPage: React.FC = () => {
  const [incidents, setIncidents] = useState<any[]>([]);
  const [selectedIncident, setSelectedIncident] = useState<any>(null);
  const [showTriggerModal, setShowTriggerModal] = useState(false);
  const [triggerForm, setTriggerForm] = useState({ title: '', severity: 'SEV-2' });
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    try {
      const data: any = await fetchIncidents();
      setIncidents(data);
      if (data.length > 0 && !selectedIncident) setSelectedIncident(data[0]);
    } catch (e) { console.error(e); } finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const handleTrigger = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const inc: any = await triggerIncident(triggerForm);
      setShowTriggerModal(false);
      setSelectedIncident(inc);
      load();
    } catch (err: any) { alert(err.message); }
  };

  const handleResolve = async (id: number) => {
    const summary = prompt('Resolution Summary:', 'Connection pool parameters tuned and hotfix deployed.');
    if (!summary) return;
    try {
      await resolveIncident(id, summary);
      load();
    } catch (err: any) { alert(err.message); }
  };

  return (
    <div style={{ padding: '24px', maxWidth: '1600px', margin: '0 auto', color: '#f8fafc' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '28px' }}>
        <div>
          <h1 style={{ fontSize: '28px', fontWeight: 900, margin: 0, background: 'linear-gradient(90deg, #ef4444, #f97316)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            🚨 Autonomous Incident Commander
          </h1>
          <p style={{ margin: '4px 0 0', color: '#64748b', fontSize: '14px' }}>Real-time incident response, automatic team routing, timeline generation & AI root cause resolution</p>
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button onClick={() => setShowTriggerModal(true)} style={{ padding: '10px 18px', borderRadius: '8px', border: 'none', background: 'linear-gradient(135deg, #ef4444, #dc2626)', color: '#fff', fontWeight: 700, cursor: 'pointer' }}>
            + Trigger Test Incident
          </button>
          <button onClick={load} style={{ padding: '10px 16px', borderRadius: '8px', border: '1px solid #334155', background: '#1e293b', color: '#94a3b8', cursor: 'pointer' }}>↻</button>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '380px 1fr', gap: '20px' }}>
        {/* Incident List */}
        <div style={card}>
          <h3 style={{ margin: '0 0 16px', fontSize: '16px', fontWeight: 700, color: '#ef4444' }}>Incidents ({incidents.length})</h3>
          {incidents.length === 0 ? <div style={{ color: '#64748b' }}>No incidents recorded</div> : (
            <div style={{ maxHeight: '550px', overflowY: 'auto' }}>
              {incidents.map(i => (
                <div key={i.id} onClick={() => setSelectedIncident(i)}
                  style={{ background: selectedIncident?.id === i.id ? '#0f172a' : '#1e293b', border: `1px solid ${selectedIncident?.id === i.id ? SEV_COLORS[i.severity] || '#ef4444' : '#334155'}`, borderRadius: '10px', padding: '12px 14px', marginBottom: '10px', cursor: 'pointer' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                    <span style={{ fontFamily: 'monospace', fontWeight: 700, color: SEV_COLORS[i.severity] || '#ef4444', fontSize: '12px' }}>{i.incident_number}</span>
                    <span style={badge(SEV_COLORS[i.severity] || '#ef4444')}>{i.severity}</span>
                  </div>
                  <div style={{ fontWeight: 700, fontSize: '13px', marginBottom: '6px' }}>{i.title}</div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontSize: '11px', color: '#64748b' }}>{i.assigned_team}</span>
                    <span style={badge(i.incident_status === 'RESOLVED' ? '#10b981' : '#f59e0b')}>{i.incident_status}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Selected Incident View */}
        {selectedIncident && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <div style={card}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
                <div>
                  <div style={{ display: 'flex', gap: '10px', alignItems: 'center', marginBottom: '6px' }}>
                    <span style={badge(SEV_COLORS[selectedIncident.severity] || '#ef4444')}>{selectedIncident.severity}</span>
                    <span style={{ fontFamily: 'monospace', color: '#64748b' }}>{selectedIncident.incident_number}</span>
                  </div>
                  <h2 style={{ margin: 0, fontSize: '20px', fontWeight: 800 }}>{selectedIncident.title}</h2>
                </div>
                {selectedIncident.incident_status !== 'RESOLVED' && (
                  <button onClick={() => handleResolve(selectedIncident.id)} style={{ padding: '8px 16px', borderRadius: '6px', border: 'none', background: 'linear-gradient(135deg, #10b981, #059669)', color: '#fff', fontWeight: 700, cursor: 'pointer' }}>
                    ✓ Mark Resolved
                  </button>
                )}
              </div>

              {/* Root Cause Card */}
              <div style={{ background: '#0f172a', borderRadius: '10px', padding: '16px', marginBottom: '16px', border: '1px solid #ef444433' }}>
                <div style={{ fontSize: '11px', color: '#ef4444', textTransform: 'uppercase', fontWeight: 700, marginBottom: '4px' }}>AI Root Cause Summary</div>
                <div style={{ fontSize: '13px', color: '#f8fafc', lineHeight: '1.5' }}>{selectedIncident.root_cause_summary}</div>
              </div>

              {/* Recommendations */}
              <div style={{ marginBottom: '16px' }}>
                <div style={{ fontSize: '12px', color: '#64748b', textTransform: 'uppercase', marginBottom: '6px' }}>Recommended Actions</div>
                {selectedIncident.recommendations?.map((r: any, idx: number) => (
                  <div key={idx} style={{ background: '#0f172a', borderRadius: '6px', padding: '8px 12px', marginBottom: '4px', fontSize: '12px', display: 'flex', justifyContent: 'space-between' }}>
                    <span>{r.action}</span>
                    <span style={badge(r.priority === 'HIGH' ? '#ef4444' : '#f59e0b')}>{r.priority}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Incident Timeline */}
            <div style={card}>
              <h3 style={{ margin: '0 0 16px', fontSize: '16px', fontWeight: 700, color: '#f97316' }}>Chronological Incident Timeline</h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {selectedIncident.timeline?.map((t: any) => (
                  <div key={t.id} style={{ background: '#0f172a', borderRadius: '8px', padding: '12px 16px', borderLeft: '3px solid #f97316' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                      <span style={{ fontWeight: 700, color: '#f97316', fontSize: '12px' }}>{t.event_type}</span>
                      <span style={{ fontSize: '11px', color: '#64748b' }}>{new Date(t.created_at).toLocaleTimeString()}</span>
                    </div>
                    <div style={{ fontSize: '13px', color: '#94a3b8' }}>{t.description}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Trigger Modal */}
      {showTriggerModal && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.8)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
          <div style={{ background: '#0f172a', borderRadius: '16px', border: '1px solid #ef4444', padding: '28px', width: '400px' }}>
            <h2 style={{ margin: '0 0 20px', fontSize: '18px', color: '#ef4444' }}>🚨 Trigger Incident</h2>
            <form onSubmit={handleTrigger} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div>
                <label style={{ fontSize: '12px', color: '#64748b', display: 'block', marginBottom: '4px' }}>Incident Title</label>
                <input value={triggerForm.title} onChange={e => setTriggerForm({ ...triggerForm, title: e.target.value })} required
                  style={{ width: '100%', padding: '9px 12px', borderRadius: '6px', border: '1px solid #334155', background: '#1e293b', color: '#fff', boxSizing: 'border-box' as const }} />
              </div>
              <div>
                <label style={{ fontSize: '12px', color: '#64748b', display: 'block', marginBottom: '4px' }}>Severity</label>
                <select value={triggerForm.severity} onChange={e => setTriggerForm({ ...triggerForm, severity: e.target.value })}
                  style={{ width: '100%', padding: '9px 12px', borderRadius: '6px', border: '1px solid #334155', background: '#1e293b', color: '#fff' }}>
                  {['SEV-1','SEV-2','SEV-3','SEV-4'].map(s => <option key={s} value={s}>{s}</option>)}
                </select>
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
                <button type="button" onClick={() => setShowTriggerModal(false)} style={{ padding: '9px 16px', borderRadius: '6px', border: '1px solid #334155', background: '#1e293b', color: '#f8fafc' }}>Cancel</button>
                <button type="submit" style={{ padding: '9px 16px', borderRadius: '6px', border: 'none', background: '#dc2626', color: '#fff', fontWeight: 700 }}>Trigger</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
