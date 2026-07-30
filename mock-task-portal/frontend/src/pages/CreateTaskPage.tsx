import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { createTask } from '../api';
import type { TaskCreate } from '../types';
import { ErrorAlert, SuccessAlert } from '../components';

const PRIORITIES = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'];
const ENVIRONMENTS = ['local', 'development', 'staging'];

export default function CreateTaskPage() {
  const navigate = useNavigate();
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);

  const [form, setForm] = useState<TaskCreate>({
    task_code: '',
    project_name: 'Demo ERP',
    module_name: '',
    title: '',
    description: '',
    assigned_developer: 'dev1',
    assigned_tester: 'tester1',
    task_given_by: 'admin',
    target_date: '',
    priority: 'MEDIUM',
    application_url: 'http://localhost:3000',
    page_path: '',
    environment: 'local',
    expected_result: '',
    acceptance_criteria: '',
    test_data: '',
  });

  function set(field: keyof TaskCreate, value: string) {
    setForm(f => ({ ...f, [field]: value }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);
    try {
      const task = await createTask(form);
      setSuccess(`Task ${task.task_code} created successfully.`);
      setTimeout(() => navigate(`/tasks/${task.id}`), 1200);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to create task');
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <div className="page-header">
        <h1>Create Task</h1>
        <p>Create a new task in the Demo ERP project</p>
      </div>
      <div className="page-body">
        {error && <ErrorAlert message={error} />}
        {success && <SuccessAlert message={success} />}

        <form id="create-task-form" onSubmit={handleSubmit}>
          <div className="card mb-4">
            <div className="card-title">Basic Info</div>
            <div className="form-grid">
              <div className="form-group">
                <label className="form-label">Task Code <span className="form-required">*</span></label>
                <input id="task-code" className="form-control" required value={form.task_code}
                  onChange={e => set('task_code', e.target.value)} placeholder="e.g. ERP-101" />
              </div>
              <div className="form-group">
                <label className="form-label">Priority</label>
                <select id="task-priority" className="form-control" value={form.priority}
                  onChange={e => set('priority', e.target.value)}>
                  {PRIORITIES.map(p => <option key={p} value={p}>{p}</option>)}
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">Project Name <span className="form-required">*</span></label>
                <input id="task-project" className="form-control" required value={form.project_name}
                  onChange={e => set('project_name', e.target.value)} />
              </div>
              <div className="form-group">
                <label className="form-label">Module Name <span className="form-required">*</span></label>
                <input id="task-module" className="form-control" required value={form.module_name}
                  onChange={e => set('module_name', e.target.value)} placeholder="e.g. HR Module" />
              </div>
              <div className="form-group" style={{ gridColumn: '1/-1' }}>
                <label className="form-label">Title <span className="form-required">*</span></label>
                <input id="task-title" className="form-control" required value={form.title}
                  onChange={e => set('title', e.target.value)} placeholder="Short descriptive title" />
              </div>
              <div className="form-group" style={{ gridColumn: '1/-1' }}>
                <label className="form-label">Description</label>
                <textarea id="task-description" className="form-control" value={form.description}
                  onChange={e => set('description', e.target.value)} placeholder="Detailed description…" />
              </div>
            </div>
          </div>

          <div className="card mb-4">
            <div className="card-title">Assignment</div>
            <div className="form-grid-3">
              <div className="form-group">
                <label className="form-label">Assigned Developer</label>
                <input id="task-developer" className="form-control" value={form.assigned_developer}
                  onChange={e => set('assigned_developer', e.target.value)} placeholder="Username" />
              </div>
              <div className="form-group">
                <label className="form-label">Assigned Tester</label>
                <input id="task-tester" className="form-control" value={form.assigned_tester}
                  onChange={e => set('assigned_tester', e.target.value)} placeholder="Username" />
              </div>
              <div className="form-group">
                <label className="form-label">Task Given By</label>
                <input className="form-control" value={form.task_given_by}
                  onChange={e => set('task_given_by', e.target.value)} placeholder="Username" />
              </div>
              <div className="form-group">
                <label className="form-label">Target Date</label>
                <input id="task-target-date" type="date" className="form-control" value={form.target_date}
                  onChange={e => set('target_date', e.target.value)} />
              </div>
            </div>
          </div>

          <div className="card mb-4">
            <div className="card-title">Environment</div>
            <div className="form-grid">
              <div className="form-group">
                <label className="form-label">Application URL</label>
                <input id="task-app-url" className="form-control" value={form.application_url}
                  onChange={e => set('application_url', e.target.value)} placeholder="http://localhost:3000" />
              </div>
              <div className="form-group">
                <label className="form-label">Page Path</label>
                <input id="task-page-path" className="form-control" value={form.page_path}
                  onChange={e => set('page_path', e.target.value)} placeholder="/hr/employees/new" />
              </div>
              <div className="form-group">
                <label className="form-label">Environment</label>
                <select id="task-environment" className="form-control" value={form.environment}
                  onChange={e => set('environment', e.target.value)}>
                  {ENVIRONMENTS.map(env => <option key={env} value={env}>{env}</option>)}
                </select>
              </div>
            </div>
          </div>

          <div className="card mb-4">
            <div className="card-title">Test Specification</div>
            <div className="form-group">
              <label className="form-label">Expected Result</label>
              <textarea className="form-control" value={form.expected_result}
                onChange={e => set('expected_result', e.target.value)}
                placeholder="What should happen when the feature works correctly?" />
            </div>
            <div className="form-group">
              <label className="form-label">Acceptance Criteria</label>
              <textarea className="form-control" value={form.acceptance_criteria}
                onChange={e => set('acceptance_criteria', e.target.value)}
                placeholder="Given… When… Then…" rows={4} />
            </div>
            <div className="form-group">
              <label className="form-label">Test Data</label>
              <textarea className="form-control" value={form.test_data}
                onChange={e => set('test_data', e.target.value)}
                placeholder="name=Demo User, role=admin…" />
            </div>
          </div>

          <div className="flex-row">
            <button id="create-task-submit" type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'Creating…' : 'Create Task'}
            </button>
            <button type="button" className="btn btn-ghost" onClick={() => navigate('/tasks')}>
              Cancel
            </button>
          </div>
        </form>
      </div>
    </>
  );
}
