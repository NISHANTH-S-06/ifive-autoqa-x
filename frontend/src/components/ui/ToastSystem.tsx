import React from 'react';
import { useToasts } from '../../stores/toastStore';
import { CheckCircle2, AlertTriangle, XCircle, Info, X } from 'lucide-react';

export function ToastSystem() {
  const { toasts, dismiss } = useToasts();

  if (!toasts || toasts.length === 0) return null;

  const getIcon = (type: string) => {
    switch (type) {
      case 'success': return <CheckCircle2 size={18} style={{ color: 'var(--color-success)' }} />;
      case 'error': return <XCircle size={18} style={{ color: 'var(--color-danger)' }} />;
      case 'warning': return <AlertTriangle size={18} style={{ color: 'var(--color-warning)' }} />;
      default: return <Info size={18} style={{ color: 'var(--color-info)' }} />;
    }
  };

  return (
    <div className="toast-container">
      {toasts.map((t) => (
        <div key={t.id} className={`toast toast-${t.type}`}>
          {getIcon(t.type)}
          <div style={{ flex: 1 }}>
            {t.title && <div style={{ fontWeight: 600, fontSize: '0.85rem' }}>{t.title}</div>}
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{t.message}</div>
          </div>
          <button 
            onClick={() => dismiss(t.id)} 
            style={{ background: 'none', border: 'none', color: 'var(--text-subtle)', cursor: 'pointer', padding: '0.2rem' }}
          >
            <X size={14} />
          </button>
        </div>
      ))}
    </div>
  );
}
