import React from 'react';

interface MetricCardProps {
  label: string;
  value: string | number;
  percentage?: number;
  color?: string;
  description?: string;
}

export function MetricCard({
  label,
  value,
  percentage,
  color = 'var(--color-primary)',
  description
}: MetricCardProps) {
  return (
    <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '0.5rem' }}>
        <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)' }}>{label}</span>
        <span style={{ 
          fontSize: String(value).length > 18 ? '0.7rem' : String(value).length > 10 ? '0.85rem' : '1.25rem', 
          fontWeight: 700, 
          color: 'var(--text-main)',
          wordBreak: 'break-word',
          textAlign: 'right',
          lineHeight: 1.2
        }}>
          {value}
        </span>
      </div>

      {percentage !== undefined && (
        <div>
          <div style={{ height: '6px', width: '100%', backgroundColor: 'var(--bg-app)', borderRadius: 'var(--radius-full)', overflow: 'hidden' }}>
            <div style={{ height: '100%', width: `${Math.min(100, Math.max(0, percentage))}%`, backgroundColor: color, borderRadius: 'var(--radius-full)', transition: 'width 0.3s ease' }} />
          </div>
          <div style={{ display: 'flex', justifyContent: 'flex-end', fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
            {percentage}%
          </div>
        </div>
      )}

      {description && (
        <span style={{ fontSize: '0.75rem', color: 'var(--text-subtle)' }}>{description}</span>
      )}
    </div>
  );
}
