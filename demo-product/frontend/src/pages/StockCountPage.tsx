import React, { useEffect, useState } from 'react';
import { createStockCount, listProducts, listStockCounts } from '../api';
import type { Product, StockCount } from '../types';

export default function StockCountPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [history, setHistory] = useState<StockCount[]>([]);
  const [selectedProductId, setSelectedProductId] = useState<number>(0);
  const [countedQty, setCountedQty] = useState<number>(0);
  const [notes, setNotes] = useState('');

  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  function loadData() {
    return Promise.all([
      listProducts().then(prods => {
        setProducts(prods);
        if (prods.length > 0 && selectedProductId === 0) {
          setSelectedProductId(prods[0].id);
          setCountedQty(prods[0].current_quantity);
        }
      }),
      listStockCounts().then(setHistory),
    ]);
  }

  useEffect(() => {
    loadData().finally(() => setLoading(false));
  }, []);

  const selectedProduct = products.find(p => p.id === selectedProductId);
  const currentQty = selectedProduct ? selectedProduct.current_quantity : 0;
  const difference = countedQty - currentQty;

  function handleProductChange(id: number) {
    setSelectedProductId(id);
    const p = products.find(prod => prod.id === id);
    if (p) {
      setCountedQty(p.current_quantity);
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (countedQty < 0) {
      setError('Counted quantity cannot be negative.');
      return;
    }

    setSubmitting(true);
    try {
      const res = await createStockCount({
        product_id: selectedProductId,
        counted_quantity: countedQty,
        notes: notes || undefined,
      });
      setSuccess(`Stock count submitted for ${res.product_name || 'product'}. Difference: ${res.difference}`);
      setNotes('');
      await loadData();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to submit stock count');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <>
      <div className="page-header">
        <h1>Inventory Stock Count</h1>
        <p>Physical Stock Reconciliation & Audit Log</p>
      </div>

      <div className="page-body">
        {error && <div className="alert alert-error">{error}</div>}
        {success && <div className="alert alert-success">{success}</div>}

        <div className="card" style={{ maxWidth: 640 }}>
          <div className="card-title">Stock Count Entry Form</div>
          {loading ? (
            <p style={{ color: 'var(--text-muted)' }}>Loading products…</p>
          ) : (
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label className="form-label" htmlFor="stock-product">Select Product *</label>
                <select
                  id="stock-product"
                  data-testid="stock-product"
                  className="form-control"
                  value={selectedProductId}
                  onChange={e => handleProductChange(Number(e.target.value))}
                >
                  {products.map(p => (
                    <option key={p.id} value={p.id}>{p.product_code} — {p.name}</option>
                  ))}
                </select>
              </div>

              <div className="form-grid">
                <div className="form-group">
                  <label className="form-label">Current System Quantity</label>
                  <input
                    data-testid="stock-current-quantity"
                    className="form-control"
                    type="number"
                    readOnly
                    value={currentQty}
                    style={{ background: 'var(--surface-2)' }}
                  />
                </div>

                <div className="form-group">
                  <label className="form-label" htmlFor="stock-counted-quantity">Physical Counted Quantity *</label>
                  <input
                    id="stock-counted-quantity"
                    data-testid="stock-counted-quantity"
                    className="form-control"
                    type="number"
                    min="0"
                    required
                    value={countedQty}
                    onChange={e => setCountedQty(Number(e.target.value))}
                  />
                </div>
              </div>

              <div className="form-group">
                <label className="form-label">Calculated Difference</label>
                <div
                  data-testid="stock-difference"
                  style={{
                    fontSize: 18,
                    fontWeight: 700,
                    color: difference >= 0 ? 'var(--success)' : 'var(--danger)',
                  }}
                >
                  {difference >= 0 ? `+${difference}` : difference}
                </div>
              </div>

              <div className="form-group">
                <label className="form-label" htmlFor="stock-notes">Audit Notes</label>
                <textarea
                  id="stock-notes"
                  data-testid="stock-notes"
                  className="form-control"
                  rows={2}
                  value={notes}
                  onChange={e => setNotes(e.target.value)}
                  placeholder="Reason for variance or audit remarks..."
                />
              </div>

              <button
                type="submit"
                data-testid="stock-submit"
                className="btn btn-primary"
                disabled={submitting}
              >
                {submitting ? 'Submitting…' : 'Submit Stock Adjustment'}
              </button>
            </form>
          )}
        </div>

        <div className="card">
          <div className="card-title">Stock Audit History Log</div>
          {history.length === 0 ? (
            <p style={{ color: 'var(--text-muted)' }}>No audit history records available.</p>
          ) : (
            <div className="table-wrap">
              <table data-testid="stock-history-table">
                <thead>
                  <tr>
                    <th>Product</th>
                    <th>Previous Qty</th>
                    <th>Counted Qty</th>
                    <th>Difference</th>
                    <th>Notes</th>
                    <th>Auditor</th>
                    <th>Timestamp</th>
                  </tr>
                </thead>
                <tbody>
                  {history.map(row => (
                    <tr key={row.id}>
                      <td style={{ fontWeight: 600 }}>{row.product_name}</td>
                      <td>{row.previous_quantity}</td>
                      <td>{row.counted_quantity}</td>
                      <td style={{ fontWeight: 700, color: row.difference >= 0 ? 'var(--success)' : 'var(--danger)' }}>
                        {row.difference >= 0 ? `+${row.difference}` : row.difference}
                      </td>
                      <td>{row.notes || '—'}</td>
                      <td>{row.created_by}</td>
                      <td>{new Date(row.created_at).toLocaleString()}</td>
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
