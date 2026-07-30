import React from 'react';
import { PageHeader } from '../components/layout/PageHeader';
import { DefectsCore } from '../components/DefectsCore';

export function DefectsPage() {
  return (
    <div>
      <PageHeader
        breadcrumbs={[{ label: 'Defects' }]}
        title="Defect Management & Fingerprint Tracking"
        description="Track execution failures, manage defect lifecycles, inspect evidence, and trigger automated retests."
      />

      <div className="card" style={{ padding: '1.25rem' }}>
        <DefectsCore />
      </div>
    </div>
  );
}
