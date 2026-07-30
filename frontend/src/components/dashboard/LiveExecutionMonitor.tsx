import React from 'react';
import { motion } from 'framer-motion';
import { CheckCircle2, Clock, Loader2, AlertCircle } from 'lucide-react';

export type PipelineStage = 'DISCOVERY' | 'CONTEXT' | 'VALIDATION' | 'EXECUTION' | 'DECISION' | 'COMPLETED';

interface Props {
  currentStage: PipelineStage;
  status: 'RUNNING' | 'FAILED' | 'SUCCESS';
}

const STAGES: { id: PipelineStage; label: string }[] = [
  { id: 'DISCOVERY', label: 'Website Discovery' },
  { id: 'CONTEXT', label: 'Context Build' },
  { id: 'VALIDATION', label: 'Validation Plan' },
  { id: 'EXECUTION', label: 'Playwright Execution' },
  { id: 'DECISION', label: 'AI Decision' },
  { id: 'COMPLETED', label: 'Completed' }
];

export function LiveExecutionMonitor({ currentStage, status }: Props) {
  const currentIndex = STAGES.findIndex(s => s.id === currentStage);

  return (
    <div className="card" style={{ marginBottom: '1.5rem', overflowX: 'auto' }}>
      <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '1.5rem' }}>Live Execution Monitor</h3>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', minWidth: '800px' }}>
        {STAGES.map((stage, idx) => {
          const isCompleted = idx < currentIndex || (currentStage === 'COMPLETED' && status === 'SUCCESS');
          const isCurrent = idx === currentIndex && currentStage !== 'COMPLETED';
          const isFailed = isCurrent && status === 'FAILED';

          let icon = <Clock size={20} style={{ color: 'var(--text-muted)' }} />;
          if (isCompleted) icon = <CheckCircle2 size={20} style={{ color: 'var(--color-success)' }} />;
          if (isCurrent && !isFailed) icon = <Loader2 size={20} className="animate-spin" style={{ color: 'var(--color-primary)' }} />;
          if (isFailed) icon = <AlertCircle size={20} style={{ color: 'var(--color-danger)' }} />;

          return (
            <div key={stage.id} style={{ display: 'flex', alignItems: 'center', flex: 1 }}>
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.5rem', flexShrink: 0 }}>
                <motion.div
                  initial={false}
                  animate={{ scale: isCurrent ? 1.1 : 1 }}
                  style={{
                    width: '40px', height: '40px',
                    borderRadius: '50%',
                    background: isCompleted ? 'rgba(16, 185, 129, 0.1)' : isFailed ? 'rgba(239, 68, 68, 0.1)' : isCurrent ? 'rgba(59, 130, 246, 0.1)' : 'var(--bg-card-subtle)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    border: `2px solid ${isCompleted ? 'var(--color-success)' : isFailed ? 'var(--color-danger)' : isCurrent ? 'var(--color-primary)' : 'transparent'}`
                  }}
                >
                  {icon}
                </motion.div>
                <span style={{ fontSize: '0.75rem', fontWeight: isCurrent ? 600 : 500, color: isCurrent ? 'var(--text-main)' : 'var(--text-muted)' }}>
                  {stage.label}
                </span>
              </div>
              
              {idx < STAGES.length - 1 && (
                <div style={{ flex: 1, height: '2px', background: 'var(--bg-card-subtle)', margin: '0 1rem', position: 'relative', top: '-12px' }}>
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: isCompleted ? '100%' : '0%' }}
                    transition={{ duration: 0.5 }}
                    style={{ height: '100%', background: 'var(--color-success)' }}
                  />
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
