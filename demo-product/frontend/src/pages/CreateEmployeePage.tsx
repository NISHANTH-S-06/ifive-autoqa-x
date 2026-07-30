import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { createEmployee, listDepartments, listDemoSettings } from '../api';
import type { Department } from '../types';

export default function CreateEmployeePage() {
  const navigate = useNavigate();
  const [departments, setDepartments] = useState<Department[]>([]);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [departmentId, setDepartmentId] = useState<number>(0);
  const [joiningDate, setJoiningDate] = useState('2026-02-01');
  const [active, setActive] = useState(true);
  const [notes, setNotes] = useState('');

  const [error, setError] = useState('');
  const [successMsg, setSuccessMsg] = useState('');
  const [loading, setLoading] = useState(false);
  const [hideSuccessToggle, setHideSuccessToggle] = useState(false);

  useEffect(() => {
    listDepartments().then(depts => {
      setDepartments(depts);
      if (depts.length > 0) setDepartmentId(depts[0].id);
    }).catch(() => {});

    listDemoSettings().then(settings => {
      const toggle = settings.find(s => s.key === 'employee_success_message_missing');
      if (toggle && toggle.enabled) {
        setHideSuccessToggle(true);
      }
    }).catch(() => {});
  }, []);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError('');
    setSuccessMsg('');
    setLoading(true);

    try {
      const emp = await createEmployee({
        name,
        email,
        department_id: departmentId,
        joining_date: joiningDate,
        active,
        notes: notes || undefined,
      });

      // If employee_success_message_missing bug toggle is ON, do NOT show success message!
      if (!hideSuccessToggle) {
        setSuccessMsg(`Employee ${emp.name} (${emp.employee_code}) created successfully.`);
      }

      // Navigate to list after short delay
      setTimeout(() => {
        navigate('/hr/employees');
      }, 1500);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to create employee');
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <div className="page-header">
        <h1>Create Employee</h1>
        <p>Add new employee to HR system</p>
      </div>

      <div className="page-body">
        {error && <div className="alert alert-error">{error}</div>}
        {successMsg && (
          <div data-testid="employee-success" className="alert alert-success">
            {successMsg}
          </div>
        )}

        <form onSubmit={handleSubmit} style={{ maxWidth: 640 }}>
          <div className="card">
            <div className="form-group">
              <label className="form-label" htmlFor="employee-name">Employee Name *</label>
              <input
                id="employee-name"
                data-testid="employee-name"
                className="form-control"
                type="text"
                required
                value={name}
                onChange={e => setName(e.target.value)}
                placeholder="e.g. Jane Smith"
              />
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="employee-email">Email Address *</label>
              <input
                id="employee-email"
                data-testid="employee-email"
                className="form-control"
                type="email"
                required
                value={email}
                onChange={e => setEmail(e.target.value)}
                placeholder="e.g. jane.smith@demo.local"
              />
            </div>

            <div className="form-grid">
              <div className="form-group">
                <label className="form-label" htmlFor="employee-department">Department *</label>
                <select
                  id="employee-department"
                  data-testid="employee-department"
                  className="form-control"
                  required
                  value={departmentId}
                  onChange={e => setDepartmentId(Number(e.target.value))}
                >
                  {departments.map(d => (
                    <option key={d.id} value={d.id}>{d.name}</option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label className="form-label" htmlFor="employee-joining-date">Joining Date *</label>
                <input
                  id="employee-joining-date"
                  data-testid="employee-joining-date"
                  className="form-control"
                  type="date"
                  required
                  value={joiningDate}
                  onChange={e => setJoiningDate(e.target.value)}
                />
              </div>
            </div>

            <div className="form-group" style={{ display: 'flex', alignItems: 'center', gap: 8, marginTop: 8 }}>
              <input
                id="employee-active"
                data-testid="employee-active"
                type="checkbox"
                checked={active}
                onChange={e => setActive(e.target.checked)}
              />
              <label htmlFor="employee-active" className="form-label" style={{ marginBottom: 0, cursor: 'pointer' }}>
                Active Employment Status
              </label>
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="employee-notes">Notes</label>
              <textarea
                id="employee-notes"
                data-testid="employee-notes"
                className="form-control"
                rows={3}
                value={notes}
                onChange={e => setNotes(e.target.value)}
                placeholder="Optional notes..."
              />
            </div>

            <div style={{ display: 'flex', gap: 12, marginTop: 24 }}>
              <button
                type="submit"
                data-testid="employee-save"
                className="btn btn-primary"
                disabled={loading}
              >
                {loading ? 'Saving…' : 'Save Employee'}
              </button>
              <button
                type="button"
                className="btn btn-ghost"
                onClick={() => navigate('/hr/employees')}
              >
                Cancel
              </button>
            </div>
          </div>
        </form>
      </div>
    </>
  );
}
