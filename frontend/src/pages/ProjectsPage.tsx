import React, { useState } from 'react';
import { PageHeader } from '../components/layout/PageHeader';
import { DataTable, Column } from '../components/ui/DataTable';
import { StatusBadge } from '../components/ui/StatusBadge';
import { StatCard } from '../components/ui/StatCard';
import { Modal } from '../components/ui/Modal';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { FormField } from '../components/ui/FormField';
import { createTestProject, archiveTestProject } from '../services/testManagement';
import type { TestProject } from '../types/testManagement';
import { useProject } from '../stores/projectStore';
import { toast } from '../stores/toastStore';
import { Plus, Archive, FolderGit2, ShieldCheck } from 'lucide-react';

export function ProjectsPage() {
  const { projects, refreshProjects } = useProject();
  const [loading, setLoading] = useState(false);
  const [showModal, setShowModal] = useState(false);

  const [name, setName] = useState('');
  const [code, setCode] = useState('');
  const [accessProjectId, setAccessProjectId] = useState(1);
  const [description, setDescription] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name || !code) return;
    setSubmitting(true);
    try {
      await createTestProject({ access_project_id: accessProjectId, name, code, description });
      toast.success('Test Project created successfully.');
      setShowModal(false);
      setName('');
      setCode('');
      setDescription('');
      await refreshProjects();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Failed to create project.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleArchive = async (id: number) => {
    try {
      await archiveTestProject(id);
      toast.success('Project archived.');
      await refreshProjects();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Failed to archive project.');
    }
  };

  const activeCount = projects.filter(p => !p.archived_at).length;
  const archivedCount = projects.filter(p => p.archived_at).length;

  const columns: Column<TestProject>[] = [
    { key: 'id', header: 'ID', render: (p) => <span style={{ fontWeight: 600, fontFamily: 'var(--font-mono)' }}>#{p.id}</span> },
    { key: 'code', header: 'Project Code', render: (p) => <span style={{ fontWeight: 700, color: 'var(--color-primary)' }}>{p.code}</span> },
    { key: 'name', header: 'Project Name', render: (p) => <span style={{ fontWeight: 600 }}>{p.name}</span> },
    { key: 'access_project_id', header: 'Access Scope ID', render: (p) => <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Scope #{p.access_project_id}</span> },
    { key: 'status', header: 'Status', render: (p) => <StatusBadge status={p.archived_at ? 'REJECTED' : 'APPROVED'} label={p.archived_at ? 'Archived' : 'Active'} size="sm" /> },
    { key: 'actions', header: 'Actions', render: (p) => (
      !p.archived_at ? (
        <Button size="sm" variant="ghost" style={{ color: 'var(--color-danger)' }} onClick={() => void handleArchive(p.id)} leftIcon={<Archive size={13} />}>
          Archive
        </Button>
      ) : <span style={{ fontSize: '0.75rem', color: 'var(--text-subtle)' }}>Archived</span>
    )}
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      <PageHeader
        breadcrumbs={[{ label: 'Projects' }]}
        title="Test Projects & Multi-Tenant Isolation"
        description="Configure isolated test project contexts, RBAC scope boundaries, and tenant isolation."
        actions={(
          <Button size="sm" variant="primary" onClick={() => setShowModal(true)} leftIcon={<Plus size={14} />}>
            New Test Project
          </Button>
        )}
      />

      <div className="grid grid-cols-3">
        <StatCard title="Active Projects" value={activeCount} subtitle="Isolated test suites" icon={FolderGit2} variant="primary" loading={loading} />
        <StatCard title="Archived Projects" value={archivedCount} subtitle="Historical suites" icon={Archive} variant="warning" loading={loading} />
        <StatCard title="Multi-Tenant Scope" value="ISOLATED" subtitle="ProjectGuard enforced" icon={ShieldCheck} variant="success" loading={loading} />
      </div>

      <div className="card" style={{ padding: '1.25rem' }}>
        <DataTable
          columns={columns}
          data={projects}
          keyExtractor={(p) => p.id}
          loading={loading}
          emptyMessage="No test projects configured yet."
        />
      </div>

      <Modal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        title="Create Test Project"
        subtitle="Establish an isolated test project suite with RBAC access scope"
        footer={(
          <>
            <Button variant="secondary" onClick={() => setShowModal(false)}>Cancel</Button>
            <Button variant="primary" onClick={handleCreate} isLoading={submitting} disabled={!name || !code}>
              Create Project
            </Button>
          </>
        )}
      >
        <form onSubmit={handleCreate} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <FormField label="Project Code" required hint="Short identifier (e.g. AUTH-API, PAYMENTS)">
            <Input
              required
              placeholder="e.g. PROD-AUTH"
              value={code}
              onChange={(e) => setCode(e.target.value)}
            />
          </FormField>

          <FormField label="Project Name" required>
            <Input
              required
              placeholder="e.g. Authentication Service Test Suite"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </FormField>

          <FormField label="Access Project Scope ID">
            <Input
              type="number"
              value={accessProjectId}
              onChange={(e) => setAccessProjectId(Number(e.target.value))}
            />
          </FormField>

          <FormField label="Scope Description">
            <textarea
              className="textarea"
              placeholder="Project scope and testing objective details..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              style={{ minHeight: '70px' }}
            />
          </FormField>
        </form>
      </Modal>
    </div>
  );
}
