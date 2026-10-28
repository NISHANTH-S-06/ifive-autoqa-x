import React, { useEffect, useState, useCallback } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import {
  getTask, changeStatus, addDeveloperNotes, addReworkRemarks,
  recordQAResult, getTaskHistory, deleteTask,
} from '../api';
import type { Task, HistoryRecord, QAResult } from '../types';
import { StatusBadge, PriorityBadge, DetailField, Loading, ErrorAlert, SuccessAlert } from '../components';
import { fmtDate } from '../components';
import { useAuth } from '../AuthContext';

export default function TaskDetailPage() {
  const { taskId } = useParams<{ taskId: string }>();
  const id = Number(taskId);
  const navigate = useNavigate();
  const { user } = useAuth();

  const [task, setTask] = useState<Task | null>(null);
  const [history, setHistory] = useState<HistoryRecord[]>([]);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Action modal state
  const [modal, setModal] = useState<'status' | 'notes' | 'remarks' | 'qa' | 'delete' | null>(null);
  const [statusTarget, setStatusTarget] = useState('');
  const [reason, setReason] = useState('');
  const [notesText, setNotesText] = useState('');
  const [remarksText, setRemarksText] = useState('');
  const [qaResult, setQaResult] = useState<QAResult>('PASS');
  const [actionLoading, setActionLoading] = useState(false);

  const loadTask = useCallback(async () => {
    try {
      const [t, h] = await Promise.all([getTask(id), getTaskHistory(id)]);
      setTask(t);
      setHistory(h);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to load task');
    }
  }, [id]);

  useEffect(() => { loadTask(); }, [loadTask]);

  async function runAction() {
    setActionLoading(true);
    setError('');
    try {
      if (modal === 'status') {
        const t = await changeStatus(id, statusTarget, reason || undefined);
        setTask(t);
        setSuccess(`Status changed to ${t.status}`);
      } else if (modal === 'notes') {
        const t = await addDeveloperNotes(id, notesText);
        setTask(t);
        setSuccess('Developer notes saved.');
      } else if (modal === 'remarks') {
        const t = await addReworkRemarks(id, remarksText);
        setTask(t);
        setSuccess('Rework remarks saved.');
      } else if (modal === 'qa') {
        const t = await recordQAResult(id, qaResult, reason || undefined);
        setTask(t);
        setSuccess(`QA result recorded: ${qaResult}`);
      } else if (modal === 'delete') {
        await deleteTask(id);
        navigate('/tasks');
        return;
      }
      setModal(null);
      await loadTask();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Action failed');
    } finally {
      setActionLoading(false);
    }
  }

  if (!task && !error) return <Loading />;
  if (!task) return <div className="page-body"><ErrorAlert message={error} /></div>;

  const role = user?.role ?? '';

  // Determine what actions are available
  const canChangeStatus =
    role === 'SUPERADMIN' ||
    (role === 'DEVELOPER' && task.assigned_developer === user?.username) ||
    role === 'TESTER' ||
    role === 'DELIVERY';

  const canAddNotes = (role === 'DEVELOPER' && task.assigned_developer === user?.username) || role === 'SUPERADMIN';
  const canAddRemarks = role === 'TESTER' || role === 'SUPERADMIN';
  const canQA = (role === 'TESTER' || role === 'SUPERADMIN') && ['TESTING_L2', 'QA_RUNNING'].includes(task.status);
  const canDelete = role === 'SUPERADMIN';

  return (
    <>
      <div className="page-header">
        <div className="flex-between" style={{ paddingBottom: 12 }}>
          <div>
            <h1>{task.title}</h1>
            <p style={{ color: 'var(--text-muted)' }}>{task.task_code} · {task.project_name} / {task.module_name}</p>
          </div>
          <div className="flex-row">
            <StatusBadge status={task.status} />
            <PriorityBadge priority={task.priority} />
            <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>Rev {task.revision}</span>
          </div>
        </div>
      </div>

      <div className="page-body">
        {error && <ErrorAlert message={error} />}
        {success && <SuccessAlert message={success} />}

        {/* Actions */}
        <div className="card mb-4">
          <div className="card-title">Actions</div>
          <div className="flex-row" style={{ flexWrap: 'wrap' }}>
            {canChangeStatus && (
              <button id="btn-change-status" className="btn btn-primary btn-sm"
                onClick={() => { setStatusTarget(''); setReason(''); setModal('status'); }}>
                Change Status
              </button>
            )}
            {canAddNotes && (
              <button id="btn-add-notes" className="btn btn-ghost btn-sm"
                onClick={() => { setNotesText(task.developer_notes ?? ''); setModal('notes'); }}>
                Developer Notes
              </button>
            )}
            {canAddRemarks && (
              <button id="btn-add-remarks" className="btn btn-ghost btn-sm"
                onClick={() => { setRemarksText(task.rework_remarks ?? ''); setModal('remarks'); }}>
                Rework Remarks
              </button>
            )}
            {canQA && (
              <button id="btn-qa-result" className="btn btn-warning btn-sm"
                onClick={() => { setQaResult('PASS'); setReason(''); setModal('qa'); }}>
                Record QA Result
              </button>
            )}
            <Link to={`/tasks/${task.id}/history`} className="btn btn-ghost btn-sm">
              Status History
            </Link>
            {canDelete && (
              <button
                id="btn-delete-task"
                className="btn btn-danger btn-sm"
                style={{ marginLeft: 'auto' }}
                onClick={() => setModal('delete')}
              >
                🗑 Delete Task
              </button>
            )}
          </div>
        </div>

        {/* Detail Grid */}
        <div className="detail-grid">
          <div className="card">
            <div className="card-title">Task Details</div>
            <DetailField label="Description" value={task.description} />
            <DetailField label="Expected Result" value={task.expected_result} />
            <DetailField label="Acceptance Criteria" value={task.acceptance_criteria} />
            <DetailField label="Test Data" value={task.test_data} />
          </div>
          <div>
            <div className="card mb-3">
              <div className="card-title">Assignment</div>
              <DetailField label="Developer" value={task.assigned_developer} />
              <DetailField label="Tester" value={task.assigned_tester} />
              <DetailField label="Given By" value={task.task_given_by} />
              <DetailField label="Target Date" value={task.target_date} />
            </div>
            <div className="card mb-3">
              <div className="card-title">Environment</div>
              <DetailField label="Application URL" value={task.application_url} />
              <DetailField label="Page Path" value={task.page_path} />
              <DetailField label="Environment" value={task.environment} />
            </div>
            <div className="card">
              <div className="card-title">Timestamps</div>
              <DetailField label="Created" value={fmtDate(task.created_at)} />
              <DetailField label="Updated" value={fmtDate(task.updated_at)} />
              <DetailField label="Testing L2 At" value={fmtDate(task.testing_l2_at)} />
              <DetailField label="Completed At" value={fmtDate(task.completed_at)} />
            </div>
          </div>
        </div>

        {/* Notes / Remarks */}
        {(task.developer_notes || task.rework_remarks) && (
          <div className="form-grid mb-4">
            {task.developer_notes && (
              <div className="card">
                <div className="card-title">Developer Notes</div>
                <p style={{ fontSize: 13, whiteSpace: 'pre-wrap' }}>{task.developer_notes}</p>
              </div>
            )}
            {task.rework_remarks && (
              <div className="card">
                <div className="card-title">Rework Remarks</div>
                <p style={{ fontSize: 13, whiteSpace: 'pre-wrap', color: 'var(--danger)' }}>{task.rework_remarks}</p>
              </div>
            )}
          </div>
        )}

        {/* Recent History Preview */}
        {history.length > 0 && (
          <div className="card">
            <div className="flex-between mb-2">
              <div className="card-title" style={{ marginBottom: 0 }}>Recent History</div>
              <Link to={`/tasks/${task.id}/history`} style={{ fontSize: 12 }}>View All</Link>
            </div>
            <div className="history-list">
              {history.slice(-4).reverse().map(h => (
                <div key={h.id} className="history-item">
                  <div className="history-dot" />
                  <div className="history-content">
                    <div className="history-transition">
                      {h.previous_status ? `${h.previous_status} → ${h.new_status}` : `Created as ${h.new_status}`}
                    </div>
                    <div className="history-meta">
                      by {h.changed_by} · {fmtDate(h.timestamp)}
                      {h.reason && ` · ${h.reason}`}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* ── Modals ── */}
      {modal === 'status' && (
        <div className="modal-overlay" onClick={() => setModal(null)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <h2>Change Status</h2>
            <div className="form-group">
              <label className="form-label">New Status</label>
              <select id="modal-new-status" className="form-control" value={statusTarget}
                onChange={e => setStatusTarget(e.target.value)}>
                <option value="">— Select —</option>
                {['ASSIGNED','IN_PROGRESS','TESTING_L1','TESTING_L2','QA_RUNNING','QA_PASSED',
                  'QA_FAILED','REWORK','DELIVERY_READY','DELIVERY_COMPLETED',
                  'NEED_CLARITY','HOLD','CANCELLED'].map(s => (
                  <option key={s} value={s}>{s.replace(/_/g,' ')}</option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Reason (optional)</label>
              <input id="modal-reason" className="form-control" value={reason}
                onChange={e => setReason(e.target.value)} placeholder="Reason for change…" />
            </div>
            <div className="modal-actions">
              <button className="btn btn-ghost" onClick={() => setModal(null)}>Cancel</button>
              <button id="modal-confirm-status" className="btn btn-primary"
                disabled={!statusTarget || actionLoading} onClick={runAction}>
                {actionLoading ? 'Saving…' : 'Confirm'}
              </button>
            </div>
          </div>
        </div>
      )}

      {modal === 'notes' && (
        <div className="modal-overlay" onClick={() => setModal(null)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <h2>Developer Notes</h2>
            <div className="form-group">
              <textarea id="modal-notes" className="form-control" rows={6}
                value={notesText} onChange={e => setNotesText(e.target.value)}
                placeholder="Add your notes here…" />
            </div>
            <div className="modal-actions">
              <button className="btn btn-ghost" onClick={() => setModal(null)}>Cancel</button>
              <button id="modal-save-notes" className="btn btn-primary"
                disabled={!notesText.trim() || actionLoading} onClick={runAction}>
                {actionLoading ? 'Saving…' : 'Save Notes'}
              </button>
            </div>
          </div>
        </div>
      )}

      {modal === 'remarks' && (
        <div className="modal-overlay" onClick={() => setModal(null)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <h2>Rework Remarks</h2>
            <div className="form-group">
              <textarea id="modal-remarks" className="form-control" rows={5}
                value={remarksText} onChange={e => setRemarksText(e.target.value)}
                placeholder="Describe what needs to be reworked…" />
            </div>
            <div className="modal-actions">
              <button className="btn btn-ghost" onClick={() => setModal(null)}>Cancel</button>
              <button id="modal-save-remarks" className="btn btn-primary"
                disabled={!remarksText.trim() || actionLoading} onClick={runAction}>
                {actionLoading ? 'Saving…' : 'Save Remarks'}
              </button>
            </div>
          </div>
        </div>
      )}

      {modal === 'qa' && (
        <div className="modal-overlay" onClick={() => setModal(null)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <h2>Record QA Result</h2>
            <div className="form-group">
              <label className="form-label">Result</label>
              <div className="flex-row">
                {(['PASS','FAIL','BLOCKED'] as QAResult[]).map(r => (
                  <button key={r}
                    id={`qa-${r.toLowerCase()}`}
                    className={`btn btn-sm ${qaResult === r ? (r === 'PASS' ? 'btn-success' : r === 'FAIL' ? 'btn-danger' : 'btn-warning') : 'btn-ghost'}`}
                    onClick={() => setQaResult(r)}
                    type="button"
                  >
                    {r}
                  </button>
                ))}
              </div>
            </div>
            <div className="form-group">
              <label className="form-label">Reason / Notes (optional)</label>
              <textarea id="modal-qa-reason" className="form-control" rows={3}
                value={reason} onChange={e => setReason(e.target.value)}
                placeholder="Details about the result…" />
            </div>
            <div className="modal-actions">
              <button className="btn btn-ghost" onClick={() => setModal(null)}>Cancel</button>
              <button id="modal-confirm-qa" className="btn btn-primary"
                disabled={actionLoading} onClick={runAction}>
                {actionLoading ? 'Saving…' : `Record ${qaResult}`}
              </button>
            </div>
          </div>
        </div>
      )}

      {modal === 'delete' && (
        <div className="modal-overlay" onClick={() => setModal(null)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <h2 style={{ color: 'var(--danger)' }}>⚠ Delete Task</h2>
            <p style={{ marginBottom: 16, color: 'var(--text-muted)', fontSize: 14 }}>
              Are you sure you want to permanently delete{' '}
              <strong style={{ color: 'var(--text)' }}>{task.title}</strong>{' '}
              (<code>{task.task_code}</code>)?
              <br />
              <span style={{ color: 'var(--danger)', fontWeight: 600 }}>
                This action cannot be undone. All status history will also be deleted.
              </span>
            </p>
            <div className="modal-actions">
              <button className="btn btn-ghost" onClick={() => setModal(null)} disabled={actionLoading}>
                Cancel
              </button>
              <button
                id="btn-confirm-delete"
                className="btn btn-danger"
                disabled={actionLoading}
                onClick={runAction}
              >
                {actionLoading ? 'Deleting…' : 'Yes, Delete Task'}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
