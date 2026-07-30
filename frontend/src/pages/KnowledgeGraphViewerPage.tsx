import React, { useEffect, useState } from 'react';
import { PageHeader } from '../components/layout/PageHeader';
import { StatusBadge } from '../components/ui/StatusBadge';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { FormField } from '../components/ui/FormField';
import { GitBranch, Layers, HelpCircle, ArrowRight, RefreshCw } from 'lucide-react';
import { apiGet } from '../services/api';
import { toast } from '../stores/toastStore';

interface ChainNode {
  type: string;
  key: string;
  label: string;
}

interface ChainResponse {
  defect_id: string;
  chain_depth: number;
  nodes: ChainNode[];
  explanation: Record<string, string>;
}

export function KnowledgeGraphViewerPage() {
  const [defectId, setDefectId] = useState('DEF-001');
  const [chain, setChain] = useState<ChainResponse | null>(null);
  const [loading, setLoading] = useState(false);

  const fetchChain = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setLoading(true);
    try {
      const res = await apiGet<ChainResponse>(`/api/root-cause-graph/chain?defect_id=${defectId}`);
      setChain(res);
    } catch (err) {
      toast.error('Failed to load root cause dependency chain');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void fetchChain();
  }, []);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      <PageHeader
        breadcrumbs={[{ label: 'AI QA Brain' }, { label: 'Knowledge Graph Viewer' }]}
        title="AI Root Cause Dependency Graph Viewer"
        description="Traverse root cause dependency chains linking Bug -> Component -> API -> Database -> Service -> Task -> Release -> Customer Impact."
      />

      <div className="card" style={{ padding: '1.25rem' }}>
        <form onSubmit={fetchChain} style={{ display: 'flex', gap: '1rem', alignItems: 'flex-end' }}>
          <div style={{ flex: 1 }}>
            <FormField label="Defect ID / Key">
              <Input value={defectId} onChange={(e) => setDefectId(e.target.value)} />
            </FormField>
          </div>
          <Button variant="primary" type="submit" isLoading={loading} leftIcon={<GitBranch size={16} />}>
            Traverse Root Cause Chain
          </Button>
        </form>
      </div>

      {chain && (
        <>
          {/* Dependency Chain Flow */}
          <div className="card" style={{ padding: '1.25rem' }}>
            <h3 style={{ margin: '0 0 1rem 0' }}>Root Cause Dependency Chain ({chain.chain_depth} Nodes)</h3>
            <div style={{ display: 'flex', gap: '0.75rem', overflowX: 'auto', paddingBottom: '0.5rem' }}>
              {chain.nodes.map((node, nIdx) => (
                <React.Fragment key={nIdx}>
                  <div style={{ background: 'var(--bg-muted)', padding: '1rem', borderRadius: '8px', border: '1px solid var(--border-color)', minWidth: '180px' }}>
                    <div style={{ fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--color-primary)', marginBottom: '0.3rem' }}>
                      {node.type}
                    </div>
                    <div style={{ fontWeight: 700, fontSize: '0.85rem' }}>
                      {node.label}
                    </div>
                  </div>
                  {nIdx < chain.nodes.length - 1 && (
                    <div style={{ display: 'flex', alignItems: 'center', color: 'var(--text-muted)' }}>
                      <ArrowRight size={18} />
                    </div>
                  )}
                </React.Fragment>
              ))}
            </div>
          </div>

          {/* Root Cause Explanation */}
          <div className="card" style={{ padding: '1.25rem' }}>
            <h3 style={{ margin: '0 0 1rem 0' }}>AI Senior QA Root Cause Justification</h3>
            <div className="grid grid-cols-2" style={{ gap: '1rem' }}>
              {Object.entries(chain.explanation || {}).map(([exKey, exVal], idx) => (
                <div key={idx} style={{ background: 'var(--bg-muted)', padding: '1rem', borderRadius: '8px' }}>
                  <div style={{ fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-muted)' }}>
                    {exKey}
                  </div>
                  <div style={{ fontSize: '0.9rem', fontWeight: 600, marginTop: '0.25rem' }}>
                    {exVal}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
