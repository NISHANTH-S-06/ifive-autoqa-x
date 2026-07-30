import React from 'react';
import { useProject } from '../../stores/projectStore';
import { FolderGit2 } from 'lucide-react';

interface ProjectGuardProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

export function ProjectGuard({ children, fallback }: ProjectGuardProps) {
  const { activeProject, loading } = useProject();

  if (loading) {
    return (
      <div className="card" style={{ padding: '2rem', textAlign: 'center' }}>
        <div className="skeleton" style={{ height: '2rem', width: '40%', margin: '0 auto' }}></div>
      </div>
    );
  }

  if (!activeProject) {
    if (fallback) return <>{fallback}</>;
    return (
      <div className="card" style={{ padding: '2.5rem 1.5rem', textAlign: 'center' }}>
        <FolderGit2 size={36} style={{ color: 'var(--color-primary)', margin: '0 auto 0.75rem' }} />
        <h3 style={{ fontSize: '1.05rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: '0.35rem' }}>No Active Project Selected</h3>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', maxWidth: '420px', margin: '0 auto' }}>
          Please select a test project from the top dropdown or create a new test project to view project-specific artifacts.
        </p>
      </div>
    );
  }

  return <>{children}</>;
}
