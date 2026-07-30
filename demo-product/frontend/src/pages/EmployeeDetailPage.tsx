import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getEmployee } from '../api';
import type { Employee } from '../types';

export default function EmployeeDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [employee, setEmployee] = useState<Employee | null>(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (id) {
      getEmployee(Number(id))
        .then(setEmployee)
        .catch(err => setError(err.message))
        .finally(() => setLoading(false));
    }
  }, [id]);

  if (loading) return <div className="page-body">Loading details…</div>;
  if (error || !employee) return <div className="page-body"><div className="alert alert-error">{error || 'Employee not found'}</div></div>;

  return (
    <>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1>{employee.name}</h1>
          <p>{employee.employee_code} · {employee.department_name}</p>
        </div>
        <Link to="/hr/employees" className="btn btn-ghost">← Back to List</Link>
      </div>

      <div className="page-body">
        <div className="card" style={{ maxWidth: 640 }}>
          <div className="card-title">Employee Information</div>
          <div className="form-grid">
            <div>
              <span className="form-label">Employee Name</span>
              <div data-testid="detail-name" style={{ fontWeight: 600 }}>{employee.name}</div>
            </div>
            <div>
              <span className="form-label">Email Address</span>
              <div data-testid="detail-email">{employee.email}</div>
            </div>
            <div>
              <span className="form-label">Department</span>
              <div data-testid="detail-department">{employee.department_name}</div>
            </div>
            <div>
              <span className="form-label">Joining Date</span>
              <div data-testid="detail-joining-date">{employee.joining_date}</div>
            </div>
            <div>
              <span className="form-label">Status</span>
              <div>
                <span className={`badge ${employee.active ? 'badge-active' : 'badge-inactive'}`}>
                  {employee.active ? 'Active' : 'Inactive'}
                </span>
              </div>
            </div>
          </div>
          {employee.notes && (
            <div style={{ marginTop: 16, paddingTop: 16, borderTop: '1px solid var(--border)' }}>
              <span className="form-label">Notes</span>
              <div data-testid="detail-notes">{employee.notes}</div>
            </div>
          )}
        </div>
      </div>
    </>
  );
}
