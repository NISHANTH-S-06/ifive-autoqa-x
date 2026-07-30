import React, { useState } from 'react';
import { Copy, Check } from 'lucide-react';

export interface JSONViewerProps {
  data: unknown;
  title?: string;
  maxHeight?: string;
}

export function JSONViewer({ data, title, maxHeight = '350px' }: JSONViewerProps) {
  const [copied, setCopied] = useState(false);
  const formatted = typeof data === 'string' ? data : JSON.stringify(data, null, 2);

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(formatted);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      /* ignore */
    }
  };

  return (
    <div style={{ borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)', overflow: 'hidden', background: '#0d1117' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.5rem 0.75rem', background: '#161b22', borderBottom: '1px solid #21262d' }}>
        <span style={{ fontSize: '0.75rem', fontWeight: 600, color: '#8b949e', fontFamily: 'var(--font-mono)' }}>
          {title ?? 'JSON Payload'}
        </span>
        <button
          onClick={copy}
          className="btn btn-ghost"
          style={{ padding: '0.2rem 0.4rem', fontSize: '0.7rem', color: '#c9d1d9' }}
          title="Copy payload"
        >
          {copied ? <Check size={13} color="#3fb950" /> : <Copy size={13} />}
          {copied ? 'Copied' : 'Copy'}
        </button>
      </div>
      <pre style={{ margin: 0, padding: '0.75rem', fontSize: '0.8rem', fontFamily: 'var(--font-mono)', color: '#c9d1d9', overflow: 'auto', maxHeight }}>
        <code>{formatted}</code>
      </pre>
    </div>
  );
}
