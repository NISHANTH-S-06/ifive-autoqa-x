import React from 'react';

interface LoadingSkeletonProps {
  type?: 'card' | 'table' | 'stats' | 'details';
  count?: number;
}

export function LoadingSkeleton({ type = 'card', count = 1 }: LoadingSkeletonProps) {
  const items = Array.from({ length: count });

  if (type === 'stats') {
    return (
      <div className="grid grid-cols-4">
        {items.map((_, i) => (
          <div key={i} className="card" style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            <div className="skeleton" style={{ height: '0.875rem', width: '40%' }}></div>
            <div className="skeleton" style={{ height: '2rem', width: '60%' }}></div>
          </div>
        ))}
      </div>
    );
  }

  if (type === 'table') {
    return (
      <div className="table-container">
        <div style={{ padding: '1rem', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {items.map((_, i) => (
            <div key={i} className="skeleton" style={{ height: '2.5rem', width: '100%' }}></div>
          ))}
        </div>
      </div>
    );
  }

  if (type === 'details') {
    return (
      <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        <div className="skeleton" style={{ height: '1.5rem', width: '50%' }}></div>
        <div className="skeleton" style={{ height: '1rem', width: '80%' }}></div>
        <div className="skeleton" style={{ height: '10rem', width: '100%' }}></div>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-3">
      {items.map((_, i) => (
        <div key={i} className="card" style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          <div className="skeleton" style={{ height: '1.25rem', width: '70%' }}></div>
          <div className="skeleton" style={{ height: '0.875rem', width: '90%' }}></div>
          <div className="skeleton" style={{ height: '4rem', width: '100%' }}></div>
        </div>
      ))}
    </div>
  );
}
