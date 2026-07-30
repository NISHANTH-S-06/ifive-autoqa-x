import React from 'react';
import { LucideIcon, Inbox } from 'lucide-react';

interface EmptyStateProps {
  title?: string;
  description?: string;
  icon?: LucideIcon;
  actionLabel?: string;
  onAction?: () => void;
}

export function EmptyState({
  title = 'No items found',
  description = 'There are currently no records to display.',
  icon: Icon = Inbox,
  actionLabel,
  onAction
}: EmptyStateProps) {
  return (
    <div className="card" style={{ padding: '3.5rem 1.5rem', textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
      <div style={{ padding: '1rem', borderRadius: 'var(--radius-full)', backgroundColor: 'var(--bg-card-subtle)', color: 'var(--text-subtle)', marginBottom: '1rem' }}>
        <Icon size={32} />
      </div>
      <h3 style={{ fontSize: '1.1rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: '0.35rem' }}>{title}</h3>
      <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)', maxWidth: '400px', marginBottom: actionLabel ? '1.25rem' : 0 }}>{description}</p>
      {actionLabel && onAction && (
        <button className="btn btn-primary" onClick={onAction}>
          {actionLabel}
        </button>
      )}
    </div>
  );
}
