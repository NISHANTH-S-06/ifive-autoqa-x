import React from 'react';
import { BrainCircuit, ShieldAlert, Activity, GitMerge } from 'lucide-react';
import { MetricCard } from '../ui/MetricCard';

interface Props {
  decision: 'HEAL' | 'ABORT' | 'CONTINUE' | 'PENDING';
  confidenceScore: number;
  riskLevel: 'LOW' | 'MEDIUM' | 'HIGH';
  healingAttempts: number;
  reason: string;
}

export function AIDecisionPanel({ decision, confidenceScore, riskLevel, healingAttempts, reason }: Props) {
  return (
    <div className="card" style={{ marginBottom: '1.5rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
        <BrainCircuit size={20} style={{ color: 'var(--color-primary)' }} />
        <h3 style={{ fontSize: '1rem', fontWeight: 600 }}>AI Decision Engine</h3>
      </div>
      
      <div className="grid grid-cols-4" style={{ marginBottom: '1.25rem' }}>
        <MetricCard label="Confidence Score" value={`${confidenceScore}%`} percentage={confidenceScore} color="var(--color-primary)" />
        <MetricCard label="Decision" value={decision} percentage={100} color={decision === 'ABORT' ? 'var(--color-danger)' : decision === 'HEAL' ? 'var(--color-warning)' : 'var(--color-success)'} />
        <MetricCard label="Risk Level" value={riskLevel} percentage={riskLevel === 'HIGH' ? 90 : riskLevel === 'MEDIUM' ? 50 : 10} color={riskLevel === 'HIGH' ? 'var(--color-danger)' : 'var(--color-info)'} />
        <MetricCard label="Healing Attempts" value={healingAttempts.toString()} percentage={healingAttempts > 0 ? 100 : 0} color="var(--color-accent)" />
      </div>

      <div style={{ background: 'var(--bg-card-subtle)', padding: '1rem', borderRadius: 'var(--radius-md)' }}>
        <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Reasoning / Recommendation</span>
        <p style={{ fontSize: '0.9rem', marginTop: '0.5rem', lineHeight: 1.5 }}>
          {reason || "Awaiting execution failure to analyze."}
        </p>
      </div>
    </div>
  );
}
