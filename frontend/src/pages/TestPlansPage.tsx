import React from 'react';
import { PageHeader } from '../components/layout/PageHeader';
import { TestManagementCore } from '../components/TestManagementCore';

export function TestPlansPage() {
  return (
    <div>
      <PageHeader
        breadcrumbs={[{ label: 'Test Plans' }]}
        title="Test Plan Management & Visual Editor"
        description="Design multi-scenario test plans with locators, actions, assertions, and strict approval workflows."
      />

      <TestManagementCore hideTitle={true} />
    </div>
  );
}
