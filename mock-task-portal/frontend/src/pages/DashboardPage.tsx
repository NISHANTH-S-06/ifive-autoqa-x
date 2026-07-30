import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getDashboardSummary } from '../api';
import type { DashboardSummary } from '../types';
import { Loading, ErrorAlert } from '../components';

const STATUS_DISPLAY: Array<{ key: string; label: string; color: string }> = [
  { key: 'CREATED',             label: 'Created',             color: '#94a3b8' },
  { key: 'ASSIGNED',            label: 'Assigned',            color: '#818cf8' },
  { key: 'IN_PROGRESS',         label: 'In Progress',         color: '#60a5fa' },
  { key: 'TESTING_L1',          label: 'Testing L1',          color: '#c084fc' },
  { key: 'TESTING_L2',          label: 'Testing L2',          color: '#fbbf24' },
  { key: 'QA_RUNNING',          label: 'QA Running',          color: '#facc15' },
  { key: 'QA_PASSED',           label: 'QA Passed',           color: '#34d399' },
  { key: 'QA_FAILED',           label: 'QA Failed',           color: '#f87171' },
  { key: 'REWORK',              label: 'Rework',              color: '#fb923c' },
  { key: 'NEED_CLARITY',        label: 'Need Clarity',        color: '#fde68a' },
  { key: 'HOLD',                label: 'Hold',                color: '#cbd5e1' },
  { key: 'DELIVERY_READY',      label: 'Delivery Ready',      color: '#2dd4bf' },
  { key: 'DELIVERY_COMPLETED',  label: 'Delivery Completed',  color: '#6ee7b7' },
  { key: 'CANCELLED',           label: 'Cancelled',           color: '#fca5a5' },
];

export default function DashboardPage() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    getDashboardSummary()
      .then(setSummary)
      .catch(e => setError(e.message));
  }, []);

  if (error) return (
    <div className="page-body">
      <ErrorAlert message={error} />
    </div>
  );
  if (!summary) return <Loading />;

  return (
    <>
      <div className="page-header">
        <h1>Dashboard</h1>
        <p>Task status summary — {summary.total} total tasks</p>
      </div>
      <div className="page-body">
        <div className="stats-grid">
          {STATUS_DISPLAY.map(({ key, label, color }) => (
            <Link
              key={key}
              to={`/tasks?status=${key}`}
              style={{ textDecoration: 'none' }}
            >
              <div className="stat-card" style={{ borderTop: `3px solid ${color}` }}>
                <div className="stat-value" style={{ color }}>
                  {summary.counts[key] ?? 0}
                </div>
                <div className="stat-label">{label}</div>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </>
  );
}
