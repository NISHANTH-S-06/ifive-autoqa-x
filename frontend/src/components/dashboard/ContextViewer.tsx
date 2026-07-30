import React from 'react';
import { Database, Search, List, MousePointerClick } from 'lucide-react';
import { JSONViewer } from '../ui/JSONViewer';

interface Props {
  contextData: any;
}

export function ContextViewer({ contextData }: Props) {
  if (!contextData) {
    return (
      <div className="card" style={{ marginBottom: '1.5rem', opacity: 0.7 }}>
        <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '1rem' }}>AI Context Viewer</h3>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Awaiting website discovery data...</p>
      </div>
    );
  }

  const buttonsCount = contextData.buttons?.length || 0;
  const linksCount = contextData.links?.length || 0;
  const inputsCount = contextData.inputs?.length || 0;
  const url = contextData.url || 'Unknown URL';

  return (
    <div className="card" style={{ marginBottom: '1.5rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
        <Database size={20} style={{ color: 'var(--color-primary)' }} />
        <h3 style={{ fontSize: '1rem', fontWeight: 600 }}>AI Context Snapshot</h3>
      </div>
      
      <div style={{ padding: '0.75rem', background: 'var(--bg-card-subtle)', borderRadius: 'var(--radius-md)', marginBottom: '1rem' }}>
        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Target Extracted</span>
        <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.85rem', marginTop: '0.25rem' }}>
          {url}
        </div>
      </div>

      <div className="grid grid-cols-3" style={{ gap: '1rem', marginBottom: '1.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '1rem', border: '1px solid var(--border-color)', borderRadius: 'var(--radius-md)' }}>
          <MousePointerClick size={24} style={{ color: 'var(--color-info)' }} />
          <div>
            <div style={{ fontSize: '1.25rem', fontWeight: 700 }}>{buttonsCount}</div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Buttons Discovered</div>
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '1rem', border: '1px solid var(--border-color)', borderRadius: 'var(--radius-md)' }}>
          <Search size={24} style={{ color: 'var(--color-accent)' }} />
          <div>
            <div style={{ fontSize: '1.25rem', fontWeight: 700 }}>{linksCount}</div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Links Crawled</div>
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '1rem', border: '1px solid var(--border-color)', borderRadius: 'var(--radius-md)' }}>
          <List size={24} style={{ color: 'var(--color-warning)' }} />
          <div>
            <div style={{ fontSize: '1.25rem', fontWeight: 700 }}>{inputsCount}</div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Inputs / Forms</div>
          </div>
        </div>
      </div>

      <div style={{ maxHeight: '300px', overflowY: 'auto', border: '1px solid var(--border-color)', borderRadius: 'var(--radius-md)' }}>
        <JSONViewer data={contextData} />
      </div>
    </div>
  );
}
