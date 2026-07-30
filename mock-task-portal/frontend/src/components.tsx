import React from 'react';

/** Render a status badge with auto-colour via CSS class */
export function StatusBadge({ status }: { status: string }) {
  return <span className={`badge badge-${status}`}>{status.replace(/_/g, ' ')}</span>;
}

/** Render a priority badge */
export function PriorityBadge({ priority }: { priority: string }) {
  return <span className={`badge badge-${priority}`}>{priority}</span>;
}

/** Format ISO timestamp to human-readable */
export function fmtDate(iso?: string | null): string {
  if (!iso) return '—';
  return new Date(iso).toLocaleString('en-IN', {
    day: '2-digit', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit', hour12: false,
  });
}

/** Field/value display for detail pages */
export function DetailField({
  label,
  value,
}: {
  label: string;
  value?: string | number | null;
}) {
  return (
    <div className="detail-field">
      <div className="detail-field-label">{label}</div>
      <div className={`detail-field-value${!value ? ' empty' : ''}`}>
        {value ?? '—'}
      </div>
    </div>
  );
}

/** Simple loading placeholder */
export function Loading() {
  return <div className="loading">Loading…</div>;
}

/** Error alert */
export function ErrorAlert({ message }: { message: string }) {
  return <div className="alert alert-error">{message}</div>;
}

/** Success alert */
export function SuccessAlert({ message }: { message: string }) {
  return <div className="alert alert-success">{message}</div>;
}

/** Empty state */
export function EmptyState({ message = 'No records found.' }: { message?: string }) {
  return <div className="empty-state"><p>{message}</p></div>;
}
