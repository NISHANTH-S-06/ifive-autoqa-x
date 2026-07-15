import { useEffect, useState } from 'react';
import { fetchProjects } from '../services/testRuns';
import type { Project, ProductCode } from '../types/product';

const modules: Record<ProductCode, string[]> = {
  ERP: ['Customer', 'Inventory', 'Purchase', 'Sales', 'Finance'],
  HRMS: ['Employee', 'Attendance', 'Leave', 'Payroll Preview', 'Permissions'],
  CRM: ['Lead', 'Opportunity', 'Follow-up', 'Quotation', 'Reports'],
  IIOT: ['Device Status', 'Telemetry', 'Alerts', 'Charts', 'Data Freshness'],
  INTEGRATION: ['API Mapping', 'Schema', 'Retry', 'Duplicate Handling', 'Webhooks', 'Error Logs'],
  AUTOQA: ['Projects', 'Test Runs', 'Evidence', 'Reports', 'Safety'],
};

export function ProductConnections() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true); setError('');
    try { setProjects(await fetchProjects()); } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Unable to load projects.');
    } finally { setLoading(false); }
  };

  useEffect(() => { void load(); }, []);

  return (
    <section className="section" id="products">
      <div className="section-inner">
        <div className="section-title"><h2>Product Testing Scope</h2><p>Each local project receives focused test packs for business-critical modules and permissions.</p></div>
        {loading && <div className="state-panel" role="status">Loading projects…</div>}
        {error && <div className="state-panel state-error" role="alert">{error}<button className="button button-secondary" onClick={() => void load()}>Retry</button></div>}
        {!loading && !error && projects.length === 0 && <div className="state-panel">No active projects yet.</div>}
        {!loading && !error && projects.length > 0 && <div className="grid grid-3">
          {projects.map((project) => <article className="card" key={project.id} data-testid="project-card"><h3>{project.name}</h3><ul>{modules[project.product_code].map((module) => <li key={module}>{module}</li>)}</ul></article>)}
        </div>}
      </div>
    </section>
  );
}
