import React from 'react';
import { GitPullRequest, CheckCircle2, XCircle } from 'lucide-react';

interface Props {
  originalLocator: string;
  recoveredLocator: string | null;
  recoveryMethod: string;
  success: boolean;
  confidence: number;
}

export function SelfHealingPanel({ originalLocator, recoveredLocator, recoveryMethod, success, confidence }: Props) {
  return (
    <div className="card" style={{ marginBottom: '1.5rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <GitPullRequest size={20} style={{ color: 'var(--color-accent)' }} />
          <h3 style={{ fontSize: '1rem', fontWeight: 600 }}>Self-Healing Analysis</h3>
        </div>
        <span className={`badge ${success ? 'badge-pass' : 'badge-fail'}`} style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
          {success ? <CheckCircle2 size={12} /> : <XCircle size={12} />}
          {success ? 'HEALED' : 'FAILED'}
        </span>
      </div>

      <div className="grid grid-cols-2" style={{ gap: '1rem', marginBottom: '1rem' }}>
        <div style={{ background: 'var(--status-fail-bg)', padding: '1rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--status-fail-border)' }}>
          <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--status-fail-text)', textTransform: 'uppercase' }}>Original Locator</span>
          <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.85rem', marginTop: '0.5rem', wordBreak: 'break-all' }}>
            {originalLocator || 'N/A'}
          </div>
        </div>

        <div style={{ background: 'var(--status-pass-bg)', padding: '1rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--status-pass-border)' }}>
          <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--status-pass-text)', textTransform: 'uppercase' }}>Recovered Locator</span>
          <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.85rem', marginTop: '0.5rem', wordBreak: 'break-all' }}>
            {recoveredLocator || 'Unable to determine'}
          </div>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.75rem', background: 'var(--bg-card-subtle)', borderRadius: 'var(--radius-md)' }}>
        <div>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Recovery Method</span>
          <div style={{ fontSize: '0.9rem', fontWeight: 500 }}>{recoveryMethod}</div>
        </div>
        <div style={{ textAlign: 'right' }}>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>AI Confidence</span>
          <div style={{ fontSize: '0.9rem', fontWeight: 600, color: confidence > 80 ? 'var(--color-success)' : 'var(--color-warning)' }}>
            {confidence}%
          </div>
        </div>
      </div>
    </div>
  );
}
