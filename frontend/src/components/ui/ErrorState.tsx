import React, { useState } from 'react';
import { AlertTriangle, RefreshCw, ChevronDown, ChevronUp } from 'lucide-react';

interface ErrorStateProps {
  title?: string;
  message?: string;
  details?: string;
  onRetry?: () => void;
}

export function ErrorState({
  title = 'Failed to load data',
  message = 'An unexpected error occurred while processing your request.',
  details,
  onRetry
}: ErrorStateProps) {
  const [showDetails, setShowDetails] = useState(false);

  return (
    <div className="card" style={{ borderLeft: '4px solid var(--color-danger)', padding: '1.5rem' }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: '1rem' }}>
        <div style={{ padding: '0.5rem', borderRadius: 'var(--radius-md)', backgroundColor: 'var(--status-fail-bg)', color: 'var(--color-danger)' }}>
          <AlertTriangle size={20} />
        </div>
        <div style={{ flex: 1 }}>
          <h4 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: '0.25rem' }}>{title}</h4>
          <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginBottom: '0.75rem' }}>{message}</p>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            {onRetry && (
              <button className="btn btn-secondary btn-sm" onClick={onRetry}>
                <RefreshCw size={13} />
                Try Again
              </button>
            )}
            {details && (
              <button 
                className="btn btn-ghost btn-sm"
                onClick={() => setShowDetails(!showDetails)}
                style={{ fontSize: '0.75rem' }}
              >
                {showDetails ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
                {showDetails ? 'Hide Error Log' : 'View Error Log'}
              </button>
            )}
          </div>

          {showDetails && details && (
            <pre style={{ 
              marginTop: '0.75rem', 
              padding: '0.75rem', 
              borderRadius: 'var(--radius-md)', 
              backgroundColor: 'var(--bg-app)', 
              border: '1px solid var(--border-color)', 
              color: 'var(--color-danger)', 
              fontSize: '0.75rem', 
              fontFamily: 'var(--font-mono)', 
              whiteSpace: 'pre-wrap', 
              maxHeight: '200px', 
              overflowY: 'auto' 
            }}>
              {details}
            </pre>
          )}
        </div>
      </div>
    </div>
  );
}
