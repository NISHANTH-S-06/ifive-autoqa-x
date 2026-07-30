import React, { useState } from 'react';
import { PageHeader } from '../components/layout/PageHeader';
import { StatCard } from '../components/ui/StatCard';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { FormField } from '../components/ui/FormField';
import { StatusBadge } from '../components/ui/StatusBadge';
import { toast } from '../stores/toastStore';
import { Globe, Cpu, GitMerge, CheckCircle, XCircle, Sparkles, Layers, ListChecks, Play } from 'lucide-react';
import { apiPost } from '../services/api';

interface TestRecommendation {
  category: string;
  title: string;
  description: string;
  severity: string;
  priority: string;
  confidence: number;
}

interface DiscoveryData {
  id: number;
  status: string;
  target_url: string;
  ui_map: any;
  module_tree: any;
  flow_graph: any;
  recommendations: TestRecommendation[];
  confidence_score: number;
}

export function EnterpriseDiscoveryPage() {
  const [targetUrl, setTargetUrl] = useState('https://demo.playwright.dev/todomvc');
  const [scanning, setScanning] = useState(false);
  const [discovery, setDiscovery] = useState<DiscoveryData | null>(null);
  const [activeTab, setActiveTab] = useState<'ui_map' | 'module_tree' | 'flow_graph' | 'recommendations'>('recommendations');

  const handleScan = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!targetUrl) return;
    setScanning(true);
    try {
      const res = await apiPost<DiscoveryData>('/api/discovery/scan', {
        project_id: 1,
        target_url: targetUrl
      });
      setDiscovery(res);
      toast.success('AI Website & Flow Discovery scan completed successfully.');
    } catch (err: any) {
      toast.error(err.message || 'Failed to execute discovery scan');
    } finally {
      setScanning(false);
    }
  };

  const handleApprove = async () => {
    if (!discovery) return;
    try {
      await apiPost(`/api/discovery/results/${discovery.id}/approve`, {});
      setDiscovery({ ...discovery, status: 'APPROVED' });
      toast.success('AI Discovery & Test Suite approved by Tester.');
    } catch (err) {
      toast.error('Failed to approve discovery result');
    }
  };

  const handleReject = async () => {
    if (!discovery) return;
    try {
      await apiPost(`/api/discovery/results/${discovery.id}/reject`, { rejection_reason: 'Rejected during Tester review' });
      setDiscovery({ ...discovery, status: 'REJECTED' });
      toast.error('AI Discovery rejected.');
    } catch (err) {
      toast.error('Failed to reject discovery result');
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      <PageHeader
        breadcrumbs={[{ label: 'AI Autonomous QA' }, { label: 'Website & Flow Discovery' }]}
        title="AI Website Topology & Flow Discovery"
        description="Autonomous Playwright DOM scanning, AI Module classification, Flow Graph extraction, and 15-category Test Recommendation engine."
      />

      {/* URL Scan Bar */}
      <div className="card" style={{ padding: '1.25rem' }}>
        <form onSubmit={handleScan} style={{ display: 'flex', gap: '1rem', alignItems: 'flex-end' }}>
          <div style={{ flex: 1 }}>
            <FormField label="Target Enterprise Website / Application URL" required>
              <Input
                placeholder="https://company.example.com"
                value={targetUrl}
                onChange={(e) => setTargetUrl(e.target.value)}
              />
            </FormField>
          </div>
          <Button variant="primary" type="submit" isLoading={scanning} leftIcon={<Sparkles size={16} />}>
            Run AI Discovery Scan
          </Button>
        </form>
      </div>

      {discovery && (
        <>
          <div className="grid grid-cols-4">
            <StatCard title="Target Application" value={discovery.target_url.replace(/^https?:\/\//, '')} subtitle="Live URL Scanned" icon={Globe} variant="primary" />
            <StatCard title="AI Confidence Score" value={`${Math.round(discovery.confidence_score * 100)}%`} subtitle="High Accuracy" icon={Cpu} variant="success" />
            <StatCard title="Discovered Flow Nodes" value={discovery.flow_graph?.total_nodes || 4} subtitle="User Journeys Mapped" icon={GitMerge} variant="info" />
            <StatCard title="Recommended Tests" value={discovery.recommendations?.length || 15} subtitle="Across 15 Categories" icon={ListChecks} variant="warning" />
          </div>

          {/* Tester Approval Workflow Banner */}
          <div className="card" style={{ padding: '1.25rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderLeft: `4px solid ${discovery.status === 'APPROVED' ? '#10b981' : discovery.status === 'REJECTED' ? '#ef4444' : '#f59e0b'}` }}>
            <div>
              <h4 style={{ margin: 0, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                Approval Workflow Status: <StatusBadge status={discovery.status === 'APPROVED' ? 'APPROVED' : discovery.status === 'REJECTED' ? 'REJECTED' : 'IN_REVIEW'} label={discovery.status} />
              </h4>
              <p style={{ margin: '0.25rem 0 0 0', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                Tester review required before Playwright execution engine trigger.
              </p>
            </div>
            {discovery.status === 'PENDING_APPROVAL' && (
              <div style={{ display: 'flex', gap: '0.75rem' }}>
                <Button variant="danger" size="sm" onClick={handleReject} leftIcon={<XCircle size={15} />}>
                  Reject Test Plan
                </Button>
                <Button variant="primary" size="sm" onClick={handleApprove} leftIcon={<CheckCircle size={15} />}>
                  Approve & Ready Execution
                </Button>
              </div>
            )}
            {discovery.status === 'APPROVED' && (
              <Button variant="primary" size="sm" leftIcon={<Play size={15} />}>
                Execute Autonomous Playwright Engine
              </Button>
            )}
          </div>

          {/* Navigation Tabs */}
          <div style={{ display: 'flex', gap: '0.5rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.5rem' }}>
            <Button size="sm" variant={activeTab === 'recommendations' ? 'primary' : 'ghost'} onClick={() => setActiveTab('recommendations')} leftIcon={<ListChecks size={14} />}>
              15-Category Test Recommendations ({discovery.recommendations.length})
            </Button>
            <Button size="sm" variant={activeTab === 'module_tree' ? 'primary' : 'ghost'} onClick={() => setActiveTab('module_tree')} leftIcon={<Layers size={14} />}>
              AI Module Tree
            </Button>
            <Button size="sm" variant={activeTab === 'flow_graph' ? 'primary' : 'ghost'} onClick={() => setActiveTab('flow_graph')} leftIcon={<GitMerge size={14} />}>
              User Flow Graph
            </Button>
            <Button size="sm" variant={activeTab === 'ui_map' ? 'primary' : 'ghost'} onClick={() => setActiveTab('ui_map')} leftIcon={<Globe size={14} />}>
              DOM UI Map Tree
            </Button>
          </div>

          {/* Tab Content */}
          {activeTab === 'recommendations' && (
            <div className="grid grid-cols-2" style={{ gap: '1rem' }}>
              {discovery.recommendations.map((rec, idx) => (
                <div key={idx} className="card" style={{ padding: '1rem', borderTop: '3px solid var(--color-primary)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                    <StatusBadge status="INFO" label={rec.category} size="sm" />
                    <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)' }}>Confidence: {Math.round(rec.confidence * 100)}%</span>
                  </div>
                  <h4 style={{ margin: '0 0 0.4rem 0' }}>{rec.title}</h4>
                  <p style={{ margin: '0 0 0.75rem 0', fontSize: '0.85rem', color: 'var(--text-muted)' }}>{rec.description}</p>
                  <div style={{ display: 'flex', gap: '0.5rem' }}>
                    <StatusBadge status={rec.severity === 'CRITICAL' ? 'CRITICAL' : 'WARNING'} label={`Severity: ${rec.severity}`} size="sm" />
                    <StatusBadge status="APPROVED" label={`Priority: ${rec.priority}`} size="sm" />
                  </div>
                </div>
              ))}
            </div>
          )}

          {activeTab === 'module_tree' && (
            <div className="card" style={{ padding: '1.25rem' }}>
              <h3>AI Classified Module Hierarchy</h3>
              <pre style={{ background: 'var(--bg-muted)', padding: '1rem', borderRadius: '8px', overflowX: 'auto', fontSize: '0.85rem' }}>
                {JSON.stringify(discovery.module_tree, null, 2)}
              </pre>
            </div>
          )}

          {activeTab === 'flow_graph' && (
            <div className="card" style={{ padding: '1.25rem' }}>
              <h3>User Journey Flow Graph</h3>
              <pre style={{ background: 'var(--bg-muted)', padding: '1rem', borderRadius: '8px', overflowX: 'auto', fontSize: '0.85rem' }}>
                {JSON.stringify(discovery.flow_graph, null, 2)}
              </pre>
            </div>
          )}

          {activeTab === 'ui_map' && (
            <div className="card" style={{ padding: '1.25rem' }}>
              <h3>Complete DOM UI Map Tree</h3>
              <pre style={{ background: 'var(--bg-muted)', padding: '1rem', borderRadius: '8px', overflowX: 'auto', fontSize: '0.85rem' }}>
                {JSON.stringify(discovery.ui_map, null, 2)}
              </pre>
            </div>
          )}
        </>
      )}
    </div>
  );
}
