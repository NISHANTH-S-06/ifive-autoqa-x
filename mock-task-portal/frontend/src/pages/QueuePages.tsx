import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { listTasks } from '../api';
import type { Task } from '../types';
import { StatusBadge, PriorityBadge, Loading, ErrorAlert, EmptyState } from '../components';
import { fmtDate } from '../components';

/** Reusable queue list for specific status filters */
export function QueueList({
  title,
  subtitle,
  status,
  emptyMessage,
}: {
  title: string;
  subtitle: string;
  status: string;
  emptyMessage?: string;
}) {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    listTasks({ status })
      .then(setTasks)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, [status]);

  return (
    <>
      <div className="page-header">
        <h1>{title}</h1>
        <p>{subtitle} · {tasks.length} task{tasks.length !== 1 ? 's' : ''}</p>
      </div>
      <div className="page-body">
        {error && <ErrorAlert message={error} />}
        <div className="card" style={{ padding: 0 }}>
          {loading ? <Loading /> : tasks.length === 0 ? (
            <EmptyState message={emptyMessage ?? `No tasks in ${status.replace(/_/g,' ')} status.`} />
          ) : (
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Code</th>
                    <th>Title</th>
                    <th>Project / Module</th>
                    <th>Status</th>
                    <th>Priority</th>
                    <th>Developer</th>
                    <th>Tester</th>
                    <th>Rev</th>
                    <th>Updated</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {tasks.map(t => (
                    <tr key={t.id}>
                      <td style={{ fontFamily: 'monospace', fontSize: 12 }}>{t.task_code}</td>
                      <td>{t.title}</td>
                      <td style={{ color: 'var(--text-muted)', fontSize: 12 }}>
                        {t.project_name}<br />
                        <span style={{ fontSize: 11 }}>{t.module_name}</span>
                      </td>
                      <td><StatusBadge status={t.status} /></td>
                      <td><PriorityBadge priority={t.priority} /></td>
                      <td style={{ color: 'var(--text-muted)', fontSize: 12 }}>{t.assigned_developer ?? '—'}</td>
                      <td style={{ color: 'var(--text-muted)', fontSize: 12 }}>{t.assigned_tester ?? '—'}</td>
                      <td style={{ textAlign: 'center', fontSize: 12 }}>{t.revision}</td>
                      <td style={{ color: 'var(--text-muted)', fontSize: 11 }}>{fmtDate(t.updated_at)}</td>
                      <td>
                        <Link to={`/tasks/${t.id}`} className="btn btn-ghost btn-sm">
                          View
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </>
  );
}

export function DeveloperTaskView() {
  return (
    <QueueList
      title="My Tasks"
      subtitle="Tasks assigned to me (Developer view)"
      status=""
      emptyMessage="No tasks assigned to you."
    />
  );
}

export function TestingL2QueuePage() {
  return (
    <QueueList
      title="Testing L2 Queue"
      subtitle="Tasks ready for L2 QA testing"
      status="TESTING_L2"
      emptyMessage="No tasks in Testing L2 queue."
    />
  );
}

export function ReworkQueuePage() {
  return (
    <QueueList
      title="Rework Queue"
      subtitle="Tasks returned for rework"
      status="REWORK"
      emptyMessage="No tasks in Rework queue."
    />
  );
}

export function DeliveryReadyPage() {
  return (
    <QueueList
      title="Delivery Ready"
      subtitle="Tasks passed QA and ready for delivery"
      status="DELIVERY_READY"
      emptyMessage="No tasks in Delivery Ready queue."
    />
  );
}

export function DeliveryCompletedPage() {
  return (
    <QueueList
      title="Delivery Completed"
      subtitle="Delivered and closed tasks"
      status="DELIVERY_COMPLETED"
      emptyMessage="No tasks have been delivered yet."
    />
  );
}
