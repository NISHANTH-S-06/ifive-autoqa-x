import React from 'react';
import { CheckCircle2, XCircle, Clock, PlayCircle, AlertCircle } from 'lucide-react';
import { StatusBadge } from './StatusBadge';

export interface TimelineStep {
  id: string | number;
  title: string;
  subtitle?: string;
  status: string;
  timestamp?: string;
  durationMs?: number;
  details?: string;
  error?: string;
}

interface TimelineProps {
  steps: TimelineStep[];
}

export function Timeline({ steps }: TimelineProps) {
  if (!steps || steps.length === 0) {
    return <div style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>No step events recorded yet.</div>;
  }

  const getStepIcon = (status: string) => {
    const s = status.toUpperCase();
    if (s === 'PASS' || s === 'PASSED' || s === 'APPROVED') return <CheckCircle2 size={16} style={{ color: 'var(--color-success)' }} />;
    if (s === 'FAIL' || s === 'FAILED' || s === 'REJECTED') return <XCircle size={16} style={{ color: 'var(--color-danger)' }} />;
    if (s === 'RUNNING') return <PlayCircle size={16} style={{ color: 'var(--color-accent)' }} />;
    if (s === 'BLOCKED') return <AlertCircle size={16} style={{ color: 'var(--color-warning)' }} />;
    return <Clock size={16} style={{ color: 'var(--text-subtle)' }} />;
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', position: 'relative', paddingLeft: '1rem' }}>
      <div style={{ 
        position: 'absolute', 
        left: '0.45rem', 
        top: '0.5rem', 
        bottom: '0.5rem', 
        width: '2px', 
        backgroundColor: 'var(--border-color)' 
      }} />

      {steps.map((step, idx) => (
        <div key={step.id || idx} style={{ position: 'relative', display: 'flex', alignItems: 'flex-start', gap: '0.75rem' }}>
          <div style={{ 
            position: 'absolute', 
            left: '-1rem', 
            top: '0.2rem', 
            background: 'var(--bg-surface)', 
            borderRadius: '50%', 
            padding: '2px' 
          }}>
            {getStepIcon(step.status)}
          </div>

          <div style={{ flex: 1, backgroundColor: 'var(--bg-card-subtle)', padding: '0.75rem 1rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '0.5rem', flexWrap: 'wrap' }}>
              <span style={{ fontWeight: 600, fontSize: '0.875rem', color: 'var(--text-main)' }}>{step.title}</span>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                {step.durationMs !== undefined && (
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                    {step.durationMs}ms
                  </span>
                )}
                <StatusBadge status={step.status} size="sm" />
              </div>
            </div>

            {step.subtitle && (
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
                {step.subtitle}
              </div>
            )}

            {step.details && (
              <pre style={{ marginTop: '0.5rem', padding: '0.5rem', background: 'var(--bg-app)', border: '1px solid var(--border-color)', borderRadius: 'var(--radius-sm)', fontSize: '0.75rem', fontFamily: 'var(--font-mono)', color: 'var(--text-main)', overflowX: 'auto' }}>
                {step.details}
              </pre>
            )}

            {step.error && (
              <div style={{ marginTop: '0.5rem', padding: '0.5rem', background: 'var(--status-fail-bg)', color: 'var(--status-fail-text)', border: '1px solid var(--status-fail-border)', borderRadius: 'var(--radius-sm)', fontSize: '0.75rem', fontFamily: 'var(--font-mono)' }}>
                {step.error}
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
