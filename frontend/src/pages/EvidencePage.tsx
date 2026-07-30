import React, { useEffect, useState } from 'react';
import { PageHeader } from '../components/layout/PageHeader';
import { FilterBar } from '../components/ui/FilterBar';
import { EvidenceGallery, EvidenceItem } from '../components/ui/EvidenceGallery';
import { ErrorState } from '../components/ui/ErrorState';
import { LoadingSkeleton } from '../components/ui/LoadingSkeleton';
import { fetchAutomatedRuns, fetchExecutionArtifacts } from '../services/automatedExecution';
import { RefreshCw } from 'lucide-react';

export function EvidencePage() {
  const [items, setItems] = useState<EvidenceItem[]>([]);
  const [search, setSearch] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const loadEvidence = async () => {
    setLoading(true);
    setError('');
    try {
      const runsRes = await fetchAutomatedRuns('?limit=20');
      const runs = runsRes.items || [];

      const allArtifacts: EvidenceItem[] = [];

      for (const run of runs) {
        try {
          const artifacts = await fetchExecutionArtifacts(run.id);
          artifacts.forEach(a => {
            allArtifacts.push({
              id: a.id,
              name: a.original_filename || `Run #${run.id} Artifact`,
              type: a.artifact_type || 'screenshot',
              url: `/api/execution-artifacts/${a.id}/download`,
              timestamp: a.created_at
            });
          });
        } catch {
          // ignore individual run artifact failures
        }
      }

      setItems(allArtifacts);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load evidence repository.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadEvidence();
  }, []);

  const filteredItems = items.filter(item => {
    const matchSearch = search.trim() === '' || item.name.toLowerCase().includes(search.toLowerCase());
    const matchType = typeFilter === '' || item.type.toLowerCase().includes(typeFilter.toLowerCase());
    return matchSearch && matchType;
  });

  return (
    <div>
      <PageHeader
        breadcrumbs={[{ label: 'Evidence' }]}
        title="Evidence & Artifact Repository"
        description="Centralized store for execution screenshots, trace ZIPs, DOM snapshots, and video recordings."
        actions={(
          <button className="btn btn-secondary btn-sm" onClick={loadEvidence} disabled={loading}>
            <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
            Refresh Artifacts
          </button>
        )}
      />

      <FilterBar
        searchQuery={search}
        onSearchChange={setSearch}
        filters={[
          {
            key: 'type',
            label: 'Artifact Type',
            value: typeFilter,
            options: [
              { label: 'Screenshot', value: 'screenshot' },
              { label: 'Trace ZIP', value: 'trace' },
              { label: 'Video Recording', value: 'video' },
              { label: 'Execution Log', value: 'log' }
            ]
          }
        ]}
        onFilterChange={(_, val) => setTypeFilter(val)}
        onClearFilters={() => { setSearch(''); setTypeFilter(''); }}
      />

      {error && <div style={{ marginBottom: '1.5rem' }}><ErrorState message={error} onRetry={loadEvidence} /></div>}

      {loading ? (
        <LoadingSkeleton type="card" count={6} />
      ) : (
        <EvidenceGallery items={filteredItems} />
      )}
    </div>
  );
}
