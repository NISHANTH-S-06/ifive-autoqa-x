import React from 'react';
import { PageHeader } from '../components/layout/PageHeader';
import { ManagementReportsCore } from '../components/ManagementReportsCore';

export function ReportsPage() {
  return (
    <div>
      <PageHeader
        breadcrumbs={[{ label: 'Reports' }]}
        title="Management Reports & Quality Export Engine"
        description="Generate executive quality reports, export HTML/PDF/CSV summaries, and verify cryptographic report hashes."
      />

      <div className="card" style={{ padding: '1.25rem' }}>
        <ManagementReportsCore />
      </div>
    </div>
  );
}
