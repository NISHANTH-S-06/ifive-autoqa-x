import React from 'react';
import { PageHeader } from '../components/layout/PageHeader';
import { AutomatedRunsCore } from '../components/AutomatedRunsCore';

export function AutomatedRunsPage() {
  return (
    <div>
      <PageHeader
        breadcrumbs={[{ label: 'Automated Runs' }]}
        title="Automated Test Execution Runs"
        description="Monitor live deterministic test execution, view UI step timelines, inspect API/DB validations, and download artifacts."
      />

      <div className="card" style={{ padding: '1.25rem' }}>
        <AutomatedRunsCore />
      </div>
    </div>
  );
}
