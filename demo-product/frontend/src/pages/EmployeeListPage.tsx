import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { listEmployees } from '../api';
import type { Employee } from '../types';
import { useAuth } from '../AuthContext';

export default function EmployeeListPage() {
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const { user } = useAuth();

  useEffect(() => {
    listEmployees()
      .then(setEmployees)
      .catch(err => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  const canCreate = user && ['DEMO_ADMIN', 'HR_USER'].includes(user.role);

  return (
    <>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1>Employee Directory</h1>
          <p>HR Management Module · {employees.length} employees</p>
        </div>
        {canCreate && (
          <Link to="/hr/employees/new" className="btn btn-primary">
            + Create Employee
          </Link>
        )}
      </div>

      <div className="page-body">
        {error && <div className="alert alert-error">{error}</div>}

        <div className="card" style={{ padding: 0 }}>
          {loading ? (
            <div style={{ padding: 24, color: 'var(--text-muted)' }}>Loading employees…</div>
          ) : employees.length === 0 ? (
            <div style={{ padding: 24, color: 'var(--text-muted)' }}>No employees found.</div>
          ) : (
            <div className="table-wrap">
              <table data-testid="employee-table">
                <thead>
                  <tr>
                    <th>Code</th>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Department</th>
                    <th>Joining Date</th>
                    <th>Status</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {employees.map(emp => (
                    <tr key={emp.id}>
                      <td style={{ fontFamily: 'monospace' }}>{emp.employee_code}</td>
                      <td style={{ fontWeight: 600 }}>{emp.name}</td>
                      <td>{emp.email}</td>
                      <td>{emp.department_name ?? '—'}</td>
                      <td>{emp.joining_date}</td>
                      <td>
                        <span className={`badge ${emp.active ? 'badge-active' : 'badge-inactive'}`}>
                          {emp.active ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                      <td>
                        <Link
                          to={`/hr/employees/${emp.id}`}
                          data-testid={`employee-view-${emp.id}`}
                          className="btn btn-ghost"
                          style={{ padding: '4px 10px', fontSize: 12 }}
                        >
                          View Details
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
