import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { listEmployees, listProducts, listStockCounts } from '../api';
import type { Employee, Product, StockCount } from '../types';

export default function DashboardPage() {
  const [empCount, setEmpCount] = useState(0);
  const [prodCount, setProdCount] = useState(0);
  const [stockCounts, setStockCounts] = useState<StockCount[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      listEmployees().then(res => setEmpCount(res.length)).catch(() => 0),
      listProducts().then(res => setProdCount(res.length)).catch(() => 0),
      listStockCounts().then(setStockCounts).catch(() => []),
    ]).finally(() => setLoading(false));
  }, []);

  return (
    <>
      <div className="page-header">
        <h1>Dashboard</h1>
        <p>Demo ERP System Overview</p>
      </div>
      <div className="page-body">
        <div className="form-grid" style={{ marginBottom: 20 }}>
          <div className="card">
            <div className="card-title">Employees</div>
            <div style={{ fontSize: 32, fontWeight: 700, color: 'var(--primary)' }}>{empCount}</div>
            <Link to="/hr/employees" style={{ fontSize: 12, marginTop: 8, display: 'inline-block' }}>View All Employees →</Link>
          </div>
          <div className="card">
            <div className="card-title">Products</div>
            <div style={{ fontSize: 32, fontWeight: 700, color: 'var(--success)' }}>{prodCount}</div>
            <Link to="/inventory/products" style={{ fontSize: 12, marginTop: 8, display: 'inline-block' }}>View Inventory Products →</Link>
          </div>
        </div>

        <div className="card">
          <div className="card-title">Recent Stock Count Audit Log</div>
          {loading ? (
            <p style={{ color: 'var(--text-muted)' }}>Loading records…</p>
          ) : stockCounts.length === 0 ? (
            <p style={{ color: 'var(--text-muted)' }}>No stock count adjustments recorded yet.</p>
          ) : (
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Product</th>
                    <th>Previous Qty</th>
                    <th>Counted Qty</th>
                    <th>Difference</th>
                    <th>Auditor</th>
                    <th>Date</th>
                  </tr>
                </thead>
                <tbody>
                  {stockCounts.slice(0, 5).map(sc => (
                    <tr key={sc.id}>
                      <td>{sc.product_name ?? `Product #${sc.product_id}`}</td>
                      <td>{sc.previous_quantity}</td>
                      <td>{sc.counted_quantity}</td>
                      <td style={{ color: sc.difference >= 0 ? 'var(--success)' : 'var(--danger)', fontWeight: 600 }}>
                        {sc.difference >= 0 ? `+${sc.difference}` : sc.difference}
                      </td>
                      <td>{sc.created_by}</td>
                      <td>{new Date(sc.created_at).toLocaleString()}</td>
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
