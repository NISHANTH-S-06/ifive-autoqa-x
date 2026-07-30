import React, { useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { listTasks } from '../api';
import type { Task } from '../types';
import { StatusBadge, PriorityBadge, Loading, ErrorAlert, EmptyState } from '../components';
import { fmtDate } from '../components';

const ALL_STATUSES = [
  'CREATED','ASSIGNED','IN_PROGRESS','TESTING_L1','TESTING_L2',
  'QA_RUNNING','QA_PASSED','QA_FAILED','REWORK',
  'DELIVERY_READY','DELIVERY_COMPLETED','NEED_CLARITY','HOLD','CANCELLED',
];

export default function TaskListPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchParams, setSearchParams] = useSearchParams();

  const statusFilter = searchParams.get('status') ?? '';
  const projectFilter = searchParams.get('project') ?? '';
  const developerFilter = searchParams.get('developer') ?? '';
  const priorityFilter = searchParams.get('priority') ?? '';

  useEffect(() => {
    setLoading(true);
    listTasks({
      status: statusFilter || undefined,
      project: projectFilter || undefined,
      developer: developerFilter || undefined,
      priority: priorityFilter || undefined,
    })
      .then(setTasks)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, [statusFilter, projectFilter, developerFilter, priorityFilter]);

  function setFilter(key: string, value: string) {
    const params = new URLSearchParams(searchParams);
    if (value) params.set(key, value);
    else params.delete(key);
    setSearchParams(params);
  }

  return (
    <>
      <div className="page-header">
        <h1>Task List</h1>
        <p>{tasks.length} task{tasks.length !== 1 ? 's' : ''}</p>
      </div>
      <div className="page-body">
        <div className="filters-bar">
          <select
            id="filter-status"
            value={statusFilter}
            onChange={e => setFilter('status', e.target.value)}
          >
            <option value="">All Statuses</option>
            {ALL_STATUSES.map(s => <option key={s} value={s}>{s.replace(/_/g,' ')}</option>)}
          </select>
          <select
            id="filter-priority"
            value={priorityFilter}
            onChange={e => setFilter('priority', e.target.value)}
          >
            <option value="">All Priorities</option>
            {['CRITICAL','HIGH','MEDIUM','LOW'].map(p => <option key={p} value={p}>{p}</option>)}
          </select>
          <input
            id="filter-project"
            placeholder="Project…"
            value={projectFilter}
            onChange={e => setFilter('project', e.target.value)}
          />
          <input
            id="filter-developer"
            placeholder="Developer…"
            value={developerFilter}
            onChange={e => setFilter('developer', e.target.value)}
          />
          {(statusFilter || projectFilter || developerFilter || priorityFilter) && (
            <button
              className="btn btn-ghost btn-sm"
              onClick={() => setSearchParams({})}
            >
              Clear
            </button>
          )}
        </div>

        {error && <ErrorAlert message={error} />}

        <div className="card" style={{ padding: 0 }}>
          {loading ? <Loading /> : tasks.length === 0 ? (
            <EmptyState message="No tasks match the current filters." />
          ) : (
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Code</th>
                    <th>Title</th>
                    <th>Project</th>
                    <th>Status</th>
                    <th>Priority</th>
                    <th>Developer</th>
                    <th>Tester</th>
                    <th>Target</th>
                    <th>Rev</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {tasks.map(t => (
                    <tr key={t.id}>
                      <td style={{ fontFamily: 'monospace', fontSize: 12 }}>{t.task_code}</td>
                      <td>{t.title}</td>
                      <td style={{ color: 'var(--text-muted)', fontSize: 12 }}>{t.project_name}</td>
                      <td><StatusBadge status={t.status} /></td>
                      <td><PriorityBadge priority={t.priority} /></td>
                      <td style={{ color: 'var(--text-muted)', fontSize: 12 }}>{t.assigned_developer ?? '—'}</td>
                      <td style={{ color: 'var(--text-muted)', fontSize: 12 }}>{t.assigned_tester ?? '—'}</td>
                      <td style={{ color: 'var(--text-muted)', fontSize: 12 }}>{t.target_date ?? '—'}</td>
                      <td style={{ textAlign: 'center', fontSize: 12 }}>{t.revision}</td>
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
