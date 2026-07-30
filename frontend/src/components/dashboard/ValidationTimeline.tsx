import React from 'react';
import { Network, Check, ShieldCheck } from 'lucide-react';

interface ValidationStep {
  step_number: number;
  action: string;
  selector?: string;
  validations: string[];
}

interface Props {
  planTitle: string;
  steps: ValidationStep[];
}

export function ValidationTimeline({ planTitle, steps }: Props) {
  if (!steps || steps.length === 0) {
    return (
      <div className="card" style={{ marginBottom: '1.5rem', opacity: 0.7 }}>
        <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '1rem' }}>Validation Planner Timeline</h3>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>No validations generated yet.</p>
      </div>
    );
  }

  return (
    <div className="card" style={{ marginBottom: '1.5rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
        <Network size={20} style={{ color: 'var(--color-primary)' }} />
        <h3 style={{ fontSize: '1rem', fontWeight: 600 }}>{planTitle || 'Validation Plan'}</h3>
      </div>

      <div style={{ paddingLeft: '1rem', borderLeft: '2px solid var(--border-color)', display: 'flex', flexDirection: 'column', gap: '1.5rem', marginTop: '1rem' }}>
        {steps.map((step) => (
          <div key={step.step_number} style={{ position: 'relative' }}>
            <div style={{
              position: 'absolute',
              left: '-1.45rem',
              top: '0.2rem',
              width: '14px',
              height: '14px',
              borderRadius: '50%',
              background: 'var(--color-primary)',
              border: '2px solid var(--bg-card)'
            }} />
            
            <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
              <div>
                <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)' }}>STEP {step.step_number}</span>
                <div style={{ fontSize: '1rem', fontWeight: 600, marginTop: '0.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  {step.action}
                  {step.selector && <span style={{ fontSize: '0.8rem', fontFamily: 'var(--font-mono)', background: 'var(--bg-card-subtle)', padding: '0.1rem 0.4rem', borderRadius: '4px', fontWeight: 400 }}>{step.selector}</span>}
                </div>
              </div>
              <span className="badge badge-pass" style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                <Check size={12} /> ENFORCED
              </span>
            </div>

            <div style={{ marginTop: '0.75rem', display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
              {step.validations.map((val, idx) => (
                <div key={idx} style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '0.35rem',
                  fontSize: '0.75rem',
                  padding: '0.25rem 0.5rem',
                  background: 'rgba(59, 130, 246, 0.1)',
                  color: 'var(--color-primary)',
                  borderRadius: '4px',
                  fontWeight: 500
                }}>
                  <ShieldCheck size={12} />
                  {val}
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
