import React from 'react';
import { PageHeader } from '../components/layout/PageHeader';
import { LocalSchedulesCore } from '../components/LocalSchedulesCore';

export function LocalSchedulesPage() {
  return (
    <div>
      <PageHeader
        breadcrumbs={[{ label: 'Local Schedules' }]}
        title="Local Schedules & Cron Automation"
        description="Automate periodic execution of approved test plans with validation profiles and frequency controls."
      />

      <div className="card" style={{ padding: '1.25rem' }}>
        <LocalSchedulesCore />
      </div>
    </div>
  );
}
