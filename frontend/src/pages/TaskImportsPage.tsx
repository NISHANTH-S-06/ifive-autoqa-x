import React, { useState } from 'react';
import { PageHeader } from '../components/layout/PageHeader';
import { FilterBar } from '../components/ui/FilterBar';
import { StatusBadge } from '../components/ui/StatusBadge';
import { DataTable, Column } from '../components/ui/DataTable';
import { TaskImportsCore } from '../components/TaskImportsCore';
import { RefreshCw, Play, Sparkles, AlertCircle, FileText, X } from 'lucide-react';
import { toast } from '../stores/toastStore';

export function TaskImportsPage() {
  const [selectedTask, setSelectedTask] = useState<any | null>(null);

  return (
    <div>
      <PageHeader
        breadcrumbs={[{ label: 'Task Imports' }]}
        title="Task Imports & Requirement Management"
        description="Sync, analyze, and convert backlog task requirements into deterministic test plans."
      />

      <div className="card" style={{ padding: '1.25rem' }}>
        <TaskImportsCore />
      </div>
    </div>
  );
}
