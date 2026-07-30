import React, { useState } from 'react';
import { AlertCircle, X } from 'lucide-react';

interface ConfirmationDialogProps {
  isOpen: boolean;
  title: string;
  message: string;
  confirmLabel?: string;
  cancelLabel?: string;
  variant?: 'danger' | 'warning' | 'primary';
  requireReason?: boolean;
  reasonPlaceholder?: string;
  onConfirm: (reason?: string) => void;
  onCancel: () => void;
  submitting?: boolean;
}

export function ConfirmationDialog({
  isOpen,
  title,
  message,
  confirmLabel = 'Confirm',
  cancelLabel = 'Cancel',
  variant = 'primary',
  requireReason = false,
  reasonPlaceholder = 'Please enter a detailed reason...',
  onConfirm,
  onCancel,
  submitting = false
}: ConfirmationDialogProps) {
  const [reason, setReason] = useState('');
  const [error, setError] = useState('');

  if (!isOpen) return null;

  const handleConfirm = () => {
    if (requireReason && !reason.trim()) {
      setError('A reason is required to proceed.');
      return;
    }
    setError('');
    onConfirm(reason.trim());
  };

  const getConfirmBtnClass = () => {
    if (variant === 'danger') return 'btn-danger';
    if (variant === 'warning') return 'btn-primary';
    return 'btn-primary';
  };

  return (
    <div className="modal-overlay" onClick={onCancel}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <AlertCircle size={20} style={{ color: variant === 'danger' ? 'var(--color-danger)' : 'var(--color-primary)' }} />
            <h3 style={{ fontSize: '1.1rem', fontWeight: 600, color: 'var(--text-main)' }}>{title}</h3>
          </div>
          <button className="btn btn-ghost btn-sm" onClick={onCancel}>
            <X size={16} />
          </button>
        </div>

        <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginBottom: '1.25rem' }}>
          {message}
        </p>

        {requireReason && (
          <div style={{ marginBottom: '1.25rem' }}>
            <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: '0.35rem' }}>
              Reason <span style={{ color: 'var(--color-danger)' }}>*</span>
            </label>
            <textarea
              className="textarea"
              rows={3}
              placeholder={reasonPlaceholder}
              value={reason}
              onChange={(e) => { setReason(e.target.value); setError(''); }}
            />
            {error && <div style={{ fontSize: '0.75rem', color: 'var(--color-danger)', marginTop: '0.25rem' }}>{error}</div>}
          </div>
        )}

        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: '0.75rem' }}>
          <button className="btn btn-secondary" onClick={onCancel} disabled={submitting}>
            {cancelLabel}
          </button>
          <button className={`btn ${getConfirmBtnClass()}`} onClick={handleConfirm} disabled={submitting}>
            {submitting ? 'Processing...' : confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}
