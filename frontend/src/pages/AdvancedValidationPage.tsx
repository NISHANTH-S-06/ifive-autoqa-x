import React from 'react';
import { PageHeader } from '../components/layout/PageHeader';
import { AdvancedValidationCore } from '../components/AdvancedValidationCore';

export function AdvancedValidationPage() {
  return (
    <div>
      <PageHeader
        breadcrumbs={[{ label: 'Advanced Validation' }]}
        title="Advanced Validation Profile Manager"
        description="Configure API contracts, read-only DB queries, accessibility WCAG rules, and performance thresholds."
      />

      <div className="card" style={{ padding: '1.25rem' }}>
        <AdvancedValidationCore />
      </div>
    </div>
  );
}
