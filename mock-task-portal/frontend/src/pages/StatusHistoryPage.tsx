import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getTask, getTaskHistory } from '../api';
import type { Task, HistoryRecord } from '../types';
import { StatusBadge, Loading, ErrorAlert, EmptyState } from '../components';
import { fmtDate } from '../components';

export default function StatusHistoryPage() {
  const { taskId } = useParams<{ taskId: string }>();
  const id = Number(taskId);

  const [task, setTask] = useState<Task | null>(null);
  const [history, setHistory] = useState<HistoryRecord[]>([]);
  const [error, setError] = useState('');

  useEffect(() => {
    Promise.all([getTask(id), getTaskHistory(id)])
      .then(([t, h]) => { setTask(t); setHistory(h); })
      .catch(e => setError(e.message));
  }, [id]);

  if (error) return <div className="page-body"><ErrorAlert message={error} /></div>;
  if (!task) return <Loading />;

  return (
    <>
      <div className="page-header">
        <h1>Status History</h1>
        <p>
          <Link to={`/tasks/${task.id}`}>{task.task_code} — {task.title}</Link>
          {' '} · Current: <StatusBadge status={task.status} />
        </p>
      </div>
      <div className="page-body">
        {history.length === 0 ? (
          <EmptyState message="No history records found." />
        ) : (
          <div className="card">
            <div className="history-list">
              {[...history].reverse().map((h, i) => (
                <div key={h.id} className="history-item">
                  <div className="history-dot"
                    style={{ background: i === 0 ? 'var(--primary)' : 'var(--border)' }}
                  />
                  <div className="history-content">
                    <div className="history-transition">
                      {h.previous_status
                        ? <><StatusBadge status={h.previous_status} /> → <StatusBadge status={h.new_status} /></>
                        : <>Task created as <StatusBadge status={h.new_status} /></>
                      }
                    </div>
                    <div className="history-meta mt-1">
                      Changed by <strong style={{ color: 'var(--text)' }}>{h.changed_by}</strong>
                      {' · '}{fmtDate(h.timestamp)}
                      {h.reason && <> · <em>{h.reason}</em></>}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
        <div className="mt-4 text-muted">
          History records are append-only and cannot be edited or deleted.
        </div>
      </div>
    </>
  );
}
