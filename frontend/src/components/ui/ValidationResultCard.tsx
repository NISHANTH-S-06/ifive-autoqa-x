import React from 'react';
import { CheckCircle2, XCircle, AlertTriangle, ShieldCheck } from 'lucide-react';
import { StatusBadge } from './StatusBadge';

interface ValidationItem {
  layer: 'UI' | 'API' | 'DB' | 'ACCESSIBILITY' | 'PERFORMANCE' | 'CONSOLE' | string;
  status: string;
  mandatory?: boolean;
  score?: number | string;
  details?: string;
  warnings?: string[];
  errors?: string[];
}

interface ValidationResultCardProps {
  validations: ValidationItem[];
}

export function ValidationResultCard({ validations }: ValidationResultCardProps) {
  if (!validations || validations.length === 0) {
    return <div style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>No advanced validation layers executed.</div>;
  }

  return (
    <div className="grid grid-cols-2">
      {validations.map((item, idx) => {
        const isPass = item.status.toUpperCase() === 'PASS' || item.status.toUpperCase() === 'PASSED';
        const isFail = item.status.toUpperCase() === 'FAIL' || item.status.toUpperCase() === 'FAILED';

        return (
          <div key={idx} className="card" style={{ borderLeft: `4px solid ${isPass ? 'var(--color-success)' : isFail ? 'var(--color-danger)' : 'var(--color-warning)'}` }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <ShieldCheck size={18} style={{ color: 'var(--color-primary)' }} />
                <span style={{ fontWeight: 700, fontSize: '0.875rem', color: 'var(--text-main)' }}>{item.layer} Validation</span>
                {item.mandatory && (
                  <span style={{ fontSize: '0.65rem', fontWeight: 600, padding: '0.1rem 0.35rem', borderRadius: 'var(--radius-sm)', background: 'var(--status-rejected-bg)', color: 'var(--status-rejected-text)' }}>
                    MANDATORY
                  </span>
                )}
              </div>
              <StatusBadge status={item.status} size="sm" />
            </div>

            {item.score !== undefined && (
              <div style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--text-main)', margin: '0.25rem 0' }}>
                Score: {item.score}
              </div>
            )}

            {item.details && (
              <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>{item.details}</p>
            )}

            {item.errors && item.errors.length > 0 && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem', marginTop: '0.5rem' }}>
                {item.errors.map((err, i) => (
                  <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', fontSize: '0.75rem', color: 'var(--color-danger)' }}>
                    <XCircle size={13} />
                    <span>{err}</span>
                  </div>
                ))}
              </div>
            )}

            {item.warnings && item.warnings.length > 0 && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem', marginTop: '0.5rem' }}>
                {item.warnings.map((warn, i) => (
                  <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', fontSize: '0.75rem', color: 'var(--color-warning)' }}>
                    <AlertTriangle size={13} />
                    <span>{warn}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
